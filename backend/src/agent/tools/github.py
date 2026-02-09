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


# =============================================================================
# ISSUE MANAGEMENT TOOLS
# =============================================================================


@tool
async def search_issues(
    owner: Optional[str] = None,
    repository: Optional[str] = None,
    title: Optional[str] = None,
    body: Optional[str] = None,
    days_ago: Optional[int] = 30,
):
    """Searches for issues based on the title and body

    Args:
        owner: The owner of the repository
        repository: The name of the repository
        title: Optional search terms to look for in the title
        body: Optional search terms to look for in the body
        days_ago: Optional number of days ago to search for issues
    """
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
async def list_repository_issues(
    runtime: ToolRuntime[TaskContext],
    milestone: Optional[str] = None,
    state: str = "open",
    assignee: Optional[str] = None,
    creator: Optional[str] = None,
    mentioned: Optional[str] = None,
    labels: Optional[str] = None,
    sort: str = "created",
    direction: str = "desc",
    per_page: int = 30,
    page: int = 1,
):
    """Lists issues in a repository

    Args:
        milestone: Milestone number, '*' for any milestone, 'none' for no milestone
        state: State of issues to return ('open', 'closed', 'all')
        assignee: Username of assignee, 'none' for unassigned, '*' for any assignee
        creator: The user that created the issue
        mentioned: A user that's mentioned in the issue
        labels: Comma-separated list of label names (e.g., 'bug,ui,@high')
        sort: What to sort results by ('created', 'updated', 'comments')
        direction: Direction to sort ('asc', 'desc')
        per_page: Number of results per page (max 100)
        page: Page number of results to fetch
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    params = {
        "state": state,
        "sort": sort,
        "direction": direction,
        "per_page": min(per_page, 100),
        "page": page,
    }

    if milestone:
        params["milestone"] = milestone
    if assignee:
        params["assignee"] = assignee
    if creator:
        params["creator"] = creator
    if mentioned:
        params["mentioned"] = mentioned
    if labels:
        params["labels"] = labels

    async with httpx.AsyncClient(headers=get_default_headers()) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repository}/issues", params=params
        )
        response.raise_for_status()
        data = response.json()

        issues = []
        for issue in data:
            issues.append(get_issue_dict(issue))

        return {"issues": issues}


@tool
async def list_assigned_issues(
    runtime: ToolRuntime[TaskContext],
    filter: str = "assigned",
    state: str = "open",
    labels: Optional[str] = None,
    sort: str = "created",
    direction: str = "desc",
    per_page: int = 30,
    page: int = 1,
):
    """Lists issues assigned to the authenticated user across all repositories

    Args:
        filter: Filter type ('assigned', 'created', 'mentioned', 'subscribed', 'repos', 'all')
        state: State of issues to return ('open', 'closed', 'all')
        labels: Comma-separated list of label names
        sort: What to sort results by ('created', 'updated', 'comments')
        direction: Direction to sort ('asc', 'desc')
        per_page: Number of results per page (max 100)
        page: Page number of results to fetch
    """
    params = {
        "filter": filter,
        "state": state,
        "sort": sort,
        "direction": direction,
        "per_page": min(per_page, 100),
        "page": page,
    }

    if labels:
        params["labels"] = labels

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.get(f"{BASE_URL}/issues", params=params)
        response.raise_for_status()
        data = response.json()

        issues = []
        for issue in data:
            issues.append(get_issue_dict(issue))

        return {"issues": issues}


@tool
async def create_issue(
    runtime: ToolRuntime[TaskContext],
    title: str,
    body: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    milestone: Optional[int] = None,
    labels: Optional[List[str]] = None,
):
    """Creates a new issue in the repository

    Args:
        title: The title of the issue (required)
        body: The contents of the issue
        assignees: List of usernames to assign to this issue
        milestone: The number of the milestone to associate this issue with
        labels: List of labels to associate with this issue
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {"title": title}

    if body:
        payload["body"] = body
    if assignees:
        payload["assignees"] = assignees
    if milestone:
        payload["milestone"] = milestone
    if labels:
        payload["labels"] = labels

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.post(
            f"{BASE_URL}/repos/{owner}/{repository}/issues", json=payload
        )
        response.raise_for_status()
        data = response.json()

        return get_issue_dict(data)


