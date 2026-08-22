# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "urllib3>=2.0.0",
# ]
# ///

"""
Test runner per secure-url-fetcher.
Usa unittest stdlib (no pytest necessario) con dipendenze gestite da uv.

Esecuzione:
    uv run --offline run_tests.py
"""

import unittest
import sys
import pathlib

# Aggiunge la root del progetto al path
sys.path.insert(0, str(pathlib.Path(__file__).parent))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(pathlib.Path(__file__).parent / "tests"),
        pattern="test_*.py",
    )

    print("=" * 70)
    print("  secure-url-fetcher — Test Suite (uv + unittest)")
    print("=" * 70)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"  ✅  {result.testsRun} test passati con successo")
    else:
        print(f"  ❌  {len(result.failures)} fallimenti, {len(result.errors)} errori su {result.testsRun} test")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
