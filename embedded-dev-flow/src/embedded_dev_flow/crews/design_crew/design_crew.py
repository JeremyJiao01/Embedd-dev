from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from embedded_dev_flow.models import DesignOutput
from embedded_dev_flow.tools import (
    CodeSearchTool,
    GetSnippetTool,
    ListAPITool,
    QueryGraphTool,
)


@CrewBase
class DesignCrew:
    """接口设计 Crew：选择已有接口并设计模块伪代码。"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def interface_selector(self) -> Agent:
        return Agent(
            config=self.agents_config["interface_selector"],
            tools=[ListAPITool()],
        )

    @agent
    def logic_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["logic_designer"],
            tools=[GetSnippetTool(), QueryGraphTool(), CodeSearchTool()],
        )

    @task
    def select_interfaces(self) -> Task:
        return Task(config=self.tasks_config["select_interfaces"])

    @task
    def design_modules(self) -> Task:
        return Task(
            config=self.tasks_config["design_modules"],
            output_pydantic=DesignOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
