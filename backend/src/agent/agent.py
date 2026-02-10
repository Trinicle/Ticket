from dataclasses import dataclass
import sqlite3
from typing import Callable
import httpx
import json
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRequest,
    ModelResponse,
    ToolCallRequest,
    wrap_model_call,
    wrap_tool_call,
)
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langgraph.checkpoint.sqlite import SQLiteSaver
from backend.src.agent.tools.github import (
    github_tools,
    GITHUB_SYSTEM_PROMPT,
    IssueState,
)

checkpointer = SQLiteSaver(sqlite3.connect("backend/tool-approval.db"))


@dataclass
class TaskContext:
    platform: str
    token: str
    owner: str
    repository: str


@wrap_tool_call
def auth_guard_middleware(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    tool_name = request.tool.name
    platform = request.runtime.context.get("platform")

    try:
        return handler(request)
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code

        try:
            error_data = e.response.json()
            error_message = error_data.get("message", "Unknown error")
        except (json.JSONDecodeError, AttributeError):
            error_message = f"HTTP {status_code} error"

        if status_code == 401:
            return ToolMessage(
                content=f"Authentication required for {tool_name}. "
                f"The operation requires a valid {platform} token. "
                f"Error: {error_message}"
            )

        elif status_code == 404:
            return ToolMessage(
                content=f"Resource not found for {tool_name}. "
                f"This could mean: 1) The repository/issue doesn't exist, "
                f"2) The repository is private and you don't have access, or "
                f"3) You need authentication to view this resource. "
                f"Error: {error_message}"
            )
        else:
            return ToolMessage(
                content=f"HTTP {status_code} error for {tool_name}: {error_message}"
            )
    except Exception as e:
        print(f"Unexpected error in tool {tool_name}: {e}")
        return ToolMessage(
            content=f"Unexpected error occurred while executing {tool_name}: {str(e)}"
        )


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
        model="openai:gpt-4o-mini",
        system_prompt=GITHUB_SYSTEM_PROMPT,
        tools=github_tools,
        state_schema=IssueState,
        context_schema=TaskContext,
        middleware=[change_available_tools, auth_guard_middleware],
        checkpointer=checkpointer,
    )
