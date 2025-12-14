#!/usr/bin/env python3
"""
Legacy Scratch Processor - 暫存區處理引擎

處理 _legacy_scratch 暫存區中的舊資產，執行：
1. 詞彙/映射/引用掃描
2. 高階推理分析決策
3. 位置分配與整合類型判定
4. 批量處理與報告生成

Usage:
    python process_legacy_scratch.py scan
    python process_legacy_scratch.py analyze --asset <filename>
    python process_legacy_scratch.py decide --asset <filename>
    python process_legacy_scratch.py batch --all

Version: 1.0.0
"""

import argparse
import yaml
import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

# 導入認知引擎
try:
    from cognitive_engine import (
        CognitiveEngine, UnderstandingLayer, ReasoningLayer,
        SearchLayer, IntegrationLayer, CognitiveContext
    )
    COGNITIVE_AVAILABLE = True
except ImportError:
    COGNITIVE_AVAILABLE = False

# ============================================================================
# 常數與配置
# ============================================================================

BASE_PATH = Path(__file__).parent.parent.parent
PLAYBOOKS_PATH = BASE_PATH / "docs" / "refactor_playbooks"
SCRATCH_PATH = PLAYBOOKS_PATH / "_legacy_scratch"
CONFIG_PATH = PLAYBOOKS_PATH / "config" / "legacy-scratch-processor.yaml"

# ============================================================================
# 枚舉定義
# ============================================================================

class AssetType(Enum):
    """資產類型"""
    DOCUMENTATION = "documentation"      # 文檔
    CONFIGURATION = "configuration"      # 配置
    CODE = "code"                        # 代碼
    DATA = "data"                        # 數據
    SCHEMA = "schema"                    # 架構定義
    MANIFEST = "manifest"                # 清單
    TEMPLATE = "template"                # 模板
    UNKNOWN = "unknown"                  # 未知

class IntegrationType(Enum):
    """整合類型"""
    FULL_INTEGRATION = "full_integration"        # 完整整合
    EMBEDDED_INTEGRATION = "embedded_integration" # 嵌入式整合
    REFERENCE_ONLY = "reference_only"            # 僅引用
    ARCHIVE = "archive"                          # 歸檔
    DISCARD = "discard"                          # 丟棄

class ProcessingStage(Enum):
    """處理階段"""
    INTAKE = "intake"           # 接收
    SCANNING = "scanning"       # 掃描中
    ANALYZING = "analyzing"     # 分析中
    DECIDED = "decided"         # 已決策
    INTEGRATED = "integrated"   # 已整合
    ARCHIVED = "archived"       # 已歸檔

# ============================================================================
# 資料結構
# ============================================================================

@dataclass
class VocabularyMatch:
    """詞彙匹配"""
    term: str
    category: str           # namespace, module, domain, keyword
    context: str            # 匹配的上下文
    line_number: int
    confidence: float

@dataclass
class ReferenceMatch:
    """引用匹配"""
    reference_type: str     # file, url, module, function
    target: str
    source_location: str
    is_internal: bool
    exists: bool

@dataclass
class StructureAnalysis:
    """結構分析"""
    file_type: str
    encoding: str
    line_count: int
    sections: List[Dict]
    hierarchy_depth: int
    has_frontmatter: bool
    metadata: Dict

@dataclass
class AssetAnalysis:
    """資產分析結果"""
    asset_id: str
    filename: str
    asset_type: AssetType
    file_hash: str
    vocabulary_matches: List[VocabularyMatch]
    reference_matches: List[ReferenceMatch]
    structure: StructureAnalysis
    domain_classification: Dict[str, float]
    quality_score: float
    timestamp: str

@dataclass
class PlacementDecision:
    """位置決策"""
    asset_id: str
    integration_type: IntegrationType
    target_directory: str
    target_filename: Optional[str]
    embedding_location: Optional[str]    # 用於嵌入式整合
    embedding_section: Optional[str]
    reasoning: List[str]
    confidence: float
    alternatives: List[Dict]
    requires_manual_review: bool

@dataclass
class AssetInventory:
    """資產清單"""
    scan_timestamp: str
    scratch_path: str
    total_assets: int
    by_type: Dict[str, int]
    by_stage: Dict[str, int]
    assets: List[Dict]

# ============================================================================
# 詞彙掃描器
# ============================================================================

