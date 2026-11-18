# Contributing to ChronoVault 2.0

Thanks for your interest in contributing! This document provides guidelines for contributing to ChronoVault.

## 📋 How to Contribute

### Reporting Bugs

1. Use the GitHub Issues page to report bugs
2. Include:
   - Operating system and Python version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages (if any)
   - Relevant code snippets

### Suggesting Features

1. Open an issue with "Feature Request" label
2. Describe the problem you're trying to solve
3. Explain your proposed solution
4. Include mockups or examples if helpful

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python chrono.py selftest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a pull request

## 🧪 Testing

Before submitting a pull request:

1. Run the test suite:
   ```bash
   python chrono.py selftest
   ```

2. Test new functionality manually:
   ```bash
   python chrono.py ask "your test question"
   python chrono.py cockpit  # Test web UI
   ```

3. If adding new sources, test them individually:
   ```bash
   python -c "from chronovault import sources; print(sources.your_new_source(...))"
   ```

## 📝 Code Style

- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add comments for complex logic
- Keep functions focused and small
- Use type hints where appropriate

## 🏗️ Architecture

ChronoVault is organized into:

- `chrono.py` - CLI entry point
- `engine/chronovault/` - Core modules
  - `ask.py` - Main orchestrator
  - `sources.py` - Data sources
  - `forecast.py` - Statistical forecasting
  - `oracle.py` - Paradox Ledger
  - `probes.py` - Verification system
  - `memory.py` - SQLite storage
  - `ui.py` - Web UI logic
  - `serve.py` - HTTP server
  - `cockpit.html` - Web interface
- `engine/providers/` - Registry generation

## 🔌 Adding New Sources

To add a new data source:

1. Add it to `sources.py` with proper error handling
2. Include fallback options where possible
3. Add tests in `tests/test_core.py`
4. Update the registry if it's a new endpoint
5. Document the source in comments

## 📚 Documentation

- Update README.md for new features
- Add comments for complex code
- Update documentation in `08_CHRONO_V2.md` if needed

## 🤝 Community

- Be respectful and constructive
- Help others in issues and discussions
- Follow the project's code of conduct

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Happy coding! 🚀⏳