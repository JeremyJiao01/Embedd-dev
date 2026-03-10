"""CodeGraphWiki 单例客户端，所有 Tool 共享同一个实例。"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from code_graph_builder import CodeGraphBuilder
from code_graph_builder.tools.graph_query import GraphQueryService
from code_graph_builder.tools.semantic_search import SemanticSearchService
from code_graph_builder.embeddings import create_embedder, create_vector_store


@lru_cache(maxsize=1)
def get_builder() -> CodeGraphBuilder:
    repo_path = os.environ["INVERTER_REPO_PATH"]
    db_path = os.environ.get("CGB_DB_PATH", "./.code-graph/graph.db")
    return CodeGraphBuilder(
        repo_path=repo_path,
        backend="kuzu",
        backend_config={"db_path": db_path},
    )


@lru_cache(maxsize=1)
def get_graph_query_service() -> GraphQueryService:
    builder = get_builder()
    ingestor = builder._get_ingestor()
    return GraphQueryService(ingestor, backend="kuzu")


@lru_cache(maxsize=1)
def get_semantic_search_service() -> SemanticSearchService:
    builder = get_builder()
    embedder = create_embedder()
    vector_store = create_vector_store(backend="memory", dimension=1536)
    ingestor = builder._get_ingestor()
    return SemanticSearchService(embedder, vector_store, ingestor)
