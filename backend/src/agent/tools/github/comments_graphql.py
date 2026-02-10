from typing import Optional
from langchain.tools import ToolRuntime, tool

from backend.src.agent.agent import TaskContext
from backend.src.agent.tools.github.graphql_utils import (
    execute_graphql_query,
    COMMENT_FRAGMENT,
)


@tool("get_issue_comments")
async def get_issue_comments_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    first: int = 20,
    after: Optional[str] = None,
):
    """Gets comments for a specific issue using GraphQL
    
    Args:
        issue_number: The number of the issue to get comments for
        first: Number of comments to fetch (max 100)
        after: Cursor for pagination
    """
    owner = runtime.context.owner
    repository = runtime.context.repository
    
    query = f"""
    query GetIssueComments($owner: String!, $name: String!, $number: Int!, $first: Int!, $after: String) {{
      repository(owner: $owner, name: $name) {{
        issue(number: $number) {{
          comments(first: $first, after: $after) {{
            totalCount
            pageInfo {{
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }}
            nodes {{
              ...CommentFields
            }}
          }}
        }}
      }}
    }}
    
    {COMMENT_FRAGMENT}
    """
    
    variables = {
        "owner": owner,
        "name": repository,
        "number": issue_number,
        "first": min(first, 100),
    }
    if after:
        variables["after"] = after
    
    data = await execute_graphql_query(runtime, query, variables)
    comments_data = data["repository"]["issue"]["comments"]
    
    return {
        "totalCount": comments_data["totalCount"],
        "pageInfo": comments_data["pageInfo"],
        "comments": [format_comment_graphql(comment) for comment in comments_data["nodes"]],
    }


@tool("add_comment_to_issue")
async def add_comment_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    body: str,
):
    """Adds a comment to an issue using GraphQL
    
    Args:
        issue_number: The number of the issue to comment on
        body: The contents of the comment
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
    
    subject_id = issue_data["repository"]["issue"]["id"]
    
    mutation = f"""
    mutation AddComment($subjectId: ID!, $body: String!) {{
      addComment(input: {{subjectId: $subjectId, body: $body}}) {{
        commentEdge {{
          node {{
            ...CommentFields
          }}
        }}
      }}
    }}
    
    {COMMENT_FRAGMENT}
    """
    
    variables = {
        "subjectId": subject_id,
        "body": body,
    }
    
    data = await execute_graphql_query(runtime, mutation, variables)
    comment = data["addComment"]["commentEdge"]["node"]
    
    return format_comment_graphql(comment)


@tool("update_comment")
async def update_comment_graphql(
    runtime: ToolRuntime[TaskContext],
    comment_id: str,
    body: str,
):
    """Updates a comment using GraphQL
    
    Args:
        comment_id: The GraphQL node ID of the comment
        body: The updated contents of the comment
    """
    mutation = f"""
    mutation UpdateComment($id: ID!, $body: String!) {{
      updateIssueComment(input: {{id: $id, body: $body}}) {{
        issueComment {{
          ...CommentFields
        }}
      }}
    }}
    
    {COMMENT_FRAGMENT}
    """
    
    variables = {
        "id": comment_id,
        "body": body,
    }
    
    data = await execute_graphql_query(runtime, mutation, variables)
    comment = data["updateIssueComment"]["issueComment"]
    
    return format_comment_graphql(comment)


@tool("delete_comment")
async def delete_comment_graphql(
    runtime: ToolRuntime[TaskContext],
    comment_id: str,
):
    """Deletes a comment using GraphQL
    
    Args:
        comment_id: The GraphQL node ID of the comment to delete
    """
    mutation = """
    mutation DeleteComment($id: ID!) {
      deleteIssueComment(input: {id: $id}) {
        clientMutationId
      }
    }
    """
    
    variables = {
        "id": comment_id,
    }
    
    await execute_graphql_query(runtime, mutation, variables)
    
    return {"message": f"Comment {comment_id} deleted successfully"}


def format_comment_graphql(comment: dict) -> dict:
    """Convert GraphQL comment response to simplified dictionary"""
    return {
        "id": comment.get("id"),
        "body": comment.get("body", ""),
        "author": comment.get("author", {}).get("login") if comment.get("author") else None,
        "created_at": comment.get("createdAt"),
        "updated_at": comment.get("updatedAt"),
        "url": comment.get("url"),
    }

comments_tools = [
    get_issue_comments_graphql,
    add_comment_graphql,
    update_comment_graphql,
    delete_comment_graphql,
]