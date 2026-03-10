"""嵌入式开发全流程 Flow：需求文本 → 任务列表 → 接口设计 → 代码草稿 → 审核结论。"""

from __future__ import annotations

import json
from pathlib import Path

from crewai.flow import Flow, listen, router, start

from embedded_dev_flow.crews.codegen_crew.codegen_crew import CodegenCrew
from embedded_dev_flow.crews.design_crew.design_crew import DesignCrew
from embedded_dev_flow.crews.requirements_crew.requirements_crew import RequirementsCrew
from embedded_dev_flow.crews.review_crew.review_crew import ReviewCrew
from embedded_dev_flow.models import DevFlowState


class EmbeddedDevFlow(Flow[DevFlowState]):
    """从需求文本到代码交付的全流程编排。"""

    # ── 阶段 1: 接收需求 ──────────────────────────────────────────

    @start()
    def receive_requirement(self):
        print(f"\n{'='*60}")
        print(f"[阶段 1] 接收需求")
        print(f"{'='*60}")
        print(f"需求内容: {self.state.raw_requirement[:200]}...")

    # ── 阶段 2: 需求拆解 ──────────────────────────────────────────

    @listen(receive_requirement)
    def decompose_requirements(self):
        print(f"\n{'='*60}")
        print(f"[阶段 2] 需求拆解")
        print(f"{'='*60}")

        result = (
            RequirementsCrew()
            .crew()
            .kickoff(inputs={"requirement": self.state.raw_requirement})
        )
        self.state.requirements = result.pydantic
        print(f"拆解完成: {len(self.state.requirements.sub_tasks)} 个子任务")

    # ── 阶段 3: 接口设计（可从审核打回重入）────────────────────────

    @listen(decompose_requirements)
    def design_modules(self):
        print(f"\n{'='*60}")
        revision = f"(第 {self.state.revision_count} 次修订)" if self.state.revision_count else ""
        print(f"[阶段 3] 接口设计 {revision}")
        print(f"{'='*60}")

        review_feedback = ""
        if self.state.review and self.state.review.verdict == "revise":
            review_feedback = self.state.review.summary
            for issue in self.state.review.issues:
                if issue.severity == "error":
                    review_feedback += f"\n- [{issue.severity}] {issue.file_name}: {issue.description}"

        result = (
            DesignCrew()
            .crew()
            .kickoff(inputs={
                "task_list": self.state.requirements.model_dump_json(),
                "review_feedback": review_feedback,
            })
        )
        self.state.design = result.pydantic
        print(f"设计完成: {len(self.state.design.modules)} 个模块")

    # ── 阶段 4: 代码生成 ──────────────────────────────────────────

    @listen(design_modules)
    def generate_code(self):
        print(f"\n{'='*60}")
        print(f"[阶段 4] 代码生成")
        print(f"{'='*60}")

        result = (
            CodegenCrew()
            .crew()
            .kickoff(inputs={
                "design": self.state.design.model_dump_json(),
            })
        )
        self.state.code = result.pydantic
        print(f"生成完成: {len(self.state.code.files)} 个文件")

    # ── 阶段 5: 代码审核 ──────────────────────────────────────────

    @listen(generate_code)
    def review_code(self):
        print(f"\n{'='*60}")
        print(f"[阶段 5] 代码审核")
        print(f"{'='*60}")

        code_text = "\n\n".join(
            f"// === {f.file_name} ===\n{f.content}"
            for f in self.state.code.files
        )

        result = (
            ReviewCrew()
            .crew()
            .kickoff(inputs={
                "requirement": self.state.raw_requirement,
                "task_list": self.state.requirements.model_dump_json(),
                "design": self.state.design.model_dump_json(),
                "code": code_text,
            })
        )
        self.state.review = result.pydantic
        print(f"审核结论: {self.state.review.verdict}")
        if self.state.review.issues:
            for issue in self.state.review.issues:
                print(f"  [{issue.severity}] {issue.file_name}: {issue.description}")

    # ── 路由: 审核通过 → 交付 / 不通过 → 打回设计 ─────────────────

    @router(review_code)
    def check_review(self):
        if self.state.review.verdict == "pass":
            return "deliver"
        if self.state.revision_count >= self.state.max_revisions:
            print(f"\n已达最大修订次数 ({self.state.max_revisions})，强制交付。")
            return "deliver"
        self.state.revision_count += 1
        print(f"\n审核未通过，打回重做设计（第 {self.state.revision_count} 次）...")
        return "revise"

    # ── 打回: 重新进入设计阶段 ────────────────────────────────────

    @listen("revise")
    def redesign(self):
        self.design_modules()

    # ── 交付: 写入文件 ────────────────────────────────────────────

    @listen("deliver")
    def deliver_code(self):
        print(f"\n{'='*60}")
        print(f"[交付] 输出代码文件")
        print(f"{'='*60}")

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        for f in self.state.code.files:
            path = output_dir / f.file_name
            path.write_text(f.content, encoding="utf-8")
            print(f"  已写入: {path}")

        # 写入审核报告
        report = {
            "verdict": self.state.review.verdict,
            "revision_count": self.state.revision_count,
            "issues": [i.model_dump() for i in self.state.review.issues],
            "summary": self.state.review.summary,
        }
        report_path = output_dir / "review_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  已写入: {report_path}")

        print(f"\n交付完成！共 {len(self.state.code.files)} 个代码文件，"
              f"经过 {self.state.revision_count} 次修订。")


# ── 入口函数 ──────────────────────────────────────────────────────

def kickoff():
    """命令行入口：从 stdin 或参数读取需求。"""
    import sys

    if len(sys.argv) > 1:
        requirement = sys.argv[1]
    else:
        print("请输入需求文本（输入完成后按 Ctrl+D）：")
        requirement = sys.stdin.read().strip()

    if not requirement:
        print("错误：需求文本为空。")
        sys.exit(1)

    flow = EmbeddedDevFlow()
    flow.kickoff(inputs={"raw_requirement": requirement})


def plot():
    """可视化 Flow 结构。"""
    flow = EmbeddedDevFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
