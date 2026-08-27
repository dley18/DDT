"""
DDT (Data Download Tool) - Main Entry Point

A data analysis application for Longwall Shearer data dumps.


Author: Dane Ley
Version: 2.3
"""

import sys, os
from pathlib import Path

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent  # Go up one level to DDT directory
sys.path.insert(0, str(project_root))

# Add src directory to Python path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))


def _setup_console_for_pyinstaller():
    """Fix PyInstaller console issues that cause 'NoneType' write errors."""
    if getattr(sys, "frozen", False):
        # Running in PyInstaller bundle
        import io

        # Ensure stdout and stderr exist and are writable
        if sys.stdout is None or not hasattr(sys.stdout, "write"):
            sys.stdout = io.StringIO()
        if sys.stderr is None or not hasattr(sys.stderr, "write"):
            sys.stderr = io.StringIO()

        # Also redirect stdin to prevent input issues
        if sys.stdin is None:
            sys.stdin = io.StringIO()


def main():
    """Main entry point for DDT"""
    print("DEBUG: Starting DDT - from {main.main}")

    # Fix PyInstaller console issues BEFORE importing anything
    _setup_console_for_pyinstaller()
    print("DEBUG: Console setup complete - from {main.main}")
    try:
        from core.application_controller import run_application

        run_application()
        print("DEBUG: DDT Exited - from {main.main}")
    except Exception as e:
        print(f"DEBUG: Exception in main: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
