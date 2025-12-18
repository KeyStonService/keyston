#!/usr/bin/env python3
"""
Unit tests for path validation in security_scanner.py
測試 security_scanner.py 中的路徑驗證功能
"""

import os
import pathlib
import sys
import tempfile
from pathlib import Path

import pytest

# Import the module containing validate_project_path
sys.path.insert(
    0, str(Path(__file__).parent.parent / "docs" / "examples" / "configuration" / "python")
)
from security_scanner import validate_project_path  # noqa: E402


@pytest.fixture
def temp_base_dir(monkeypatch):
    """Create a temporary base directory and set it as CWD"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)
        yield pathlib.Path(tmpdir)


@pytest.fixture
def nested_dir(temp_base_dir):
    """Create a nested directory structure"""
    nested = temp_base_dir / "project" / "subdir"
    nested.mkdir(parents=True, exist_ok=True)
    return nested


class TestPathValidation:
    """Test suite for validate_project_path function"""

    def test_valid_current_directory(self, temp_base_dir):
        """Test validation with current directory"""
        result = validate_project_path(".")
        assert pathlib.Path(result).resolve() == temp_base_dir.resolve()

    def test_valid_subdirectory(self, temp_base_dir, nested_dir):  # noqa: ARG002
        """Test validation with valid subdirectory"""
        result = validate_project_path("project/subdir")
        assert pathlib.Path(result).resolve() == nested_dir.resolve()

    def test_valid_absolute_path(self, temp_base_dir, nested_dir):  # noqa: ARG002
        """Test validation with absolute path inside base dir"""
        result = validate_project_path(str(nested_dir))
        assert pathlib.Path(result).resolve() == nested_dir.resolve()

    def test_forbidden_semicolon(self, temp_base_dir):  # noqa: ARG002
        """Test that semicolon is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test;rm -rf /")

    def test_forbidden_pipe(self, temp_base_dir):  # noqa: ARG002
        """Test that pipe character is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test|cat /etc/passwd")

    def test_forbidden_ampersand(self, temp_base_dir):  # noqa: ARG002
        """Test that ampersand is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test&whoami")

    def test_forbidden_backtick(self, temp_base_dir):  # noqa: ARG002
        """Test that backtick is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test`whoami`")

    def test_forbidden_dollar(self, temp_base_dir):  # noqa: ARG002
        """Test that dollar sign is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test$(whoami)")

    def test_forbidden_redirect_greater(self, temp_base_dir):  # noqa: ARG002
        """Test that > is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test>output.txt")

    def test_forbidden_redirect_less(self, temp_base_dir):  # noqa: ARG002
        """Test that < is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test<input.txt")

    def test_forbidden_newline(self, temp_base_dir):  # noqa: ARG002
        """Test that newline is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test\necho hacked")

    def test_forbidden_carriage_return(self, temp_base_dir):  # noqa: ARG002
        """Test that carriage return is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test\recho hacked")

    def test_forbidden_tab(self, temp_base_dir):  # noqa: ARG002
        """Test that tab character is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test\tpath")

    def test_forbidden_null_byte(self, temp_base_dir):  # noqa: ARG002
        """Test that null byte is rejected"""
        with pytest.raises(ValueError, match="forbidden characters"):
            validate_project_path("test\x00path")

    def test_path_traversal_with_dotdot(self, temp_base_dir, nested_dir):  # noqa: ARG002
        """Test that path traversal is prevented (.. in path)"""
        # Create a parent directory outside base
        parent = temp_base_dir.parent / "outside"
        parent.mkdir(exist_ok=True)

        # Try to access it via ../
        with pytest.raises(ValueError, match="must be within the current working directory"):
            validate_project_path("../outside")

    def test_absolute_path_outside_base(self, temp_base_dir):  # noqa: ARG002
        """Test that absolute path outside base directory is rejected"""
        with (
            tempfile.TemporaryDirectory() as outside_dir,
            pytest.raises(ValueError, match="must be within the current working directory"),
        ):
            validate_project_path(outside_dir)

    def test_nonexistent_path(self, temp_base_dir):  # noqa: ARG002
        """Test that nonexistent path is rejected"""
        with pytest.raises(ValueError, match="does not exist or is not a directory"):
            validate_project_path("nonexistent/path")

    def test_file_instead_of_directory(self, temp_base_dir):
        """Test that file path is rejected (must be directory)"""
        test_file = temp_base_dir / "test.txt"
        test_file.write_text("content")
        with pytest.raises(ValueError, match="does not exist or is not a directory"):
            validate_project_path(str(test_file))

    def test_symlink_inside_base(self, temp_base_dir, nested_dir):
        """Test that symlink pointing inside base dir is allowed"""
        link_path = temp_base_dir / "link_to_nested"
        link_path.symlink_to(nested_dir)

        result = validate_project_path(str(link_path))
        # Result should be the resolved path
        assert pathlib.Path(result).resolve() == nested_dir.resolve()

    def test_symlink_outside_base(self, temp_base_dir):
        """Test that symlink pointing outside base dir is rejected"""
        with tempfile.TemporaryDirectory() as outside_dir:
            outside_path = pathlib.Path(outside_dir)
            link_path = temp_base_dir / "link_to_outside"
            link_path.symlink_to(outside_path)

            with pytest.raises(ValueError, match="must be within the current working directory"):
                validate_project_path(str(link_path))

    def test_tilde_expansion(self, temp_base_dir, monkeypatch):  # noqa: ARG002
        """Test that tilde expansion works correctly"""
        # Create a temporary directory outside the base to simulate home
        with tempfile.TemporaryDirectory() as outside_home:
            monkeypatch.setenv("HOME", outside_home)

            # This should expand ~ to outside_home, which is outside temp_base_dir
            with pytest.raises(ValueError, match="must be within the current working directory"):
                validate_project_path("~")

    def test_complex_path_traversal_attempt(self, temp_base_dir, nested_dir):  # noqa: ARG002
        """Test complex path traversal attempt with ../../../"""
        # Even if the path eventually resolves inside base,
        # if it tries to escape, it should be caught
        outside_attempt = temp_base_dir / "outside"
        outside_attempt.mkdir()

        # Try something like project/subdir/../../../outside
        with pytest.raises(ValueError):
            validate_project_path("project/subdir/../../../outside")

    def test_empty_path(self, temp_base_dir):
        """Test that empty path resolves to current directory"""
        # Empty string resolves to current directory, which should be valid
        result = validate_project_path(".")
        assert pathlib.Path(result).resolve() == temp_base_dir.resolve()

    def test_whitespace_only_path(self, temp_base_dir):  # noqa: ARG002
        """Test that whitespace-only path is rejected"""
        with pytest.raises(ValueError):
            validate_project_path("   ")


class TestPathValidationEdgeCases:
    """Test edge cases for path validation"""

    def test_path_with_spaces(self, temp_base_dir):
        """Test that paths with spaces are handled correctly"""
        dir_with_spaces = temp_base_dir / "dir with spaces"
        dir_with_spaces.mkdir()

        result = validate_project_path("dir with spaces")
        assert pathlib.Path(result).resolve() == dir_with_spaces.resolve()

    def test_path_with_unicode(self, temp_base_dir):
        """Test that paths with unicode characters are handled"""
        unicode_dir = temp_base_dir / "測試目錄"
        unicode_dir.mkdir()

        result = validate_project_path("測試目錄")
        assert pathlib.Path(result).resolve() == unicode_dir.resolve()

    def test_case_sensitivity(self, temp_base_dir):
        """Test path case sensitivity handling"""
        test_dir = temp_base_dir / "TestDir"
        test_dir.mkdir()

        # This behavior may vary by OS
        if os.name == "nt":  # Windows is case-insensitive
            result = validate_project_path("testdir")
            assert pathlib.Path(result).resolve() == test_dir.resolve()
        else:  # Unix-like systems are case-sensitive
            with pytest.raises(ValueError, match="does not exist or is not a directory"):
                validate_project_path("testdir")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
