#!/usr/bin/env python3
"""
RAG Query Script for Governance Index
=====================================

This script provides semantic search capabilities over the governance index
using vector embeddings and RAG (Retrieval Augmented Generation).

Usage:
    python rag-query.py "your query here"
    python rag-query.py --query "security policies" --top-k 5
    python rag-query.py --interactive

Evolution Stages:
    Phase 1: Keyword-based search (current fallback)
    Phase 2: Vector similarity search (current)
    Phase 3: Multi-vector fusion
    Phase 4: Pure vector autonomy with AI interpretation
"""

import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Try to import sentence-transformers, fall back to keyword search if not available
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    print("Note: sentence-transformers not installed. Using keyword-based search.")
    print("Install with: pip install sentence-transformers torch")


@dataclass
class SearchResult:
    """Represents a search result from the governance index."""
    id: str
    name: str
    score: float
    semantic_text: str
    keywords: List[str]
    compliance_tags: List[str]
    security_level: str
    path: str
    type: str  # 'dimension' or 'shared'


class GovernanceRAG:
    """RAG-based search engine for the governance index."""

    def __init__(self, index_path: Optional[Path] = None):
        """Initialize the RAG engine with the governance index."""
        if index_path is None:
            index_path = Path(__file__).parent.parent

        self.index_path = index_path
        self.vectors_path = index_path / "vectors.json"
        self.dimensions_path = index_path / "dimensions.json"
        self.compliance_path = index_path / "compliance.json"

        # Load index data
        self.vectors_data = self._load_json(self.vectors_path)
        self.dimensions_data = self._load_json(self.dimensions_path)
        self.compliance_data = self._load_json(self.compliance_path)

        # Initialize model if available
        self.model = None
        self.embeddings_cache = {}

        if VECTOR_SEARCH_AVAILABLE:
            model_name = self.vectors_data.get("embedding_config", {}).get("model", "all-MiniLM-L6-v2")
            try:
                self.model = SentenceTransformer(model_name)
                self._build_embeddings_cache()
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                print("Falling back to keyword search.")

    def _load_json(self, path: Path) -> Dict:
        """Load JSON file from path."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Index file not found: {path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {path}: {e}")
            return {}

    def _build_embeddings_cache(self):
        """Build embeddings cache for all dimensions."""
        if not self.model or not self.vectors_data:
            return

        print("Building embeddings cache...")

        # Build embeddings for dimensions
        dimensions = self.vectors_data.get("dimensions", [])
        for dim in dimensions:
            text = dim.get("semantic_text", "")
            if text:
                self.embeddings_cache[dim["id"]] = {
                    "embedding": self.model.encode(text, convert_to_tensor=True),
                    "data": dim,
                    "type": "dimension"
                }

        # Build embeddings for shared resources
        shared = self.vectors_data.get("shared_resources", [])
        for res in shared:
            text = res.get("semantic_text", "")
            if text:
                self.embeddings_cache[f"shared_{res['id']}"] = {
                    "embedding": self.model.encode(text, convert_to_tensor=True),
                    "data": res,
                    "type": "shared"
                }

        print(f"Cached {len(self.embeddings_cache)} embeddings.")

    def search(self, query: str, top_k: int = 5,
               include_compliance: bool = True,
               security_filter: Optional[str] = None) -> List[SearchResult]:
        """
        Search the governance index using the query.

        Args:
            query: The search query
            top_k: Number of results to return
            include_compliance: Whether to include compliance information
            security_filter: Filter by security level (critical, high, medium, low)

        Returns:
            List of SearchResult objects
        """
        if VECTOR_SEARCH_AVAILABLE and self.model and self.embeddings_cache:
            return self._vector_search(query, top_k, include_compliance, security_filter)
        else:
            return self._keyword_search(query, top_k, include_compliance, security_filter)

    def _vector_search(self, query: str, top_k: int,
                       include_compliance: bool,
                       security_filter: Optional[str]) -> List[SearchResult]:
        """Perform vector similarity search."""
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        results = []
        for key, cached in self.embeddings_cache.items():
            # Apply security filter if specified
            if security_filter:
                item_security = cached["data"].get("security_level", "").lower()
                if item_security != security_filter.lower():
                    continue

            similarity = util.cos_sim(query_embedding, cached["embedding"]).item()

            data = cached["data"]
            result = SearchResult(
                id=data.get("id", key),
                name=data.get("name", key),
                score=similarity,
                semantic_text=data.get("semantic_text", ""),
                keywords=data.get("keywords", []),
                compliance_tags=data.get("compliance_tags", []) if include_compliance else [],
                security_level=data.get("security_level", "unknown"),
                path=self._get_dimension_path(data.get("id", key)),
                type=cached["type"]
            )
            results.append(result)

        # Sort by score and return top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _keyword_search(self, query: str, top_k: int,
                        include_compliance: bool,
                        security_filter: Optional[str]) -> List[SearchResult]:
        """Perform keyword-based search as fallback."""
        query_terms = set(query.lower().split())
        results = []

        # Search dimensions
        dimensions = self.vectors_data.get("dimensions", [])
        for dim in dimensions:
            # Apply security filter if specified
            if security_filter:
                item_security = dim.get("security_level", "").lower()
                if item_security != security_filter.lower():
                    continue

            # Calculate keyword match score
            keywords = set(k.lower() for k in dim.get("keywords", []))
            text_words = set(dim.get("semantic_text", "").lower().split())
            all_words = keywords | text_words

            matches = query_terms & all_words
            score = len(matches) / len(query_terms) if query_terms else 0

            if score > 0:
                result = SearchResult(
                    id=dim.get("id", ""),
                    name=dim.get("name", ""),
                    score=score,
                    semantic_text=dim.get("semantic_text", ""),
                    keywords=dim.get("keywords", []),
                    compliance_tags=dim.get("compliance_tags", []) if include_compliance else [],
                    security_level=dim.get("security_level", "unknown"),
                    path=self._get_dimension_path(dim.get("id", "")),
                    type="dimension"
                )
                results.append(result)

        # Search shared resources
        shared = self.vectors_data.get("shared_resources", [])
        for res in shared:
            keywords = set(k.lower() for k in res.get("keywords", []))
            text_words = set(res.get("semantic_text", "").lower().split())
            all_words = keywords | text_words

            matches = query_terms & all_words
            score = len(matches) / len(query_terms) if query_terms else 0

            if score > 0:
                result = SearchResult(
                    id=res.get("id", ""),
                    name=res.get("name", ""),
                    score=score,
                    semantic_text=res.get("semantic_text", ""),
                    keywords=res.get("keywords", []),
                    compliance_tags=[],
                    security_level="medium",
                    path=res.get("id", ""),
                    type="shared"
                )
                results.append(result)

        # Sort by score and return top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _get_dimension_path(self, dim_id: str) -> str:
        """Get the file path for a dimension."""
        dimensions = self.dimensions_data.get("dimensions", [])
        for dim in dimensions:
            if dim.get("id") == dim_id:
                return dim.get("path", f"{dim_id}-unknown")
        return dim_id

    def get_compliance_info(self, dimension_id: str) -> Dict:
        """Get compliance framework information for a dimension."""
        matrix = self.compliance_data.get("compliance_matrix", {}).get("by_dimension", {})
        frameworks = matrix.get(dimension_id, [])

        result = {
            "dimension": dimension_id,
            "frameworks": frameworks,
            "details": []
        }

        # Get detailed framework info
        all_frameworks = self.compliance_data.get("frameworks", [])
        for fw in all_frameworks:
            if fw["id"] in frameworks:
                result["details"].append({
                    "id": fw["id"],
                    "name": fw["name"],
                    "status": fw.get("status", "unknown"),
                    "audit_frequency": fw.get("audit_frequency", "unknown")
                })

        return result

    def get_dependencies(self, dimension_id: str) -> Dict:
        """Get dependency information for a dimension."""
        dimensions = self.dimensions_data.get("dimensions", [])

        for dim in dimensions:
            if dim.get("id") == dimension_id:
                return {
                    "id": dimension_id,
                    "name": dim.get("name"),
                    "depends_on": dim.get("depends_on", []),
                    "layer": dim.get("layer"),
                    "execution": dim.get("execution"),
                    "priority": dim.get("priority")
                }

        return {"id": dimension_id, "error": "Dimension not found"}

    def format_results(self, results: List[SearchResult], verbose: bool = False) -> str:
        """Format search results for display."""
        if not results:
            return "No results found."

        output = []
        output.append(f"\n{'='*60}")
        output.append(f"Found {len(results)} relevant governance dimensions:")
        output.append(f"{'='*60}\n")

        for i, result in enumerate(results, 1):
            output.append(f"{i}. [{result.id}] {result.name}")
            output.append(f"   Score: {result.score:.4f}")
            output.append(f"   Type: {result.type}")
            output.append(f"   Path: {result.path}/")
            output.append(f"   Security Level: {result.security_level}")

            if verbose:
                output.append(f"   Description: {result.semantic_text[:100]}...")
                if result.keywords:
                    output.append(f"   Keywords: {', '.join(result.keywords[:5])}")
                if result.compliance_tags:
                    output.append(f"   Compliance: {', '.join(result.compliance_tags[:3])}")

            output.append("")

        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="RAG Query for Governance Index",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s "security policies"
    %(prog)s --query "compliance frameworks" --top-k 10
    %(prog)s --query "agent governance" --verbose
    %(prog)s --query "audit" --security-filter critical
    %(prog)s --interactive
        """
    )

    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--query", "-q", dest="query_opt", help="Search query (alternative)")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed results")
    parser.add_argument("--security-filter", "-s", choices=["critical", "high", "medium", "low"],
                        help="Filter by security level")
    parser.add_argument("--compliance", "-c", action="store_true",
                        help="Show compliance info for top result")
    parser.add_argument("--dependencies", "-d", action="store_true",
                        help="Show dependencies for top result")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("--index-path", type=Path, help="Path to index directory")

    args = parser.parse_args()

    # Initialize RAG engine
    rag = GovernanceRAG(args.index_path)

    # Get query
    query = args.query or args.query_opt

    if args.interactive:
        print("\nGovernance RAG Interactive Mode")
        print("Type 'quit' or 'exit' to leave")
        print("-" * 40)

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() in ["quit", "exit", "q"]:
                    break
                if not query:
                    continue

                results = rag.search(query, args.top_k, security_filter=args.security_filter)
                print(rag.format_results(results, args.verbose))

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                break

    elif query:
        results = rag.search(query, args.top_k, security_filter=args.security_filter)
        print(rag.format_results(results, args.verbose))

        if results:
            if args.compliance:
                print("\nCompliance Information for top result:")
                print("-" * 40)
                compliance = rag.get_compliance_info(results[0].id)
                print(json.dumps(compliance, indent=2))

            if args.dependencies:
                print("\nDependency Information for top result:")
                print("-" * 40)
                deps = rag.get_dependencies(results[0].id)
                print(json.dumps(deps, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
