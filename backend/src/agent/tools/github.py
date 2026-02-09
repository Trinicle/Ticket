import httpx
from datetime import date, timedelta
from typing import List, Optional
from langchain.agents import AgentState
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import SystemMessage

from backend.src.agent.agent import TaskContext


GITHUB_SYSTEM_PROMPT = SystemMessage(
    content="""
You are a helpful assistant that can investigate, create, modify, and delete GitHub issues and Comments.
"""
)


class IssueState(AgentState):
    """Context about a GitHub issue for RAG"""

    issue_number: int
    title: str
    body: str
    state: str
    created_at: str
    updated_at: str
    comments_count: int
    labels: List[str]
    assignees: List[str]
    repository: str


BASE_URL = "https://api.github.com"


@tool
async def search_issues(
    runtime: ToolRuntime[TaskContext],
    title: Optional[str] = None,
    body: Optional[str] = None,
    days_ago: Optional[int] = 30,
):
    """Searches for issues based on the title and body

    Args:
        title: Optional search terms to look for in the title
        body: Optional search terms to look for in the body
        days_ago: Optional number of days ago to search for issues
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    query = [
        f"repo:{owner}/{repository}",
        f"created:>{date.today() - timedelta(days=days_ago)}",
    ]

    if title:
        query.append(f"title:{title}")

    if body:
        query.append(f"body:{body}")

    params = {
        "q": " ".join(query),
        "per_page": 15,
        "page": 1,
    }

    async with httpx.AsyncClient(headers=get_default_headers()) as client:
        response = await client.get(f"{BASE_URL}/search/issues", params=params)
        response.raise_for_status()
        data = response.json()

        simplified_issues = []

        for issue in data.get("items", []):
            simplified_issue = get_issue_dict(issue)
            simplified_issues.append(simplified_issue)

        return {
            "total_count": data.get("total_count"),
            "issues": simplified_issues,
        }


@tool
def create_issue(runtime: ToolRuntime[TaskContext]):
    pass


@tool
def update_issue(runtime: ToolRuntime[TaskContext]):
    pass


@tool
async def get_issue(issue_number: int, runtime: ToolRuntime[TaskContext]):
    """Gets the information about a specific issue

    Args:
        issue_number: The number of the issue to get
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    async with httpx.AsyncClient(headers=get_default_headers()) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}"
        )
        response.raise_for_status()
        data = response.json()

        return get_issue_dict(data)


@tool
def get_issue_comments(runtime: ToolRuntime[TaskContext]):
    pass


@tool
def add_comment(runtime: ToolRuntime[TaskContext]):
    pass


@tool
def update_comment(runtime: ToolRuntime[TaskContext]):
    pass


@tool
def delete_comment(runtime: ToolRuntime[TaskContext]):
    pass


def get_issue_dict(issue: dict) -> dict:
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "body": (
            issue["body"][:500] + "..."
            if len(issue.get("body", "")) > 500
            else issue.get("body", "")
        ),
        "state": issue.get("state"),
        "url": issue.get("html_url"),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "comments_count": issue.get("comments"),
        "labels": [label.get("name") for label in issue.get("labels", [])],
        "author": issue.get("user", {}).get("login"),
        "assignee": (
            issue.get("assignee", {}).get("login") if issue.get("assignee") else None
        ),
    }


def get_default_headers():
    return {
        "Accept": "application/vnd.github.v3+json",
    }


def get_auth_headers(runtime: ToolRuntime[TaskContext]):
    return {
        "Authorization": f"Bearer {get_token(runtime)}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


github_tools = []
