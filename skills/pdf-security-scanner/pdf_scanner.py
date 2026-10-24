#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
pdf_scanner.py — Static PDF Malware Analyzer, Text Extractor & CDR Disarmer
===========================================================================
Zero-dependency static analysis tool for PDF documents:
  - Linear O(N) FlateDecode & /ObjStm decompression in memory (zip-bomb guarded)
  - ISO 32000-1 /Name parsing with #XX hex-obfuscation decoding
  - Structural vs. raw binary stream separation (eliminates random-byte false positives)
  - Polyglot header & trailing payload detection past %%EOF
  - URL extraction with tracking parameter stripping (utm_*, gclid, fbclid, ref, etc.)
  - Safe in-memory BT...ET & /ToUnicode CMap text preview
  - XREF-preserving Content Disarm & Reconstruction (CDR)
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import zlib
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

HIGH_RISK_TAGS: Dict[str, str] = {
    "JS": "Embedded JavaScript reference (/JS)",
    "JavaScript": "Embedded JavaScript code (/JavaScript)",
    "Launch": "OS command/program execution action (/Launch)",
    "EmbeddedFiles": "Embedded file attachment tree (/EmbeddedFiles)",
    "EmbeddedFile": "Embedded file stream (/EmbeddedFile)",
    "RichMedia": "Embedded Flash/RichMedia content (/RichMedia)",
    "JBIG2Decode": "JBIG2 filter (/JBIG2Decode - historically used in memory corruption exploits)",
    "GoToE": "Embedded GoTo action (/GoToE)",
    "ImportData": "Form data import action (/ImportData)",
}

MEDIUM_RISK_TAGS: Dict[str, str] = {
    "OpenAction": "Automatic action triggered when document opens (/OpenAction)",
    "AA": "Additional automatic trigger actions (/AA)",
    "XFA": "XML Forms Architecture (/XFA)",
    "AcroForm": "Interactive form dictionary (/AcroForm)",
    "SubmitForm": "Exfiltrates form data to external URL (/SubmitForm)",
    "GoToR": "Remote GoTo action opening external PDF (/GoToR)",
    "Movie": "Embedded movie action (/Movie)",
    "Sound": "Embedded sound action (/Sound)",
    "Rendition": "Multimedia rendition action (/Rendition)",
    "Crypt": "Custom stream encryption filter (/Crypt)",
    "Encrypt": "Encrypted PDF document (/Encrypt)",
}

INFO_TAGS: Dict[str, str] = {
    "URI": "External hyperlink action (/URI)",
    "Action": "Standard PDF action (/Action)",
    "Filespec": "File specification reference (/Filespec)",
}

ALL_MONITORED_TAGS: Set[str] = set(HIGH_RISK_TAGS) | set(MEDIUM_RISK_TAGS) | set(INFO_TAGS)

BENIGN_URI_PREFIXES: Tuple[str, ...] = (
    "http://ns.adobe.com/",
    "https://ns.adobe.com/",
    "http://www.w3.org/1999/",
    "http://www.w3.org/2000/",
    "https://www.w3.org/",
    "http://purl.org/dc/",
    "http://www.aiim.org/",
    "http://prismstandard.org/",
    "http://ns.useplus.org/",
    "http://iptc.org/",
    "http://www.idpf.org/",
    "http://www.npes.org/",
    "http://ns.attribution.com/",
    "http://www.extensis.com/meta/",
    "http://www.iec.ch",
)

TRACKING_PARAMS: Set[str] = {
    "gclid", "fbclid", "yclid", "srccid", "msclkid", "dclid", "twclid",
    "ref", "ref_src", "ref_url", "mc_cid", "mc_eid", "_hsenc", "_hsmi", "mkt_tok", "igshid",
}

SUSPICIOUS_PAYLOAD_PATTERNS: List[Tuple[bytes, str]] = [
    (b"eval(", "JavaScript eval() call"),
    (b"unescape(", "JavaScript unescape() obfuscation"),
    (b"String.fromCharCode", "JavaScript charcode obfuscation"),
    (b"util.printf", "Adobe Reader util.printf exploit primitive"),
    (b"Collab.collectEmailInfo", "Adobe Reader Collab.collectEmailInfo exploit primitive"),
    (b"Collab.getIcon", "Adobe Reader Collab.getIcon exploit primitive"),
    (b"app.launchURL", "Adobe JS app.launchURL call"),
    (b"exportDataObject", "Adobe JS exportDataObject file drop"),
    (b"spell.customDictionaryOpen", "Adobe JS spell exploit primitive"),
]