class VocabularyScanner:
    """
    詞彙掃描器：掃描資產中的關鍵詞彙並與現有專案映射
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

        # 命名空間關鍵字
        self.namespace_keywords = {
            "hlp": ["hlp", "executor", "core", "HLP_EXECUTOR"],
            "kg": ["kg", "knowledge", "graph", "builder", "KG_BUILDER"],
            "quantum": ["quantum", "qsign", "signature"],
            "axiom": ["axiom", "architecture", "foundation"],
            "k8s": ["kubernetes", "k8s", "deployment", "rbac", "helm"],
            "refactor": ["refactor", "playbook", "migration"],
        }

        # 模組類型關鍵字
        self.module_keywords = {
            "config": ["config", "configuration", "settings", "env"],
            "schema": ["schema", "model", "type", "interface"],
            "service": ["service", "handler", "processor", "worker"],
            "util": ["util", "helper", "common", "shared"],
            "test": ["test", "spec", "mock", "fixture"],
        }

        # 領域關鍵字
        self.domain_keywords = {
            "deconstruction": ["deconstruct", "decompose", "break", "split"],
            "integration": ["integrate", "merge", "combine", "unify"],
            "refactor": ["refactor", "restructure", "reorganize", "optimize"],
            "legacy": ["legacy", "deprecated", "old", "migration"],
        }

    def scan(self, content: str, filename: str) -> List[VocabularyMatch]:
        """掃描內容中的詞彙"""
        matches = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()

            # 掃描命名空間
            for ns, keywords in self.namespace_keywords.items():
                for kw in keywords:
                    if kw.lower() in line_lower:
                        matches.append(VocabularyMatch(
                            term=kw,
                            category="namespace",
                            context=line.strip()[:100],
                            line_number=line_num,
                            confidence=0.9 if kw == ns else 0.7,
                        ))

            # 掃描模組類型
            for mod, keywords in self.module_keywords.items():
                for kw in keywords:
                    if kw.lower() in line_lower:
                        matches.append(VocabularyMatch(
                            term=kw,
                            category="module_type",
                            context=line.strip()[:100],
                            line_number=line_num,
                            confidence=0.8,
                        ))

            # 掃描領域
            for domain, keywords in self.domain_keywords.items():
                for kw in keywords:
                    if kw.lower() in line_lower:
                        matches.append(VocabularyMatch(
                            term=kw,
                            category="domain",
                            context=line.strip()[:100],
                            line_number=line_num,
                            confidence=0.75,
                        ))

        # 去重並保留最高信心度
        unique_matches = {}
        for match in matches:
            key = (match.term, match.category)
            if key not in unique_matches or match.confidence > unique_matches[key].confidence:
                unique_matches[key] = match

        return list(unique_matches.values())

    def extract_domain_classification(self, matches: List[VocabularyMatch]) -> Dict[str, float]:
        """從詞彙匹配中提取領域分類"""
        classification = defaultdict(float)

        for match in matches:
            if match.category == "namespace":
                classification[match.term] += match.confidence * 2
            elif match.category == "domain":
                classification[match.term] += match.confidence
            elif match.category == "module_type":
                classification[f"module_{match.term}"] += match.confidence * 0.5

        # 正規化
        total = sum(classification.values())
        if total > 0:
            classification = {k: round(v/total, 3) for k, v in classification.items()}

        return dict(sorted(classification.items(), key=lambda x: -x[1]))

# ============================================================================
# 引用掃描器
# ============================================================================

class ReferenceScanner:
    """
    引用掃描器：掃描資產中的引用並驗證
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # 引用模式
        self.patterns = {
            "markdown_link": r'\[([^\]]+)\]\(([^)]+)\)',
            "file_path": r'(?:^|[\s\'"])([a-zA-Z0-9_\-./]+\.[a-zA-Z]{2,4})(?:[\s\'"]|$)',
            "url": r'https?://[^\s\'"<>]+',
            "import": r'(?:from|import)\s+([a-zA-Z0-9_.]+)',
            "yaml_ref": r'\$ref:\s*[\'"]?([^\'">\s]+)[\'"]?',
        }

    def scan(self, content: str, source_path: Path) -> List[ReferenceMatch]:
        """掃描內容中的引用"""
        matches = []

        for ref_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, content, re.MULTILINE):
                if ref_type == "markdown_link":
                    target = match.group(2)
                elif ref_type == "url":
                    target = match.group(0)
                else:
                    target = match.group(1) if match.lastindex else match.group(0)

                # 判斷是否為內部引用
                is_internal = not target.startswith(('http://', 'https://', 'ftp://'))

                # 驗證引用是否存在
                exists = self._check_reference_exists(target, source_path, is_internal)

                matches.append(ReferenceMatch(
                    reference_type=ref_type,
                    target=target,
                    source_location=str(source_path),
                    is_internal=is_internal,
                    exists=exists,
                ))

        # 去重
        seen = set()
        unique = []
        for m in matches:
            key = (m.reference_type, m.target)
            if key not in seen:
                seen.add(key)
                unique.append(m)

        return unique

    def _check_reference_exists(self, target: str, source_path: Path, is_internal: bool) -> bool:
        """檢查引用是否存在"""
        if not is_internal:
            return True  # 外部連結假設存在

        # 嘗試解析相對路徑
        if target.startswith('./') or target.startswith('../'):
            resolved = (source_path.parent / target).resolve()
        else:
            resolved = self.project_root / target

        return resolved.exists()

