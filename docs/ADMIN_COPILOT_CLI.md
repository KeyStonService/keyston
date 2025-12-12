# Admin Copilot CLI (Public Preview)

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)
![Node.js](https://img.shields.io/badge/Node.js-22+-green?style=for-the-badge&logo=node.js)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

**The power of Admin Copilot, now in your terminal.**

</div>

---

Admin Copilot CLI brings AI-powered code analysis and operation capabilities to
your command line. It enables the system to understand its own code through
natural language and execute build, debug, and maintenance workflows. Powered by
the same agentic harness as Admin Copilot coding agent, it provides intelligent
assistance while staying deeply integrated with your GitHub workflow.

<p align="center">
  <img src="https://github.com/user-attachments/assets/51ac25d2-c074-467a-9c88-38a8d76690e3" alt="Admin Copilot CLI Demo" width="800">
</p>

## 🚀 Introduction and Overview

We're bringing the power of Admin Copilot coding agent directly to your
terminal. With Admin Copilot CLI, you can work locally and synchronously with an
AI agent that understands your code and GitHub context.

### Key Features

- **Terminal-native development:** Work with Copilot coding agent directly in
  your command line — no context switching required.
- **GitHub integration out of the box:** Access your repositories, issues, and
  pull requests using natural language, all authenticated with your existing
  GitHub account.
- **Agentic capabilities:** Build, edit, debug, and refactor code with an AI
  collaborator that can plan and execute complex tasks.
- **MCP-powered extensibility:** Take advantage of the fact that the coding
  agent ships with GitHub's MCP server by default and supports custom MCP
  servers to extend capabilities.
- **Full control:** Preview every action before execution — nothing happens
  without your explicit approval.

We're still early in our journey, but with your feedback, we're rapidly
iterating to make the Admin Copilot CLI the best possible companion in your
terminal.

## 📦 Getting Started

### Supported Platforms

| Platform    | Status                       |
| ----------- | ---------------------------- |
| **Linux**   | ✅ Supported                 |
| **macOS**   | ✅ Supported                 |
| **Windows** | ✅ Supported (PowerShell 6+) |

### Prerequisites

- **Node.js** v22 or higher
- **npm** v10 or higher
- (On Windows) **PowerShell** v6 or higher
- An **active Copilot subscription**. See
  [Copilot plans](https://github.com/features/copilot/plans?ref_cta=Copilot+plans+signup&ref_loc=install-copilot-cli&ref_page=docs).

> **Note:** If you have access to GitHub Copilot via your organization or
> enterprise, you cannot use Admin Copilot CLI if your organization owner or
> enterprise administrator has disabled it in the organization or enterprise
> settings. See
> [Managing policies and features for GitHub Copilot in your organization](http://docs.github.com/copilot/managing-copilot/managing-github-copilot-in-your-organization/managing-github-copilot-features-in-your-organization/managing-policies-for-copilot-in-your-organization)
> for more information.

### Installation

Install globally with npm:

```bash
npm install -g @synergymesh/admin-copilot-cli
```

Or install locally from the repository:

```bash
cd tools/cli
npm install
npm link
```

### Launching the CLI

```bash
admin-copilot
```

Or use the short alias:

```bash
smcli
```

On first launch, you'll be greeted with our adorable animated banner! If you'd
like to see this banner again, launch `admin-copilot` with the `--banner` flag.

If you're not currently logged in to GitHub, you'll be prompted to use the
`/login` slash command. Enter this command and follow the on-screen instructions
to authenticate.

### Authenticate with a Personal Access Token (PAT)

You can also authenticate using a fine-grained PAT with the "Copilot Requests"
permission enabled.

1. Visit <https://github.com/settings/personal-access-tokens/new>
2. Under "Permissions," click "add permissions" and select "Copilot Requests"
3. Generate your token
4. Add the token to your environment via the environment variable `GH_TOKEN` or
   `GITHUB_TOKEN` (in order of precedence)

## 🛠️ Using the CLI

Launch `admin-copilot` in a folder that contains code you want to work with.

### Available Commands

| Command                  | Description                             |
| ------------------------ | --------------------------------------- |
| `chat`                   | Start an interactive AI chat session    |
| `analyze [path]`         | Analyze code in the specified directory |
| `fix`                    | Fix issues in your codebase             |
| `explain <query>`        | Explain code or concepts                |
| `generate <description>` | Generate code from natural language     |
| `review [path]`          | Review code for best practices          |
| `test [path]`            | Generate tests for your code            |

### Slash Commands (in chat)

| Command     | Description                                      |
| ----------- | ------------------------------------------------ |
| `/login`    | Authenticate with GitHub                         |
| `/logout`   | Sign out of GitHub                               |
| `/model`    | Choose AI model (Claude Sonnet 4.5, GPT-5, etc.) |
| `/feedback` | Submit feedback                                  |
| `/help`     | Show help information                            |
| `/exit`     | Exit the CLI                                     |

### Model Selection

By default, `admin-copilot` utilizes **Claude Sonnet 4.5**. Run the `/model`
slash command to choose from other available models:

- Claude Sonnet 4.5 (default)
- Claude Sonnet 4
- GPT-5
- GPT-4o

### Premium Requests

Each time you submit a prompt to Admin Copilot CLI, your monthly quota of
premium requests is reduced by one. For information about premium requests, see
[About premium requests](https://docs.github.com/copilot/managing-copilot/monitoring-usage-and-entitlements/about-premium-requests).

## 💡 Examples

### Start a Chat Session

```bash
admin-copilot chat
```

### Analyze Your Code

```bash
admin-copilot analyze ./src
```

### Auto-fix Issues

```bash
admin-copilot fix --auto
```

### Explain a Concept

```bash
smcli explain "What is SLSA provenance?"
```

### Generate Code

```bash
admin-copilot generate "Create a REST API endpoint for user authentication" --language typescript
```

### Review Code

```bash
admin-copilot review ./src/controllers
```

### Generate Tests

```bash
admin-copilot test ./src/utils --framework jest
```

## 🔧 Configuration

### Environment Variables

| Variable              | Description                                    |
| --------------------- | ---------------------------------------------- |
| `GH_TOKEN`            | GitHub authentication token (highest priority) |
| `GITHUB_TOKEN`        | Alternative GitHub authentication token        |
| `ADMIN_COPILOT_MODEL` | Default AI model                               |
| `ADMIN_COPILOT_DEBUG` | Enable debug logging                           |

### Configuration File

You can also create a `.admin-copilot.yml` configuration file in your home
directory or project root:

```yaml
# ~/.admin-copilot.yml
model: claude-sonnet-4.5
theme: dark
autoApprove: false
mcp:
  servers:
    - name: github
      enabled: true
    - name: custom-server
      url: http://localhost:3000
```

## 🔌 MCP Integration

Admin Copilot CLI supports Model Context Protocol (MCP) servers for extended
functionality. By default, it ships with GitHub's MCP server enabled.

### Connecting Custom MCP Servers

```bash
admin-copilot mcp add --name my-server --url http://localhost:3000
```

### Listing Connected Servers

```bash
admin-copilot mcp list
```

## 🏝️ Unmanned Island System Integration

Admin Copilot CLI is fully integrated with the SynergyMesh Unmanned Island
System, providing:

- **Drone Control:** Issue commands to the autonomous drone fleet
- **System Monitoring:** Query system health and metrics
- **Configuration Management:** Update system configurations through natural
  language
- **Incident Response:** Get AI-assisted incident analysis and recommendations

### Island-Specific Commands

```bash
# Check system status
smcli island status

# Deploy to island
smcli island deploy --target production

# Query metrics
smcli island metrics --range 24h
```

## 📢 Feedback and Participation

We're excited to have you join us early in the Admin Copilot CLI journey.

> **Note:** This is an early-stage preview, and we're building quickly. Expect
> frequent updates—please keep your client up to date for the latest features
> and fixes!

Your insights are invaluable!

- **Open issues** in this repo
- **Join Discussions** on GitHub
- **Run `/feedback`** from the CLI to submit a confidential feedback survey

## 📚 Additional Resources

- [Official Documentation](https://docs.synergymesh.io/admin-copilot-cli)
- [SynergyMesh Main Documentation](../README.md)
- [MCP Servers Documentation](../../mcp-servers/README.md)
- [Contributing Guide](../../CONTRIBUTING.md)

## 🔒 Security

For security concerns, please see our [Security Policy](../../SECURITY.md).

## 📄 License

This project is licensed under the MIT License - see the
[LICENSE](../../LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by the SynergyMesh Team**

🏝️ _Unmanned Island System - Autonomous Intelligence at Scale_ 🏝️

</div>
