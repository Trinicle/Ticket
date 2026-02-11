import httpx
import json
from typing import Dict, Any, List, Optional
from backend.src.agent.agent import TaskContext
from langchain.tools import ToolRuntime

GRAPHQL_URL = "https://api.github.com/graphql"


def get_graphql_headers(runtime: ToolRuntime[TaskContext]) -> Dict[str, str]:
    """Get headers for authenticated GraphQL requests"""
    return {
        "Authorization": f"Bearer {runtime.context.token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


async def execute_graphql_query(
    runtime: ToolRuntime[TaskContext],
    query: str,
    variables: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a GraphQL query against GitHub's API"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    async with httpx.AsyncClient(headers=get_graphql_headers(runtime)) as client:
        response = await client.post(GRAPHQL_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        # Check for GraphQL errors
        if "errors" in data:
            error_messages = [
                error.get("message", "Unknown error") for error in data["errors"]
            ]
            raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")

        return data.get("data", {})


async def get_label_ids_from_names(
    runtime: ToolRuntime[TaskContext], label_names: List[str]
) -> List[str]:
    """
    Retrieves label IDs from GitHub by their names.
    
    Args:
        runtime: Tool runtime with context containing owner and repository.
        label_names: List of label names to look up.
        
    Returns:
        List of label IDs matching the provided names.
    """
    if not label_names:
        return []

    owner = runtime.context.owner
    repository = runtime.context.repository

    query = f"""
    query GetLabelIdsByNames($owner: String!, $name: String!, $first: Int!) {{
      repository(owner: $owner, name: $name) {{
        labels(first: $first) {{
          nodes {{
            id
            name
          }}
        }}
      }}
    }}
    """

    variables = {
        "owner": owner,
        "name": repository,
        "first": 100,
    }

    data = await execute_graphql_query(runtime, query, variables)
    repository_labels = data["repository"]["labels"]["nodes"]

    label_ids = []
    label_names_set = set[str](label_names)

    for label in repository_labels:
        if label["name"] in label_names_set:
            label_ids.append(label["id"])

    return label_ids


async def get_issue_id(runtime: ToolRuntime[TaskContext], issue_number: int) -> str:
    """
    Retrieves the GraphQL ID for a GitHub issue by its number.
    
    Args:
        runtime: Tool runtime with context containing owner and repository.
        issue_number: The issue number to look up.
        
    Returns:
        The GraphQL ID of the issue.
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    issue_query = """
      query GetIssueId($owner: String!, $name: String!, $number: Int!) {
        repository(owner: $owner, name: $name) {
          issue(number: $number) {
            id
          }
        }
      }
      """

    issue_data = await execute_graphql_query(
        runtime,
        issue_query,
        {
            "owner": owner,
            "name": repository,
            "number": issue_number,
        },
    )

    return issue_data["repository"]["issue"]["id"]


# Common GraphQL fragments for reuse
ISSUE_FRAGMENT = """
fragment IssueFields on Issue {
  id
  number
  title
  body
  state
  createdAt
  updatedAt
  closedAt
  url
  author {
    login
  }
  assignees(first: 10) {
    nodes {
      login
    }
  }
  labels(first: 20) {
    nodes {
      id
      name
      description
      color
    }
  }
  milestone {
    number
    title
    state
  }
  comments {
    totalCount
  }
  locked
  activeLockReason
  linkedBranches(first: 10) {
    nodes {
      id
      ref {
        name
        repository {
          nameWithOwner
        }
      }
    }
  }
  closedByPullRequestsReferences(first: 10) {
    nodes {
      id
      number
      title
      url
      state
      mergeCommit {
        oid
        messageHeadline
      }
      headRefOid
    }
  }
  trackedIssues(first: 5) {
    totalCount
    nodes {
      id
      number
      title
      url
      state
      repository {
        nameWithOwner
      }
    }
  }
  trackedInIssues(first: 5) {
    totalCount
    nodes {
      id
      number
      title
      url
      state
      repository {
        nameWithOwner
      }
    }
  }
  subIssues(first: 5) {
    totalCount
    nodes {
        id
        number
        title
        url
        state
        repository {
            nameWithOwner
        }
        author {
            login
        }
    }
  }
  parent {
    id
    number
    title
    url
    state
    repository {
      nameWithOwner
    }
    author {
      login
    }
  }
}
"""

COMMENT_FRAGMENT = """
fragment CommentFields on IssueComment {
  id
  body
  createdAt
  updatedAt
  url
  author {
    login
  }
}
"""

LABEL_FRAGMENT = """
fragment LabelFields on Label {
  id
  name
  description
  color
  isDefault
  url
}
"""