# ============================================================================
# 結構分析器
# ============================================================================

class StructureAnalyzer:
    """
    結構分析器：分析資產的結構特性
    """

    def analyze(self, content: str, filepath: Path) -> StructureAnalysis:
        """分析內容結構"""
        lines = content.split('\n')

        # 檢測檔案類型
        file_type = self._detect_file_type(filepath, content)

        # 檢測編碼
        encoding = self._detect_encoding(content)

        # 分析段落結構
        sections = self._analyze_sections(content, file_type)

        # 計算層級深度
        hierarchy_depth = self._calculate_hierarchy_depth(content, file_type)

        # 檢查 frontmatter
        has_frontmatter = content.startswith('---\n')

        # 提取元數據
        metadata = self._extract_metadata(content, file_type)

        return StructureAnalysis(
            file_type=file_type,
            encoding=encoding,
            line_count=len(lines),
            sections=sections,
            hierarchy_depth=hierarchy_depth,
            has_frontmatter=has_frontmatter,
            metadata=metadata,
        )

    def _detect_file_type(self, filepath: Path, content: str) -> str:
        """檢測檔案類型"""
        ext = filepath.suffix.lower()

        type_map = {
            '.md': 'markdown',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.py': 'python',
            '.ts': 'typescript',
            '.js': 'javascript',
            '.txt': 'text',
        }

        return type_map.get(ext, 'unknown')

    def _detect_encoding(self, content: str) -> str:
        """檢測編碼"""
        try:
            content.encode('ascii')
            return 'ascii'
        except UnicodeEncodeError:
            return 'utf-8'

    def _analyze_sections(self, content: str, file_type: str) -> List[Dict]:
        """分析段落結構"""
        sections = []

        if file_type == 'markdown':
            # 提取 Markdown 標題
            for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
                sections.append({
                    'level': len(match.group(1)),
                    'title': match.group(2),
                    'position': match.start(),
                })

        elif file_type == 'yaml':
            # 提取 YAML 頂層鍵
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    sections = [{'key': k, 'type': type(v).__name__} for k, v in data.items()]
            except:
                pass

        return sections

    def _calculate_hierarchy_depth(self, content: str, file_type: str) -> int:
        """計算層級深度"""
        if file_type == 'markdown':
            levels = re.findall(r'^(#{1,6})', content, re.MULTILINE)
            return max(len(l) for l in levels) if levels else 0

        elif file_type in ['yaml', 'json']:
            # 基於縮排計算
            max_indent = 0
            for line in content.split('\n'):
                stripped = line.lstrip()
                if stripped:
                    indent = len(line) - len(stripped)
                    max_indent = max(max_indent, indent // 2)
            return max_indent

        return 0

    def _extract_metadata(self, content: str, file_type: str) -> Dict:
        """提取元數據"""
        metadata = {}

        if file_type == 'markdown' and content.startswith('---\n'):
            # 提取 YAML frontmatter
            end = content.find('\n---\n', 4)
            if end > 0:
                try:
                    metadata = yaml.safe_load(content[4:end])
                except:
                    pass

        elif file_type == 'yaml':
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    for key in ['version', 'name', 'description', 'metadata']:
                        if key in data:
                            metadata[key] = data[key]
            except:
                pass

        return metadata

# ============================================================================
# 高階決策引擎
# ============================================================================

class DecisionEngine:
    """
    高階決策引擎：基於分析結果做出整合決策

    決策流程：
    1. 評估資產品質
    2. 識別目標領域
    3. 判定整合類型
    4. 確定目標位置
    5. 評估置信度
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}

        # 目錄映射規則
        self.directory_mapping = {
            "hlp": "03_refactor/hlp-executor-core/",
            "kg": "03_refactor/kg-builder/",
            "quantum": "03_refactor/quantum/",
            "axiom": "03_refactor/axiom/",
            "k8s": "02_integration/k8s/",
            "deconstruction": "01_deconstruction/",
            "integration": "02_integration/",
            "refactor": "03_refactor/",
            "config": "config/",
            "template": "templates/",
        }

        # 整合類型閾值
        self.thresholds = {
            "full_integration": 0.7,
            "embedded_integration": 0.5,
            "reference_only": 0.3,
            "archive": 0.1,
        }

    def decide(self, analysis: AssetAnalysis) -> PlacementDecision:
        """做出位置決策"""
        reasoning = []

        # 步驟1: 評估品質
        quality = analysis.quality_score
        reasoning.append(f"品質評分: {quality:.2f}")

        # 步驟2: 識別主要領域
        primary_domain = self._identify_primary_domain(analysis)
        reasoning.append(f"主要領域: {primary_domain}")

        # 步驟3: 判定整合類型
        integration_type = self._determine_integration_type(analysis, quality)
        reasoning.append(f"整合類型: {integration_type.value}")

        # 步驟4: 確定目標位置
        target_dir, target_file = self._determine_target_location(
            analysis, primary_domain, integration_type
        )
        reasoning.append(f"目標位置: {target_dir}")

        # 步驟5: 確定嵌入位置 (如果是嵌入式整合)
        embedding_loc, embedding_sec = None, None
        if integration_type == IntegrationType.EMBEDDED_INTEGRATION:
            embedding_loc, embedding_sec = self._determine_embedding_location(
                analysis, target_dir
            )
            reasoning.append(f"嵌入位置: {embedding_loc} / {embedding_sec}")

        # 步驟6: 計算置信度
        confidence = self._calculate_confidence(analysis, integration_type)
        reasoning.append(f"決策置信度: {confidence:.2f}")

        # 步驟7: 生成備選方案
        alternatives = self._generate_alternatives(analysis, primary_domain)

        # 步驟8: 判斷是否需要人工審核
        requires_review = confidence < 0.6 or quality < 0.5

        return PlacementDecision(
            asset_id=analysis.asset_id,
            integration_type=integration_type,
            target_directory=target_dir,
            target_filename=target_file,
            embedding_location=embedding_loc,
            embedding_section=embedding_sec,
            reasoning=reasoning,
            confidence=confidence,
            alternatives=alternatives,
            requires_manual_review=requires_review,
        )

    def _identify_primary_domain(self, analysis: AssetAnalysis) -> str:
        """識別主要領域"""
        if not analysis.domain_classification:
            return "unknown"

        # 返回最高評分的領域
        return list(analysis.domain_classification.keys())[0]

    def _determine_integration_type(self, analysis: AssetAnalysis,
                                   quality: float) -> IntegrationType:
        """判定整合類型"""
        # 基於品質和結構判定
        if quality >= self.thresholds["full_integration"]:
            # 高品質，完整整合
            if analysis.structure.line_count > 50:
                return IntegrationType.FULL_INTEGRATION
            else:
                return IntegrationType.EMBEDDED_INTEGRATION

        elif quality >= self.thresholds["embedded_integration"]:
            # 中等品質，嵌入式
            return IntegrationType.EMBEDDED_INTEGRATION

        elif quality >= self.thresholds["reference_only"]:
            # 低品質，僅引用
            return IntegrationType.REFERENCE_ONLY

        else:
            # 極低品質，歸檔
            return IntegrationType.ARCHIVE

    def _determine_target_location(self, analysis: AssetAnalysis,
                                   primary_domain: str,
                                   integration_type: IntegrationType) -> Tuple[str, Optional[str]]:
        """確定目標位置"""
        # 基於領域映射
        if primary_domain in self.directory_mapping:
            target_dir = self.directory_mapping[primary_domain]
        else:
            # 默認位置
            if integration_type == IntegrationType.ARCHIVE:
                target_dir = "_legacy_scratch/archive/"
            else:
                target_dir = "03_refactor/misc/"

        # 確定目標檔名
        if integration_type == IntegrationType.FULL_INTEGRATION:
            target_file = analysis.filename
        else:
            target_file = None

        return target_dir, target_file

    def _determine_embedding_location(self, analysis: AssetAnalysis,
                                      target_dir: str) -> Tuple[Optional[str], Optional[str]]:
        """確定嵌入位置"""
        # 尋找目標目錄中的主要文件
        target_path = PLAYBOOKS_PATH / target_dir

        if target_path.exists():
            # 優先嵌入到 INDEX.md 或 README.md
            for candidate in ["INDEX.md", "README.md", "index.yaml"]:
                if (target_path / candidate).exists():
                    return str(target_path / candidate), "## Related Assets"

        return None, None

    def _calculate_confidence(self, analysis: AssetAnalysis,
                             integration_type: IntegrationType) -> float:
        """計算決策置信度"""
        confidence = 0.5

        # 基於詞彙匹配數量
        vocab_count = len(analysis.vocabulary_matches)
        if vocab_count > 10:
            confidence += 0.2
        elif vocab_count > 5:
            confidence += 0.1

        # 基於引用驗證
        valid_refs = sum(1 for r in analysis.reference_matches if r.exists)
        total_refs = len(analysis.reference_matches)
        if total_refs > 0:
            ref_ratio = valid_refs / total_refs
            confidence += ref_ratio * 0.2

        # 基於結構完整性
        if analysis.structure.has_frontmatter:
            confidence += 0.1

        return min(confidence, 1.0)

    def _generate_alternatives(self, analysis: AssetAnalysis,
                              primary_domain: str) -> List[Dict]:
        """生成備選方案"""
        alternatives = []

        # 基於次要領域生成備選
        for domain, score in list(analysis.domain_classification.items())[1:3]:
            if domain in self.directory_mapping:
                alternatives.append({
                    "target": self.directory_mapping[domain],
                    "reason": f"次要領域匹配: {domain} ({score:.2f})",
                    "confidence": score,
                })

        return alternatives

# ============================================================================
# 暫存區處理器 (主類)
# ============================================================================

class LegacyScratchProcessor:
    """
    暫存區處理器：協調所有處理組件
    """

    def __init__(self, scratch_path: Optional[Path] = None):
        self.scratch_path = scratch_path or SCRATCH_PATH
        self.playbooks_path = PLAYBOOKS_PATH

        # 初始化組件
        self.vocab_scanner = VocabularyScanner()
        self.ref_scanner = ReferenceScanner(BASE_PATH)
        self.struct_analyzer = StructureAnalyzer()
        self.decision_engine = DecisionEngine()

        # 初始化認知引擎 (如果可用)
        if COGNITIVE_AVAILABLE:
            self.cognitive_engine = CognitiveEngine()
        else:
            self.cognitive_engine = None

    def scan_inventory(self) -> AssetInventory:
        """掃描暫存區生成資產清單"""
        print(f"📂 掃描暫存區: {self.scratch_path}")

        assets = []
        by_type = defaultdict(int)
        by_stage = defaultdict(int)

        if not self.scratch_path.exists():
            print(f"⚠️ 暫存區不存在: {self.scratch_path}")
            return AssetInventory(
                scan_timestamp=datetime.now().isoformat(),
                scratch_path=str(self.scratch_path),
                total_assets=0,
                by_type={},
                by_stage={},
                assets=[],
            )

        for file in self.scratch_path.rglob("*"):
            if file.is_file() and not file.name.startswith('.'):
                # 判斷資產類型
                asset_type = self._classify_asset_type(file)
                by_type[asset_type.value] += 1

                # 判斷處理階段
                stage = self._determine_stage(file)
                by_stage[stage.value] += 1

                assets.append({
                    "filename": file.name,
                    "path": str(file.relative_to(self.scratch_path)),
                    "type": asset_type.value,
                    "stage": stage.value,
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                })

        print(f"   找到 {len(assets)} 個資產")

        return AssetInventory(
            scan_timestamp=datetime.now().isoformat(),
            scratch_path=str(self.scratch_path),
            total_assets=len(assets),
            by_type=dict(by_type),
            by_stage=dict(by_stage),
            assets=assets,
        )

    def analyze_asset(self, filename: str, deep: bool = False) -> AssetAnalysis:
        """分析單一資產"""
        filepath = self.scratch_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"資產不存在: {filename}")

        print(f"🔍 分析資產: {filename}")

        # 讀取內容
        content = filepath.read_text(encoding='utf-8', errors='ignore')

        # 計算哈希
        file_hash = hashlib.md5(content.encode()).hexdigest()

        # 詞彙掃描
        print("   詞彙掃描...")
        vocab_matches = self.vocab_scanner.scan(content, filename)

        # 引用掃描
        print("   引用掃描...")
        ref_matches = self.ref_scanner.scan(content, filepath)

        # 結構分析
        print("   結構分析...")
        structure = self.struct_analyzer.analyze(content, filepath)

        # 領域分類
        domain_class = self.vocab_scanner.extract_domain_classification(vocab_matches)

        # 計算品質評分
        quality = self._calculate_quality_score(vocab_matches, ref_matches, structure)

        # 如果啟用深度分析且認知引擎可用
        if deep and self.cognitive_engine:
            print("   深度認知分析...")
            cognitive_result = self.cognitive_engine.process({
                "text": content[:5000],  # 限制長度
                "filename": filename,
                "type": "asset_analysis",
            })
            # 可以用認知結果進一步豐富分析

        analysis = AssetAnalysis(
            asset_id=file_hash[:8],
            filename=filename,
            asset_type=self._classify_asset_type(filepath),
            file_hash=file_hash,
            vocabulary_matches=vocab_matches,
            reference_matches=ref_matches,
            structure=structure,
            domain_classification=domain_class,
            quality_score=quality,
            timestamp=datetime.now().isoformat(),
        )

        print(f"   品質評分: {quality:.2f}")
        print(f"   詞彙匹配: {len(vocab_matches)}")
        print(f"   引用匹配: {len(ref_matches)}")

        return analysis

    def decide_placement(self, analysis: AssetAnalysis) -> PlacementDecision:
        """為資產做出位置決策"""
        print(f"🎯 決策: {analysis.filename}")

        decision = self.decision_engine.decide(analysis)

        print(f"   整合類型: {decision.integration_type.value}")
        print(f"   目標位置: {decision.target_directory}")
        print(f"   置信度: {decision.confidence:.2f}")

        if decision.requires_manual_review:
            print("   ⚠️ 需要人工審核")

        return decision

    def batch_process(self, filter_stage: Optional[ProcessingStage] = None) -> List[Dict]:
        """批量處理所有資產"""
        print("🔄 開始批量處理...")

        inventory = self.scan_inventory()
        results = []

        for asset_info in inventory.assets:
            # 過濾階段
            if filter_stage and asset_info["stage"] != filter_stage.value:
                continue

            try:
                # 分析
                analysis = self.analyze_asset(asset_info["filename"])

                # 決策
                decision = self.decide_placement(analysis)

                results.append({
                    "asset": asset_info["filename"],
                    "analysis_id": analysis.asset_id,
                    "decision": asdict(decision),
                    "status": "success",
                })

            except Exception as e:
                results.append({
                    "asset": asset_info["filename"],
                    "status": "error",
                    "error": str(e),
                })

        print(f"\n✅ 批量處理完成: {len(results)} 個資產")
        return results

    def _classify_asset_type(self, filepath: Path) -> AssetType:
        """分類資產類型"""
        ext = filepath.suffix.lower()
        name_lower = filepath.name.lower()

        if ext == '.md':
            return AssetType.DOCUMENTATION
        elif ext in ['.yaml', '.yml']:
            if 'config' in name_lower:
                return AssetType.CONFIGURATION
            elif 'schema' in name_lower:
                return AssetType.SCHEMA
            else:
                return AssetType.DATA
        elif ext == '.json':
            if 'manifest' in name_lower:
                return AssetType.MANIFEST
            else:
                return AssetType.DATA
        elif ext in ['.py', '.ts', '.js']:
            return AssetType.CODE
        elif 'template' in name_lower:
            return AssetType.TEMPLATE
        else:
            return AssetType.UNKNOWN

    def _determine_stage(self, filepath: Path) -> ProcessingStage:
        """確定處理階段"""
        rel_path = str(filepath.relative_to(self.scratch_path))

        if rel_path.startswith('intake/'):
            return ProcessingStage.INTAKE
        elif rel_path.startswith('processing/'):
            return ProcessingStage.SCANNING
        elif rel_path.startswith('analyzed/'):
            return ProcessingStage.DECIDED
        elif rel_path.startswith('archive/'):
            return ProcessingStage.ARCHIVED
        else:
            return ProcessingStage.INTAKE

    def _calculate_quality_score(self, vocab_matches: List[VocabularyMatch],
                                 ref_matches: List[ReferenceMatch],
                                 structure: StructureAnalysis) -> float:
        """計算品質評分"""
        score = 0.5  # 基礎分

        # 詞彙豐富度
        if len(vocab_matches) > 10:
            score += 0.15
        elif len(vocab_matches) > 5:
            score += 0.1

        # 引用有效性
        valid_refs = sum(1 for r in ref_matches if r.exists)
        if ref_matches:
            score += (valid_refs / len(ref_matches)) * 0.15

        # 結構完整性
        if structure.has_frontmatter:
            score += 0.1
        if structure.hierarchy_depth > 0:
            score += 0.05
        if len(structure.sections) > 3:
            score += 0.05

        return min(score, 1.0)

# ============================================================================
# CLI 入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Legacy Scratch Processor - 暫存區處理引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # scan 命令
    scan_parser = subparsers.add_parser("scan", help="掃描暫存區")
    scan_parser.add_argument("--output", "-o", help="輸出檔案")

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析資產")
    analyze_parser.add_argument("--asset", "-a", required=True, help="資產檔名")
    analyze_parser.add_argument("--deep", action="store_true", help="深度分析")
    analyze_parser.add_argument("--output", "-o", help="輸出檔案")

    # decide 命令
    decide_parser = subparsers.add_parser("decide", help="位置決策")
    decide_parser.add_argument("--asset", "-a", required=True, help="資產檔名")
    decide_parser.add_argument("--output", "-o", help="輸出檔案")

    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量處理")
    batch_parser.add_argument("--all", action="store_true", help="處理所有")
    batch_parser.add_argument("--stage", choices=["intake", "scanning", "analyzing"],
                             help="過濾階段")
    batch_parser.add_argument("--output", "-o", help="輸出檔案")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    processor = LegacyScratchProcessor()

    if args.command == "scan":
        inventory = processor.scan_inventory()
        output = asdict(inventory)

        output_str = yaml.dump(output, allow_unicode=True, default_flow_style=False)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            print(f"\n✅ 清單已儲存: {args.output}")
        else:
            print("\n" + output_str)

    elif args.command == "analyze":
        analysis = processor.analyze_asset(args.asset, deep=args.deep)

        output = {
            "asset_id": analysis.asset_id,
            "filename": analysis.filename,
            "type": analysis.asset_type.value,
            "quality_score": analysis.quality_score,
            "domain_classification": analysis.domain_classification,
            "vocabulary_count": len(analysis.vocabulary_matches),
            "reference_count": len(analysis.reference_matches),
            "structure": asdict(analysis.structure),
        }

        output_str = yaml.dump(output, allow_unicode=True, default_flow_style=False)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            print(f"\n✅ 分析已儲存: {args.output}")
        else:
            print("\n" + output_str)

    elif args.command == "decide":
        analysis = processor.analyze_asset(args.asset)
        decision = processor.decide_placement(analysis)

        output = asdict(decision)
        output["integration_type"] = decision.integration_type.value

        output_str = yaml.dump(output, allow_unicode=True, default_flow_style=False)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            print(f"\n✅ 決策已儲存: {args.output}")
        else:
            print("\n" + output_str)

    elif args.command == "batch":
        stage = ProcessingStage(args.stage) if args.stage else None
        results = processor.batch_process(filter_stage=stage)

        output_str = yaml.dump(results, allow_unicode=True, default_flow_style=False)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_str)
            print(f"\n✅ 結果已儲存: {args.output}")
        else:
            print("\n" + output_str)

if __name__ == "__main__":
    main()