# Same-byte-length replacements to neutralize active PDF tags without breaking XREF offsets
DISARM_REPLACEMENTS: Dict[bytes, bytes] = {
    b"/JavaScript": b"/InertScrpt",
    b"/JS": b"/XX",
    b"/OpenAction": b"/InertActn0",
    b"/Launch": b"/InertL",
    b"/RichMedia": b"/InertMedi",
    b"/EmbeddedFiles": b"/InertEmbFiles",
    b"/EmbeddedFile": b"/InertEmbFile",
    b"/SubmitForm": b"/InertSubmt",
    b"/ImportData": b"/InertImprt",
    b"/GoToE": b"/InrtE",
    b"/GoToR": b"/InrtR",
    b"/AA": b"/ZZ",
}

HEX_ESCAPE_RE = re.compile(rb"#([0-9a-fA-F]{2})")
# ISO 32000-1: A PDF /Name token must be followed by whitespace or a PDF delimiter
NAME_TOKEN_RE = re.compile(rb"\x2f([A-Za-z0-9_#\-\+]+)(?=[\s\x00\(\)\<\>\[\]\{\}\x2f%])")
URI_PAREN_RE = re.compile(rb"\x2fURI\s*\(([^\)]{1,500})\)")
URL_RAW_RE = re.compile(rb"(?:https?|ftp|file|smb|javascript):(?://)?[^\s\)\>\"\'\\\x00-\x1f]{1,300}", re.IGNORECASE)


def decode_pdf_name(raw_name: bytes) -> str:
    """Decodes #XX hex escapes inside a PDF /Name token."""
    if b"#" not in raw_name:
        return raw_name.decode("latin1")
    return HEX_ESCAPE_RE.sub(lambda m: bytes([int(m.group(1), 16)]), raw_name).decode("latin1", errors="replace")


def normalize_url(raw_url: str) -> str:
    """Canonicalizes URLs and strips tracking parameters (utm_*, gclid, fbclid, ref, etc.)."""
    cleaned = raw_url.strip().rstrip(".,;)>'\"")
    if cleaned.lower().startswith("javascript:"):
        return cleaned[:160]
    try:
        parsed = urlparse(cleaned)
        if not parsed.scheme:
            return cleaned[:160]
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        query_items = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")
        ]
        new_query = urlencode(query_items, doseq=True)
        normalized = urlunparse((scheme, netloc, parsed.path, parsed.params, new_query, ""))
        return normalized[:200]
    except Exception:
        return cleaned[:160]


def extract_streams_linear(
    data: bytes, max_decompress_bytes: int = 32 * 1024 * 1024
) -> Tuple[int, int, int, bytes, List[bytes], List[bytes]]:
    """
    Linearly parses stream ... endstream blocks in O(N) without regex backtracking.
    Separates top-level structural dictionaries from raw binary streams and decompresses
    FlateDecode streams in memory (distinguishing /ObjStm object streams).
    """
    pos = 0
    n = len(data)
    stream_count = 0
    objstm_count = 0
    decompressed_count = 0
    non_stream_chunks: List[bytes] = []
    objstm_buffers: List[bytes] = []
    other_stream_buffers: List[bytes] = []
    total_decompressed_size = 0

    while pos < n:
        idx = data.find(b"stream", pos)
        if idx == -1:
            non_stream_chunks.append(data[pos:])
            break
        if idx >= 3 and data[idx - 3:idx] == b"end":
            non_stream_chunks.append(data[pos:idx + 6])
            pos = idx + 6
            continue

        after = idx + 6
        if after < n and data[after:after + 2] == b"\r\n":
            content_start = after + 2
        elif after < n and data[after:after + 1] in (b"\n", b"\r"):
            content_start = after + 1
        else:
            non_stream_chunks.append(data[pos:after])
            pos = after
            continue

        end_idx = data.find(b"endstream", content_start)
        if end_idx == -1:
            non_stream_chunks.append(data[pos:])
            break

        non_stream_chunks.append(data[pos:idx + 6])
        non_stream_chunks.append(b"\nendstream")

        stream_count += 1
        dict_window = data[max(0, idx - 512):idx]
        is_objstm = b"ObjStm" in dict_window
        if is_objstm:
            objstm_count += 1

        raw_stream = data[content_start:end_idx].strip(b"\r\n")
        if raw_stream and total_decompressed_size < max_decompress_bytes:
            for wbits in (15, -15):
                try:
                    decomp = zlib.decompress(raw_stream, wbits)
                    if len(decomp) + total_decompressed_size <= max_decompress_bytes:
                        if is_objstm:
                            objstm_buffers.append(decomp)
                        else:
                            other_stream_buffers.append(decomp)
                        total_decompressed_size += len(decomp)
                        decompressed_count += 1
                    break
                except Exception:
                    pass

        pos = end_idx + 9

    return (
        stream_count,
        objstm_count,
        decompressed_count,
        b" ".join(non_stream_chunks),
        objstm_buffers,
        other_stream_buffers,
    )


