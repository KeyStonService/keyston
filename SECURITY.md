# Security Policy / 安全政策

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

### 🔒 How to Report Security Vulnerabilities

We take security issues seriously. If you discover a security vulnerability,
please **DO NOT** report it through public Issues.

#### Reporting Channels

**Preferred Method**: Use GitHub Security Advisories

1. Go to
   [Security Advisories](https://github.com/SynergyMesh/SynergyMesh/security/advisories)
2. Click "Report a vulnerability"
3. Fill in the detailed information
4. Submit the report

**Email**: <security@synergymesh.io>

### 📋 Information to Include in Your Report

Please include the following in your report:

- **Vulnerability Type**: SQL injection, XSS, CSRF, etc.
- **Affected Components**: Specific files, features, or endpoints
- **Vulnerability Description**: Detailed explanation of the issue
- **Reproduction Steps**: How to reproduce the vulnerability
- **Impact Assessment**: Potential security impact
- **Suggested Fix**: If you have suggestions for fixing (optional)

### ⏱️ Response Timeline

| Stage                    | Timeframe         |
| ------------------------ | ----------------- |
| Initial Acknowledgment   | Within 24 hours   |
| Vulnerability Assessment | Within 72 hours   |
| Fix Plan                 | Within 7 days     |
| Patch Release            | Based on severity |

**Severity and Fix Timeline**:

- **Critical**: Begin fixing within 4 hours, release patch within 24 hours
- **High**: Begin fixing within 24 hours, release patch within 7 days
- **Medium**: Begin fixing within 7 days, release patch within 30 days
- **Low**: Begin fixing within 30 days, release patch within 90 days

### 🔐 Security Features

This project implements the following security measures:

#### Automated Security Scanning

- **CodeQL**: Static Application Security Testing (SAST)
  - Supports 8 programming languages
  - Custom enterprise-level query rules
  - Weekly automatic scanning

- **Secret Scanning**: Secret Detection
  - 30+ secret patterns
  - Push protection
  - Real-time detection and blocking

- **Dependency Scanning**: Dependency Scanning
  - Dependabot automatic updates
  - Automatic vulnerability fixes
  - SLA-driven fix process

#### Security Workflows

- PR Security Gate: Critical level automatically blocks merge
- Automatic Vulnerability Fix: Daily scanning and intelligent fixes
- Secret Bypass Approval: Standardized exception handling process

### 🔐 Organization Security Settings

```yaml
Two-Factor Authentication: Required for all members
SAML SSO: Enabled for enterprise accounts
IP Allowlists: Configured for sensitive repositories
Audit Log: Full access logging enabled
Dependency Scanning: Automated security updates
Secret Scanning: Enabled for all repositories
```

### Branch Protection Rules

```yaml
Branch Protection Rules:
  - Require pull request reviews: 2 reviewers minimum
  - Require status checks: All CI tests must pass
  - Require branches to be up to date: Yes
  - Include administrators: No
  - Allow force pushes: No
  - Allow deletions: No
```

### 📊 Security Monitoring

We use the following tools to monitor security status:

- **Prometheus**: Metrics collection and alerting
- **Elasticsearch**: Log aggregation and analysis
- **GitHub Advanced Security**: Comprehensive security platform

### 🔍 Responsible Disclosure Policy

We follow responsible disclosure principles:

1. **Confidentiality Period**: We require confidentiality until fix release
   (usually 90 days)
2. **Coordinated Disclosure**: We coordinate disclosure timing with reporters
3. **Acknowledgment**: We publicly thank reporters when fixes are released (if
   agreed)
4. **CVE Assignment**: For qualifying vulnerabilities, we apply for CVE numbers

### 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

### 🔗 Related Documentation

- [GHAS Complete Implementation Guide](docs/GHAS_COMPLETE_GUIDE.md)
- [CodeQL Setup Guide](docs/CODEQL_SETUP.md)
- [Secret Scanning Guide](docs/SECRET_SCANNING.md)
- [Vulnerability Management Process](docs/VULNERABILITY_MANAGEMENT.md)

### 📞 Contact

- **Security Team Email**: <security@synergymesh.io>
- **Emergency Contact**: <emergency@synergymesh.io>
- **Website**: [synergymesh.io](https://synergymesh.io)

### 🔄 Policy Updates

Last updated: November 2025

---

Thank you for helping keep SynergyMesh secure!
