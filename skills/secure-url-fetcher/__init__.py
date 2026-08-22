"""
Secure URL Fetcher Skill — Ottimizzato per UV Manager

Il filename 'secure-fetcher.py' contiene un trattino, quindi non può essere
importato con la sintassi standard 'import secure-fetcher'.
Si usa importlib per caricare il modulo dal percorso assoluto.
"""

import importlib.util
import pathlib

_script = pathlib.Path(__file__).parent / "secure-fetcher.py"
_spec = importlib.util.spec_from_file_location("secure_fetcher", _script)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

secure_url_fetch = _mod.secure_url_fetch

__all__ = ["secure_url_fetch"]