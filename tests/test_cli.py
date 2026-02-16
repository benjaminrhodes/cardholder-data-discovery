"""Tests for CLI interface."""

from src.cli import main


class TestCLI:
    """Tests for CLI."""

    def test_main_no_args(self, capsys):
        """Main with no args prints usage."""
        result = main([])
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert result == 1

    def test_main_scan_missing_file(self, capsys):
        """Main scan with missing file prints error."""
        result = main(["scan"])
        captured = capsys.readouterr()
        assert "No file specified" in captured.out
        assert result == 1

    def test_main_scan_nonexistent_file(self):
        """Main scan with nonexistent file returns error."""
        result = main(["scan", "/nonexistent/file.txt"])
        assert result == 1

    def test_main_scan_no_pan(self, capsys, tmp_path):
        """Main scan file with no PAN prints appropriate message."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("No PANs here")
        result = main(["scan", str(file_path)])
        captured = capsys.readouterr()
        assert "No PANs found" in captured.out
        assert result == 0

    def test_main_scan_with_pan(self, capsys, tmp_path):
        """Main scan file with PAN prints finding."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Card: 4111111111111111")
        result = main(["scan", str(file_path)])
        captured = capsys.readouterr()
        assert "Found 1 PAN" in captured.out
        assert "visa" in captured.out
        assert result == 0

    def test_main_scan_multiple_pans(self, capsys, tmp_path):
        """Main scan file with multiple PANs prints all findings."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Cards: 4111111111111111 and 5500000000000004")
        result = main(["scan", str(file_path)])
        captured = capsys.readouterr()
        assert "Found 2 PAN" in captured.out
        assert result == 0
