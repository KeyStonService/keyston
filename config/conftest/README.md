# Conftest Configuration

This directory contains the Conftest framework configuration.

## Structure

```
.config/
└── conftest/
    └── policies -> ../../.meta/policies/  # Symlink to centralized policies
```

## Usage

Conftest policies are centralized in `.meta/policies/`. This directory only contains framework configuration.

## Running Policy Checks

```bash
conftest test <file> -p .meta/policies/
```

## See Also

- [Conftest Documentation](https://www.conftest.dev/)
- [Policies Directory](../../.meta/policies/)
