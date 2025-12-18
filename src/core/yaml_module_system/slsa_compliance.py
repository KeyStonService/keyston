"""
SLSA Compliance System (SLSA 合規系統)

實現 SLSA Level 3 合規性，包括溯源生成、製品簽名和 SBOM 生成。

Reference: SLSA framework, DevSecOps best practices [6]
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json
import hashlib
import base64


class SLSALevel(Enum):
    """SLSA 安全等級"""
    LEVEL_0 = 0  # 無保證
    LEVEL_1 = 1  # 溯源存在
    LEVEL_2 = 2  # 託管構建平台
    LEVEL_3 = 3  # 硬化構建
    LEVEL_4 = 4  # 完全驗證


class DigestAlgorithm(Enum):
    """摘要算法"""
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"


class SignatureAlgorithm(Enum):
    """簽名算法"""
    ECDSA_P256 = "ecdsa-p256"
    ECDSA_P384 = "ecdsa-p384"
    RSA_PSS_256 = "rsa-pss-256"
    ED25519 = "ed25519"


@dataclass
class BuildDefinition:
    """構建定義"""
    build_type: str
    external_parameters: Dict[str, Any]
    internal_parameters: Dict[str, Any] = field(default_factory=dict)
    resolved_dependencies: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'buildType': self.build_type,
            'externalParameters': self.external_parameters,
            'internalParameters': self.internal_parameters,
            'resolvedDependencies': self.resolved_dependencies,
        }


@dataclass
class RunDetails:
    """運行詳情"""
    builder_id: str
    builder_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    by_products: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'builder': {
                'id': self.builder_id,
                'version': self.builder_version,
            },
            'metadata': self.metadata,
            'byProducts': self.by_products,
        }


@dataclass
class Subject:
    """製品主體"""
    name: str
    digest: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'digest': self.digest,
        }


@dataclass
class SLSAProvenance:
    """
    SLSA 溯源記錄
    
    符合 SLSA v1.0 溯源格式。
    """
    id: str
    predicate_type: str = "https://slsa.dev/provenance/v1"
    subjects: List[Subject] = field(default_factory=list)
    build_definition: Optional[BuildDefinition] = None
    run_details: Optional[RunDetails] = None
    generated_at: datetime = field(default_factory=datetime.now)
    slsa_level: SLSALevel = SLSALevel.LEVEL_3
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式（符合 in-toto 格式）"""
        return {
            '_type': 'https://in-toto.io/Statement/v1',
            'subject': [s.to_dict() for s in self.subjects],
            'predicateType': self.predicate_type,
            'predicate': {
                'buildDefinition': self.build_definition.to_dict() if self.build_definition else {},
                'runDetails': self.run_details.to_dict() if self.run_details else {},
            },
            'metadata': {
                'id': self.id,
                'generatedAt': self.generated_at.isoformat(),
                'slsaLevel': self.slsa_level.value,
            },
        }
    
    def to_json(self) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=2)


class SLSAProvenanceGenerator:
    """
    SLSA 溯源生成器
    
    生成符合 SLSA Level 3 的溯源記錄。
    """
    
    def __init__(self, builder_id: str, builder_version: Optional[str] = None):
        self.builder_id = builder_id
        self.builder_version = builder_version
    
    def generate(self, 
                 artifact_name: str,
                 artifact_digest: str,
                 build_type: str,
                 external_parameters: Dict[str, Any],
                 dependencies: Optional[List[Dict[str, Any]]] = None,
                 internal_parameters: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> SLSAProvenance:
        """
        生成溯源記錄
        
        Args:
            artifact_name: 製品名稱
            artifact_digest: 製品摘要（SHA256）
            build_type: 構建類型
            external_parameters: 外部參數
            dependencies: 解析的依賴
            internal_parameters: 內部參數
            metadata: 額外元數據
        
        Returns:
            SLSAProvenance: 溯源記錄
        """
        subject = Subject(
            name=artifact_name,
            digest={'sha256': artifact_digest},
        )
        
        build_definition = BuildDefinition(
            build_type=build_type,
            external_parameters=external_parameters,
            internal_parameters=internal_parameters or {},
            resolved_dependencies=dependencies or [],
        )
        
        run_details = RunDetails(
            builder_id=self.builder_id,
            builder_version=self.builder_version,
            metadata=metadata or {},
        )
        
        return SLSAProvenance(
            id=str(uuid.uuid4()),
            subjects=[subject],
            build_definition=build_definition,
            run_details=run_details,
        )
    
    def generate_from_module(self, module_data: Dict[str, Any], 
                            build_params: Dict[str, Any]) -> SLSAProvenance:
        """從模組生成溯源"""
        # 計算模組摘要
        module_json = json.dumps(module_data, sort_keys=True)
        module_digest = hashlib.sha256(module_json.encode()).hexdigest()
        
        return self.generate(
            artifact_name=module_data.get('name', 'unknown'),
            artifact_digest=module_digest,
            build_type=build_params.get('build_type', 'yaml-module'),
            external_parameters=build_params,
            dependencies=module_data.get('dependencies', []),
            metadata={
                'module_id': module_data.get('id'),
                'module_version': module_data.get('version'),
            },
        )


@dataclass
class SignedArtifact:
    """簽名的製品"""
    artifact_name: str
    artifact_digest: str
    signature: str
    signature_algorithm: SignatureAlgorithm
    key_id: str
    signed_at: datetime = field(default_factory=datetime.now)
    certificate: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'artifact': {
                'name': self.artifact_name,
                'digest': self.artifact_digest,
            },
            'signature': {
                'value': self.signature,
                'algorithm': self.signature_algorithm.value,
                'keyId': self.key_id,
                'signedAt': self.signed_at.isoformat(),
            },
            'certificate': self.certificate,
        }
    
    def verify(self, public_key: str) -> bool:
        """驗證簽名（模擬）"""
        # 在實際實現中，這裡會使用真正的密碼學驗證
        return bool(self.signature and self.key_id)


