# Validation Guide | 驗證指南

## Overview | 概述

The SynergyMesh validation system provides comprehensive multi-layer validation.

## Validation Layers | 驗證層

### 1. Syntax Validation
- Python: AST parsing
- YAML: Safe load
- JSON: JSON parsing

### 2. Semantic Validation
- Type checking
- Scope validation
- API contract validation

### 3. Security Validation
- Hardcoded secrets detection
- SQL injection prevention
- XSS prevention
- OWASP Top 10 checks

### 4. Performance Validation
- Complexity analysis
- Benchmark testing

### 5. Compliance Validation
- Policy enforcement
- Standards compliance

## Configuration

Edit `config/validation-rules.yaml` to customize validation rules.

## Custom Validators

Create custom validators by extending base classes.
