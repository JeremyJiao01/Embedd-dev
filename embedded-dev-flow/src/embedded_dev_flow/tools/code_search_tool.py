"""语义搜索工具 — 在代码仓中查找相似的已有实现。"""

from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CodeSearchInput(BaseModel):
    query: str = Field(description="自然语言描述，如"MPPT 最大功率点追踪"")
    top_k: int = Field(default=5, description="返回结果数量")


class CodeSearchTool(BaseTool):
    name: str = "code_search"
    description: str = (
        "在代码仓中进行语义搜索，找到与描述最相似的函数或模块。"
        "用于查找是否有已有实现可以参考，或了解现有代码风格。"
    )
    args_schema: type[BaseModel] = CodeSearchInput

    def _run(self, query: str, top_k: int = 5) -> str:
        from embedded_dev_flow.tools._graph_client import get_semantic_search_service

        svc = get_semantic_search_service()
        results = svc.search(query, top_k=top_k)
        if not results:
            return "未找到相关代码。"

        lines: list[str] = []
        for r in results:
            lines.append(f"--- {r.qualified_name} (相似度: {r.score:.2f}) ---")
            lines.append(f"文件: {r.file_path}  行: {r.start_line}-{r.end_line}")
            if r.source_code:
                lines.append(r.source_code)
            lines.append("")
        return "\n".join(lines)
