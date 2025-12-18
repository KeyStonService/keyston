"""
YAML Module Definition System (YAML 模組定義系統)

定義 YAML 模組的完整結構，包含元數據、Schema、測試向量、生命週期等。

Reference: Schema validation best practices [8]
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LifecycleState(Enum):
    """模組生命週期狀態"""
    DRAFT = "draft"           # 草稿階段
    REVIEW = "review"         # 審核中
    APPROVED = "approved"     # 已批准
    ACTIVE = "active"         # 活躍使用中
    DEPRECATED = "deprecated" # 已棄用
    ARCHIVED = "archived"     # 已歸檔


class TestVectorType(Enum):
    """測試向量類型"""
    VALID = "valid"           # 有效輸入測試
    INVALID = "invalid"       # 無效輸入測試
    EDGE_CASE = "edge_case"   # 邊界條件測試
    SECURITY = "security"     # 安全測試
    PERFORMANCE = "performance"  # 性能測試


@dataclass
class ModuleOwner:
    """模組所有者資訊"""
    team: str
    contacts: list[str]
    approvers: list[str] = field(default_factory=list)
    escalation_path: list[str] = field(default_factory=list)


@dataclass
class ModuleMetadata:
    """模組元數據"""
    created_at: datetime
    updated_at: datetime
    labels: list[str] = field(default_factory=list)
    compliance_tags: list[str] = field(default_factory=list)
    pipeline_id: str | None = None
    commit_sha: str | None = None
    environment: str | None = None
    region: str | None = None


@dataclass
class TestVector:
    """測試向量定義"""
    id: str
    name: str
    type: TestVectorType
    description: str
    input_data: dict[str, Any]
    expected_result: Any
    tags: list[str] = field(default_factory=list)
    timeout_ms: int = 5000

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'description': self.description,
            'input_data': self.input_data,
            'expected_result': self.expected_result,
            'tags': self.tags,
            'timeout_ms': self.timeout_ms,
        }


@dataclass
class ChangelogEntry:
    """變更日誌條目"""
    version: str
    date: datetime
    author: str
    changes: list[str]
    breaking: bool = False
    security_impact: bool = False
    reviewed_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'version': self.version,
            'date': self.date.isoformat(),
            'author': self.author,
            'changes': self.changes,
            'breaking': self.breaking,
            'security_impact': self.security_impact,
            'reviewed_by': self.reviewed_by,
        }


@dataclass
class ModuleLifecycle:
    """模組生命週期管理"""
    state: LifecycleState
    state_history: list[dict[str, Any]] = field(default_factory=list)
    approved_at: datetime | None = None
    approved_by: str | None = None
    deprecated_at: datetime | None = None
    deprecation_reason: str | None = None
    sunset_date: datetime | None = None

    def transition_to(self, new_state: LifecycleState, actor: str, reason: str | None = None) -> bool:
        """狀態轉換"""
        valid_transitions = {
            LifecycleState.DRAFT: [LifecycleState.REVIEW],
            LifecycleState.REVIEW: [LifecycleState.DRAFT, LifecycleState.APPROVED],
            LifecycleState.APPROVED: [LifecycleState.ACTIVE, LifecycleState.DEPRECATED],
            LifecycleState.ACTIVE: [LifecycleState.DEPRECATED],
            LifecycleState.DEPRECATED: [LifecycleState.ARCHIVED],
            LifecycleState.ARCHIVED: [],
        }

        if new_state not in valid_transitions.get(self.state, []):
            return False

        self.state_history.append({
            'from_state': self.state.value,
            'to_state': new_state.value,
            'actor': actor,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
        })

        self.state = new_state

        if new_state == LifecycleState.APPROVED:
            self.approved_at = datetime.now()
            self.approved_by = actor
        elif new_state == LifecycleState.DEPRECATED:
            self.deprecated_at = datetime.now()
            self.deprecation_reason = reason

        return True


@dataclass
class YAMLModuleDefinition:
    """
    YAML 模組定義
    
    完整的模組結構，包含所有必要的驗證和追蹤資訊。
    """
    id: str
    kind: str
    version: str
    name: str
    description: str
    owner: ModuleOwner
    metadata: ModuleMetadata
    schema: dict[str, Any]  # JSON Schema
    test_vectors: list[TestVector] = field(default_factory=list)
    lifecycle: ModuleLifecycle = field(default_factory=lambda: ModuleLifecycle(state=LifecycleState.DRAFT))
    changelog: list[ChangelogEntry] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize with generated ID if not provided"""
        if not self.id:
            self.id = str(uuid.uuid4())

    def add_test_vector(self, test_vector: TestVector) -> None:
        """添加測試向量"""
        self.test_vectors.append(test_vector)

    def add_changelog_entry(self, entry: ChangelogEntry) -> None:
        """添加變更日誌"""
        self.changelog.append(entry)

    def get_test_vectors_by_type(self, vector_type: TestVectorType) -> list[TestVector]:
        """按類型獲取測試向量"""
        return [tv for tv in self.test_vectors if tv.type == vector_type]

    def is_approved(self) -> bool:
        """檢查模組是否已批准"""
        return self.lifecycle.state in [LifecycleState.APPROVED, LifecycleState.ACTIVE]

    def is_active(self) -> bool:
        """檢查模組是否活躍"""
        return self.lifecycle.state == LifecycleState.ACTIVE

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典格式"""
        return {
            'id': self.id,
            'kind': self.kind,
            'version': self.version,
            'name': self.name,
            'description': self.description,
            'owner': {
                'team': self.owner.team,
                'contacts': self.owner.contacts,
                'approvers': self.owner.approvers,
            },
            'metadata': {
                'created_at': self.metadata.created_at.isoformat(),
                'updated_at': self.metadata.updated_at.isoformat(),
                'labels': self.metadata.labels,
                'compliance_tags': self.metadata.compliance_tags,
                'pipeline_id': self.metadata.pipeline_id,
                'commit_sha': self.metadata.commit_sha,
            },
            'schema': self.schema,
            'test_vectors': [tv.to_dict() for tv in self.test_vectors],
            'lifecycle': {
                'state': self.lifecycle.state.value,
                'approved_at': self.lifecycle.approved_at.isoformat() if self.lifecycle.approved_at else None,
                'approved_by': self.lifecycle.approved_by,
            },
            'changelog': [ce.to_dict() for ce in self.changelog],
            'dependencies': self.dependencies,
            'examples': self.examples,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'YAMLModuleDefinition':
        """從字典創建模組定義"""
        owner = ModuleOwner(
            team=data['owner']['team'],
            contacts=data['owner']['contacts'],
            approvers=data['owner'].get('approvers', []),
        )

        metadata = ModuleMetadata(
            created_at=datetime.fromisoformat(data['metadata']['created_at']),
            updated_at=datetime.fromisoformat(data['metadata']['updated_at']),
            labels=data['metadata'].get('labels', []),
            compliance_tags=data['metadata'].get('compliance_tags', []),
            pipeline_id=data['metadata'].get('pipeline_id'),
            commit_sha=data['metadata'].get('commit_sha'),
        )

        test_vectors = [
            TestVector(
                id=tv['id'],
                name=tv['name'],
                type=TestVectorType(tv['type']),
                description=tv['description'],
                input_data=tv['input_data'],
                expected_result=tv['expected_result'],
                tags=tv.get('tags', []),
                timeout_ms=tv.get('timeout_ms', 5000),
            )
            for tv in data.get('test_vectors', [])
        ]

        lifecycle = ModuleLifecycle(
            state=LifecycleState(data['lifecycle']['state']),
            approved_at=datetime.fromisoformat(data['lifecycle']['approved_at']) if data['lifecycle'].get('approved_at') else None,
            approved_by=data['lifecycle'].get('approved_by'),
        )

        changelog = [
            ChangelogEntry(
                version=ce['version'],
                date=datetime.fromisoformat(ce['date']),
                author=ce['author'],
                changes=ce['changes'],
                breaking=ce.get('breaking', False),
                security_impact=ce.get('security_impact', False),
            )
            for ce in data.get('changelog', [])
        ]

        return cls(
            id=data['id'],
            kind=data['kind'],
            version=data['version'],
            name=data['name'],
            description=data['description'],
            owner=owner,
            metadata=metadata,
            schema=data['schema'],
            test_vectors=test_vectors,
            lifecycle=lifecycle,
            changelog=changelog,
            dependencies=data.get('dependencies', []),
            examples=data.get('examples', []),
        )
