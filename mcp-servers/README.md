# SynergyMesh MCP Servers
# MCP 服務器

Enterprise-grade Model Context Protocol (MCP) servers for the AutoExecutionEngine Agent.

> LLM 工具端點，提供 MCP 協議的工具供 LLM 調用。
> LLM tool endpoints, providing MCP protocol tools for LLM invocation.

## 🎯 Overview 概述

This directory contains specialized MCP servers that provide advanced capabilities for code analysis, testing, documentation, SLSA validation, security scanning, and performance optimization.

本目錄包含專門的 MCP 服務器，提供代碼分析、測試、文檔、SLSA 驗證、安全掃描和性能優化等高級功能。

## 🔷 What This Directory Does 本目錄負責什麼

### ✅ Responsibilities 職責

- 提供 **LLM 可調用的工具端點**（MCP 協議）
- 封裝特定功能為標準化 MCP 工具
- 處理工具的輸入驗證和輸出格式化
- 提供工具元數據和能力描述

### ❌ What This Directory Does NOT Do 本目錄不負責什麼

- **不實作核心業務邏輯** - 使用 `core/` 中的平台能力
- **不管理長生命週期代理狀態** - 使用 `agent/`
- **不組合複雜工作流** - 使用 `automation/intelligent/`

## 🔗 Dependencies 依賴關係

### ✅ Allowed Dependencies 允許的依賴

| Dependency 依賴 | Purpose 用途 |
|----------------|--------------|
| `core/` | 調用平台級 AI 能力 |
| `shared/` | 共用工具和配置 |

### ❌ Prohibited Dependencies 禁止的依賴

| Should NOT depend on 不應依賴 | Reason 原因 |
|------------------------------|-------------|
| `agent/` | MCP 端點不應依賴業務代理 |
| `automation/intelligent/` | MCP 端點不應依賴 pipeline |

---

## 📦 MCP Servers

### 1. Code Analyzer (`code-analyzer.js`)
**Capabilities:**
- `analyze-code` - Comprehensive code quality and complexity analysis
- `detect-issues` - Issue detection with severity filtering
- `suggest-improvements` - AI-powered code improvement suggestions

**Features:**
- Cyclomatic and cognitive complexity calculation
- Security vulnerability detection
- Performance issue identification
- Best practice validation
- Code smell detection

### 2. Test Generator (`test-generator.js`)
**Capabilities:**
- `generate-unit-tests` - Generate unit tests for functions and classes
- `generate-integration-tests` - Generate API integration tests
- `generate-e2e-tests` - Generate end-to-end test scenarios

**Features:**
- Multiple framework support (Jest, Mocha, Vitest, Playwright, Cypress)
- Configurable coverage levels (basic, comprehensive, exhaustive)
- Automatic test scaffold generation
- Edge case and error handling tests

### 3. Documentation Generator (`doc-generator.js`)
**Capabilities:**
- `generate-jsdoc` - Generate JSDoc documentation
- `generate-api-docs` - Generate API documentation (Markdown, OpenAPI)
- `generate-guides` - Generate comprehensive guides

**Features:**
- Multiple documentation styles (standard, Google, TypeScript)
- Automatic API reference generation
- Context-aware guide generation
- Multiple output formats (Markdown, OpenAPI, Postman)

### 4. SLSA Validator (`slsa-validator.js`)
**Capabilities:**
- `validate-provenance` - Validate SLSA provenance data
- `check-slsa-compliance` - Check compliance for target SLSA level
- `generate-compliance-report` - Generate comprehensive compliance reports

**Features:**
- SLSA Level 1-4 validation
- Compliance gap analysis
- Remediation recommendations
- Detailed compliance reporting

### 5. Security Scanner (`security-scanner.js`)
**Capabilities:**
- `scan-vulnerabilities` - Scan for security vulnerabilities
- `check-dependencies` - Check dependencies for known CVEs
- `analyze-secrets` - Detect exposed secrets and credentials

**Features:**
- SQL injection detection
- XSS vulnerability detection
- Command injection detection
- Hardcoded secret detection
- Dependency vulnerability checking
- CWE and OWASP mapping

### 6. Performance Analyzer (`performance-analyzer.js`)
**Capabilities:**
- `analyze-performance` - Analyze code performance metrics
- `identify-bottlenecks` - Identify performance bottlenecks
- `suggest-optimizations` - Suggest performance optimizations

**Features:**
- Complexity analysis (cyclomatic, cognitive, Halstead)
- Memory usage analysis
- Loop optimization detection
- Async performance analysis
- Bottleneck identification
- Optimization recommendations

## 🚀 Installation

```bash
cd mcp-servers
npm install
```

## ✅ Strict Validation & Quality Checks

This project includes enterprise-grade validation tools:

### Available Validation Commands

