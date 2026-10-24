# PDF Malware Threat Model & Forensic Reference

## 1. Attack Vectors in ISO 32000-1 Documents

| Vector | Monitored Tags / Primitives | Mechanism & Viewer Impact |
| :--- | :--- | :--- |
| **1. Active Scripting & Auto-Triggers** | `/JS`, `/JavaScript`, `/OpenAction`, `/AA` | Executes embedded JavaScript when the document opens or a page is rendered. Supported in Adobe Acrobat/Reader; ignored by design in sandboxed macOS `Preview.app` (`PDFKit`). |
| **2. OS Command & Payload Drop** | `/Launch`, `/EmbeddedFiles`, `/EmbeddedFile`, `/GoToE`, `/GoToR`, `/ImportData` | Attempts to spawn an operating system binary/shell or extract an embedded archive/executable stored inside the PDF object tree. |
| **3. Parser Memory Corruption** | `/JBIG2Decode`, `/RichMedia`, `/XFA` | Targets C/C++ stream decoders and font/image parsers (e.g., CVE-2021-30860 FORCEDENTRY integer overflow in JBIG2). |
| **4. Credential Harvesting & SSRF/SMB Leaks** | `/URI`, `/SubmitForm`, `smb://`, `file://`, `javascript:` | Coerces outbound NTLM/SMB authentication (`smb://`), local file probing (`file://`), or form submission to external endpoints. |

---

## 2. Evasion Countermeasures in `pdf_scanner.py`

1. **Object Stream (`/ObjStm`) Decompression**:
   PDF 1.5+ allows indirect objects to be compressed inside `/Type /ObjStm` streams using `/FlateDecode`. Naive keyword scanners miss tags hidden inside `/ObjStm`. `pdf_scanner.py` linearly locates and decompresses `/ObjStm` payloads in memory with strict decompression size caps (`32 MB` default) to prevent zip-bomb denial of service.
2. **Hex Name Normalization (`/#XX`)**:
   Per ISO 32000-1 Section 7.3.5, any character in a `/Name` token may be written as a two-digit hex escape (e.g., `/#4a#53` for `/JS`, `/#4c#61#75#6e#63#68` for `/Launch`). `pdf_scanner.py` decodes all `#XX` sequences prior to classification and flags obfuscated sensitive tags as high-risk evasion (`+70` risk score).
3. **Structural vs. Binary Stream Separation (False-Positive Elimination)**:
   Short 3-byte sequences such as `/JS` (`0x2f 0x4a 0x53`) or `/AA` (`0x2f 0x41 0x41`) occur randomly in compressed image or font streams roughly once every $256^3 \approx 16.7\text{ MB}$. `pdf_scanner.py` strips raw compressed `stream...endstream` bytes from structural dictionary scans and enforces valid PDF token delimiters (`[\s\x00()<>[\]{}/%]`) after every `/Name`.
4. **XREF-Preserving Content Disarm (`disarm`)**:
   Neutralizing active tags by deleting bytes invalidates the PDF Cross-Reference (`xref`) byte-offset table. `disarm_pdf_bytes` replaces dangerous tags with inert tags of the exact same byte length (e.g., `/JavaScript` $\rightarrow$ `/InertScrpt`, `/Launch` $\rightarrow$ `/InertL`), rendering triggers inert while preserving document layout and `xref` integrity.
