from ast import List
from deepagents import CompiledSubAgent
from langchain.agents import AgentState, create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import SystemMessage

from backend.src.agent.agent import TaskContext, checkpointer
from backend.src.agent.tools.github.issues_graphql import issues_tools
from backend.src.agent.tools.github.comments_graphql import comments_tools
from backend.src.agent.tools.github.labels_graphql import labels_tools

GITHUB_SYSTEM_PROMPT = SystemMessage(
    content="""
You are a helpful assistant that can investigate, create, modify, and delete GitHub issues and Comments.
"""
)


class IssueState(AgentState):
    issue_number: int
    title: str
    body: str
    state: str
    created_at: str
    updated_at: str
    comments_count: int
    milestone: dict
    labels: List[str]
    assignees: List[str]
    repository: str
    linked_branches: List[dict]
    closed_by_pull_requests: List[dict]
    tracked_issues: dict
    tracked_in_issues: dict
    sub_issues: dict
    parent_issue: dict


GRAPHQL_URL = "https://api.github.com/graphql"


def get_issue_agent():
    return create_agent(
        name="issue_agent",
        tools=issues_tools,
        interrupt_before={
            "get_issue": False,
            "list_repository_issues": False,
            "search_issues": False,
            "create_issue": True,
            "update_issue": True,
        }
    )


def get_comment_agent():
    return create_agent(
        name="comment_agent",
        tools=comments_tools,
        interrupt_before={
            "get_issue_comments": False,
            "add_comment_to_issue": True,
            "update_comment": True,
            "delete_comment": True,
        }
    )


def get_label_agent():
    return create_agent(
        name="label_agent",
        tools=labels_tools,
        interrupt_before={
            "list_issue_labels": False,
            "add_label_to_issue": True,
            "clear_labels_from_issue": True,
            "remove_label_from_issue": True,
            "get_repository_labels": False,
            "create_label": True,
            "get_label_by_name": False,
            "update_label": True,
            "delete_label": True,
        }
    )


github_sub_agents = [
    CompiledSubAgent(
        name="issue_agent",
        tools=issues_tools,
        runnable=get_issue_agent(),
    ),
    CompiledSubAgent(
        name="comment_agent",
        tools=comments_tools,
        runnable=get_comment_agent(),
    ),
    CompiledSubAgent(
        name="label_agent",
        tools=labels_tools,
        runnable=get_label_agent(),
    ),
]