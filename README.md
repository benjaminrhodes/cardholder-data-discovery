# Cardholder Data Discovery

Scan for PANs in files/logs for PCI DSS compliance.

## Features

- ✅ Detects Visa, Mastercard, Amex, and Discover card numbers
- ✅ Luhn algorithm validation to filter false positives
- ✅ CLI interface for scanning files
- ✅ Returns masked PANs (last 4 digits visible)

## Usage

```bash
pip install cardholder-data-discovery
python -m src.cli scan <file>
```

## Testing

```bash
pytest tests/ -v
pytest tests/ --cov -  # with coverage
```

## Security

- Uses synthetic/test data only
- No real credentials or production systems

## License

MIT
