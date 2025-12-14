#!/usr/bin/env python3
"""
Knowledge Engine - 知識引擎
Repository Graph, Embeddings, and Vector Search

提供代碼庫理解和語義搜索能力
"""

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    """節點類型"""

    FILE = "file"
    DIRECTORY = "directory"
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"
    IMPORT = "import"
    COMMENT = "comment"


class EdgeType(Enum):
    """邊類型"""

    CONTAINS = "contains"  # 目錄包含文件
    IMPORTS = "imports"  # 導入關係
    CALLS = "calls"  # 函數調用
    EXTENDS = "extends"  # 類繼承
    IMPLEMENTS = "implements"  # 接口實現
    REFERENCES = "references"  # 一般引用


@dataclass
class GraphNode:
    """圖節點"""

    id: str
    name: str
    node_type: NodeType
    path: str
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)


@dataclass
class GraphEdge:
    """圖邊"""

    source_id: str
    target_id: str
    edge_type: EdgeType
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """搜索結果"""

    node: GraphNode
    score: float
    context: str = ""


class RepoGraph:
    """
    倉庫圖

    建立代碼庫的圖結構表示。
    """

    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[GraphEdge] = []

    def add_node(self, node: GraphNode) -> None:
        """添加節點"""
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        """添加邊"""
        self.edges.append(edge)

    def get_node(self, node_id: str) -> GraphNode | None:
        """獲取節點"""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, edge_type: EdgeType | None = None) -> list[GraphNode]:
        """獲取鄰居節點"""
        neighbors = []
        for edge in self.edges:
            if edge.source_id == node_id:
                if edge_type is None or edge.edge_type == edge_type:
                    neighbor = self.nodes.get(edge.target_id)
                    if neighbor:
                        neighbors.append(neighbor)
        return neighbors

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典"""
        return {
            "nodes": [
                {"id": n.id, "name": n.name, "type": n.node_type.value, "path": n.path}
                for n in self.nodes.values()
            ],
            "edges": [
                {"source": e.source_id, "target": e.target_id, "type": e.edge_type.value}
                for e in self.edges
            ],
        }


class EmbeddingProvider:
    """
    嵌入提供者

    生成文本的向量嵌入。
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._dimension = 1536  # OpenAI 嵌入維度

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(self, text: str) -> list[float]:
        """生成單個文本的嵌入"""
        # 實際實現會調用 OpenAI API
        # 這裡返回模擬嵌入
        return self._mock_embedding(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量生成嵌入"""
        return [self._mock_embedding(text) for text in texts]

    def _mock_embedding(self, text: str) -> list[float]:
        """生成模擬嵌入（用於測試）"""
        # 使用 hash 生成確定性的模擬嵌入
        hash_bytes = hashlib.sha256(text.encode()).digest()
        embedding = []
        for i in range(0, min(len(hash_bytes), self._dimension // 8)):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding.append((byte_val / 255.0) - 0.5)

        # 填充到完整維度
        while len(embedding) < self._dimension:
            embedding.append(0.0)

        return embedding[: self._dimension]


class VectorStore:
    """
    向量存儲

    存儲和搜索向量嵌入。
    """

    def __init__(self):
        self.vectors: dict[str, list[float]] = {}
        self.metadata: dict[str, dict[str, Any]] = {}

    def upsert(self, id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        """插入或更新向量"""
        self.vectors[id] = vector
        self.metadata[id] = metadata or {}

    def delete(self, id: str) -> None:
        """刪除向量"""
        self.vectors.pop(id, None)
        self.metadata.pop(id, None)

    def search(self, query_vector: list[float], top_k: int = 10) -> list[tuple[str, float]]:
        """搜索最相似的向量"""
        scores = []
        for id, vector in self.vectors.items():
            score = self._cosine_similarity(query_vector, vector)
            scores.append((id, score))

        # 按分數排序
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """計算餘弦相似度"""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


class KnowledgeEngine:
    """
    知識引擎

    整合倉庫圖、嵌入和向量搜索，提供代碼庫理解能力。

    功能：
    - Repo Graph 圖譜
    - Embeddings 向量嵌入
    - Vector Search 向量搜索
    - Context Retrieval 上下文檢索
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.repo_graph = RepoGraph()
        self.embedding_provider = EmbeddingProvider(
            model=self.config.get("embedding_model", "text-embedding-3-small")
        )
        self.vector_store = VectorStore()

    async def index_file(self, path: str, content: str) -> None:
        """索引文件"""
        # 創建節點
        node_id = self._generate_id(path)

        # 生成嵌入
        embedding = await self.embedding_provider.embed(content)

        # 創建圖節點
        node = GraphNode(
            id=node_id,
            name=path.split("/")[-1],
            node_type=NodeType.FILE,
            path=path,
            content=content,
            embedding=embedding,
        )

        # 添加到圖
        self.repo_graph.add_node(node)

        # 添加到向量存儲
        self.vector_store.upsert(
            id=node_id, vector=embedding, metadata={"path": path, "type": "file"}
        )

    async def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """語義搜索"""
        # 生成查詢嵌入
        query_embedding = await self.embedding_provider.embed(query)

        # 搜索向量存儲
        results = self.vector_store.search(query_embedding, top_k)

        # 構建搜索結果
        search_results = []
        for node_id, score in results:
            node = self.repo_graph.get_node(node_id)
            if node:
                search_results.append(
                    SearchResult(
                        node=node, score=score, context=node.content[:500] if node.content else ""
                    )
                )

        return search_results

    async def get_context(self, path: str, depth: int = 2) -> dict[str, Any]:
        """獲取文件上下文"""
        node_id = self._generate_id(path)
        node = self.repo_graph.get_node(node_id)

        if not node:
            return {"error": "Node not found"}

        # 收集上下文
        context = {
            "node": {
                "id": node.id,
                "name": node.name,
                "type": node.node_type.value,
                "path": node.path,
            },
            "neighbors": [],
            "related": [],
        }

        # 獲取鄰居
        for neighbor in self.repo_graph.get_neighbors(node_id):
            context["neighbors"].append(
                {"id": neighbor.id, "name": neighbor.name, "type": neighbor.node_type.value}
            )

        return context

    @staticmethod
    def _generate_id(path: str) -> str:
        """生成節點 ID"""
        return hashlib.md5(path.encode()).hexdigest()