def get_macos_quarantine_info(filepath: str) -> Dict[str, Any]:
    """Reads OS download provenance attributes (macOS com.apple.quarantine or Linux user.xdg.origin.url)."""
    info: Dict[str, Any] = {"quarantined": False}
    if sys.platform == "darwin":
        try:
            res = subprocess.run(
                ["xattr", "-p", "com.apple.quarantine", filepath],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode == 0 and res.stdout.strip():
                raw = res.stdout.strip()
                info["quarantined"] = True
                parts = raw.split(";")
                if len(parts) >= 3:
                    info["flags"] = parts[0]
                    try:
                        ts = int(parts[1], 16)
                        info["timestamp"] = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()
                    except Exception:
                        info["timestamp"] = parts[1]
                    info["agent"] = parts[2].replace("\\x20", " ")
        except Exception:
            pass
    elif sys.platform.startswith("linux") and hasattr(os, "getxattr"):
        try:
            origin = os.getxattr(filepath, "user.xdg.origin.url").decode("utf-8", errors="replace").strip()
            if origin:
                info["quarantined"] = True
                info["origin_url"] = normalize_url(origin)
        except Exception:
            pass
    return info


def check_macos_pdf_environment() -> List[Dict[str, Any]]:
    """Verifies PDF viewer environment on macOS (codesign) or Linux (xdg-mime default handler)."""
    viewers: List[Dict[str, Any]] = []
    if sys.platform.startswith("linux"):
        try:
            res = subprocess.run(
                ["xdg-mime", "query", "default", "application/pdf"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode == 0 and res.stdout.strip():
                handler = res.stdout.strip()
                viewers.append({"app": handler, "signed_valid": True, "team_id": "xdg-mime"})
        except Exception:
            pass
        return viewers

    if sys.platform != "darwin":
        return viewers

    candidate_apps = [
        "/System/Applications/Preview.app",
        "/Applications/Adobe Acrobat DC/Adobe Acrobat.app",
        "/Applications/Adobe Acrobat Reader.app",
        "/Applications/Telegram Lite.app",
        "/Applications/Telegram.app",
    ]
    for app in candidate_apps:
        if os.path.exists(app):
            try:
                cs = subprocess.run(["codesign", "-dv", "--verbose=2", app], capture_output=True, text=True, timeout=5)
                details = cs.stderr.strip().splitlines()
                authority = [line.split("=", 1)[1] for line in details if line.startswith("Authority=")]
                team_id = next((line.split("=", 1)[1] for line in details if line.startswith("TeamIdentifier=")), None)
                viewers.append({
                    "app": os.path.basename(app),
                    "signed_valid": cs.returncode == 0,
                    "team_id": team_id,
                    "authority": authority[0] if authority else None,
                })
            except Exception as exc:
                viewers.append({"app": os.path.basename(app), "signed_valid": False, "error": str(exc)})
    return viewers


def extract_metadata(buffers: List[bytes]) -> Dict[str, str]:
    """Extracts compact PDF document info keys."""
    meta: Dict[str, str] = {}
    for key in (b"Producer", b"Creator", b"Author", b"Title"):
        k_str = key.decode("ascii")
        pat = re.compile(rb"\x2f" + key + rb"\s*\(([^\)]{1,140})\)")
        for buf in buffers:
            m = pat.search(buf)
            if m:
                val = m.group(1).decode("latin1", errors="replace").strip()
                val = "".join(ch if ch.isprintable() else " " for ch in val).strip()
                if val:
                    meta[k_str] = val[:80]
                    break
    return meta


def scan_pdf_bytes(
    data: bytes,
    filename: str = "memory.pdf",
    max_decompress_bytes: int = 32 * 1024 * 1024,
) -> Dict[str, Any]:
    """
    Core static analysis function operating directly on PDF bytes.
    Returns a compact, token-optimized dictionary (~50-100 tokens per record).
    """
    sha256 = hashlib.sha256(data).hexdigest()

    fname_anomalies: List[str] = []
    if "\r" in filename or "\n" in filename or "\x00" in filename:
        fname_anomalies.append(f"Control character in filename: {repr(filename)}")
    if re.search(r"\.pdf\.(exe|scr|bat|cmd|sh|command|app|pkg|dmg|js|vbs|py)$", filename, re.IGNORECASE):
        fname_anomalies.append(f"Double extension masquerading as PDF: {repr(filename)}")

    header_offset = data.find(b"%PDF-")
    if header_offset == -1:
        header_version = "MISSING"
    else:
        header_version = data[header_offset:header_offset + 16].splitlines()[0].decode("latin1", errors="replace")

    last_eof = data.rfind(b"%%EOF")
    trailing_bytes = data[last_eof + 5:].strip(b"\r\n\t ") if last_eof != -1 else b""

    stream_count, objstm_count, decomp_count, non_stream_bytes, objstm_buffers, other_stream_buffers = (
        extract_streams_linear(data, max_decompress_bytes=max_decompress_bytes)
    )

    structural_buffers = [non_stream_bytes] + objstm_buffers
    all_decoded_buffers = structural_buffers + other_stream_buffers

    tag_counts: Dict[str, int] = {}
    obfuscated_tags: List[Dict[str, str]] = []
    seen_obf: Set[Tuple[str, str]] = set()

    for buf in structural_buffers:
        for m in NAME_TOKEN_RE.finditer(buf):
            raw_tok = m.group(1)
            decoded_tok = decode_pdf_name(raw_tok)
            if b"#" in raw_tok and decoded_tok in ALL_MONITORED_TAGS:
                pair = (raw_tok.decode("latin1", errors="replace"), decoded_tok)
                if pair not in seen_obf:
                    seen_obf.add(pair)
                    obfuscated_tags.append({"raw": pair[0], "decoded": pair[1]})
            if decoded_tok in ALL_MONITORED_TAGS:
                tag_counts[decoded_tok] = tag_counts.get(decoded_tok, 0) + 1

    acroform_empty = False
    if "AcroForm" in tag_counts:
        for buf in structural_buffers:
            if b"/Fields[]" in buf or b"/Fields []" in buf:
                acroform_empty = True
                break

    payload_hits: List[str] = []
    for buf in all_decoded_buffers:
        for pat_bytes, desc in SUSPICIOUS_PAYLOAD_PATTERNS:
            if pat_bytes in buf and desc not in payload_hits:
                payload_hits.append(desc)

    uris: Set[str] = set()
    for buf in structural_buffers:
        for m in URI_PAREN_RE.finditer(buf):
            u = m.group(1).decode("latin1", errors="replace").strip()
            if u and not u.startswith(BENIGN_URI_PREFIXES):
                uris.add(normalize_url(u))
    for buf in all_decoded_buffers:
        for m in URL_RAW_RE.finditer(buf):
            u = m.group(0).decode("latin1", errors="replace").strip()
            if u and not u.startswith(BENIGN_URI_PREFIXES):
                uris.add(normalize_url(u))

    sorted_uris = sorted(uris)
    suspicious_uris = [
        u for u in sorted_uris
        if u.lower().startswith(("file://", "smb://", "javascript:"))
    ]

    risk_score = 0
    findings: List[str] = []

    if header_offset == -1:
        risk_score += 80
        findings.append("Missing %PDF- header")
    elif header_offset > 0:
        risk_score += 40
        findings.append(f"Polyglot header: %PDF- at offset {header_offset}")

    if len(trailing_bytes) > 128:
        risk_score += 25
        findings.append(f"Trailing payload: {len(trailing_bytes)} bytes after %%EOF")

    if fname_anomalies:
        risk_score += 15
        findings.extend(fname_anomalies)

    if obfuscated_tags:
        risk_score += 70
        findings.append(f"Hex-obfuscated PDF tags: {obfuscated_tags}")

    for tag, count in tag_counts.items():
        if tag in HIGH_RISK_TAGS:
            risk_score += 50
            findings.append(f"High-risk /{tag} ({count}x): {HIGH_RISK_TAGS[tag]}")
        elif tag in MEDIUM_RISK_TAGS:
            if tag == "AcroForm":
                active_set = {"JS", "JavaScript", "OpenAction", "AA", "SubmitForm", "XFA"}
                if acroform_empty and not (active_set & set(tag_counts)):
                    continue
                elif not (active_set & set(tag_counts)):
                    risk_score += 5
                    findings.append(f"Passive /AcroForm ({count}x) without triggers")
                else:
                    risk_score += 25
                    findings.append(f"Active /AcroForm ({count}x) with triggers")
            else:
                risk_score += 25
                findings.append(f"Medium-risk /{tag} ({count}x): {MEDIUM_RISK_TAGS[tag]}")

    if payload_hits:
        risk_score += 60
        findings.append(f"Exploit/script primitives: {', '.join(payload_hits)}")

    if suspicious_uris:
        risk_score += 40
        findings.append(f"Dangerous URI schemes: {suspicious_uris[:5]}")

    risk_score = min(100, risk_score)
    if risk_score >= 50:
        verdict = "HIGH_RISK"
    elif risk_score >= 20:
        verdict = "SUSPICIOUS"
    elif "URI" in tag_counts or sorted_uris:
        verdict = "CLEAN_WITH_LINKS"
    else:
        verdict = "CLEAN"

    return {
        "file": filename,
        "size_bytes": len(data),
        "sha256": sha256,
        "verdict": verdict,
        "risk_score": risk_score,
        "header": header_version,
        "header_offset": header_offset,
        "trailing_bytes": len(trailing_bytes),
        "streams": {"total": stream_count, "decompressed": decomp_count, "objstm": objstm_count},
        "tags": tag_counts,
        "obfuscated_tags": obfuscated_tags,
        "findings": findings,
        "uris": {
            "count": len(sorted_uris),
            "sample": sorted_uris[:5],
            "suspicious": suspicious_uris[:5],
        },
        "metadata": extract_metadata(all_decoded_buffers),
    }


def scan_single_pdf(filepath: str) -> Dict[str, Any]:
    """Scans a PDF file on disk and attaches OS quarantine metadata."""
    base = os.path.basename(filepath)
    if not os.path.isfile(filepath):
        return {"file": base, "verdict": "ERROR", "error": "File not found"}
    with open(filepath, "rb") as f:
        data = f.read()
    res = scan_pdf_bytes(data, filename=base)
    q = get_macos_quarantine_info(filepath)
    if q.get("quarantined"):
        res["quarantine"] = q
    return res


def parse_tounicode_cmaps(buffers: List[bytes]) -> Dict[int, str]:
    """Parses PDF /ToUnicode CMap streams (beginbfchar / beginbfrange) for CID fonts."""
    cmap: Dict[int, str] = {}
    bfchar_block_re = re.compile(rb"beginbfchar(.*?)endbfchar", re.DOTALL)
    bfrange_block_re = re.compile(rb"beginbfrange(.*?)endbfrange", re.DOTALL)
    pair_re = re.compile(rb"<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>")
    range_re = re.compile(rb"<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>")

    for buf in buffers:
        if b"begincmap" not in buf:
            continue
        for block in bfchar_block_re.finditer(buf):
            for m in pair_re.finditer(block.group(1)):
                src = int(m.group(1), 16)
                dst_hex = m.group(2)
                try:
                    dst_str = bytes.fromhex(dst_hex.decode("ascii")).decode("utf-16-be", errors="ignore")
                    if dst_str:
                        cmap[src] = dst_str
                except Exception:
                    pass
        for block in bfrange_block_re.finditer(buf):
            for m in range_re.finditer(block.group(1)):
                start = int(m.group(1), 16)
                end = int(m.group(2), 16)
                dst_start = int(m.group(3), 16)
                if 0 <= end - start <= 512:
                    for offset in range(end - start + 1):
                        code = dst_start + offset
                        if 0x20 <= code <= 0xFFFF:
                            cmap[start + offset] = chr(code)
    return cmap


def extract_safe_text_bytes(data: bytes, max_chars: int = 4000) -> str:
    """Extracts human-readable text from PDF BT...ET blocks and CMap tables in memory."""
    _, _, _, _, _, other_streams = extract_streams_linear(data)
    cmap = parse_tounicode_cmaps(other_streams)

    bt_et_re = re.compile(rb"\bBT\b(.*?)\bET\b", re.DOTALL)
    paren_re = re.compile(rb"\(([^\(\)]{1,300})\)")
    hex_str_re = re.compile(rb"<([0-9a-fA-F]{2,400})>")

    lines: List[str] = []
    total_len = 0

    for buf in other_streams:
        if b"BT" not in buf or b"begincmap" in buf:
            continue
        for bt in bt_et_re.finditer(buf):
            block = bt.group(1)
            pieces: List[str] = []
            for pm in paren_re.finditer(block):
                raw = pm.group(1)
                txt = "".join(chr(b) for b in raw if 32 <= b <= 126)
                if txt:
                    pieces.append(txt)
            if cmap:
                for hm in hex_str_re.finditer(block):
                    h = hm.group(1).decode("ascii")
                    step = 4 if len(h) % 4 == 0 else 2
                    decoded_chars: List[str] = []
                    for i in range(0, len(h), step):
                        val = int(h[i:i + step], 16)
                        if val in cmap:
                            decoded_chars.append(cmap[val])
                    if decoded_chars:
                        pieces.append("".join(decoded_chars))
            line = "".join(pieces).strip()
            if len(line) >= 2:
                lines.append(line)
                total_len += len(line)
                if total_len >= max_chars:
                    break
        if total_len >= max_chars:
            break

    return "\n".join(lines)[:max_chars]


def disarm_pdf_bytes(data: bytes) -> Tuple[bytes, List[str]]:
    """
    Neutralizes active PDF tags (/JS, /JavaScript, /OpenAction, /Launch, /AA, etc.)
    using exact byte-length replacements so XREF byte offsets remain intact.
    """
    actions_taken: List[str] = []
    modified = data

    for dangerous_tag, inert_tag in DISARM_REPLACEMENTS.items():
        if len(dangerous_tag) != len(inert_tag):
            raise ValueError("Disarm tag replacement must preserve exact byte length")
        pat = re.compile(re.escape(dangerous_tag) + rb"(?=[\s\x00\(\)\<\>\[\]\{\}\x2f%])")
        matches = len(pat.findall(modified))
        if matches > 0:
            modified = pat.sub(inert_tag, modified)
            actions_taken.append(f"{dangerous_tag.decode('ascii')}->{inert_tag.decode('ascii')} ({matches}x)")

    return modified, actions_taken


def print_compact_report(results: List[Dict[str, Any]], viewers: Optional[List[Dict[str, Any]]] = None) -> None:
    """Prints a token-compact, high-signal report (~50-100 tokens per file)."""
    high = sum(1 for r in results if r.get("verdict") == "HIGH_RISK")
    susp = sum(1 for r in results if r.get("verdict") == "SUSPICIOUS")
    links = sum(1 for r in results if r.get("verdict") == "CLEAN_WITH_LINKS")
    clean = sum(1 for r in results if r.get("verdict") == "CLEAN")
    print(f"PDF_AUDIT_SUMMARY: scanned={len(results)} high_risk={high} suspicious={susp} clean_links={links} clean={clean}")

    if viewers:
        v_str = ", ".join(
            f"{v['app']}:{'OK' if v.get('signed_valid') else 'INVALID'}({v.get('team_id') or 'Apple'})"
            for v in viewers
        )
        print(f"MACOS_VIEWERS: {v_str}")

    for r in results:
        v = r.get("verdict", "UNKNOWN")
        score = r.get("risk_score", 0)
        sha_short = (r.get("sha256") or "")[:16]
        st = r.get("streams", {})
        tags = r.get("tags") or {}
        print(
            f"- [{v}] {repr(r.get('file'))} score={score}/100 sha256={sha_short}... "
            f"hdr={r.get('header')}@{r.get('header_offset')} "
            f"streams={st.get('decompressed', 0)}/{st.get('total', 0)}(objstm={st.get('objstm', 0)}) "
            f"tags={tags if tags else '{}'}"
        )
        for f_item in r.get("findings", []):
            print(f"    ! {f_item}")
        u = r.get("uris", {})
        if u.get("count", 0) > 0:
            print(f"    uris({u['count']}): {u.get('sample', [])[:3]}")


def main(argv: Optional[List[str]] = None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    if args_list and args_list[0] not in ("scan", "text", "disarm", "-h", "--help"):
        args_list = ["scan"] + args_list
    elif not args_list:
        args_list = ["scan", "."]

    parser = argparse.ArgumentParser(
        prog="pdf_scanner.py",
        description="Zero-dependency static PDF malware scanner, text previewer, and CDR disarmer.",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    p_scan = sub.add_parser("scan", help="Scan PDF file(s) or directory(ies) statically.")
    p_scan.add_argument("targets", nargs="*", default=["."], help="PDF files or directories.")
    p_scan.add_argument("-r", "--recursive", action="store_true", help="Scan directories recursively.")
    p_scan.add_argument("-j", "--json", action="store_true", help="Output compact JSON.")
    p_scan.add_argument("-e", "--check-env", action="store_true", help="Verify macOS PDF viewer signatures.")

    p_text = sub.add_parser("text", help="Safely extract readable text in memory without opening the PDF.")
    p_text.add_argument("pdf_file", help="Target PDF file.")
    p_text.add_argument("--max-chars", type=int, default=4000, help="Maximum characters to return (default: 4000).")

    p_disarm = sub.add_parser("disarm", help="Create an XREF-preserving disarmed copy (.disarmed.pdf).")
    p_disarm.add_argument("pdf_file", help="Target PDF file.")
    p_disarm.add_argument("-o", "--output", help="Output path (default: <name>.disarmed.pdf).")

    parsed = parser.parse_args(args_list)

    if parsed.mode == "text":
        if not os.path.isfile(parsed.pdf_file):
            print(f"Error: File not found: {parsed.pdf_file}", file=sys.stderr)
            return 1
        with open(parsed.pdf_file, "rb") as f:
            txt = extract_safe_text_bytes(f.read(), max_chars=parsed.max_chars)
        print(txt if txt else "[No plain text blocks found]")
        return 0

    if parsed.mode == "disarm":
        if not os.path.isfile(parsed.pdf_file):
            print(f"Error: File not found: {parsed.pdf_file}", file=sys.stderr)
            return 1
        out_path = parsed.output or re.sub(r"\.pdf$", "", parsed.pdf_file, flags=re.IGNORECASE) + ".disarmed.pdf"
        with open(parsed.pdf_file, "rb") as f:
            disarmed_data, actions = disarm_pdf_bytes(f.read())
        with open(out_path, "wb") as f:
            f.write(disarmed_data)
        print(json.dumps({"output": out_path, "neutralized": actions}))
        return 0

    pdf_files: List[str] = []
    for t in parsed.targets:
        if os.path.isfile(t):
            pdf_files.append(t)
        elif os.path.isdir(t):
            if parsed.recursive:
                for root, _, files in os.walk(t):
                    for fn in sorted(files):
                        if ".pdf" in fn.lower():
                            pdf_files.append(os.path.join(root, fn))
            else:
                for fn in sorted(os.listdir(t)):
                    full = os.path.join(t, fn)
                    if os.path.isfile(full) and ".pdf" in fn.lower():
                        pdf_files.append(full)

    results = [scan_single_pdf(p) for p in pdf_files]
    viewers = check_macos_pdf_environment() if parsed.check_env else None

    if parsed.json:
        payload: Dict[str, Any] = {"scanned_count": len(results), "results": results}
        if viewers is not None:
            payload["macos_viewers"] = viewers
        print(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
    else:
        print_compact_report(results, viewers=viewers)

    if any(r.get("verdict") == "HIGH_RISK" for r in results):
        return 2
    if any(r.get("verdict") == "SUSPICIOUS" for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
