# Contributing to print-daily

Thank you for your interest in contributing to print-daily! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/print-daily.git`
3. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
4. Install development dependencies: `pip install -r requirements-dev.txt`
5. Create a branch: `git checkout -b feature/your-feature-name`

## Development Setup

Copy the environment template and add your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run a specific test file
pytest tests/test_guardian.py -v
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where practical
- Keep functions focused and well-documented
- Use meaningful variable names

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Keep commits atomic and well-described
5. Reference any related issues

## Adding New Data Sources

To add a new data source:

1. Create a new file in `data_sources/`
2. Follow the existing pattern:
   - Use dataclasses for return types
   - Handle API errors gracefully
   - Return `None` or empty values on failure
   - Use `logging` instead of `print`
3. Add tests in `tests/test_your_source.py`
4. Update `generate_daily.py` to use the new source
5. Update `pdf_generator.py` if layout changes are needed

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Any error messages

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
