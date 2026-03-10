from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from embedded_dev_flow.models import RequirementsOutput
from embedded_dev_flow.tools import CodeSearchTool


@CrewBase
class RequirementsCrew:
    """需求拆解 Crew：将原始需求拆解为结构化子任务列表。"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def technical_scout(self) -> Agent:
        return Agent(
            config=self.agents_config["technical_scout"],
            tools=[CodeSearchTool()],
        )

    @agent
    def requirements_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["requirements_analyst"],
        )

    @task
    def scout_existing_code(self) -> Task:
        return Task(
            config=self.tasks_config["scout_existing_code"],
        )

    @task
    def decompose_requirements(self) -> Task:
        return Task(
            config=self.tasks_config["decompose_requirements"],
            output_pydantic=RequirementsOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
