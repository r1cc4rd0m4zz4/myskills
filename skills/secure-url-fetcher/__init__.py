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
if _spec is not None and _spec.loader is not None:
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    secure_url_fetch = getattr(_mod, "secure_url_fetch")
else:
    raise ImportError("Impossibile caricare secure-fetcher")

__all__ = ["secure_url_fetch"]
