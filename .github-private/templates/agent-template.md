# {Agent Name} Agent

## Description

{簡短描述（中文）}

{Short description in English}

## Capabilities

- **{Capability 1}**: {Description}
- **{Capability 2}**: {Description}
- **{Capability 3}**: {Description}

## Configuration

```yaml
{ agent_name }:
  enabled: true
  # Add agent-specific configuration here
```

## Triggers

- {Trigger 1}
- {Trigger 2}
- {Trigger 3}

## Instructions

You are a {domain} expert for the SynergyMesh platform. When performing your
tasks:

1. **{Task Category 1}**
   - {Subtask 1.1}
   - {Subtask 1.2}
   - {Subtask 1.3}

2. **{Task Category 2}**
   - {Subtask 2.1}
   - {Subtask 2.2}
   - {Subtask 2.3}

3. **{Task Category 3}**
   - {Subtask 3.1}
   - {Subtask 3.2}
   - {Subtask 3.3}

## Output Format

```json
{
  "task_id": "{task_id}",
  "timestamp": "ISO8601 timestamp",
  "summary": {
    // Summary fields
  },
  "results": [
    // Result items
  ]
}
```

## Example Report

```markdown
# {Report Title}

**Date**: {date} **Status**: {status}

## Summary

{Summary content}

## Details

{Detailed content}

## Recommendations

{Recommendations}
```

## Integration

This agent integrates with:

- {Integration 1}
- {Integration 2}
- {Integration 3}

## Permissions Required

- `{permission1}: {access_level}`
- `{permission2}: {access_level}`
- `{permission3}: {access_level}`

---

## Template Usage Notes

1. Replace all `{placeholder}` values with actual content
2. Add agent-specific sections as needed
3. Keep documentation bilingual (Chinese and English) where appropriate
4. Follow existing agent patterns in this directory
5. Update `config/agent-settings.yml` with new agent configuration

## Checklist for New Agents

- [ ] Replace all placeholders
- [ ] Add meaningful capabilities
- [ ] Define clear triggers
- [ ] Write detailed instructions
- [ ] Specify output format
- [ ] Include example report
- [ ] List required integrations
- [ ] Document required permissions
- [ ] Update README.md
- [ ] Add configuration to agent-settings.yml
