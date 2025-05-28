# Contributing to FastDEV

First off, thank you for considering contributing to FastDEV! It's people like you that make FastDEV such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include logs and error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python style guide (PEP 8)
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Process

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/your-username/fastdev.git
cd fastdev

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
ruff check .
mypy .
```

## Style Guide

We use the following tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **Ruff** for linting
- **mypy** for type checking

Run all checks with:
```bash
make lint
```

## Testing

- Write tests for any new functionality
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Use meaningful test names

## Documentation

- Update README.md if needed
- Add docstrings to all public functions
- Update changelog for notable changes
- Include examples for new features

## Questions?

Feel free to open an issue with your question or reach out on our Discord server.

Thank you for contributing! 🎉
