# Contributing to Code Review Agent

Thank you for your interest in contributing! Here's how to get started.

---

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/karthikpagnis/code-review-agent.git
   cd code-review-agent
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up your development environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Make your changes**
   - Follow PEP 8 style guidelines
   - Add tests for new features
   - Update documentation as needed

5. **Test your changes**
   ```bash
   # Run linting
   pylint app/
   
   # Run tests (if applicable)
   pytest tests/
   ```

6. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "Add: [feature description]"
   ```

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**
   - Go to https://github.com/karthikpagnis/code-review-agent/pulls
   - Click "New Pull Request"
   - Describe your changes clearly
   - Link any related issues

---

## Code Style

- **Python**: PEP 8 compliant
- **Naming**: descriptive, lowercase with underscores
- **Functions**: docstrings with parameter and return documentation
- **Imports**: organized (stdlib, third-party, local)

Example:
```python
def analyze_code_chunk(code: str, language: str) -> dict:
    """
    Analyze a code chunk for security issues.
    
    Args:
        code: Source code as string
        language: Programming language ('python', 'javascript', etc.)
        
    Returns:
        Dictionary with 'findings' list containing security issues
    """
    # Implementation
    pass
```

---

## Areas to Contribute

### 🔒 Security Agent
- Improve OWASP vulnerability detection
- Add more security rules
- Optimize scanning performance

### 🐛 Logic/Bug Agent
- Enhance null reference detection
- Improve exception handling analysis
- Add race condition detection

### ✨ Quality Agent
- Expand code quality metrics
- Improve naming suggestions
- Better complexity analysis

### 📚 Documentation
- Improve setup guides
- Add more examples
- Create video tutorials

### 🧪 Testing
- Add unit tests
- Add integration tests
- Test edge cases

### 🚀 Deployment
- Azure App Service integration
- Docker containerization
- CI/CD pipeline improvements

---

## Reporting Bugs

Found a bug? Please create an issue with:

1. **Title**: Brief description of the bug
2. **Description**: What happened vs. what you expected
3. **Steps to reproduce**: Clear steps to replicate
4. **Environment**: OS, Python version, etc.
5. **Logs**: Any error messages or tracebacks

Example:
```
Title: Security agent fails on Python 3.12

Description:
When running reviews on Python 3.12, the security agent crashes with a TypeError.

Steps to reproduce:
1. Use Python 3.12
2. Submit a Python file for review
3. Wait for security agent to run

Expected: Security findings displayed
Actual: TypeError in agent logs

Environment:
- macOS 14.5
- Python 3.12.1
- Code Review Agent v1.0
```

---

## Feature Requests

Have an idea? Open an issue with:
- **Title**: Feature name
- **Description**: What problem does this solve?
- **Use case**: How would this be used?
- **Alternative solutions**: Other approaches considered

---

## Pull Request Guidelines

- **Keep PRs focused**: One feature/fix per PR
- **Write clear commit messages**: Follow the "Add:", "Fix:", "Docs:" convention
- **Test thoroughly**: Verify your changes work end-to-end
- **Update docs**: Keep README and guides current
- **Request review**: Tag reviewers when ready

---

## Questions?

- Open a GitHub Discussion
- Check existing issues
- Read the documentation in `infra/` and `README.md`

---

## Recognition

Contributors will be recognized in:
- GitHub repository contributors section
- `CONTRIBUTORS.md` file (coming soon)
- Release notes for significant contributions

Thank you for helping make Code Review Agent better! 🎉
