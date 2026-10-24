---
name: pdf-security-scanner
description: Zero-dependency static PDF malware analyzer, in-memory CMap text extractor, and XREF-preserving Content Disarm & Reconstruction (CDR) tool.
---

# PDF Security Scanner

Perform read-only static forensic analysis, safe in-memory text extraction, and active-tag neutralization (CDR) on PDF files without opening or rendering them in a GUI viewer.

## Protocol & Decision Matrix

Invoke whenever inspecting, summarizing, or verifying untrusted `.pdf` documents:

1. **Never Open Untrusted PDFs**: Do not invoke `open`, `xdg-open`, or GUI viewers prior to static verification.
2. **Audit (`scan`)**: Default mode for single files or directories (cross-platform: Linux, macOS, Windows). Decompresses `/FlateDecode` and `/ObjStm` streams in memory, decodes `#XX` hex-obfuscated PDF names, verifies `%PDF-` header offsets (polyglot detection) and trailing bytes past `%%EOF`, extracts normalized URIs, and inspects OS provenance attributes (`com.apple.quarantine` on macOS, `user.xdg.origin.url` on Linux).
3. **Preview Text (`text`)**: Extract human-readable text from `BT...ET` blocks and `/ToUnicode` CMap tables in memory without rendering fonts or images.
4. **Disarm (`disarm`)**: Neutralize active triggers (`/JS`, `/JavaScript`, `/OpenAction`, `/Launch`, `/AA`, `/RichMedia`, `/EmbeddedFiles`, `/SubmitForm`, `/GoToR`, `/GoToE`) into a `.disarmed.pdf` copy using exact byte-length replacements that preserve XREF offsets.

## Execution

```bash
# 1. Static security audit (compact JSON or human summary; works with uv run or python3)
uv run <skill_dir>/pdf_scanner.py scan "<path/to/file_or_dir>" [--json] [--recursive] [--check-env]

# 2. Safe in-memory text extraction (default: 4000 chars max for token economy)
uv run <skill_dir>/pdf_scanner.py text "<path/to/file.pdf>" [--max-chars 4000]

# 3. XREF-preserving Content Disarm & Reconstruction (CDR)
uv run <skill_dir>/pdf_scanner.py disarm "<path/to/file.pdf>" [-o "<path/to/output.disarmed.pdf>"]
```

## Verdicts & Exit Codes

- **`0` (`CLEAN` / `CLEAN_WITH_LINKS`)**: Valid header at offset `0`, zero active code/trigger tags, benign or empty `/AcroForm` (`/Fields[]`).
- **`1` (`SUSPICIOUS`, Risk Score 20–49)**: Automatic triggers (`/OpenAction`, `/AA`), interactive form submission (`/SubmitForm`, `/GoToR`), trailing data after `%%EOF`, or filename control characters.
- **`2` (`HIGH_RISK`, Risk Score 50–100)**: Active code or exploit vectors (`/JS`, `/JavaScript`, `/Launch`, `/EmbeddedFiles`, `/RichMedia`, `/JBIG2Decode`), hex-obfuscated sensitive tags (`/#4a#53`), polyglot headers, suspicious URI schemes (`file://`, `smb://`, `javascript:`), or exploit primitives (`eval(`, `util.printf`, `Collab.collectEmailInfo`).

## Context & Token Optimization

- **Compaction Guarantee**: Strips benign XML/XMP namespaces (`ns.adobe.com`, `w3.org`, `purl.org`), normalizes URLs by removing tracking parameters (`utm_*`, `gclid`, `fbclid`, `ref`, `mc_*`, `yclid`, `srccid`), deduplicates findings, and caps URI samples (~80% token reduction vs raw object dumps).
- **False-Positive Immunity**: Separates structural PDF dictionaries and decompressed `/ObjStm` object streams from raw compressed binary payloads, requiring strict ISO 32000-1 PDF token delimiters after `/Name` tokens.
- **Threat Reference**: See [`references/THREAT_MODEL.md`](references/THREAT_MODEL.md) for vector classification and viewer sandboxing details.
