"""Tests for PAN detection and Luhn algorithm."""

import pytest
from src.scanner import PANScanner, PAN_PATTERN


class TestLuhnAlgorithm:
    """Tests for Luhn checksum validation."""

    def test_valid_visa(self):
        """Valid Visa test numbers pass Luhn check."""
        from src.luhn import luhn_validate

        assert luhn_validate("4111111111111111") is True

    def test_valid_mastercard(self):
        """Valid Mastercard test numbers pass Luhn check."""
        from src.luhn import luhn_validate

        assert luhn_validate("5500000000000004") is True

    def test_valid_amex(self):
        """Valid Amex test numbers pass Luhn check."""
        from src.luhn import luhn_validate

        assert luhn_validate("340000000000009") is True

    def test_valid_discover(self):
        """Valid Discover test numbers pass Luhn check."""
        from src.luhn import luhn_validate

        assert luhn_validate("6011000000000004") is True

    def test_invalid_number(self):
        """Invalid numbers fail Luhn check."""
        from src.luhn import luhn_validate

        assert luhn_validate("4111111111111112") is False

    def test_all_zeros(self):
        """All zeros passes Luhn algorithm but scanner filters by card patterns."""
        from src.luhn import luhn_validate

        assert luhn_validate("0000000000000000") is True

    def test_short_number(self):
        """Numbers shorter than 13 digits fail."""
        from src.luhn import luhn_validate

        assert luhn_validate("411111111111") is False


class TestPANPattern:
    """Tests for PAN regex patterns."""

    def test_visa_pattern(self):
        """Visa pattern matches 13 or 16 digit numbers starting with 4."""
        import re

        pattern = PAN_PATTERN["visa"]
        assert re.search(pattern, "4111111111111111") is not None
        assert re.search(pattern, "41111111111111111111") is None

    def test_mastercard_pattern(self):
        """Mastercard pattern matches 16 digit numbers starting with 51-55."""
        import re

        pattern = PAN_PATTERN["mastercard"]
        assert re.search(pattern, "5500000000000004") is not None
        assert re.search(pattern, "5000000000000000") is None

    def test_amex_pattern(self):
        """Amex pattern matches 15 digit numbers starting with 34 or 37."""
        import re

        pattern = PAN_PATTERN["amex"]
        assert re.search(pattern, "340000000000009") is not None
        assert re.search(pattern, "370000000000009") is not None

    def test_discover_pattern(self):
        """Discover pattern matches 16 digit numbers starting with 6011 or 65."""
        import re

        pattern = PAN_PATTERN["discover"]
        assert re.search(pattern, "6011000000000004") is not None
        assert re.search(pattern, "6500000000000000") is not None


class TestPANScanner:
    """Tests for PAN scanner."""

    def test_scan_empty_file(self, tmp_path):
        """Empty file returns no findings."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert findings == []

    def test_scan_file_with_no_pan(self, tmp_path):
        """File without PAN returns no findings."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("This is just some regular text without any credit card numbers.")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert findings == []

    def test_scan_file_with_valid_visa(self, tmp_path):
        """File with valid Visa PAN returns finding."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("My card number is 4111111111111111 for testing.")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert len(findings) == 1
        assert findings[0]["card_type"] == "visa"
        assert findings[0]["masked_pan"] == "************1111"

    def test_scan_file_with_invalid_pan(self, tmp_path):
        """File with invalid PAN (fails Luhn) returns no findings."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("My card number is 4111111111111112 for testing.")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert findings == []

    def test_scan_file_with_multiple_pans(self, tmp_path):
        """File with multiple valid PANs returns all findings."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Card 1: 4111111111111111, Card 2: 5500000000000004")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert len(findings) == 2

    def test_scan_file_with_amex(self, tmp_path):
        """File with valid Amex PAN returns finding."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Amex card: 340000000000009")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert len(findings) == 1
        assert findings[0]["card_type"] == "amex"
        assert findings[0]["masked_pan"] == "***********0009"

    def test_scan_file_with_discover(self, tmp_path):
        """File with valid Discover PAN returns finding."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Discover card: 6011000000000004")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert len(findings) == 1
        assert findings[0]["card_type"] == "discover"

    def test_scan_file_with_embedded_pan(self, tmp_path):
        """File with PAN embedded in JSON returns finding."""
        file_path = tmp_path / "test.txt"
        file_path.write_text('{"card_number": "4111111111111111"}')
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert len(findings) == 1

    def test_scan_file_with_line_number(self, tmp_path):
        """Finding includes line number."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("line1\nline2\n4111111111111111\nline4")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert len(findings) == 1
        assert findings[0]["line_number"] == 3

    def test_scan_binary_file(self, tmp_path):
        """Binary file is handled gracefully."""
        file_path = tmp_path / "binary.bin"
        file_path.write_bytes(b"\x00\x01\x02\x00\x4111111111111111\x00")
        scanner = PANScanner()
        findings = scanner.scan_file(str(file_path))
        assert findings == []

    def test_scan_nonexistent_file(self):
        """Scanning nonexistent file raises error."""
        scanner = PANScanner()
        with pytest.raises(FileNotFoundError):
            scanner.scan_file("/nonexistent/file.txt")

    def test_scan_text_method(self):
        """scan_text method works correctly."""
        scanner = PANScanner()
        findings = scanner.scan_text("My card: 4111111111111111")
        assert len(findings) == 1
        assert findings[0]["card_type"] == "visa"
