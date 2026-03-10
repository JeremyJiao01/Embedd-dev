"""图查询工具 — 查询函数调用关系和依赖。"""

from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class QueryGraphInput(BaseModel):
    function_name: str = Field(description="要查询的函数名或全限定名")
    direction: str = Field(
        default="both",
        description="查询方向: callers(谁调用了它) / callees(它调用了谁) / both",
    )


class QueryGraphTool(BaseTool):
    name: str = "query_graph"
    description: str = (
        "查询函数的调用关系图。可以查看某个函数被谁调用、它调用了哪些函数。"
        "用于理解现有代码的依赖关系，避免重复实现。"
    )
    args_schema: type[BaseModel] = QueryGraphInput

    def _run(self, function_name: str, direction: str = "both") -> str:
        from embedded_dev_flow.tools._graph_client import get_graph_query_service

        svc = get_graph_query_service()
        lines: list[str] = []

        if direction in ("callers", "both"):
            callers = svc.fetch_callers(function_name)
            lines.append(f"=== 调用 {function_name} 的函数 ({len(callers)}) ===")
            for node in callers:
                lines.append(f"  {node.qualified_name}  ({node.path}:{node.start_line})")

        if direction in ("callees", "both"):
            callees = svc.fetch_callees(function_name)
            lines.append(f"\n=== {function_name} 调用的函数 ({len(callees)}) ===")
            for node in callees:
                lines.append(f"  {node.qualified_name}  ({node.path}:{node.start_line})")

        return "\n".join(lines) if lines else f"未找到 {function_name} 的调用关系。"