@tool
async def update_issue(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,
    state_reason: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    milestone: Optional[int] = None,
    labels: Optional[List[str]] = None,
):
    """Updates an existing issue

    Args:
        issue_number: The number that identifies the issue
        title: The title of the issue
        body: The contents of the issue
        state: The state of the issue ('open' or 'closed')
        state_reason: The reason for the state change ('completed', 'not_planned', 'duplicate', 'reopened')
        assignees: List of usernames to assign to this issue (replaces current assignees)
        milestone: The number of the milestone to associate this issue with (use None to remove)
        labels: List of labels to associate with this issue (replaces current labels)
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {}

    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if state is not None:
        payload["state"] = state
    if state_reason is not None:
        payload["state_reason"] = state_reason
    if assignees is not None:
        payload["assignees"] = assignees
    if milestone is not None:
        payload["milestone"] = milestone
    if labels is not None:
        payload["labels"] = labels

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.patch(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}", json=payload
        )
        response.raise_for_status()
        data = response.json()

        return get_issue_dict(data)


@tool
async def lock_issue(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    lock_reason: Optional[str] = None,
):
    """Locks an issue's conversation

    Args:
        issue_number: The number that identifies the issue
        lock_reason: Reason for locking ('off-topic', 'too heated', 'resolved', 'spam')
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {}
    if lock_reason:
        payload["lock_reason"] = lock_reason

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.put(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/lock",
            json=payload,
        )
        response.raise_for_status()

        return {"message": f"Issue {issue_number} locked successfully"}


@tool
async def unlock_issue(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
):
    """Unlocks an issue's conversation

    Args:
        issue_number: The number that identifies the issue
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.delete(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/lock"
        )
        response.raise_for_status()

        return {"message": f"Issue {issue_number} unlocked successfully"}


# =============================================================================
# COMMENT MANAGEMENT TOOLS
# =============================================================================


@tool
async def get_issue_comments(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    per_page: int = 30,
    page: int = 1,
):
    """Gets comments for a specific issue

    Args:
        issue_number: The number of the issue to get comments for
        per_page: The number of results per page (max 100)
        page: The page number of the results to fetch
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    params = {
        "per_page": min(per_page, 100),
        "page": page,
    }

    async with httpx.AsyncClient(headers=get_default_headers()) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/comments",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        comments = []
        for comment in data:
            comments.append(get_comment_dict(comment))

        return {"comments": comments}


