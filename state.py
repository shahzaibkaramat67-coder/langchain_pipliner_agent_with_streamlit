from pydantic import BaseModel, Field


class AgentHistory(BaseModel):
    agent: str
    input: str
    output: str


class Plan(BaseModel):
    tool: str
    tool_input: list


class State(BaseModel):
    search_result: list = Field(default_factory=list)
    reserach_result: list = Field(default_factory=list)
    evaluator: dict | None = None
    user_input: str
    plan: Plan | None = None
    result: str | list = ""
    history: list[AgentHistory] = Field(default_factory=list)
