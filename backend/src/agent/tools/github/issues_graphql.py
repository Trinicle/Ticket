from typing import List, Optional
from langchain.tools import ToolRuntime, tool

from backend.src.agent.agent import TaskContext
from backend.src.agent.tools.github.graphql_utils import (
    execute_graphql_query,
    ISSUE_FRAGMENT,
)


@tool
async def get_issue_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
):
    """Gets detailed information about a specific issue using GraphQL
    
    Args:
        issue_number: The number of the issue to get
    """
    owner = runtime.context.owner
    repository = runtime.context.repository
    
    query = f"""
    query GetIssue($owner: String!, $name: String!, $number: Int!) {{
      repository(owner: $owner, name: $name) {{
        issue(number: $number) {{
          ...IssueFields
        }}
      }}
    }}
    
    {ISSUE_FRAGMENT}
    """
    
    variables = {
        "owner": owner,
        "name": repository,
        "number": issue_number,
    }
    
    data = await execute_graphql_query(runtime, query, variables)
    issue = data["repository"]["issue"]
    
    if not issue:
        return {"error": f"Issue #{issue_number} not found"}
    
    return format_issue_graphql(issue)


@tool
async def list_repository_issues_graphql(
    runtime: ToolRuntime[TaskContext],
    states: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    assignee: Optional[str] = None,
    first: int = 20,
    after: Optional[str] = None,
):
    """Lists issues in a repository using GraphQL with cursor-based pagination
    
    Args:
        states: List of issue states ('OPEN', 'CLOSED')
        labels: List of label names to filter by
        assignee: Username of assignee to filter by
        first: Number of issues to fetch (max 100)
        after: Cursor for pagination
    """
    owner = runtime.context.owner
    repository = runtime.context.repository
    
    # Build filter conditions
    filter_conditions = []
    if states:
        state_list = ", ".join([f'"{state}"' for state in states])
        filter_conditions.append(f"states: [{state_list}]")
    if labels:
        label_list = ", ".join([f'"{label}"' for label in labels])
        filter_conditions.append(f"labels: [{label_list}]")
    if assignee:
        filter_conditions.append(f'assignee: "{assignee}"')
    
    filter_string = ", ".join(filter_conditions)
    if filter_string:
        filter_string = f"filterBy: {{{filter_string}}}"
    
    query = f"""
    query ListIssues($owner: String!, $name: String!, $first: Int!, $after: String) {{
      repository(owner: $owner, name: $name) {{
        issues(first: $first, after: $after{', ' + filter_string if filter_string else ''}) {{
          totalCount
          pageInfo {{
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
          }}
          nodes {{
            ...IssueFields
          }}
        }}
      }}
    }}
    
    {ISSUE_FRAGMENT}
    """
    
    variables = {
        "owner": owner,
        "name": repository,
        "first": min(first, 100),
    }
    if after:
        variables["after"] = after
    
    data = await execute_graphql_query(runtime, query, variables)
    issues_data = data["repository"]["issues"]
    
    return {
        "totalCount": issues_data["totalCount"],
        "pageInfo": issues_data["pageInfo"],
        "issues": [format_issue_graphql(issue) for issue in issues_data["nodes"]],
    }


@tool
async def search_issues_graphql(
    runtime: ToolRuntime[TaskContext],
    query_string: str,
    first: int = 20,
    after: Optional[str] = None,
):
    """Search for issues using GraphQL
    
    Args:
        query_string: GitHub search query (e.g., "repo:owner/name is:issue label:bug")
        first: Number of results to fetch (max 100)
        after: Cursor for pagination
    """
    query = f"""
    query SearchIssues($query: String!, $first: Int!, $after: String) {{
      search(query: $query, type: ISSUE, first: $first, after: $after) {{
        issueCount
        pageInfo {{
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }}
        nodes {{
          ... on Issue {{
            ...IssueFields
            repository {{
              name
              owner {{
                login
              }}
            }}
          }}
        }}
      }}
    }}
    
    {ISSUE_FRAGMENT}
    """
    
    variables = {
        "query": query_string,
        "first": min(first, 100),
    }
    if after:
        variables["after"] = after
    
    data = await execute_graphql_query(runtime, query, variables)
    search_data = data["search"]
    
    return {
        "totalCount": search_data["issueCount"],
        "pageInfo": search_data["pageInfo"],
        "issues": [format_issue_graphql(issue) for issue in search_data["nodes"]],
    }


