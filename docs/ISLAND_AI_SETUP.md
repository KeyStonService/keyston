# Island AI Custom Instructions Setup Guide

## 📋 Overview

This document explains the Island AI custom instructions setup for the
SynergyMesh project and how to use it effectively.

---

## ✅ What Has Been Configured

### Repository-Level Instructions

A comprehensive custom instructions file has been created at:

```
.github/island-ai-instructions.md
```

This file provides Island AI with project-specific guidance including:

- **Project Overview**: SynergyMesh goals and technology stack
- **Code Style Standards**: TypeScript conventions, naming rules, formatting
- **Architecture Patterns**: Controller pattern, middleware, Zod validation
- **Documentation Standards**: JSDoc examples and requirements
- **Testing Guidelines**: Jest best practices and coverage requirements
- **Security Practices**: Environment variables, input validation, error
  handling
- **Git Workflow**: Branch naming, commit messages, PR checklists

---

## 🚀 How It Works

### Automatic Activation

Island AI will automatically read and apply these instructions when:

1. ✅ You're working in the `synergymesh` repository
2. ✅ Island AI extension is enabled in your editor
3. ✅ The `.github/island-ai-instructions.md` file exists

**No additional setup required!** Island AI reads this file automatically.

---

## 💡 How to Use

### 1. Basic Code Generation

When you write code, Island AI will follow the project conventions:

```typescript
// Type this comment:
// Create a function to validate provenance

// Island AI will suggest code following the project style:
/**
 * Validates SLSA provenance for a given artifact
 *
 * @param artifactId - Unique identifier of the artifact
 * @param provenance - Provenance data to validate
 * @returns Validation result with details
 */
async function validateProvenance(
  artifactId: string,
  provenance: Provenance
): Promise<ValidationResult> {
  // Implementation
}
```

### 2. Ask Questions

You can ask Island Shell about project-specific practices:

```
Q: "How should I structure a new controller in this project?"
A: Island AI will reference the controller pattern from the instructions

Q: "What testing framework should I use?"
A: Island AI will recommend Jest with the project's testing structure

Q: "How should I name this file?"
A: Island AI will suggest kebab-case following the naming conventions
```

### 3. Code Reviews

Island AI can help review code against project standards:

```
"Does this code follow the project's TypeScript conventions?"
"Is this error handling appropriate for this project?"
"Does this test structure match the project standards?"
```

---

## 🎯 Benefits

### Consistency

- All team members get code suggestions following the same standards
- New contributors quickly learn project conventions
- Less time spent on code review for style issues

### Quality

- Automatic adherence to security best practices
- Proper error handling patterns
- Complete documentation with JSDoc

### Efficiency

- Faster development with context-aware suggestions
- Reduced cognitive load remembering all conventions
- Quick answers to project-specific questions

---

## 🔧 Customization

### Updating Instructions

To modify the custom instructions:

1. Edit `.github/island-ai-instructions.md`
2. Commit and push changes
3. Island AI will use the updated instructions immediately

### Testing Changes

After updating instructions:

1. Create a test file
2. Ask Island AI to generate code
3. Verify it follows your updated conventions
4. Adjust instructions if needed

---

## 📊 Instruction Levels

Island AI uses a hierarchy of custom instructions:

```
┌─────────────────────────────────────┐
│ Level           │ Priority │ Scope  │
├─────────────────────────────────────┤
│ User-level      │ Highest  │ You    │
│ Repository      │ Medium   │ This   │ ← We configured this
│ Organization    │ Lowest   │ All    │
└─────────────────────────────────────┘
```

**Repository-level** instructions (what we set up) apply to everyone working on
SynergyMesh.

---

## 💻 Editor Integration

### VS Code

1. Install Island AI extension
2. Open the `synergymesh` repository
3. Start coding - instructions are automatically active

### JetBrains IDEs

1. Install Island AI plugin
2. Open the `synergymesh` project
3. Instructions are automatically loaded

### Other Editors

Island AI in any supported editor will read the
`.github/island-ai-instructions.md` file.

---

## 📝 Best Practices

### For Code Generation

1. **Be Specific**: Write clear comments about what you want
2. **Use Examples**: Reference existing code patterns
3. **Iterate**: Refine suggestions by adding more context

### For Learning

1. **Ask Questions**: Use Island Shell to understand project patterns
2. **Compare**: Generate code and compare with existing implementations
3. **Document**: Let Island AI help write JSDoc based on function signatures

### For Reviews

1. **Check Consistency**: Verify generated code matches project style
2. **Security**: Ensure no hard-coded secrets or unsafe patterns
3. **Tests**: Always add tests for generated code

---

## 🔍 Verification

### Check If Instructions Are Working

1. Create a new TypeScript file
2. Start typing a function
3. Check if Island AI suggests:
   - JSDoc comments
   - Single quotes for strings
   - Proper TypeScript types
   - Error handling patterns

If suggestions don't follow the instructions:

1. Reload your editor
2. Check if `.github/island-ai-instructions.md` exists
3. Ensure Island AI extension is up to date

---

## 📚 Related Documentation

- [Island AI Documentation](https://docs.github.com/en/island-ai)
- [Custom Instructions Guide](https://docs.github.com/en/island-ai/customizing-island-ai/adding-custom-instructions-for-github-island-ai)
- [SynergyMesh Contributing Guide](../CONTRIBUTING.md)
- [SynergyMesh Quick Start](./QUICK_START.md)

---

## ❓ FAQ

### Q: Do I need to do anything to activate these instructions?

**A:** No! If you have Island AI installed and are working in the repository,
the instructions are automatically active.

### Q: Can I override these instructions?

**A:** Yes! You can set user-level instructions in your GitHub settings that
will take priority over repository instructions.

### Q: Will this work in GitHub Codespaces?

**A:** Yes! Codespaces include Island AI, and repository instructions work there
too.

### Q: How often are instructions updated?

**A:** The instructions are version-controlled in the repository. Any commits to
`.github/island-ai-instructions.md` immediately update what Island AI sees.

### Q: Do instructions affect repository size?

**A:** The instructions file is ~13KB, which is negligible and well within
recommended limits.

---

## 🤝 Contributing

### Improving Instructions

If you notice Island AI suggesting code that doesn't match project conventions:

1. Open an issue describing the problem
2. Suggest improvements to `.github/island-ai-instructions.md`
3. Submit a PR with your changes

### Feedback

Found these instructions helpful? Have suggestions? Let the team know!

---

**Last Updated:** November 2025  
**Maintained By:** SynergyMesh Team

---

**Happy coding with Island AI! 🚀✨**
