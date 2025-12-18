"""
Provenance Generator - Generate SLSA-compliant provenance

This module provides functionality to generate SLSA (Supply-chain Levels for
Software Artifacts) compliant provenance data for build artifacts.
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# SLSA Provenance constants
SLSA_PREDICATE_TYPE = 'https://slsa.dev/provenance/v1'
STATEMENT_TYPE = 'https://in-toto.io/Statement/v1'


class SLSALevel(Enum):
    """SLSA security levels"""
    L0 = 0  # No guarantees
    L1 = 1  # Documentation of build process
    L2 = 2  # Tamper resistance of build service
    L3 = 3  # Hardened builds
    L4 = 4  # Hermetic, reproducible builds


class DigestAlgorithm(Enum):
    """Supported digest algorithms"""
    SHA256 = 'sha256'
    SHA384 = 'sha384'
    SHA512 = 'sha512'


@dataclass
class ResourceDescriptor:
    """Describes a software artifact or resource"""
    uri: str
    digest: Dict[str, str]
    name: Optional[str] = None
    download_location: Optional[str] = None
    media_type: Optional[str] = None
    content: Optional[str] = None
    annotations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'uri': self.uri,
            'digest': self.digest
        }
        if self.name:
            result['name'] = self.name
        if self.download_location:
            result['downloadLocation'] = self.download_location
        if self.media_type:
            result['mediaType'] = self.media_type
        if self.annotations:
            result['annotations'] = self.annotations
        return result


@dataclass
class Builder:
    """Identifies the build platform"""
    id: str
    version: Optional[Dict[str, str]] = None
    builder_dependencies: List[ResourceDescriptor] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {'id': self.id}
        if self.version:
            result['version'] = self.version
        if self.builder_dependencies:
            result['builderDependencies'] = [
                d.to_dict() for d in self.builder_dependencies
            ]
        return result


@dataclass
class BuildMetadata:
    """Metadata about the build invocation"""
    invocation_id: str
    started_on: datetime
    finished_on: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'invocationId': self.invocation_id,
            'startedOn': self.started_on.isoformat()
        }
        if self.finished_on:
            result['finishedOn'] = self.finished_on.isoformat()
        return result


@dataclass
class RunDetails:
    """Details about the build execution"""
    builder: Builder
    metadata: BuildMetadata
    byproducts: List[ResourceDescriptor] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'builder': self.builder.to_dict(),
            'metadata': self.metadata.to_dict()
        }
        if self.byproducts:
            result['byproducts'] = [b.to_dict() for b in self.byproducts]
        return result


@dataclass
class BuildDefinition:
    """Definition of the build process"""
    build_type: str
    external_parameters: Dict[str, Any]
    internal_parameters: Dict[str, Any] = field(default_factory=dict)
    resolved_dependencies: List[ResourceDescriptor] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'buildType': self.build_type,
            'externalParameters': self.external_parameters
        }
        if self.internal_parameters:
            result['internalParameters'] = self.internal_parameters
        if self.resolved_dependencies:
            result['resolvedDependencies'] = [
                d.to_dict() for d in self.resolved_dependencies
            ]
        return result


@dataclass
class Subject:
    """Describes an artifact produced by the build"""
    name: str
    digest: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'digest': self.digest
        }


@dataclass
class Provenance:
    """SLSA Provenance attestation"""
    subjects: List[Subject]
    build_definition: BuildDefinition
    run_details: RunDetails
    predicate_type: str = SLSA_PREDICATE_TYPE
    statement_type: str = STATEMENT_TYPE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to full SLSA statement"""
        return {
            '_type': self.statement_type,
            'predicateType': self.predicate_type,
            'subject': [s.to_dict() for s in self.subjects],
            'predicate': {
                'buildDefinition': self.build_definition.to_dict(),
                'runDetails': self.run_details.to_dict()
            }
        }
        
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


