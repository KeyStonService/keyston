# AI Refactor Suggestions

**Generated:** 2025-12-06T15:00:00Z  
**Status:** Active

## Global Recommendations

### Language Strategy

1. **High-Level Languages (Business Logic & Services)**
   - Primary: TypeScript, Python
   - Use TypeScript for all web services, APIs, and frontend
   - Use Python for automation, AI/ML, and data processing

2. **Low-Level Languages (Performance & Hardware)**
   - Primary: C++, Go, Rust
   - Use C++ for ROS2 autonomous systems
   - Use Go for high-performance services
   - Use Rust for critical security components

3. **Forbidden Languages**
   - PHP: Legacy, security concerns, replace with TypeScript
   - Perl: Deprecated, replace with Python
   - Ruby: Not part of tech stack, replace with TypeScript/Python
   - Lua: Limited use cases, prefer Python or TypeScript

### Architecture Guidelines

1. **Layer Separation**
   - Core layer: TypeScript + Python only
   - Services layer: TypeScript + Python + Go
   - Autonomous layer: C++ (ROS2) + Python
   - Tools layer: Python + TypeScript

2. **Migration Priorities**
   - P0: Remove all forbidden languages (PHP, Perl)
   - P1: Convert JavaScript to TypeScript
   - P2: Consolidate similar functionality across layers

3. **Auto-Fix Opportunities**
   - JavaScript → TypeScript conversion (with type inference)
   - Simple file moves between directories
   - Import path updates
   - Code style formatting

4. **Manual Review Required**
   - Core business logic changes
   - API contract modifications
   - Cross-service dependencies
   - Security-critical code

### Best Practices

1. Keep language diversity minimal within each directory
2. Use strong typing (TypeScript over JavaScript)
3. Prefer interpreted languages for high-level logic
4. Use compiled languages for performance-critical paths
5. Maintain clear boundaries between layers

### Delivery Requirements

**All language refactoring, Auto-Fix plans, and Refactor Playbooks MUST include:**

1. **Affected Directories List**
   - Explicitly list all directories involved in the refactoring
   - Example: `core/`, `services/gateway/`, `automation/autonomous/`

2. **Complete File/Directory Structure Diagram**
   - Use tree-style text (indented directory and file listing)
   - Or use Mermaid diagrams
   - Must cover the scope of changes (not entire repo)
   - Must be clear and readable, showing directory hierarchies

3. **File and Directory Annotations**
   - For each important directory/file, provide a brief description of its purpose
   - Format: `path/to/file.ts` — One-line description of the file's responsibility
   - Format: `dir/` — Description of what type of content the directory contains

**Why This Matters:**

- Makes change scope immediately clear
- Helps future maintainers understand the refactoring
- Enables better handoff to third-party platforms or other agents
- Provides "before and after" structural snapshots for each refactoring wave

**Example Format:**

```
### Affected Directories
- services/gateway/
- core/contract_service/

### Structure View (Change Scope Only)

services/gateway/
├── router.cpp          # Legacy C++ gateway entry (migration target)
├── router.ts           # New TypeScript gateway (goal)
├── middleware/
│   ├── auth.ts         # Authentication middleware
│   └── logging.ts      # Logging middleware
└── types/
    └── request.ts      # Request type definitions

### File Descriptions
- `services/gateway/router.cpp` — Existing C++ gateway router, works with legacy core/
- `services/gateway/router.ts` — Proposed TypeScript implementation for frontend and microservices
- `services/gateway/middleware/` — Middleware directory for cross-cutting concerns
```
