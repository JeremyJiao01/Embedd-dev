"""获取函数源码工具 — 通过全限定名拉取函数完整源代码。"""

from __future__ import annotations

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class GetSnippetInput(BaseModel):
    qualified_name: str = Field(
        description="函数或类的全限定名，如 hal_adc.HAL_ADC_Read"
    )


class GetSnippetTool(BaseTool):
    name: str = "get_snippet"
    description: str = (
        "根据全限定名获取函数或类的完整源代码。"
        "用于查看已有实现的代码风格和逻辑，作为编写新代码的参考。"
    )
    args_schema: type[BaseModel] = GetSnippetInput

    def _run(self, qualified_name: str) -> str:
        from embedded_dev_flow.tools._graph_client import get_builder

        builder = get_builder()
        source = builder.get_function_source(qualified_name)
        if source:
            return source
        return f"未找到 {qualified_name} 的源代码。"
