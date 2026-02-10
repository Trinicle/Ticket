import httpx
import json
from typing import Dict, Any, Optional
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
