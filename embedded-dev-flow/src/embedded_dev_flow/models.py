"""Flow 状态与各阶段结构化输出的 Pydantic 模型。"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── 需求拆解阶段输出 ──────────────────────────────────────────────

class SubTask(BaseModel):
    name: str = Field(description="子任务名称")
    description: str = Field(description="功能描述")
    acceptance_criteria: list[str] = Field(description="验收标准")
    priority: str = Field(description="优先级: high / medium / low")


class RequirementsOutput(BaseModel):
    summary: str = Field(description="需求概述")
    sub_tasks: list[SubTask] = Field(description="拆解后的子任务列表")


# ── 接口设计阶段输出 ──────────────────────────────────────────────

class APIReference(BaseModel):
    qualified_name: str = Field(description="接口全限定名")
    signature: str = Field(description="函数签名")
    purpose: str = Field(description="在本需求中的用途")


class ModuleDesign(BaseModel):
    file_name: str = Field(description="目标文件名, 如 mppt_ctrl.c")
    description: str = Field(description="模块职责")
    apis_used: list[APIReference] = Field(description="调用的已有接口")
    pseudocode: str = Field(description="伪代码逻辑")


class DesignOutput(BaseModel):
    modules: list[ModuleDesign] = Field(description="模块设计列表")
    notes: str = Field(default="", description="设计备注")


# ── 代码生成阶段输出 ──────────────────────────────────────────────

class CodeFile(BaseModel):
    file_name: str = Field(description="文件名")
    content: str = Field(description="完整源代码")


class CodegenOutput(BaseModel):
    files: list[CodeFile] = Field(description="生成的代码文件")


# ── 审核阶段输出 ──────────────────────────────────────────────────

class ReviewIssue(BaseModel):
    file_name: str = Field(description="问题所在文件")
    line_hint: str = Field(default="", description="大致行号或函数名")
    severity: str = Field(description="严重程度: error / warning / suggestion")
    description: str = Field(description="问题描述")


class ReviewOutput(BaseModel):
    verdict: str = Field(description="审核结论: pass / revise")
    issues: list[ReviewIssue] = Field(default_factory=list, description="问题列表")
    summary: str = Field(description="审核总结")


# ── Flow 全局状态 ─────────────────────────────────────────────────

class DevFlowState(BaseModel):
    raw_requirement: str = ""
    requirements: RequirementsOutput | None = None
    design: DesignOutput | None = None
    code: CodegenOutput | None = None
    review: ReviewOutput | None = None
    revision_count: int = 0
    max_revisions: int = 2