class ProvenanceGenerator:
    """
    Generator for SLSA-compliant provenance
    
    Supports generating provenance for builds at different SLSA levels,
    with proper metadata, dependencies, and builder information.
    """
    
    def __init__(
        self,
        builder_id: str,
        builder_version: Optional[str] = None,
        default_level: SLSALevel = SLSALevel.L3
    ):
        """
        Initialize the generator
        
        Args:
            builder_id: Unique identifier for the build platform
            builder_version: Version of the builder
            default_level: Default SLSA level for generated provenance
        """
        self.builder_id = builder_id
        self.builder_version = builder_version
        self.default_level = default_level
        self._current_build: Optional[Dict[str, Any]] = None
        
    def start_build(
        self,
        build_type: str,
        external_parameters: Dict[str, Any],
        internal_parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start tracking a new build
        
        Args:
            build_type: Type of build (e.g., 'github-actions', 'ci-build')
            external_parameters: Parameters provided by external source
            internal_parameters: Parameters controlled by builder
            
        Returns:
            Build invocation ID
        """
        invocation_id = str(uuid4())
        
        self._current_build = {
            'invocation_id': invocation_id,
            'build_type': build_type,
            'external_parameters': external_parameters,
            'internal_parameters': internal_parameters or {},
            'started_on': datetime.now(timezone.utc),
            'dependencies': [],
            'byproducts': [],
            'subjects': []
        }
        
        logger.info(f'Started build tracking: {invocation_id}')
        return invocation_id
        
    def add_dependency(
        self,
        uri: str,
        digest: Dict[str, str],
        name: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Add a resolved dependency to the current build
        
        Args:
            uri: URI of the dependency
            digest: Digest of the dependency (algorithm -> hash)
            name: Optional name of the dependency
        """
        if not self._current_build:
            raise RuntimeError('No build in progress. Call start_build first.')
            
        dep = ResourceDescriptor(
            uri=uri,
            digest=digest,
            name=name,
            **kwargs
        )
        self._current_build['dependencies'].append(dep)
        
    def add_subject(
        self,
        name: str,
        file_path: Optional[str] = None,
        content: Optional[bytes] = None,
        digest: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Add a build subject (artifact)
        
        Args:
            name: Name of the artifact
            file_path: Path to the artifact file
            content: Content bytes (alternative to file_path)
            digest: Pre-computed digest (if available)
            
        Returns:
            Computed digest
        """
        if not self._current_build:
            raise RuntimeError('No build in progress. Call start_build first.')
            
        if digest:
            artifact_digest = digest
        elif file_path:
            artifact_digest = self._compute_file_digest(file_path)
        elif content:
            artifact_digest = self._compute_content_digest(content)
        else:
            raise ValueError('Must provide file_path, content, or digest')
            
        subject = Subject(name=name, digest=artifact_digest)
        self._current_build['subjects'].append(subject)
        
        return artifact_digest
        
    def finish_build(self) -> Provenance:
        """
        Finish the build and generate provenance
        
        Returns:
            Generated Provenance object
        """
        if not self._current_build:
            raise RuntimeError('No build in progress. Call start_build first.')
            
        build = self._current_build
        build['finished_on'] = datetime.now(timezone.utc)
        
        # Create builder
        builder = Builder(
            id=self.builder_id,
            version={'synergymesh': self.builder_version} if self.builder_version else None
        )
        
        # Create build metadata
        metadata = BuildMetadata(
            invocation_id=build['invocation_id'],
            started_on=build['started_on'],
            finished_on=build['finished_on']
        )
        
        # Create run details
        run_details = RunDetails(
            builder=builder,
            metadata=metadata,
            byproducts=build['byproducts']
        )
        
        # Create build definition
        build_definition = BuildDefinition(
            build_type=build['build_type'],
            external_parameters=build['external_parameters'],
            internal_parameters=build['internal_parameters'],
            resolved_dependencies=build['dependencies']
        )
        
        # Create provenance
        provenance = Provenance(
            subjects=build['subjects'],
            build_definition=build_definition,
            run_details=run_details
        )
        
        self._current_build = None
        logger.info(f'Generated provenance for build: {build["invocation_id"]}')
        
        return provenance
        
    def generate_provenance(
        self,
        subjects: List[Dict[str, Any]],
        build_type: str,
        external_parameters: Dict[str, Any],
        dependencies: Optional[List[Dict[str, Any]]] = None,
        internal_parameters: Optional[Dict[str, Any]] = None
    ) -> Provenance:
        """
        Generate provenance in one call (convenience method)
        
        Args:
            subjects: List of subject dictionaries with 'name' and 'digest'
            build_type: Type of build
            external_parameters: External parameters
            dependencies: Optional list of dependencies
            internal_parameters: Optional internal parameters
            
        Returns:
            Generated Provenance object
        """
        invocation_id = self.start_build(
            build_type=build_type,
            external_parameters=external_parameters,
            internal_parameters=internal_parameters
        )
        
        # Add dependencies
        if dependencies:
            for dep in dependencies:
                self.add_dependency(
                    uri=dep.get('uri', ''),
                    digest=dep.get('digest', {}),
                    name=dep.get('name')
                )
                
        # Add subjects
        for subj in subjects:
            self._current_build['subjects'].append(
                Subject(
                    name=subj['name'],
                    digest=subj['digest']
                )
            )
            
        return self.finish_build()
        
    def validate_provenance(
        self,
        provenance: Provenance,
        target_level: SLSALevel = SLSALevel.L3
    ) -> Dict[str, Any]:
        """
        Validate provenance meets SLSA requirements
        
        Args:
            provenance: Provenance to validate
            target_level: Target SLSA level
            
        Returns:
            Validation result with 'valid' boolean and 'issues' list
        """
        issues = []
        
        # Level 1 requirements
        if target_level.value >= 1:
            if not provenance.subjects:
                issues.append('Missing subjects')
            if not provenance.build_definition.build_type:
                issues.append('Missing build type')
                
        # Level 2 requirements
        if target_level.value >= 2:
            if not provenance.run_details.builder.id:
                issues.append('Missing builder ID')
            if not provenance.build_definition.resolved_dependencies:
                issues.append('No resolved dependencies (L2 requires source integrity)')
                
        # Level 3 requirements
        if target_level.value >= 3:
            if not provenance.run_details.metadata.invocation_id:
                issues.append('Missing invocation ID (L3 requires non-falsifiable)')
            if not provenance.run_details.metadata.started_on:
                issues.append('Missing build start time')
                
        # Level 4 requirements
        if target_level.value >= 4:
            if not provenance.build_definition.resolved_dependencies:
                issues.append('No resolved dependencies (L4 requires hermetic build)')
            params = provenance.build_definition.external_parameters
            if not params.get('reviewers'):
                issues.append('No reviewer information (L4 requires two-party review)')
                
        return {
            'valid': len(issues) == 0,
            'target_level': target_level.value,
            'issues': issues,
            'checks_passed': self._get_level_from_issues(issues, target_level)
        }
        
    def _compute_file_digest(
        self,
        file_path: str,
        algorithms: List[DigestAlgorithm] = None
    ) -> Dict[str, str]:
        """Compute digest(s) of a file"""
        if algorithms is None:
            algorithms = [DigestAlgorithm.SHA256]
            
        digests = {}
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'File not found: {file_path}')
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        for alg in algorithms:
            hasher = hashlib.new(alg.value)
            hasher.update(content)
            digests[alg.value] = hasher.hexdigest()
            
        return digests
        
    def _compute_content_digest(
        self,
        content: bytes,
        algorithms: List[DigestAlgorithm] = None
    ) -> Dict[str, str]:
        """Compute digest(s) of content"""
        if algorithms is None:
            algorithms = [DigestAlgorithm.SHA256]
            
        digests = {}
        
        for alg in algorithms:
            hasher = hashlib.new(alg.value)
            hasher.update(content)
            digests[alg.value] = hasher.hexdigest()
            
        return digests
        
    def _get_level_from_issues(
        self,
        issues: List[str],
        target_level: SLSALevel
    ) -> int:
        """Determine achieved level based on issues"""
        if not issues:
            return target_level.value
            
        # Check each level's requirements
        for level in range(target_level.value, 0, -1):
            level_issues = self._issues_for_level(issues, level)
            if not level_issues:
                return level
                
        return 0
        
    def _issues_for_level(self, issues: List[str], level: int) -> List[str]:
        """Get issues relevant to a specific level"""
        level_keywords = {
            1: ['subjects', 'build type'],
            2: ['builder ID', 'source integrity'],
            3: ['invocation ID', 'non-falsifiable', 'start time'],
            4: ['hermetic', 'two-party review']
        }
        
        keywords = level_keywords.get(level, [])
        return [
            issue for issue in issues
            if any(kw.lower() in issue.lower() for kw in keywords)
        ]


# Factory functions
def create_provenance_generator(
    builder_id: str,
    builder_version: Optional[str] = None
) -> ProvenanceGenerator:
    """Create a new ProvenanceGenerator instance"""
    return ProvenanceGenerator(builder_id, builder_version)


def compute_digest(
    content: bytes,
    algorithm: DigestAlgorithm = DigestAlgorithm.SHA256
) -> str:
    """Compute digest of content"""
    hasher = hashlib.new(algorithm.value)
    hasher.update(content)
    return hasher.hexdigest()
