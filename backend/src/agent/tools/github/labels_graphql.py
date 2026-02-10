from typing import List, Optional
from langchain.tools import ToolRuntime, tool

from backend.src.agent.agent import TaskContext
from backend.src.agent.tools.github.graphql_utils import (
    execute_graphql_query,
    LABEL_FRAGMENT,
    get_issue_id,
    get_label_ids_from_names,
)


@tool("list_issue_labels")
async def list_issue_labels_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    first: int = 20,
    after: Optional[str] = None,
):
    """Lists all labels for an issue using GraphQL

    Args:
        issue_number: The number that identifies the issue
        first: Number of results to fetch (max 100)
        after: Cursor for pagination
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    query = f"""
    query ListIssueLabels($owner: String!, $name: String!, $number: Int!, $first: Int!, $after: String) {{
      repository(owner: $owner, name: $name) {{
        issue(number: $number) {{
          labels(first: $first, after: $after) {{
            totalCount
            pageInfo {{
              hasNextPage
              hasPreviousPage
              startCursor
              endCursor
            }}
            nodes {{
              ...LabelFields
            }}
          }}
        }}
      }}
    }}
    
    {LABEL_FRAGMENT}
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
    labels_data = data["repository"]["issue"]["labels"]

    return {
        "totalCount": labels_data["totalCount"],
        "pageInfo": labels_data["pageInfo"],
        "labels": [format_label_graphql(label) for label in labels_data["nodes"]],
    }


@tool("add_label_to_issue")
async def add_labels_to_issue_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    label_names: List[str],
):
    """Adds labels to an issue using GraphQL (keeps existing labels)

    Args:
        issue_number: The number that identifies the issue
        label_names: List of label node IDs to add to the issue
    """
    label_ids = await get_label_ids_from_names(runtime, label_names)

    if not label_ids:
        return {"error": f"No labels found for the given names: {label_names}"}

    issue_id = await get_issue_id(runtime, issue_number)

    if not issue_id:
        return {"error": f"Issue {issue_number} not found"}

    # Build label IDs array string
    label_ids_string = ", ".join([f'"{lid}"' for lid in label_ids])

    mutation = f"""
    mutation AddLabelsToIssue {{
      addLabelsToLabelable(input: {{labelableId: "{issue_id}", labelIds: [{label_ids_string}]}}) {{
        labelable {{
          labels {{
            totalCount
            nodes {{
              name
            }}
          }}
        }}
      }}
    }}
    """

    data = await execute_graphql_query(runtime, mutation)
    labels = data["addLabelsToLabelable"]["labelable"]["labels"]["nodes"]

    for label in labels:
        if label["name"] not in label_names:
            return {"error": f"Label {label['name']} not added to issue {issue_number}"}

    return {
        "message": f"Labels all labels were successfully added to issue {issue_number}"
    }


@tool("clear_labels_from_issue")
async def remove_all_labels_from_issue_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
):
    """Removes all labels from an issue using GraphQL

    Args:
        issue_number: The number that identifies the issue
    """

    issue_id = await get_issue_id(runtime, issue_number)

    if not issue_id:
        return {"error": f"Issue {issue_number} not found"}

    mutation = f"""
    mutation {{
      clearLabelsFromLabelable(input: {{labelableId: "{issue_id}"}}) {{
        labelable {{
          labels {{
            totalCount
          }}
        }}
      }}
    }}
    """

    data = await execute_graphql_query(runtime, mutation)
    total_count = data["clearLabelsFromLabelable"]["labelable"]["labels"]["totalCount"]

    if total_count > 0:
        return {"error": f"Failed to remove all labels from issue {issue_number}"}

    return {"message": f"All labels removed from issue {issue_number}"}


@tool("remove_label_from_issue")
async def remove_label_from_issue_graphql(
    runtime: ToolRuntime[TaskContext],
    issue_number: int,
    label_id: str,
):
    """Removes a specific label from an issue using GraphQL

    Args:
        issue_number: The number that identifies the issue
        label_id: The GraphQL node ID of the label to remove
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

    issue_data = await execute_graphql_query(
        runtime,
        issue_query,
        {
            "owner": owner,
            "name": repository,
            "number": issue_number,
        },
    )

    issue_id = issue_data["repository"]["issue"]["id"]

    mutation = f"""
    mutation RemoveLabelFromIssue {{
      removeLabelsFromLabelable(input: {{labelableId: "{issue_id}", labelIds: ["{label_id}"]}}) {{
        labelable {{
          ... on Issue {{
            labels(first: 50) {{
              nodes {{
                ...LabelFields
              }}
            }}
          }}
        }}
      }}
    }}
    
    {LABEL_FRAGMENT}
    """

    data = await execute_graphql_query(runtime, mutation)
    labels = data["removeLabelsFromLabelable"]["labelable"]["labels"]["nodes"]

    return {"labels": [format_label_graphql(label) for label in labels]}


@tool("get_repository_labels")
async def list_repository_labels_graphql(
    runtime: ToolRuntime[TaskContext],
    first: int = 30,
    after: Optional[str] = None,
):
    """Lists all labels for a repository using GraphQL

    Args:
        first: Number of results to fetch (max 100)
        after: Cursor for pagination
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    query = f"""
    query ListRepositoryLabels($owner: String!, $name: String!, $first: Int!, $after: String) {{
      repository(owner: $owner, name: $name) {{
        labels(first: $first, after: $after) {{
          totalCount
          pageInfo {{
            hasNextPage
            hasPreviousPage
            startCursor
            endCursor
          }}
          nodes {{
            ...LabelFields
          }}
        }}
      }}
    }}
    
    {LABEL_FRAGMENT}
    """

    variables = {
        "owner": owner,
        "name": repository,
        "first": min(first, 100),
    }
    if after:
        variables["after"] = after

    data = await execute_graphql_query(runtime, query, variables)
    labels_data = data["repository"]["labels"]

    return {
        "totalCount": labels_data["totalCount"],
        "pageInfo": labels_data["pageInfo"],
        "labels": [format_label_graphql(label) for label in labels_data["nodes"]],
    }


