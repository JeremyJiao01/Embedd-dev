"""列出可用 HAL 接口工具 — 查询代码仓中暴露的公共 API。"""

from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ListAPIInput(BaseModel):
    module: str | None = Field(
        default=None,
        description="模块限定名，为空则列出所有模块的接口",
    )


class ListAPITool(BaseTool):
    name: str = "list_api"
    description: str = (
        "列出代码仓中已有的公共接口函数、类型定义和宏。"
        "用于了解可以调用哪些 HAL 层和业务层接口。"
        "只能使用此工具返回的接口，不允许自己发明新接口。"
    )
    args_schema: type[BaseModel] = ListAPIInput

    def _run(self, module: str | None = None) -> str:
        from embedded_dev_flow.tools._graph_client import get_builder

        builder = get_builder()
        ingestor = builder._get_ingestor()

        rows = ingestor.fetch_module_apis(module, visibility="public")
        type_rows = ingestor.fetch_module_type_apis(module)

        lines: list[str] = []
        if rows:
            lines.append("=== 函数接口 ===")
            for row in rows:
                name = row.get("qualified_name", row.get("name", "?"))
                sig = row.get("signature", "")
                lines.append(f"  {name}: {sig}")

        if type_rows:
            lines.append("\n=== 类型/宏定义 ===")
            for row in type_rows:
                name = row.get("qualified_name", row.get("name", "?"))
                kind = row.get("kind", row.get("type", ""))
                lines.append(f"  [{kind}] {name}")

        return "\n".join(lines) if lines else "未找到公共接口。"