class ArtifactSigner:
    """
    製品簽名器
    
    對製品進行數字簽名以確保完整性。
    """
    
    def __init__(self, key_id: str, algorithm: SignatureAlgorithm = SignatureAlgorithm.ECDSA_P256):
        self.key_id = key_id
        self.algorithm = algorithm
    
    def sign(self, artifact_name: str, artifact_data: Any) -> SignedArtifact:
        """
        簽名製品
        
        Args:
            artifact_name: 製品名稱
            artifact_data: 製品數據
        
        Returns:
            SignedArtifact: 簽名的製品
        """
        # 計算摘要
        data_str = json.dumps(artifact_data, sort_keys=True) if isinstance(artifact_data, (dict, list)) else str(artifact_data)
        digest = hashlib.sha256(data_str.encode()).hexdigest()
        
        # 生成簽名（模擬）
        # 在實際實現中，這裡會使用真正的密碼學簽名
        signature_data = f"{digest}:{self.key_id}:{self.algorithm.value}"
        signature = base64.b64encode(hashlib.sha256(signature_data.encode()).digest()).decode()
        
        return SignedArtifact(
            artifact_name=artifact_name,
            artifact_digest=digest,
            signature=signature,
            signature_algorithm=self.algorithm,
            key_id=self.key_id,
        )
    
    def sign_provenance(self, provenance: SLSAProvenance) -> SignedArtifact:
        """簽名溯源記錄"""
        return self.sign(
            artifact_name=f"provenance-{provenance.id}",
            artifact_data=provenance.to_dict(),
        )


@dataclass
class SBOMComponent:
    """SBOM 組件"""
    name: str
    version: str
    purl: Optional[str] = None  # Package URL
    licenses: List[str] = field(default_factory=list)
    hashes: Dict[str, str] = field(default_factory=dict)
    supplier: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'purl': self.purl,
            'licenses': self.licenses,
            'hashes': self.hashes,
            'supplier': self.supplier,
        }


@dataclass
class SBOM:
    """
    Software Bill of Materials (軟件物料清單)
    
    列出所有軟件組件及其依賴關係。
    """
    id: str
    name: str
    version: str
    format: str = "CycloneDX"
    spec_version: str = "1.5"
    components: List[SBOMComponent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    
    def add_component(self, component: SBOMComponent) -> None:
        """添加組件"""
        self.components.append(component)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為 CycloneDX 格式"""
        return {
            'bomFormat': self.format,
            'specVersion': self.spec_version,
            'serialNumber': f"urn:uuid:{self.id}",
            'version': 1,
            'metadata': {
                'timestamp': self.created_at.isoformat(),
                'component': {
                    'name': self.name,
                    'version': self.version,
                },
                'authors': [{'name': self.author}] if self.author else [],
            },
            'components': [c.to_dict() for c in self.components],
        }
    
    def to_json(self) -> str:
        """轉換為 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=2)


class SBOMGenerator:
    """
    SBOM 生成器
    
    生成軟件物料清單。
    """
    
    def __init__(self, author: Optional[str] = None):
        self.author = author
    
    def generate(self, name: str, version: str, 
                 dependencies: Optional[List[Dict[str, Any]]] = None) -> SBOM:
        """
        生成 SBOM
        
        Args:
            name: 軟件名稱
            version: 軟件版本
            dependencies: 依賴列表
        
        Returns:
            SBOM: 軟件物料清單
        """
        sbom = SBOM(
            id=str(uuid.uuid4()),
            name=name,
            version=version,
            author=self.author,
        )
        
        if dependencies:
            for dep in dependencies:
                component = SBOMComponent(
                    name=dep.get('name', 'unknown'),
                    version=dep.get('version', 'unknown'),
                    purl=dep.get('purl'),
                    licenses=dep.get('licenses', []),
                    hashes=dep.get('hashes', {}),
                    supplier=dep.get('supplier'),
                )
                sbom.add_component(component)
        
        return sbom
    
    def generate_from_module(self, module_data: Dict[str, Any]) -> SBOM:
        """從模組生成 SBOM"""
        dependencies = []
        
        # 轉換依賴格式
        for dep in module_data.get('dependencies', []):
            if isinstance(dep, str):
                # 簡單字符串格式
                parts = dep.split('@')
                dependencies.append({
                    'name': parts[0],
                    'version': parts[1] if len(parts) > 1 else 'unknown',
                })
            elif isinstance(dep, dict):
                dependencies.append(dep)
        
        return self.generate(
            name=module_data.get('name', 'unknown'),
            version=module_data.get('version', 'unknown'),
            dependencies=dependencies,
        )