@tool
async def create_issue_graphql(
    runtime: ToolRuntime[TaskContext],
    title: str,
    body: Optional[str] = None,
    assignee_ids: Optional[List[str]] = None,
    label_ids: Optional[List[str]] = None,
    milestone_id: Optional[str] = None,
):
    """Creates a new issue using GraphQL
    
    Args:
        title: The title of the issue
        body: The body content of the issue
        assignee_ids: List of user node IDs to assign
        label_ids: List of label node IDs to apply
        milestone_id: Milestone node ID to associate
    """
    owner = runtime.context.owner
    repository = runtime.context.repository
    
    # First, get the repository ID
    repo_query = """
    query GetRepositoryId($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
      }
    }
    """
    
    repo_data = await execute_graphql_query(runtime, repo_query, {
        "owner": owner,
        "name": repository,
    })
    
    repository_id = repo_data["repository"]["id"]
    
    # Build the input object
    input_fields = [
        f'repositoryId: "{repository_id}"',
        f'title: "{title}"',
    ]
    
    if body:
        input_fields.append(f'body: "{body}"')
    if assignee_ids:
        assignee_list = ", ".join([f'"{aid}"' for aid in assignee_ids])
        input_fields.append(f'assigneeIds: [{assignee_list}]')
    if label_ids:
        label_list = ", ".join([f'"{lid}"' for lid in label_ids])
        input_fields.append(f'labelIds: [{label_list}]')
    if milestone_id:
        input_fields.append(f'milestoneId: "{milestone_id}"')
    
    input_string = "{" + ", ".join(input_fields) + "}"
    
    mutation = f"""
    mutation CreateIssue {{
      createIssue(input: {input_string}) {{
        issue {{
          ...IssueFields
        }}
      }}
    }}
    
    {ISSUE_FRAGMENT}
    """
    
    data = await execute_graphql_query(runtime, mutation)
    issue = data["createIssue"]["issue"]
    
    return format_issue_graphql(issue)


@tool
async def update_issue_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,
    assignee_ids: Optional[List[str]] = None,
    label_ids: Optional[List[str]] = None,
    milestone_id: Optional[str] = None,
):
    """Updates an existing issue using GraphQL
    
    Args:
        issue_number: The number of the issue to update
        title: New title for the issue
        body: New body content for the issue
        state: New state ('OPEN' or 'CLOSED')
        assignee_ids: List of user node IDs to assign (replaces current)
        label_ids: List of label node IDs to apply (replaces current)
        milestone_id: Milestone node ID to associate
    """
    owner = runtime.context.owner
    repository = runtime.context.repository
    
    # First, get the issue ID
    issue_query = """
    query GetIssueId($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        issue(number: $number) {
          id
        }
      }
    }
    """
    
    issue_data = await execute_graphql_query(runtime, issue_query, {
        "owner": owner,
        "name": repository,
        "number": issue_number,
    })
    
    issue_id = issue_data["repository"]["issue"]["id"]
    
    # Build the input object
    input_fields = [f'id: "{issue_id}"']
    
    if title is not None:
        input_fields.append(f'title: "{title}"')
    if body is not None:
        input_fields.append(f'body: "{body}"')
    if state is not None:
        input_fields.append(f'state: {state}')
    if assignee_ids is not None:
        assignee_list = ", ".join([f'"{aid}"' for aid in assignee_ids])
        input_fields.append(f'assigneeIds: [{assignee_list}]')
    if label_ids is not None:
        label_list = ", ".join([f'"{lid}"' for lid in label_ids])
        input_fields.append(f'labelIds: [{label_list}]')
    if milestone_id is not None:
        input_fields.append(f'milestoneId: "{milestone_id}"')
    
    input_string = "{" + ", ".join(input_fields) + "}"
    
    mutation = f"""
    mutation UpdateIssue {{
      updateIssue(input: {input_string}) {{
        issue {{
          ...IssueFields
        }}
      }}
    }}
    
    {ISSUE_FRAGMENT}
    """
    
    data = await execute_graphql_query(runtime, mutation)
    issue = data["updateIssue"]["issue"]
    
    return format_issue_graphql(issue)


def format_issue_graphql(issue: dict) -> dict:
    """Convert GraphQL issue response to simplified dictionary"""
    return {
        "id": issue.get("id"),
        "number": issue.get("number"),
        "title": issue.get("title"),
        "body": issue.get("body", ""),
        "state": issue.get("state"),
        "url": issue.get("url"),
        "created_at": issue.get("createdAt"),
        "updated_at": issue.get("updatedAt"),
        "closed_at": issue.get("closedAt"),
        "author": issue.get("author", {}).get("login") if issue.get("author") else None,
        "assignees": [assignee["login"] for assignee in issue.get("assignees", {}).get("nodes", [])],
        "labels": [
            {
                "id": label["id"],
                "name": label["name"],
                "description": label["description"],
                "color": label["color"],
            }
            for label in issue.get("labels", {}).get("nodes", [])
        ],
        "milestone": (
            {
                "number": issue.get("milestone", {}).get("number"),
                "title": issue.get("milestone", {}).get("title"),
                "state": issue.get("milestone", {}).get("state"),
            }
            if issue.get("milestone")
            else None
        ),
        "comments_count": issue.get("comments", {}).get("totalCount", 0),
        "locked": issue.get("locked", False),
        "lock_reason": issue.get("activeLockReason"),
    }