"""
Version Management

Manages versioning for compatibility:
- API versions: v1, v2, etc.
- Event schema versions: For event log compatibility
- Policy versions: For policy change tracking

Ensures backwards compatibility during upgrades.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class VersionStatus(Enum):
    """Version status"""
    CURRENT = "current"         # Currently active version
    SUPPORTED = "supported"     # Still supported, not default
    DEPRECATED = "deprecated"   # Still works, will be removed
    RETIRED = "retired"        # No longer supported


class CompatibilityLevel(Enum):
    """Compatibility levels"""
    FULL = "full"               # Fully compatible
    FORWARD = "forward"         # Old clients can use new server
    BACKWARD = "backward"       # New clients can use old server
    NONE = "none"              # Not compatible


@functools.total_ordering
@dataclass
class SemanticVersion:
    """Semantic version (SemVer)"""
    major: int = 1
    minor: int = 0
    patch: int = 0
    prerelease: str = ""
    build: str = ""

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    def __lt__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __eq__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __ge__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    def __gt__(self, other: "SemanticVersion") -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    @classmethod
    def parse(cls, version_string: str) -> "SemanticVersion":
        """Parse a version string"""
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?(?:\+([a-zA-Z0-9.-]+))?$'
        match = re.match(pattern, version_string)

        if not match:
            raise ValueError(f"Invalid version string: {version_string}")

        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4) or "",
            build=match.group(5) or "",
        )

    def is_compatible_with(self, other: "SemanticVersion") -> bool:
        """Check if compatible (same major version)"""
        return self.major == other.major


@dataclass
class APIVersion:
    """
    API version definition
    """
    version: str = "v1"                     # e.g., "v1", "v2"
    semantic_version: SemanticVersion = field(default_factory=SemanticVersion)
    status: VersionStatus = VersionStatus.CURRENT

    # Dates
    released_at: datetime = field(default_factory=datetime.utcnow)
    deprecated_at: datetime | None = None
    sunset_at: datetime | None = None  # When it will be retired

    # Documentation
    changelog: str = ""
    migration_guide: str = ""

    # Endpoints
    base_path: str = "/api/v1"


@dataclass
class SchemaVersion:
    """
    Event/data schema version
    """
    name: str = ""                          # e.g., "webhook_event"
    version: SemanticVersion = field(default_factory=SemanticVersion)
    status: VersionStatus = VersionStatus.CURRENT

    # Schema definition
    schema: dict[str, Any] = field(default_factory=dict)
    json_schema: str | None = None

    # Compatibility
    backward_compatible_with: list[str] = field(default_factory=list)  # List of versions

    # Dates
    released_at: datetime = field(default_factory=datetime.utcnow)
    deprecated_at: datetime | None = None


@dataclass
class VersionCompatibility:
    """
    Compatibility information between versions
    """
    source_version: str
    target_version: str
    compatibility: CompatibilityLevel

    # Migration
    migration_available: bool = False
    migration_steps: list[str] = field(default_factory=list)

    # Breaking changes
    breaking_changes: list[str] = field(default_factory=list)

    # Notes
    notes: str = ""


@dataclass
class VersionManager:
    """
    Version Manager

    Manages API and schema versions with:
    - Version lifecycle (current → deprecated → retired)
    - Compatibility checking
    - Migration guidance
    """

    # Registered versions
    api_versions: dict[str, APIVersion] = field(default_factory=dict)
    schema_versions: dict[str, dict[str, SchemaVersion]] = field(default_factory=dict)

    # Compatibility matrix
    compatibility_matrix: dict[str, VersionCompatibility] = field(default_factory=dict)

    # Current defaults
    default_api_version: str = "v1"
    default_schema_versions: dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # API Version Management
    # ------------------------------------------------------------------

    def register_api_version(self, version: APIVersion) -> None:
        """Register an API version"""
        self.api_versions[version.version] = version
        logger.info(f"API version registered: {version.version}")

    def get_api_version(self, version: str) -> APIVersion | None:
        """Get an API version"""
        return self.api_versions.get(version)

    def get_current_api_version(self) -> APIVersion:
        """Get the current (default) API version"""
        return self.api_versions[self.default_api_version]

    def get_supported_api_versions(self) -> list[APIVersion]:
        """Get all supported API versions"""
        return [
            v for v in self.api_versions.values()
            if v.status in (VersionStatus.CURRENT, VersionStatus.SUPPORTED)
        ]

    def deprecate_api_version(
        self,
        version: str,
        sunset_at: datetime,
    ) -> None:
        """Deprecate an API version"""
        api_version = self.api_versions.get(version)
        if not api_version:
            raise ValueError(f"API version not found: {version}")

        api_version.status = VersionStatus.DEPRECATED
        api_version.deprecated_at = datetime.utcnow()
        api_version.sunset_at = sunset_at

        logger.warning(
            f"API version deprecated: {version}, sunset at {sunset_at}"
        )

    def retire_api_version(self, version: str) -> None:
        """Retire an API version (no longer supported)"""
        api_version = self.api_versions.get(version)
        if not api_version:
            raise ValueError(f"API version not found: {version}")

        api_version.status = VersionStatus.RETIRED

        logger.warning(f"API version retired: {version}")

    def is_api_version_supported(self, version: str) -> bool:
        """Check if an API version is supported"""
        api_version = self.api_versions.get(version)
        if not api_version:
            return False
        return api_version.status in (
            VersionStatus.CURRENT,
            VersionStatus.SUPPORTED,
            VersionStatus.DEPRECATED,
        )

    # ------------------------------------------------------------------
    # Schema Version Management
    # ------------------------------------------------------------------

    def register_schema_version(self, schema: SchemaVersion) -> None:
        """Register a schema version"""
        if schema.name not in self.schema_versions:
            self.schema_versions[schema.name] = {}

        self.schema_versions[schema.name][str(schema.version)] = schema

        # Update default if current
        if schema.status == VersionStatus.CURRENT:
            self.default_schema_versions[schema.name] = str(schema.version)

        logger.info(
            f"Schema version registered: {schema.name} v{schema.version}"
        )

    def get_schema_version(
        self,
        name: str,
        version: str | None = None,
    ) -> SchemaVersion | None:
        """Get a schema version"""
        if name not in self.schema_versions:
            return None

        if version is None:
            version = self.default_schema_versions.get(name)

        if version is None:
            return None

        return self.schema_versions[name].get(version)

    def get_latest_schema_version(self, name: str) -> SchemaVersion | None:
        """Get the latest version of a schema"""
        if name not in self.schema_versions:
            return None

        versions = [
            (SemanticVersion.parse(v), s)
            for v, s in self.schema_versions[name].items()
        ]

        if not versions:
            return None

        versions.sort(key=lambda x: x[0], reverse=True)
        return versions[0][1]

    # ------------------------------------------------------------------
    # Compatibility Checking
    # ------------------------------------------------------------------

    def check_compatibility(
        self,
        source_version: str,
        target_version: str,
    ) -> VersionCompatibility:
        """Check compatibility between two versions"""
        key = f"{source_version}->{target_version}"

        if key in self.compatibility_matrix:
            return self.compatibility_matrix[key]

        # Default check based on semantic versioning
        try:
            source = SemanticVersion.parse(source_version.lstrip("v"))
            target = SemanticVersion.parse(target_version.lstrip("v"))

            if source.major != target.major:
                level = CompatibilityLevel.NONE
            elif source.minor != target.minor:
                level = CompatibilityLevel.BACKWARD
            else:
                level = CompatibilityLevel.FULL

            return VersionCompatibility(
                source_version=source_version,
                target_version=target_version,
                compatibility=level,
            )
        except ValueError:
            return VersionCompatibility(
                source_version=source_version,
                target_version=target_version,
                compatibility=CompatibilityLevel.NONE,
            )

    def register_compatibility(
        self,
        compatibility: VersionCompatibility,
    ) -> None:
        """Register compatibility information"""
        key = f"{compatibility.source_version}->{compatibility.target_version}"
        self.compatibility_matrix[key] = compatibility

    def get_migration_path(
        self,
        from_version: str,
        to_version: str,
    ) -> list[str]:
        """
        Get migration path between versions

        Returns ordered list of versions to migrate through.
        """
        # Simple case: direct migration
        compat = self.check_compatibility(from_version, to_version)
        if compat.migration_available:
            return [from_version, to_version]

        # Find path through intermediate versions
        # This is a simplified BFS implementation
        visited = set()
        queue = [(from_version, [from_version])]

        while queue:
            current, path = queue.pop(0)
            if current == to_version:
                return path

            if current in visited:
                continue
            visited.add(current)

            # Get possible next versions
            for key, compat in self.compatibility_matrix.items():
                if key.startswith(f"{current}->"):
                    next_version = key.split("->")[1]
                    if next_version not in visited:
                        queue.append((next_version, path + [next_version]))

        return []  # No path found

    # ------------------------------------------------------------------
    # Version Headers
    # ------------------------------------------------------------------

    def parse_version_header(
        self,
        header: str,
    ) -> tuple[str, str | None]:
        """
        Parse Accept-Version or similar header

        Returns (api_version, schema_version)
        """
        # Simple format: "v1" or "v1;schema=1.2.0"
        parts = header.split(";")
        api_version = parts[0].strip()
        schema_version = None

        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                if key.strip() == "schema":
                    schema_version = value.strip()

        return api_version, schema_version

    def build_version_header(
        self,
        api_version: str | None = None,
        schema_version: str | None = None,
    ) -> str:
        """Build version header for response"""
        header = api_version or self.default_api_version

        if schema_version:
            header += f";schema={schema_version}"

        return header

    # ------------------------------------------------------------------
    # Version Discovery
    # ------------------------------------------------------------------

    def get_version_info(self) -> dict[str, Any]:
        """Get version information for API discovery"""
        return {
            "default_api_version": self.default_api_version,
            "supported_api_versions": [
                {
                    "version": v.version,
                    "status": v.status.value,
                    "base_path": v.base_path,
                    "deprecated_at": v.deprecated_at.isoformat() if v.deprecated_at else None,
                    "sunset_at": v.sunset_at.isoformat() if v.sunset_at else None,
                }
                for v in self.get_supported_api_versions()
            ],
            "schema_versions": {
                name: {
                    "default": self.default_schema_versions.get(name),
                    "available": list(versions.keys()),
                }
                for name, versions in self.schema_versions.items()
            },
        }
