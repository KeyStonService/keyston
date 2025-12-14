# Agent Configuration Directory
# 智能代理配置目錄

This directory contains all agent-related configurations for the SynergyMesh platform.

## 📁 Directory Structure

```
config/agents/
├── profiles/           # Individual agent profiles (個別代理配置)
│   └── recovery_expert.yaml
├── team/              # Team/multi-agent configurations (團隊配置)
│   └── virtual-experts.yaml
├── schemas/           # JSON schemas for validation (驗證模式)
│   └── virtual-experts.schema.json
└── README.md          # This file
```

## 📋 Configuration Types

### 1. Individual Agent Profiles (`profiles/`)

Single agent configurations defining specific capabilities and behaviors.

**Example**: `recovery_expert.yaml`
- Recovery and self-healing capabilities
- Dr. Phoenix agent configuration
- Error detection and automated repair

**Format**:
```yaml
agent:
  id: agent_id
  name: "Agent Name"
  role: "Agent Role"
  capabilities: []
  configuration: {}
```

### 2. Team Configurations (`team/`)

Multi-agent team configurations for collaborative workflows.

**Example**: `virtual-experts.yaml`
- Expert team definitions (AI Architect, NLP Expert, Security Architect, etc.)
- Domain mapping and routing
- Consultation strategies

**Format**:
```yaml
experts:
  version: "1.0.0"
  team_name: "Team Name"
team:
  - id: expert_id
    name: "Expert Name"
    role: "Expert Role"
    domains: []
    expertise: {}
```

### 3. Schemas (`schemas/`)

JSON Schema definitions for configuration validation.

**Available schemas**:
- `virtual-experts.schema.json` - Validates virtual-experts.yaml structure

## 🔧 Adding New Agents

### Step 1: Choose Configuration Type

- **Single Agent**: Create a new YAML file in `profiles/`
- **Team/Expert**: Add to `team/virtual-experts.yaml`

### Step 2: Define Configuration

Follow the format guidelines above. Key elements:
- Unique ID
- Clear role and responsibilities
- Domain expertise
- Capabilities and permissions

### Step 3: Validate Schema

If modifying team configurations:
```bash
# Validate against schema
python tools/scripts/validate-config.js
```

### Step 4: Update Domain Mapping

For expert teams, update the `domain_mapping` section in `virtual-experts.yaml`:
```yaml
domain_mapping:
  YOUR_DOMAIN:
    primary: expert_id
    secondary: [backup_expert_id]
```

### Step 5: Implement Agent

Create agent implementation in `services/agents/`:
```
services/agents/
└── your-agent/
    ├── README.md
    ├── agent.py (or .ts, .js)
    └── tests/
```

## 📖 Related Documentation

- **Agent Implementations**: `services/agents/README.md`
- **AI Constitution**: `config/ai-constitution.yaml`
- **System Architecture**: `docs/ARCHITECTURE.md`
- **Virtual Experts Guide**: `automation/autonomous/nucleus-orchestrator/README.md`

## 🔗 Configuration References

Agent configurations can reference:
- Environment configurations: `config/environment.yaml`
- AI governance principles: `config/ai-constitution.yaml`
- Tool dependencies: `config/dependencies.yaml`
- System capabilities: `config/system-manifest.yaml`

## 🚀 Usage Examples

### Loading Agent Configuration (Python)

```python
import yaml
from pathlib import Path

# Load individual profile
with open('config/agents/profiles/recovery_expert.yaml') as f:
    recovery_config = yaml.safe_load(f)

# Load expert team
with open('config/agents/team/virtual-experts.yaml') as f:
    experts_config = yaml.safe_load(f)
```

### Loading Agent Configuration (TypeScript)

```typescript
import * as yaml from 'js-yaml';
import * as fs from 'fs';

// Load configuration
const recoveryConfig = yaml.load(
  fs.readFileSync('config/agents/profiles/recovery_expert.yaml', 'utf8')
);
```

## 🔍 Validation

All configurations should be validated before deployment:

```bash
# Validate all agent configurations
npm run validate:configs

# Validate specific schema
python tools/docs/validate_index.py --verbose
```

## 🛡️ Security Considerations

- Agent configurations may contain sensitive capability definitions
- Follow principle of least privilege
- Document all permission grants
- Review configurations during security audits
- Validate against schemas before deployment

## 📝 Naming Conventions

### Agent IDs
- Format: `snake_case` or `domain.role` format
- Example: `expert_alex_chen`, `recovery.phoenix`

### File Names
- Format: `kebab-case.yaml`
- Example: `recovery-expert.yaml`, `virtual-experts.yaml`

### Domain Names
- Format: `SCREAMING_SNAKE_CASE` for domain mapping
- Example: `AI_ML`, `DATABASE`, `SECURITY`

## 🔄 Migration Notes

**Previous locations** (now consolidated here):
- `config/virtual-experts.yaml` → `config/agents/team/virtual-experts.yaml`
- `infra/config/virtual-experts.yaml` → Removed (duplicate)
- `governance/schemas/virtual-experts.schema.json` → `config/agents/schemas/virtual-experts.schema.json`

All references have been updated accordingly.

## 📞 Support

For questions or issues:
- Check `services/agents/README.md` for implementation details
- Review AI Behavior Contract: `.github/AI-BEHAVIOR-CONTRACT.md`
- See technical guidelines: `.github/copilot-instructions.md`

---

**Last Updated**: 2025-12-09
**Maintained by**: SynergyMesh Core Team
