import unittest
from unittest.mock import MagicMock, patch
import zlib

import pdf_scanner


class TestPdfSecurityScanner(unittest.TestCase):
    def _build_pdf(self, body: bytes, header: bytes = b"%PDF-1.7\r\n", trailer_extra: bytes = b"") -> bytes:
        return (
            header
            + b"1 0 obj\r\n<< /Type /Catalog /Pages 2 0 R >>\r\nendobj\r\n"
            + body
            + b"\r\n%%EOF"
            + trailer_extra
        )

    def test_clean_minimal_pdf(self) -> None:
        raw = self._build_pdf(b"2 0 obj\r\n<< /Type /Pages /Count 0 >>\r\nendobj")
        res = pdf_scanner.scan_pdf_bytes(raw, "clean.pdf")
        self.assertEqual(res["verdict"], "CLEAN")
        self.assertEqual(res["risk_score"], 0)
        self.assertEqual(res["tags"], {})

    def test_detects_direct_javascript_and_openaction(self) -> None:
        body = (
            b"2 0 obj\r\n<< /OpenAction 3 0 R /Type /Catalog >>\r\nendobj\r\n"
            b"3 0 obj\r\n<< /S /JavaScript /JS (app.alert(1);) >>\r\nendobj"
        )
        res = pdf_scanner.scan_pdf_bytes(self._build_pdf(body), "malicious_js.pdf")
        self.assertEqual(res["verdict"], "HIGH_RISK")
        self.assertGreaterEqual(res["risk_score"], 75)
        self.assertIn("JS", res["tags"])
        self.assertIn("JavaScript", res["tags"])
        self.assertIn("OpenAction", res["tags"])

    def test_detects_hex_obfuscated_pdf_names(self) -> None:
        # /#4a#53 -> /JS, /#4c#61#75#6e#63#68 -> /Launch
        body = b"2 0 obj\r\n<< /#4a#53 (eval(unescape('abc'))) /#4c#61#75#6e#63#68 (/bin/sh) >>\r\nendobj"
        res = pdf_scanner.scan_pdf_bytes(self._build_pdf(body), "obfuscated.pdf")
        self.assertEqual(res["verdict"], "HIGH_RISK")
        self.assertEqual(res["risk_score"], 100)
        decoded_set = {item["decoded"] for item in res["obfuscated_tags"]}
        self.assertIn("JS", decoded_set)
        self.assertIn("Launch", decoded_set)

    def test_detects_hidden_tags_inside_compressed_objstm(self) -> None:
        hidden_obj = b"<< /S /Launch /Win << /F (cmd.exe) >> /JS (util.printf('%45000f',1.0)) >>"
        compressed = zlib.compress(hidden_obj)
        body = (
            b"4 0 obj\r\n<< /Type /ObjStm /Filter /FlateDecode /Length "
            + str(len(compressed)).encode("ascii")
            + b" >>\r\nstream\r\n"
            + compressed
            + b"\r\nendstream\r\nendobj"
        )
        res = pdf_scanner.scan_pdf_bytes(self._build_pdf(body), "objstm_exploit.pdf")
        self.assertEqual(res["verdict"], "HIGH_RISK")
        self.assertEqual(res["streams"]["objstm"], 1)
        self.assertIn("Launch", res["tags"])
        self.assertIn("JS", res["tags"])
        self.assertTrue(any("util.printf" in f for f in res["findings"]))

    def test_ignores_random_binary_bytes_in_non_objstm_stream(self) -> None:
        # Simulate random compressed image/font bytes containing '/JS\x98*' and '/Launch ' inside raw stream
        fake_binary_stream = b"\x89\xfe/JS\x98*\x00/Launch\xff\x12"
        body = (
            b"5 0 obj\r\n<< /Subtype /Image /Length 22 >>\r\nstream\r\n"
            + fake_binary_stream
            + b"\r\nendstream\r\nendobj"
        )
        res = pdf_scanner.scan_pdf_bytes(self._build_pdf(body), "benign_image.pdf")
        self.assertEqual(res["verdict"], "CLEAN")
        self.assertEqual(res["risk_score"], 0)
        self.assertNotIn("JS", res["tags"])
        self.assertNotIn("Launch", res["tags"])

    def test_benign_empty_acroform_is_clean(self) -> None:
        body = b"6 0 obj\r\n<< /AcroForm << /Fields[] /DA (/Helv 0 Tf) >> >>\r\nendobj"
        res = pdf_scanner.scan_pdf_bytes(self._build_pdf(body), "indesign_book.pdf")
        self.assertEqual(res["verdict"], "CLEAN")
        self.assertEqual(res["risk_score"], 0)

    def test_polyglot_header_and_trailing_payload_detection(self) -> None:
        prepended = b"MZ\x90\x00\x03\x00\x00\x00%PDF-1.5\r\n"
        trailing = b"\r\n" + (b"A" * 256)
        raw = self._build_pdf(b"2 0 obj << >> endobj", header=prepended, trailer_extra=trailing)
        res = pdf_scanner.scan_pdf_bytes(raw, "polyglot.pdf.exe")
        self.assertEqual(res["verdict"], "HIGH_RISK")
        self.assertGreater(res["header_offset"], 0)
        self.assertGreater(res["trailing_bytes"], 128)
        self.assertTrue(any("Double extension" in f for f in res["findings"]))

    def test_url_normalization_strips_tracking_and_flags_smb(self) -> None:
        body = (
            b"7 0 obj\r\n<< /A << /S /URI /URI (https://Example.com/doc?id=42&utm_source=tg&fbclid=123&gclid=abc) >> >>\r\n"
            b"8 0 obj\r\n<< /A << /S /URI /URI (smb://198.51.100.7/share/steal) >> >>\r\nendobj"
        )
        res = pdf_scanner.scan_pdf_bytes(self._build_pdf(body), "links.pdf")
        self.assertEqual(res["verdict"], "SUSPICIOUS")
        self.assertIn("https://example.com/doc?id=42", res["uris"]["sample"])
        self.assertIn("smb://198.51.100.7/share/steal", res["uris"]["suspicious"])

    def test_safe_text_extraction_with_tounicode_cmap(self) -> None:
        cmap_stream = zlib.compress(
            b"/CIDInit /ProcSet findresource begin 12 dict begin begincmap\n"
            b"2 beginbfchar\n<0001> <0048>\n<0002> <0069>\nendbfchar\n"
            b"endcmap"
        )
        page_stream = zlib.compress(b"BT <00010002> Tj ( World) Tj ET")
        body = (
            b"2 0 obj\r\n<< /Filter /FlateDecode >>\r\nstream\r\n" + cmap_stream + b"\r\nendstream\r\nendobj\r\n"
            b"3 0 obj\r\n<< /Filter /FlateDecode >>\r\nstream\r\n" + page_stream + b"\r\nendstream\r\nendobj"
        )
        raw = self._build_pdf(body)
        extracted = pdf_scanner.extract_safe_text_bytes(raw)
        self.assertIn("Hi", extracted)
        self.assertIn("World", extracted)

    def test_disarm_preserves_exact_byte_length(self) -> None:
        body = (
            b"2 0 obj\r\n<< /OpenAction 3 0 R /AA << >> /Launch (cmd) >>\r\nendobj\r\n"
            b"3 0 obj\r\n<< /S /JavaScript /JS (alert(1)) /RichMedia << >> >>\r\nendobj"
        )
        original = self._build_pdf(body)
        disarmed, actions = pdf_scanner.disarm_pdf_bytes(original)
        self.assertEqual(len(original), len(disarmed))
        self.assertGreaterEqual(len(actions), 5)
        res_after = pdf_scanner.scan_pdf_bytes(disarmed, "disarmed.pdf")
        self.assertEqual(res_after["verdict"], "CLEAN")
        self.assertEqual(res_after["risk_score"], 0)

    def test_linux_xdg_origin_xattr_and_mime_handler(self) -> None:
        with patch.object(pdf_scanner.sys, "platform", "linux"):
            with patch.object(pdf_scanner.os, "getxattr", create=True, return_value=b"https://Example.com/a.pdf?utm_source=x"):
                q = pdf_scanner.get_macos_quarantine_info("dummy.pdf")
                self.assertTrue(q["quarantined"])
                self.assertEqual(q["origin_url"], "https://example.com/a.pdf")

            mock_proc = MagicMock(returncode=0, stdout="org.gnome.Evince.desktop\n")
            with patch.object(pdf_scanner.subprocess, "run", return_value=mock_proc):
                viewers = pdf_scanner.check_macos_pdf_environment()
                self.assertEqual(len(viewers), 1)
                self.assertEqual(viewers[0]["app"], "org.gnome.Evince.desktop")


if __name__ == "__main__":
    unittest.main()
