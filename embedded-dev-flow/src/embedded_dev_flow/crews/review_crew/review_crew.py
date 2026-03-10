from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from embedded_dev_flow.models import ReviewOutput
from embedded_dev_flow.tools import CodeSearchTool


@CrewBase
class ReviewCrew:
    """代码审核 Crew：审查生成的代码是否符合需求和规范。"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def code_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["code_reviewer"],
            tools=[CodeSearchTool()],
        )

    @task
    def review_code(self) -> Task:
        return Task(
            config=self.tasks_config["review_code"],
            output_pydantic=ReviewOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
