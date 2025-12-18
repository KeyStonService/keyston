# Troubleshooting Guide

## Common Issues

### Installation Issues

#### Problem: pip install fails

**Solution**:

```bash
# Upgrade pip
pip install --upgrade pip

# Try with --user flag
pip install --user synergymesh-governance
```

#### Problem: Permission denied

**Solution**:

```bash
# Use sudo (Linux/macOS)
sudo pip install synergymesh-governance

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install synergymesh-governance
```

### Runtime Issues

#### Problem: Dashboard won't start

**Solution**:

1. Check port 8080 is available
2. Check logs: `tail -f logs/governance.log`
3. Verify configuration: `governance-cli validate`

#### Problem: CLI command not found

**Solution**:

```bash
# Add to PATH
export PATH=$PATH:~/.local/bin  # Linux/macOS
```

### Configuration Issues

#### Problem: Invalid YAML configuration

**Solution**:

```bash
# Validate all configurations
make validate

# Check specific file
governance-cli validate --file path/to/file.yaml
```

## Getting Help

- Check [FAQ](docs/FAQ.md)
- Review [Documentation](docs/)
- Open GitHub Issue
- Contact: <governance-support@synergymesh.io>

---

**Last Updated**: 2025-12-10