```bash
# Run ESLint code quality checks
npm run lint

# Run deployment configuration validation
npm run validate:deployment

# Run logic and authenticity validation
npm run validate:logic

# Run comprehensive validation (all checks)
npm run validate:comprehensive

# Run complete strict validation suite
npm run check:strict
```

### Validation Features

#### 1. **Deployment Configuration Validator**
- ✅ Required files check (package.json, README.md, .gitignore)
- ✅ Package.json structure validation
- ✅ Security configuration verification
- ✅ Environment variable validation
- ✅ Node.js version compatibility check

#### 2. **Logic Validator**
- ✅ **Authenticity checks**: Detects suspicious patterns (eval, dynamic functions)
- ✅ **Obfuscation detection**: Identifies potentially obfuscated code
- ✅ **Integrity hashing**: SHA-256 hash for code verification
- ✅ **Logic validation**: Detects unreachable code, infinite loops, empty catch blocks
- ✅ **Consistency checks**: Validates indentation, naming conventions, quote styles
- ✅ **Pattern validation**: Checks error handling, async/await usage, resource cleanup
- ✅ **Dependency analysis**: Validates import/require statements

#### 3. **Comprehensive Validator**
Combines all validators and provides:
- 📊 Overall quality score and grade
- 📈 Per-file analysis with warnings count
- 🎯 Prioritized recommendations
- 📝 Detailed validation report

### Validation Report Example

```
═══════════════════════════════════════════════════════
          COMPREHENSIVE VALIDATION REPORT
═══════════════════════════════════════════════════════

Overall Status: ✓ PASSED
Overall Score: 95/100 (Grade: A)

─── SUMMARY ───
Total Files: 9
Validated Files: 9
Total Issues: 0
Critical Issues: 0
Warnings: 5

─── RECOMMENDATIONS ───
[INFO] Status
  All validations passed successfully
  → Maintain current quality standards
```

## 📖 Usage

### Running Individual Servers

Each server can be run independently:

```bash
node code-analyzer.js
node test-generator.js
node doc-generator.js
node slsa-validator.js
node security-scanner.js
node performance-analyzer.js
```

### Configuration

Servers can be configured via environment variables:

```bash
# For SLSA Validator
export SLSA_LEVELS="1,2,3,4"

# For all servers
export NODE_ENV="production"
export LOG_LEVEL="info"
```

### Integration with Agent

The MCP servers are automatically configured in `.github/agents/my-agent.agent.md`:

```yaml
mcp-servers:
  - name: code-analyzer
    command: node
    args: ["./mcp-servers/code-analyzer.js"]
    capabilities:
      - analyze-code
      - detect-issues
      - suggest-improvements
  # ... (additional servers)
```

## 🔧 Development

### Running Lint

```bash
npm run lint
```

### Running Tests

```bash
npm test
```

## 📝 Example Usage

### Code Analysis Example

```javascript
// Input
const request = {
  name: 'analyze-code',
  arguments: {
    code: 'function example() { ... }',
    language: 'javascript',
    options: {
      checkComplexity: true,
      checkSecurity: true
    }
  }
};

// Output
{
  "language": "javascript",
  "metrics": {
    "totalLines": 10,
    "codeLines": 8,
    "commentLines": 1
  },
  "complexity": {
    "cyclomatic": 3,
    "cognitive": 2,
    "rating": "A - Simple"
  },
  "issues": [],
  "score": 95
}
```

### SLSA Validation Example

```javascript
// Input
const request = {
  name: 'validate-provenance',
  arguments: {
    provenance: {
      _type: "https://in-toto.io/Statement/v0.1",
      predicateType: "https://slsa.dev/provenance/v0.2",
      subject: [...],
      predicate: {...}
    },
    level: '3'
  }
};

// Output
{
  "valid": true,
  "level": "3",
  "checks": [...],
  "errors": [],
  "warnings": [],
  "score": 95
}
```

## 🏗️ Architecture

All MCP servers follow the same architectural pattern:

1. **Server Initialization** - Create MCP server with capabilities
2. **Tool Registration** - Register available tools and schemas
3. **Request Handling** - Handle tool calls with validation
4. **Response Generation** - Return structured results
5. **Error Handling** - Comprehensive error handling and validation

## 🔒 Security

- All servers use Zod for input validation
- No external network calls without explicit permission
- Secrets are masked in analysis output
- Follow principle of least privilege

## 📊 Performance

- Efficient pattern matching algorithms
- Minimal memory footprint
- Fast response times (<100ms for most operations)
- Async/await for non-blocking operations

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

## 🆘 Support

For issues and questions:
- Open an issue in the repository
- Check documentation at `/docs`
- Contact the SynergyMesh team

---

**Version:** 1.0.0  
**Last Updated:** November 2025  
**Maintainer:** SynergyMesh Team
