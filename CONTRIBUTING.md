# 🤝 Contributing to SynergyMesh

Thank you for your interest in contributing to **SynergyMesh**! We welcome contributions of all kinds.

## 🌟 Ways to Contribute

### Reporting Bugs

If you find a bug, please:

1. Check [Issues](https://github.com/SynergyMesh/SynergyMesh/issues) to ensure the issue hasn't been reported
2. Create a new Issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected behavior vs actual behavior
   - Environment information (OS, version, etc.)
   - Related logs or screenshots

### Feature Suggestions

We welcome feature suggestions:

1. Create a Feature Request in Issues
2. Explain the purpose and value of the feature
3. Provide usage scenario examples
4. If possible, suggest an implementation approach

### Submitting Code

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Improving Documentation

- Fix spelling or grammar errors
- Improve clarity of existing documentation
- Add missing documentation
- Translate documentation to other languages

## 📋 Development Guide

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/SynergyMesh/SynergyMesh.git
cd SynergyMesh

# Install dependencies
npm install

# Run tests
npm test

# Run linting
npm run lint
```

### Code Style

- Follow existing code style conventions
- Use meaningful variable and function names
- Add appropriate comments
- Keep code clean and readable
- TypeScript strict mode is required
- Follow the project's ESLint configuration

### Commit Message Convention

Use clear commit messages following Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code format (doesn't affect functionality)
- `refactor`: Refactoring
- `perf`: Performance improvements
- `test`: Test related
- `chore`: Build process or auxiliary tools changes

### Pull Request Checklist

Before submitting a PR, please confirm:

- [ ] Code follows project style guidelines
- [ ] Necessary tests have been added
- [ ] All tests pass
- [ ] Related documentation has been updated
- [ ] Commit messages are clear
- [ ] PR description is complete
- [ ] No hard-coded sensitive information

### AI-Generated Contributions

If your PR includes AI-generated content or assistance, ensure compliance with the **[AI Behavior Contract](.github/AI-BEHAVIOR-CONTRACT.md)**:

- [ ] No vague language used (e.g., "seems to be", "might be")
- [ ] Clear binary status (CAN_COMPLETE or CANNOT_COMPLETE)
- [ ] Large tasks properly decomposed (2-3 subtasks)
- [ ] File modifications marked as draft (unless explicitly authorized)
- [ ] Validation script passed: `.github/scripts/validate-ai-response.sh`

**Validation Command:**

```bash
# Validate commit message
.github/scripts/validate-ai-response.sh --commit HEAD

# Validate PR description
.github/scripts/validate-ai-response.sh "$(gh pr view --json body -q .body)"
```

## 🏆 Contributors

Thanks to all contributors for their efforts!

## 📄 License

By contributing code, you agree that your contributions will be released under the MIT License.

## 📞 Contact

If you have questions, please contact us:

- 🌐 Website: [synergymesh.io](https://synergymesh.io)
- 📧 Email: <team@synergymesh.io>
- 🐦 Twitter: [@SynergyMesh](https://twitter.com/SynergyMesh)
- 💬 Community: [community.synergymesh.io](https://community.synergymesh.io)

---

**Thank you for helping make SynergyMesh better!** 🙏✨
