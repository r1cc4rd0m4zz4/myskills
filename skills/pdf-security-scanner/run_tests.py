# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test runner for pdf-security-scanner.
Uses Python standard library unittest with zero external dependencies.

Execution:
    uv run skills/pdf-security-scanner/run_tests.py
    python3 skills/pdf-security-scanner/run_tests.py
"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(pathlib.Path(__file__).parent / "tests"),
        pattern="test_*.py",
    )

    print("=" * 70)
    print("  pdf-security-scanner — Test Suite (stdlib unittest)")
    print("=" * 70)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"  ✅  {result.testsRun} tests passed successfully")
    else:
        print(f"  ❌  {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
