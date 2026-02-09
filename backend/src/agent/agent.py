from dataclasses import dataclass
from typing import Callable
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langgraph.checkpoint.memory import InMemorySaver
from backend.src.agent.tools.github import (
    github_tools,
    GITHUB_SYSTEM_PROMPT,
    IssueState,
)


@dataclass
class TaskContext:
    platform: str
    token: str
    owner: str
    repository: str


@wrap_model_call
def change_available_tools(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    system_prompt = request.runtime.context.get("system_prompt")
    platform = request.runtime.context.get("platform")
    state = request.runtime.state
    tools = request.tools

    if platform == "github":
        system_prompt = GITHUB_SYSTEM_PROMPT
        tools = github_tools
        state = IssueState

    return handler(
        request.override(tools=tools, system_message=system_prompt, state=state)
    )


def create_rag_agent():
    return create_agent(
        model="gpt-4o-mini",
        system_prompt=GITHUB_SYSTEM_PROMPT,
        tools=github_tools,
        state_schema=IssueState,
        context_schema=TaskContext,
        middleware=[change_available_tools],
        checkpointer=InMemorySaver(),
    )
