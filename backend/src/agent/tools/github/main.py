from ast import List
from langchain.agents import AgentState
from langchain_core.messages import SystemMessage

# GraphQL Tools
from backend.src.agent.tools.github.issues_graphql import (
    get_issue_graphql,
    list_repository_issues_graphql,
    search_issues_graphql,
    create_issue_graphql,
    update_issue_graphql,
)
from backend.src.agent.tools.github.comments_graphql import (
    get_issue_comments_graphql,
    add_comment_graphql,
    update_comment_graphql,
    delete_comment_graphql,
)
from backend.src.agent.tools.github.labels_graphql import (
    list_issue_labels_graphql,
    add_labels_to_issue_graphql,
    remove_all_labels_from_issue_graphql,
    remove_label_from_issue_graphql,
    list_repository_labels_graphql,
    create_label_graphql,
    get_label_graphql,
    update_label_graphql,
    delete_label_graphql,
    resolve_label_name_to_id_graphql,
)

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


github_tools = [
    # Issue Management (GraphQL)
    get_issue_graphql,
    list_repository_issues_graphql,
    search_issues_graphql,
    create_issue_graphql,
    update_issue_graphql,
    # Comment Management (GraphQL)
    get_issue_comments_graphql,
    add_comment_graphql,
    update_comment_graphql,
    delete_comment_graphql,
    # Label Management (GraphQL)
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
