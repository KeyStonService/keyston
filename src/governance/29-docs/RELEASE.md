# Release Guide

## Release Process

### 1. Pre-Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in VERSION and version.py
- [ ] Security scan completed

### 2. Create Release

```bash
make release VERSION=1.0.0
```

### 3. Build Packages

```bash
make build-all
```

### 4. Sign Packages

```bash
make sign-packages
```

### 5. Upload to Registry

```bash
make upload
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- MAJOR.MINOR.PATCH
- Example: 1.0.0

---

**Last Updated**: 2025-12-10
