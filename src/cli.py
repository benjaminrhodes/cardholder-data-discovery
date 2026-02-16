"""CLI interface for PAN scanner."""

import sys
from pathlib import Path
from typing import List, Optional

from src.scanner import PANScanner


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        args: Command line arguments. If None, uses sys.argv.

    Returns:
        Exit code.
    """
    if args is None:
        args = sys.argv[1:]

    if not args or args[0] != "scan":
        print("Usage: python -m src.cli scan <file>")
        return 1

    if len(args) < 2:
        print("Error: No file specified")
        print("Usage: python -m src.cli scan <file>")
        return 1

    file_path = args[1]

    if not Path(file_path).exists():
        print(f"Error: File not found: {file_path}")
        return 1

    scanner = PANScanner()
    findings = scanner.scan_file(file_path)

    if not findings:
        print("No PANs found.")
        return 0

    print(f"Found {len(findings)} PAN(s):")
    for finding in findings:
        print(f"  Line {finding['line_number']}: {finding['card_type']} - {finding['masked_pan']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
