# ollama_stat_model

An Azure Function that scrapes Ollama model statistics and stores them in Azure Blob Storage.

## Testing

This project includes comprehensive unit tests for all main functions.

### Running Tests

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Run tests using pytest:
```bash
pytest tests/ -v
```

Or use the provided test runner:
```bash
python run_tests.py
```

### Test Coverage

The test suite covers:
- Data quality validation (`check_data_quality`)
- Web scraping functionality (`scrap_ollama_models`)
- Main workflow integration (`run_scraping`)
- Error handling and edge cases
- Mocked external dependencies (HTTP requests, file I/O)

### Test Files

- `tests/test_scrap_function.py` - Main test file with all unit tests
- `tests/__init__.py` - Test package initialization
- `pytest.ini` - pytest configuration
- `requirements-test.txt` - Test dependencies
- `run_tests.py` - Test runner script