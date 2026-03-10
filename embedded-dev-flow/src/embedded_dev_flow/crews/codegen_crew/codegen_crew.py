from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from embedded_dev_flow.models import CodegenOutput
from embedded_dev_flow.tools import GetSnippetTool


@CrewBase
class CodegenCrew:
    """代码生成 Crew：根据设计文档生成 C 语言源代码。"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def c_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["c_developer"],
            tools=[GetSnippetTool()],
        )

    @task
    def generate_code(self) -> Task:
        return Task(
            config=self.tasks_config["generate_code"],
            output_pydantic=CodegenOutput,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
