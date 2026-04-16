# Contributing to OpenClaw AkShare Skill

Thank you for your interest in contributing to the OpenClaw AkShare Skill!

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find that the problem has already been reported. When creating a bug report, please include:

- **Title**: Clear and descriptive
- **Description**: Detailed explanation of the problem
- **Steps to reproduce**: Code snippets or commands
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: Python version, AkShare version, OS

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- Provide examples if applicable

### Pull Requests

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add some amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Add comments for complex logic

### Documentation

- Update relevant documentation when adding features
- Keep examples up-to-date
- Use clear, concise language
- Include code snippets where helpful

### Testing

- Add tests for new features
- Ensure all tests pass before submitting PR
- Test on multiple Python versions if possible
- Include test data when appropriate

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/openclaw-akshare-skill.git
cd openclaw-akshare-skill
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt  # if available
pip install akshare
```

4. Run tests:
```bash
python scripts/test_basic.py
python scripts/test_quick.py
```

## Project Structure

```
openclaw-akshare-skill/
├── SKILL.md              # Main skill documentation
├── README.md             # Project README
├── LICENSE               # MIT License
├── .gitignore           # Git ignore rules
├── CHANGELOG.md         # Version history
├── CONTRIBUTING.md      # Contribution guidelines
├── references/          # Reference documentation
│   ├── akshare_api.md
│   └── common_functions.md
└── scripts/             # Example scripts and tests
    ├── example_usage.py
    ├── test_basic.py
    ├── test_quick.py
    ├── akshare_tool.py
    └── install_akshare.sh
```

## Guidelines

### Commit Messages

Use clear, descriptive commit messages:
```
feat: add support for stock options
fix: correct date format in historical data
docs: update API reference
test: add tests for futures data
```

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions or changes
- `refactor/` - Code refactoring

### Versioning

This project follows Semantic Versioning:
- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality
- **PATCH**: Backwards-compatible bug fixes

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Contact maintainers via GitHub discussions
- Check existing documentation first

## Code of Conduct

Be respectful and professional:
- Treat others with respect
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Be inclusive and welcoming to all contributors

Thank you for contributing!