#!/usr/bin/env python3
"""Bootstrap the repository structure based on island.bootstrap.stage0.yaml."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required. Install it via `pip install pyyaml` before running this tool."
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Materialize the Island AI Stage 0 bootstrap manifest",
    )
    parser.add_argument("manifest", type=Path, help="Path to island.bootstrap.stage0.yaml")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually create directories, copy templates, and run shell commands",
    )
    parser.add_argument(
        "--steps",
        nargs="*",
        help="If provided, only run the bootstrap steps whose IDs match these values",
    )
    return parser.parse_args()


class BootstrapContext:
    def __init__(self, repo_root: Path, apply_changes: bool) -> None:
        self.repo_root = repo_root
        self.apply = apply_changes

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.repo_root))
        except ValueError:
            return str(path)

    def log(self, message: str) -> None:
        print(message)

    def ensure_directory(self, directory: Path) -> None:
        if self.apply:
            directory.mkdir(parents=True, exist_ok=True)
            self.log(f"[dir] ensured {self.rel(directory)}")
        else:
            self.log(f"[dry-run] mkdir -p {self.rel(directory)}")

    def copy_file(self, source: Path, target: Path, mode: str | None) -> None:
        if not source.exists():
            self.log(f"[warn] template missing: {self.rel(source)}")
            return
        if self.apply:
            if target.exists():
                self.log(f"[skip] target exists, not overwriting {self.rel(target)}")
                return
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if mode:
                # YAML automatically parses octal literals like 0755 as decimal integers (493).
                # When converted to string, we get "493" which cannot be parsed as octal.
                # We use a simple heuristic: if the string starts with "0" and has more digits,
                # treat as octal; otherwise treat as decimal (the YAML-parsed form).
                if mode.startswith("0") and len(mode) > 1:
                    # Explicit octal format like "0755"
                    target.chmod(int(mode, 8))
                else:
                    # Decimal format (YAML-parsed values like "493" for 0o755)
                    target.chmod(int(mode))
            self.log(f"[file] materialized {self.rel(target)} from {self.rel(source)}")
        else:
            self.log(f"[dry-run] cp {self.rel(source)} {self.rel(target)}")

    def run_shell(self, script: str) -> None:
        """Execute shell script with proper security considerations.
        
        Security Controls:
        - Input Source: YAML manifest should be version-controlled and code-reviewed
        - File Permissions: Manifest file should have restricted write permissions
        - Validation: Consider verifying manifest signature or checksum before execution
        - Execution Context: Runs in subprocess with cwd restricted to repo_root
        
        Note: This uses shell=True for compatibility with multi-line shell scripts
        from YAML configuration. For untrusted input, use subprocess with shell=False
        and shlex.split() for proper argument parsing.
        """
        formatted = script.strip()
        if self.apply:
            # Security: Only execute scripts from trusted YAML manifests
            # The manifest file should be version-controlled and reviewed
            tmp_path: str | None = None
            old_umask = os.umask(0o077)
            try:
                with tempfile.NamedTemporaryFile(
                    "w", delete=False, prefix="bootstrap_", suffix=".sh"
                ) as tmp:
                    tmp.write(formatted)
                    tmp_path = tmp.name
            finally:
                os.umask(old_umask)
            try:
                if tmp_path is not None:
                    os.chmod(tmp_path, 0o600)
                    subprocess.run(["/bin/bash", tmp_path], check=True, cwd=self.repo_root)
            finally:
                if tmp_path is not None:
                    try:
                        Path(tmp_path).unlink()
                    except OSError:
                        # Best-effort cleanup: ignore errors if file was already deleted
                        # or if we lack permissions (e.g., concurrent deletion, unmounted fs)
                        pass
            self.log("[shell] executed block")
        else:
            self.log("[dry-run] shell block:\n" + formatted)


def load_manifest(path: Path) -> Mapping[str, Any]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, Mapping):  # pragma: no cover
        raise SystemExit("Manifest root must be a mapping")
    return data


def _as_str(value: Any, default: str = "") -> str:
    return str(value) if value is not None else default


def _iter_sequence(obj: Any) -> Sequence[Any]:
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        return obj
    return []


def scaffold_entries(entries: Sequence[Mapping[str, Any]], ctx: BootstrapContext) -> None:
    for entry in entries:
        base = ctx.repo_root / _as_str(entry.get("base", "."))
        ctx.ensure_directory(base)
        for section in _iter_sequence(entry.get("ordered_sections")):
            target = base / _as_str(section.get("code"))
            ctx.ensure_directory(target)
        for module in _iter_sequence(entry.get("modules")):
            target = base / _as_str(module.get("name"))
            ctx.ensure_directory(target)
        for subsystem in _iter_sequence(entry.get("subsystems")):
            target = base / _as_str(subsystem.get("name"))
            ctx.ensure_directory(target)
        for extra in _iter_sequence(entry.get("extra_paths")):
            target = (base / _as_str(extra)).resolve()
            ctx.ensure_directory(target)


def materialize_templates(templates: Sequence[Mapping[str, Any]], ctx: BootstrapContext) -> None:
    for template in templates:
        source = ctx.repo_root / _as_str(template.get("source"))
        target = ctx.repo_root / _as_str(template.get("target"))
        mode = _as_str(template.get("mode")) if template.get("mode") else None
        ctx.copy_file(source, target, mode)


def execute_bootstrap_sequence(
    sequence: Sequence[Mapping[str, Any]],
    spec: Mapping[str, Any],
    ctx: BootstrapContext,
    only_steps: Sequence[str] | None,
) -> None:
    for step in sequence:
        step_id = _as_str(step.get("id", "unknown"))
        if only_steps and step_id not in only_steps:
            continue
        kind = _as_str(step.get("kind"))
        ctx.log(f"[step] {step_id} ({kind})")
        if kind == "shell":
            ctx.run_shell(_as_str(step.get("run", "")))
        elif kind == "scaffold":
            from_key = _as_str(step.get("from", ""))
            entries = spec.get(from_key, [])
            if not isinstance(entries, Sequence):  # pragma: no cover
                raise SystemExit("scaffold section must be a sequence")
            scaffold_entries(entries, ctx)
        elif kind == "materialize":
            from_key = _as_str(step.get("from", ""))
            templates = spec.get(from_key, [])
            if not isinstance(templates, Sequence):  # pragma: no cover
                raise SystemExit("templates section must be a sequence")
            materialize_templates(templates, ctx)
        else:
            ctx.log(f"[warn] unsupported step kind: {kind}")


def main() -> None:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    manifest = load_manifest(manifest_path)
    spec = manifest.get("spec", {})
    if not isinstance(spec, Mapping):  # pragma: no cover
        raise SystemExit("spec section is required in manifest")

    ctx = BootstrapContext(repo_root=manifest_path.parent, apply_changes=args.apply)
    automation = spec.get("automation")
    sequence = automation.get("bootstrap_sequence", []) if isinstance(automation, Mapping) else []
    if not sequence:
        raise SystemExit("No automation.bootstrap_sequence defined in manifest")

    execute_bootstrap_sequence(sequence, spec, ctx, args.steps)


if __name__ == "__main__":
    main()