@tool
async def add_comment(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    body: str,
):
    """Adds a comment to an issue

    Args:
        issue_number: The number of the issue to comment on
        body: The contents of the comment
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {"body": body}

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.post(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/comments",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return get_comment_dict(data)


@tool
async def update_comment(
    runtime: ToolRuntime[TaskContext],
    comment_id: int,
    body: str,
):
    """Updates a comment on an issue

    Args:
        comment_id: The unique identifier of the comment
        body: The updated contents of the comment
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {"body": body}

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.patch(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/comments/{comment_id}",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return get_comment_dict(data)


@tool
async def delete_comment(
    runtime: ToolRuntime[TaskContext],
    comment_id: int,
):
    """Deletes a comment from an issue

    Args:
        comment_id: The unique identifier of the comment to delete
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.delete(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/comments/{comment_id}"
        )
        response.raise_for_status()

        return {"message": f"Comment {comment_id} deleted successfully"}


# =============================================================================
# LABEL MANAGEMENT TOOLS
# =============================================================================


@tool
async def list_issue_labels(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    per_page: int = 30,
    page: int = 1,
):
    """Lists all labels for an issue

    Args:
        issue_number: The number that identifies the issue
        per_page: Number of results per page (max 100)
        page: Page number of results to fetch
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    params = {
        "per_page": min(per_page, 100),
        "page": page,
    }

    async with httpx.AsyncClient(headers=get_default_headers()) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/labels",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

        labels = []
        for label in data:
            labels.append(get_label_dict(label))

        return {"labels": labels}


@tool
async def add_labels_to_issue(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    labels: List[str],
):
    """Adds labels to an issue (keeps existing labels)

    Args:
        issue_number: The number that identifies the issue
        labels: List of label names to add to the issue
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {"labels": labels}

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.post(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/labels",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        labels_result = []
        for label in data:
            labels_result.append(get_label_dict(label))

        return {"labels": labels_result}


@tool
async def set_issue_labels(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    labels: List[str],
):
    """Sets labels for an issue (replaces all existing labels)

    Args:
        issue_number: The number that identifies the issue
        labels: List of label names to set for the issue (replaces existing)
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {"labels": labels}

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.put(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/labels",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        labels_result = []
        for label in data:
            labels_result.append(get_label_dict(label))

        return {"labels": labels_result}


@tool
async def remove_all_labels_from_issue(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
):
    """Removes all labels from an issue

    Args:
        issue_number: The number that identifies the issue
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.delete(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/labels"
        )
        response.raise_for_status()

        return {"message": f"All labels removed from issue {issue_number}"}


@tool
async def remove_label_from_issue(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    label_name: str,
):
    """Removes a specific label from an issue

    Args:
        issue_number: The number that identifies the issue
        label_name: The name of the label to remove
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.delete(
            f"{BASE_URL}/repos/{owner}/{repository}/issues/{issue_number}/labels/{label_name}"
        )
        response.raise_for_status()
        data = response.json()

        labels_result = []
        for label in data:
            labels_result.append(get_label_dict(label))

        return {"labels": labels_result}


@tool
async def list_repository_labels(
    runtime: ToolRuntime[TaskContext],
    per_page: int = 30,
    page: int = 1,
):
    """Lists all labels for a repository

    Args:
        per_page: Number of results per page (max 100)
        page: Page number of results to fetch
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    params = {
        "per_page": min(per_page, 100),
        "page": page,
    }

    async with httpx.AsyncClient(headers=get_default_headers()) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repository}/labels", params=params
        )
        response.raise_for_status()
        data = response.json()

        labels = []
        for label in data:
            labels.append(get_label_dict(label))

        return {"labels": labels}


@tool
async def create_label(
    runtime: ToolRuntime[TaskContext],
    name: str,
    color: str,
    description: Optional[str] = None,
):
    """Creates a new label for the repository

    Args:
        name: The name of the label (can include emoji)
        color: Hexadecimal color code without the leading # (e.g., 'f29513')
        description: Short description of the label (max 100 characters)
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {
        "name": name,
        "color": color,
    }

    if description:
        payload["description"] = description

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.post(
            f"{BASE_URL}/repos/{owner}/{repository}/labels", json=payload
        )
        response.raise_for_status()
        data = response.json()

        return get_label_dict(data)


@tool
async def get_label(
    runtime: ToolRuntime[TaskContext],
    label_name: str,
):
    """Gets a label by name

    Args:
        label_name: The name of the label to retrieve
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    async with httpx.AsyncClient(headers=get_default_headers()) as client:
        response = await client.get(
            f"{BASE_URL}/repos/{owner}/{repository}/labels/{label_name}"
        )
        response.raise_for_status()
        data = response.json()

        return get_label_dict(data)


@tool
async def update_label(
    runtime: ToolRuntime[TaskContext],
    label_name: str,
    new_name: Optional[str] = None,
    color: Optional[str] = None,
    description: Optional[str] = None,
):
    """Updates a label

    Args:
        label_name: The current name of the label to update
        new_name: The new name for the label (can include emoji)
        color: New hexadecimal color code without the leading #
        description: New description for the label (max 100 characters)
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    payload = {}

    if new_name is not None:
        payload["new_name"] = new_name
    if color is not None:
        payload["color"] = color
    if description is not None:
        payload["description"] = description

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.patch(
            f"{BASE_URL}/repos/{owner}/{repository}/labels/{label_name}", json=payload
        )
        response.raise_for_status()
        data = response.json()

        return get_label_dict(data)


@tool
async def delete_label(
    runtime: ToolRuntime[TaskContext],
    label_name: str,
):
    """Deletes a label from the repository

    Args:
        label_name: The name of the label to delete
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    async with httpx.AsyncClient(headers=get_auth_headers(runtime)) as client:
        response = await client.delete(
            f"{BASE_URL}/repos/{owner}/{repository}/labels/{label_name}"
        )
        response.raise_for_status()

        return {"message": f"Label '{label_name}' deleted successfully"}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_issue_dict(issue: dict) -> dict:
    """Converts a GitHub issue API response to a simplified dictionary"""
    return {
        "id": issue.get("id"),
        "number": issue.get("number"),
        "title": issue.get("title"),
        "body": (
            issue["body"][:500] + "..."
            if len(issue.get("body", "")) > 500
            else issue.get("body", "")
        ),
        "state": issue.get("state"),
        "state_reason": issue.get("state_reason"),
        "url": issue.get("html_url"),
        "created_at": issue.get("created_at"),
        "updated_at": issue.get("updated_at"),
        "closed_at": issue.get("closed_at"),
        "comments_count": issue.get("comments"),
        "labels": [label.get("name") for label in issue.get("labels", [])],
        "author": issue.get("user", {}).get("login"),
        "assignee": (
            issue.get("assignee", {}).get("login") if issue.get("assignee") else None
        ),
        "assignees": [assignee.get("login") for assignee in issue.get("assignees", [])],
        "milestone": (
            {
                "number": issue.get("milestone", {}).get("number"),
                "title": issue.get("milestone", {}).get("title"),
                "state": issue.get("milestone", {}).get("state"),
            }
            if issue.get("milestone")
            else None
        ),
        "locked": issue.get("locked", False),
        "lock_reason": issue.get("active_lock_reason"),
        "repository": (
            issue.get("repository", {}).get("full_name")
            if issue.get("repository")
            else None
        ),
    }


def get_comment_dict(comment: dict) -> dict:
    """Converts a GitHub comment API response to a simplified dictionary"""
    return {
        "id": comment.get("id"),
        "body": comment.get("body", ""),
        "author": comment.get("user", {}).get("login"),
        "created_at": comment.get("created_at"),
        "updated_at": comment.get("updated_at"),
        "url": comment.get("html_url"),
    }


def get_label_dict(label: dict) -> dict:
    """Converts a GitHub label API response to a simplified dictionary"""
    return {
        "id": label.get("id"),
        "name": label.get("name"),
        "description": label.get("description"),
        "color": label.get("color"),
        "default": label.get("default", False),
        "url": label.get("url"),
    }


def get_default_headers():
    return {
        "Accept": "application/vnd.github.v3+json",
    }


def get_auth_headers(runtime: ToolRuntime[TaskContext]):
    return {
        "Authorization": f"Bearer {runtime.context.token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


github_tools = [
    # Issue Management
    search_issues,
    create_issue,
    update_issue,
    get_issue,
    list_repository_issues,
    list_assigned_issues,
    lock_issue,
    unlock_issue,
    # Comment Management
    get_issue_comments,
    add_comment,
    update_comment,
    delete_comment,
    # Label Management
    list_issue_labels,
    add_labels_to_issue,
    set_issue_labels,
    remove_all_labels_from_issue,
    remove_label_from_issue,
    list_repository_labels,
    create_label,
    get_label,
    update_label,
    delete_label,
]