@tool("create_label")
async def create_label_graphql(
    runtime: ToolRuntime[TaskContext],
    name: str,
    color: str,
    description: Optional[str] = None,
):
    """Creates a new label for the repository using GraphQL

    Args:
        name: The name of the label (can include emoji)
        color: Hexadecimal color code without the leading # (e.g., 'f29513')
        description: Short description of the label (max 100 characters)
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

    repo_data = await execute_graphql_query(
        runtime,
        repo_query,
        {
            "owner": owner,
            "name": repository,
        },
    )

    repository_id = repo_data["repository"]["id"]

    # Build the input object
    input_fields = [
        f'repositoryId: "{repository_id}"',
        f'name: "{name}"',
        f'color: "{color}"',
    ]

    if description:
        input_fields.append(f'description: "{description}"')

    input_string = "{" + ", ".join(input_fields) + "}"

    mutation = f"""
    mutation CreateLabel {{
      createLabel(input: {input_string}) {{
        label {{
          ...LabelFields
        }}
      }}
    }}
    
    {LABEL_FRAGMENT}
    """

    data = await execute_graphql_query(runtime, mutation)
    label = data["createLabel"]["label"]

    return format_label_graphql(label)


@tool("get_label_by_name")
async def get_label_graphql(
    runtime: ToolRuntime[TaskContext],
    label_name: str,
):
    """Gets a label by name using GraphQL

    Args:
        label_name: The name of the label to retrieve
    """
    owner = runtime.context.owner
    repository = runtime.context.repository

    query = f"""
    query GetLabel($owner: String!, $name: String!, $labelName: String!) {{
      repository(owner: $owner, name: $name) {{
        label(name: $labelName) {{
          ...LabelFields
        }}
      }}
    }}
    
    {LABEL_FRAGMENT}
    """

    variables = {
        "owner": owner,
        "name": repository,
        "labelName": label_name,
    }

    data = await execute_graphql_query(runtime, query, variables)
    label = data["repository"]["label"]

    if not label:
        return {"error": f"Label '{label_name}' not found"}

    return format_label_graphql(label)


@tool("update_label")
async def update_label_graphql(
    runtime: ToolRuntime[TaskContext],
    label_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    description: Optional[str] = None,
):
    """Updates a label using GraphQL

    Args:
        label_id: The GraphQL node ID of the label to update
        name: The new name for the label (can include emoji)
        color: New hexadecimal color code without the leading #
        description: New description for the label (max 100 characters)
    """
    # Build the input object
    input_fields = [f'id: "{label_id}"']

    if name is not None:
        input_fields.append(f'name: "{name}"')
    if color is not None:
        input_fields.append(f'color: "{color}"')
    if description is not None:
        input_fields.append(f'description: "{description}"')

    input_string = "{" + ", ".join(input_fields) + "}"

    mutation = f"""
    mutation UpdateLabel {{
      updateLabel(input: {input_string}) {{
        label {{
          ...LabelFields
        }}
      }}
    }}
    
    {LABEL_FRAGMENT}
    """

    data = await execute_graphql_query(runtime, mutation)
    label = data["updateLabel"]["label"]

    return format_label_graphql(label)


@tool("delete_label")
async def delete_label_graphql(
    runtime: ToolRuntime[TaskContext],
    label_id: str,
):
    """Deletes a label from the repository using GraphQL

    Args:
        label_id: The GraphQL node ID of the label to delete
    """
    mutation = f"""
    mutation DeleteLabel {{
      deleteLabel(input: {{id: "{label_id}"}}) {{
        clientMutationId
      }}
    }}
    """

    await execute_graphql_query(runtime, mutation)

    return {"message": f"Label {label_id} deleted successfully"}


def format_label_graphql(label: dict) -> dict:
    """Convert GraphQL label response to simplified dictionary"""
    return {
        "id": label.get("id"),
        "name": label.get("name"),
        "description": label.get("description"),
        "color": label.get("color"),
        "default": label.get("isDefault", False),
        "url": label.get("url"),
    }


labels_tools = [
    list_issue_labels_graphql,
    add_labels_to_issue_graphql,
    remove_all_labels_from_issue_graphql,
    remove_label_from_issue_graphql,
    list_repository_labels_graphql,
    create_label_graphql,
    get_label_graphql,
    update_label_graphql,
    delete_label_graphql,
]
