"""Skeleton sanity tests — the package imports, the structure is intact, the CLI runs.

These are the release step-2 gate. Component tests (panels regenerate, baselines K1, grader numbers, env dry-run)
are added as each component is ported in steps 3-6.
"""
import subprocess
import sys

import verify_or_trust as vot


def test_version():
    assert isinstance(vot.__version__, str) and vot.__version__


def test_submodules_import():
    # every advertised module must at least import (structure is intact, no syntax errors)
    import verify_or_trust.baselines  # noqa: F401
    import verify_or_trust.cli  # noqa: F401
    import verify_or_trust.env  # noqa: F401
    import verify_or_trust.grade  # noqa: F401
    import verify_or_trust.panels  # noqa: F401
    import verify_or_trust.substrates  # noqa: F401
    import verify_or_trust.substrates.gears_norman  # noqa: F401
    import verify_or_trust.substrates.state_tahoe  # noqa: F401
    import verify_or_trust.tools  # noqa: F401


def test_cli_help_runs():
    r = subprocess.run([sys.executable, "-m", "verify_or_trust.cli", "--help"],
                       capture_output=True, text=True)
    assert r.returncode == 0
    assert "vot" in r.stdout
