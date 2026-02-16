"""PAN scanner for detecting credit card numbers in files."""

import re
from pathlib import Path

from src.luhn import luhn_validate


PAN_PATTERN = {
    "visa": r"\b4\d{3}(\d{4}){3}\b",
    "mastercard": r"\b5[1-5]\d{2}(\d{4}){3}\b",
    "amex": r"\b3[47]\d{13}\b",
    "discover": r"\b6011(\d{4}){3}\b|\b65\d{2}(\d{4}){3}\b",
}

MASK_PATTERNS = {
    "visa": 16,
    "mastercard": 16,
    "amex": 15,
    "discover": 16,
}


class PANScanner:
    """Scanner for detecting PANs (Primary Account Numbers) in files."""

    def __init__(self, validate_luhn: bool = True):
        """Initialize PAN scanner.

        Args:
            validate_luhn: Whether to validate PANs using Luhn algorithm.
        """
        self.validate_luhn = validate_luhn
        self._compiled_patterns = {
            card_type: re.compile(pattern) for card_type, pattern in PAN_PATTERN.items()
        }

    def _mask_pan(self, pan: str, card_type: str) -> str:
        """Mask PAN keeping last 4 digits visible.

        Args:
            pan: The PAN to mask.
            card_type: The type of card.

        Returns:
            Masked PAN with only last 4 digits visible.
        """
        visible_digits = 4
        if card_type == "amex":
            visible_digits = 4
        masked_length = len(pan) - visible_digits
        return "*" * masked_length + pan[-visible_digits:]

    def scan_file(self, file_path: str) -> list[dict]:
        """Scan a file for PANs.

        Args:
            file_path: Path to the file to scan.

        Returns:
            List of findings, each containing card_type, masked_pan, and line_number.

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        findings = []

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            return findings

        lines = content.split("\n")

        for line_number, line in enumerate(lines, start=1):
            for card_type, pattern in self._compiled_patterns.items():
                for match in pattern.finditer(line):
                    pan = match.group()
                    if self.validate_luhn and not luhn_validate(pan):
                        continue
                    findings.append(
                        {
                            "card_type": card_type,
                            "masked_pan": self._mask_pan(pan, card_type),
                            "line_number": line_number,
                        }
                    )

        return findings

    def scan_text(self, text: str) -> list[dict]:
        """Scan text for PANs.

        Args:
            text: Text to scan.

        Returns:
            List of findings.
        """
        findings = []
        lines = text.split("\n")

        for line_number, line in enumerate(lines, start=1):
            for card_type, pattern in self._compiled_patterns.items():
                for match in pattern.finditer(line):
                    pan = match.group()
                    if self.validate_luhn and not luhn_validate(pan):
                        continue
                    findings.append(
                        {
                            "card_type": card_type,
                            "masked_pan": self._mask_pan(pan, card_type),
                            "line_number": line_number,
                        }
                    )

        return findings
