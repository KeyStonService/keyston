# @synergymesh/advisory-database

Professional advisory database service for SynergyMesh - GitHub Advisory
Database compatible implementation.

## Features

- **OSV Format Compliance**: Full support for
  [Open Source Vulnerability (OSV)](https://ossf.github.io/osv-schema/) format
- **GHSA ID Generation**: Generate and validate GitHub Security Advisory IDs
- **Advisory Validation**: Comprehensive validation rules matching GitHub
  Advisory Database standards
- **Bot Workflow Engine**: Automated workflows for PR staging, stale PR
  management, and curation
- **Multi-Ecosystem Support**: npm, pip, maven, go, rust, cargo, rubygems,
  nuget, composer, erlang, swift, pub, actions

## Installation

```bash
npm install @synergymesh/advisory-database
```

## Quick Start

### Creating and Managing Advisories

```typescript
import {
  AdvisoryService,
  generateGHSAId,
  validateGHSAId,
} from '@synergymesh/advisory-database';

// Create a service instance
const service = new AdvisoryService();

// Create a new advisory
const { advisory } = await service.create({
  summary: 'SQL Injection in example-package',
  affected: [
    {
      package: { name: 'example-package', ecosystem: 'npm' },
      ranges: [
        {
          type: 'SEMVER',
          events: [{ introduced: '1.0.0' }, { fixed: '1.0.5' }],
        },
      ],
    },
  ],
  references: [
    {
      type: 'ADVISORY',
      url: 'https://nvd.nist.gov/vuln/detail/CVE-2024-1234',
    },
  ],
  database_specific: {
    severity: 'HIGH',
    cwe_ids: ['CWE-89'],
  },
});

console.log(`Created advisory: ${advisory.id}`);

// Search advisories
const npmAdvisories = await service.list({
  ecosystem: 'npm',
  severity: 'HIGH',
});

// Get statistics
const stats = await service.getStats();
console.log(`Total advisories: ${stats.total}`);
```

### GHSA ID Utilities

```typescript
import {
  generateGHSAId,
  validateGHSAId,
  parseGHSAId,
  extractGHSAIds,
  GHSAIdGenerator,
} from '@synergymesh/advisory-database';

// Generate a new GHSA ID
const id = generateGHSAId();
// Example: 'GHSA-c3gv-9cxf-6f57'

// Validate ID format
validateGHSAId('GHSA-c3gv-9cxf-6f57'); // true
validateGHSAId('invalid-id'); // false

// Parse ID segments
const parsed = parseGHSAId('GHSA-c3gv-9cxf-6f57');
// { prefix: 'GHSA', segment1: 'c3gv', segment2: '9cxf', segment3: '6f57' }

// Extract IDs from text
const ids = extractGHSAIds('See GHSA-c3gv-9cxf-6f57 for details');
// ['GHSA-c3gv-9cxf-6f57']

// Use the generator class for batch operations
const generator = new GHSAIdGenerator();
const id1 = generator.generate();
const id2 = generator.generate(); // Always unique
```

### Advisory Validation

```typescript
import { AdvisoryValidator } from '@synergymesh/advisory-database';

const validator = new AdvisoryValidator();

const result = validator.validate(advisory);
if (result.valid) {
  console.log('Advisory is valid!');
} else {
  console.log('Validation errors:', result.errors);
  console.log('Warnings:', result.warnings);
}

// Add custom validation rules
validator.addRule({
  id: 'CUSTOM_001',
  name: 'Require detailed description',
  severity: 'warning',
  validate: (advisory) => {
    if (!advisory.details || advisory.details.length < 100) {
      return 'Advisory should include detailed description';
    }
    return null;
  },
});
```

### Bot Workflow Engine

```typescript
import { AdvisoryBotEngine } from '@synergymesh/advisory-database';

const bot = new AdvisoryBotEngine({
  stalePR: {
    enabled: true,
    staleDays: 15,
    closeDays: 15,
    staleLabel: 'Stale',
    exemptLabels: ['Keep', 'Priority'],
    staleMessage: 'This PR has been marked as stale...',
    closeMessage: 'This PR has been closed due to inactivity.',
  },
});

// Check if a PR is stale
const staleStatus = bot.checkStaleStatus(pullRequest);
if (staleStatus.isStale) {
  console.log(`PR is stale (${staleStatus.daysSinceActivity} days)`);
}

// Generate staging branch name
const branchName = bot.generateStagingBranchName(pullRequest);
// 'username/advisory-improvement-123'

// Generate GitHub Actions workflows
const staleWorkflow = bot.generateStalePRWorkflow();
const stagingWorkflow = bot.generateStagingBranchWorkflow();
const cleanupWorkflow = bot.generateCleanupWorkflow();
```

## Supported Ecosystems

| Ecosystem  | Registry                   |
| ---------- | -------------------------- |
| `actions`  | GitHub Actions Marketplace |
| `composer` | packagist.org              |
| `erlang`   | hex.pm                     |
| `go`       | pkg.go.dev                 |
| `maven`    | repo.maven.apache.org      |
| `npm`      | npmjs.com                  |
| `nuget`    | nuget.org                  |
| `pip`      | pypi.org                   |
| `pub`      | pub.dev                    |
| `rubygems` | rubygems.org               |
| `rust`     | crates.io                  |
| `swift`    | Swift Package Registry     |

## API Reference

### AdvisoryService

| Method                              | Description                  |
| ----------------------------------- | ---------------------------- |
| `create(input)`                     | Create a new advisory        |
| `get(id)`                           | Get advisory by GHSA ID      |
| `update(id, input)`                 | Update an existing advisory  |
| `delete(id)`                        | Delete an advisory           |
| `list(filters)`                     | List advisories with filters |
| `searchByCVE(cveId)`                | Search by CVE ID             |
| `searchByPackage(name, ecosystem?)` | Search by package name       |
| `getStats()`                        | Get statistics               |
| `validate(advisory)`                | Validate without storing     |

### AdvisoryValidator

| Method               | Description                |
| -------------------- | -------------------------- |
| `validate(advisory)` | Validate an advisory       |
| `isValid(advisory)`  | Quick validation check     |
| `addRule(rule)`      | Add custom validation rule |
| `removeRule(ruleId)` | Remove a validation rule   |
| `getRules()`         | Get all active rules       |

### AdvisoryBotEngine

| Method                            | Description                      |
| --------------------------------- | -------------------------------- |
| `checkStaleStatus(pr)`            | Check if PR is stale             |
| `generateStagingBranchName(pr)`   | Generate staging branch name     |
| `shouldCreateStagingBranch(pr)`   | Check if staging branch needed   |
| `validateForCuration(advisory)`   | Validate for curation workflow   |
| `generateStalePRWorkflow()`       | Generate GitHub Actions workflow |
| `generateStagingBranchWorkflow()` | Generate staging branch workflow |
| `generateCleanupWorkflow()`       | Generate cleanup workflow        |

## Contributing

Please see the [CONTRIBUTING.md](../../CONTRIBUTING.md) file for guidelines.

## License

MIT - See [LICENSE](../../LICENSE) file for details.

## Related Resources

- [Open Source Vulnerability (OSV) Schema](https://ossf.github.io/osv-schema/)
- [GitHub Advisory Database](https://github.com/github/advisory-database)
- [GitHub Security Advisories](https://docs.github.com/en/code-security)
