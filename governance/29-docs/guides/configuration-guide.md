# Configuration Guide

## Configuration Files

Governance framework uses YAML configuration files located in `config/` directory.

### Environment-Specific Configs

- `default-config.yaml` - Default settings
- `development-config.yaml` - Development environment
- `production-config.yaml` - Production environment
- `testing-config.yaml` - Testing environment

### Custom Configuration

Create custom config file and specify via environment variable:

```bash
export GOVERNANCE_CONFIG=path/to/custom-config.yaml
```

---

**Last Updated**: 2025-12-10
