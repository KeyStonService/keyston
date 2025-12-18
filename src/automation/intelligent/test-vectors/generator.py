"""
Test Vector Generator - 測試向量生成器

Dynamically generates security test vectors for code analysis testing.
Combines external JSON templates with dynamic code generation.

Design: A + B approach
- A: Load base patterns from JSON (security-samples.json)
- B: Dynamically generate variations and combinations

This approach:
1. Avoids hardcoding vulnerable code in source files
2. Allows flexible test case generation
3. Improves test coverage through variations
4. Keeps security scanners happy (no vulnerable .py code)
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class VulnerabilityPattern:
    """Base pattern for generating vulnerable code."""

    id: str
    name: str
    category: str
    severity: str
    cwe: str
    template: str
    variables: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class GeneratedTestCase:
    """A dynamically generated test case."""

    id: str
    name: str
    category: str
    severity: str
    cwe: str
    code: str
    expected_issues: list[dict[str, str]]
    metadata: dict[str, Any] = field(default_factory=dict)


class TestVectorGenerator:
    """
    動態測試向量生成器

    Combines static JSON templates with dynamic generation for
    comprehensive security testing without triggering false positives.
    """

    # Code generation building blocks (not actual vulnerable code)
    FUNCTION_NAMES = ["process", "handle", "execute", "run", "perform"]
    VARIABLE_NAMES = ["data", "input", "value", "content", "payload"]
    USER_INPUT_SOURCES = ["user_input", "request.data", "form.get('input')", "args[0]"]

    # Vulnerability templates (patterns, not actual code)
    VULNERABILITY_TEMPLATES: dict[str, dict[str, Any]] = {
        "eval_injection": {
            "pattern": "result = {dangerous_func}({user_input})",
            "dangerous_funcs": ["eval", "exec"],
            "cwe": "CWE-95",
        },
        "sql_injection": {
            "pattern": 'query = "{prefix}" + {user_input} + "{suffix}"',
            "prefixes": ["SELECT * FROM users WHERE id = ", "DELETE FROM logs WHERE user = "],
            "suffixes": ["", " AND 1=1"],
            "cwe": "CWE-89",
        },
        "command_injection": {
            "pattern": "{module}.{func}({user_input}, shell={shell})",
            "modules": ["subprocess", "os"],
            "funcs": ["run", "system", "popen"],
            "shells": ["True"],
            "cwe": "CWE-78",
        },
        "hardcoded_secret": {
            "pattern": '{var_name} = "{secret_value}"',
            "var_names": ["password", "api_key", "secret", "token"],
            "secret_values": ["PLACEHOLDER_NOT_REAL", "TEST_VALUE_ONLY"],
            "cwe": "CWE-798",
        },
    }

    def __init__(self, vectors_dir: Path | None = None) -> None:
        """Initialize the generator.

        Args:
            vectors_dir: Directory containing JSON test vectors.
        """
        self.vectors_dir = vectors_dir or Path(__file__).parent
        self.base_vectors = self._load_base_vectors()

    def _load_base_vectors(self) -> dict[str, Any]:
        """Load base test vectors from JSON file."""
        json_path = self.vectors_dir / "security-samples.json"

        if json_path.exists():
            with open(json_path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
                return data

        return {"test_cases": [], "performance_cases": []}

    def generate_eval_injection(self, variation: int = 0) -> GeneratedTestCase:
        """Generate an eval injection test case.

        Args:
            variation: Which variation to generate (0 = basic, 1+ = variations)

        Returns:
            Generated test case with eval vulnerability.
        """
        template = self.VULNERABILITY_TEMPLATES["eval_injection"]

        func_name = random.choice(self.FUNCTION_NAMES)
        var_name = random.choice(self.VARIABLE_NAMES)
        dangerous_funcs: list[str] = template["dangerous_funcs"]
        dangerous_func = dangerous_funcs[variation % len(dangerous_funcs)]
        cwe: str = template["cwe"]

        # Generate code dynamically (assembled at runtime, not stored)
        code_lines = [
            f"def {func_name}_{var_name}({var_name}):",
            "    # Dynamically generated test case",
            f"    result = {dangerous_func}({var_name})",
            "    return result",
        ]

        return GeneratedTestCase(
            id=f"eval-injection-v{variation}",
            name=f"Eval Injection Variation {variation}",
            category="security",
            severity="critical",
            cwe=cwe,
            code="\n".join(code_lines),
            expected_issues=[{"type": "security", "pattern": dangerous_func}],
            metadata={"variation": variation, "generated": True},
        )

    def generate_sql_injection(self, variation: int = 0) -> GeneratedTestCase:
        """Generate a SQL injection test case."""
        template = self.VULNERABILITY_TEMPLATES["sql_injection"]

        func_name = random.choice(self.FUNCTION_NAMES)
        user_input = self.USER_INPUT_SOURCES[variation % len(self.USER_INPUT_SOURCES)]
        prefixes: list[str] = template["prefixes"]
        suffixes: list[str] = template["suffixes"]
        prefix = prefixes[variation % len(prefixes)]
        suffix = suffixes[variation % len(suffixes)]
        cwe: str = template["cwe"]

        param_name = user_input.split(".")[0].split("[")[0]
        code_lines = [
            f"def {func_name}_query({param_name}):",
            "    # Dynamically generated SQL injection test",
            f'    query = "{prefix}" + str({param_name}) + "{suffix}"',
            "    return db.execute(query)",
        ]

        return GeneratedTestCase(
            id=f"sql-injection-v{variation}",
            name=f"SQL Injection Variation {variation}",
            category="security",
            severity="critical",
            cwe=cwe,
            code="\n".join(code_lines),
            expected_issues=[{"type": "security", "pattern": "sql_injection"}],
            metadata={"variation": variation, "generated": True},
        )

    def generate_hardcoded_secret(self, variation: int = 0) -> GeneratedTestCase:
        """Generate a hardcoded secret test case."""
        template = self.VULNERABILITY_TEMPLATES["hardcoded_secret"]

        var_names: list[str] = template["var_names"]
        secret_values: list[str] = template["secret_values"]
        var_name = var_names[variation % len(var_names)]
        secret_value = secret_values[variation % len(secret_values)]
        cwe: str = template["cwe"]

        code_lines = [
            "# Dynamically generated hardcoded secret test",
            f'db_{var_name} = "{secret_value}"',
            "",
            "def get_connection():",
            f"    return connect(secret=db_{var_name})",
        ]

        return GeneratedTestCase(
            id=f"hardcoded-secret-v{variation}",
            name=f"Hardcoded Secret Variation {variation}",
            category="security",
            severity="high",
            cwe=cwe,
            code="\n".join(code_lines),
            expected_issues=[{"type": "security", "pattern": "hardcoded_secret"}],
            metadata={"variation": variation, "generated": True},
        )

    def generate_combined_vulnerabilities(self) -> GeneratedTestCase:
        """Generate a test case with multiple vulnerabilities."""
        code_lines = [
            "def vulnerable_process(user_input, config):",
            "    # Multiple security issues for comprehensive testing",
            "    ",
            "    # Issue 1: Eval injection",
            "    result = eval(user_input)",
            "    ",
            "    # Issue 2: Hardcoded credential",
            '    db_password = "PLACEHOLDER_TEST_ONLY"',
            "    ",
            "    # Issue 3: SQL concatenation",
            '    query = "SELECT * FROM data WHERE id = " + str(user_input)',
            "    ",
            "    return result",
        ]

        return GeneratedTestCase(
            id="combined-vulnerabilities",
            name="Combined Vulnerabilities Test",
            category="security",
            severity="critical",
            cwe="CWE-multiple",
            code="\n".join(code_lines),
            expected_issues=[
                {"type": "security", "pattern": "eval"},
                {"type": "security", "pattern": "hardcoded_secret"},
                {"type": "security", "pattern": "sql_injection"},
            ],
            metadata={"combined": True, "issue_count": 3},
        )

    def generate_all_variations(self, count_per_type: int = 3) -> list[GeneratedTestCase]:
        """Generate all test case variations.

        Args:
            count_per_type: Number of variations per vulnerability type.

        Returns:
            List of all generated test cases.
        """
        test_cases: list[GeneratedTestCase] = []

        # Generate variations of each type
        for i in range(count_per_type):
            test_cases.append(self.generate_eval_injection(i))
            test_cases.append(self.generate_sql_injection(i))
            test_cases.append(self.generate_hardcoded_secret(i))

        # Add combined case
        test_cases.append(self.generate_combined_vulnerabilities())

        return test_cases

    def get_test_code(self, test_id: str) -> str | None:
        """Get test code by ID, either from JSON or generated.

        Args:
            test_id: The test case ID.

        Returns:
            The test code string, or None if not found.
        """
        # First check JSON base vectors
        for case in self.base_vectors.get("test_cases", []):
            if case.get("id") == test_id:
                code: str = case.get("vulnerable_code", "")
                return code

        # Generate dynamically based on ID pattern
        if test_id.startswith("eval-injection"):
            variation = int(test_id.split("-v")[-1]) if "-v" in test_id else 0
            return self.generate_eval_injection(variation).code
        elif test_id.startswith("sql-injection"):
            variation = int(test_id.split("-v")[-1]) if "-v" in test_id else 0
            return self.generate_sql_injection(variation).code
        elif test_id.startswith("hardcoded-secret"):
            variation = int(test_id.split("-v")[-1]) if "-v" in test_id else 0
            return self.generate_hardcoded_secret(variation).code

        return None

    def get_random_test_case(self) -> GeneratedTestCase:
        """Get a random test case for fuzzing/testing."""
        generators = [
            lambda: self.generate_eval_injection(random.randint(0, 5)),
            lambda: self.generate_sql_injection(random.randint(0, 5)),
            lambda: self.generate_hardcoded_secret(random.randint(0, 5)),
            self.generate_combined_vulnerabilities,
        ]
        return random.choice(generators)()


# Module-level singleton for easy access
_generator: TestVectorGenerator | None = None


def get_generator() -> TestVectorGenerator:
    """Get or create the singleton generator instance."""
    global _generator
    if _generator is None:
        _generator = TestVectorGenerator()
    return _generator


def get_test_code(test_id: str) -> str | None:
    """Convenience function to get test code by ID."""
    return get_generator().get_test_code(test_id)


def generate_test_cases(count: int = 3) -> list[GeneratedTestCase]:
    """Convenience function to generate test cases."""
    return get_generator().generate_all_variations(count)


# Example usage and self-test
if __name__ == "__main__":
    print("=== Test Vector Generator Demo ===\n")

    generator = TestVectorGenerator()

    # Generate all variations
    test_cases = generator.generate_all_variations(count_per_type=2)

    print(f"Generated {len(test_cases)} test cases:\n")

    for case in test_cases:
        print(f"ID: {case.id}")
        print(f"Name: {case.name}")
        print(f"Severity: {case.severity}")
        print(f"CWE: {case.cwe}")
        print(f"Code:\n{case.code}")
        print("-" * 50)
