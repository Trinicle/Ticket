from typing import Any, List, Tuple
from deepagents import CompiledSubAgent
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_core.tools import StructuredTool, BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from backend.src.agent.tools.github.comments import (
    update_comment_graphql,
    delete_comment_graphql,
)
from backend.src.agent.tools.github.issues import GITHUB_MCP_ISSUE_TOOLS
from backend.src.agent.tools.github.labels import GITHUB_MCP_LABEL_TOOLS
from backend.src.agent.tools.github.comments import GITHUB_MCP_COMMENT_TOOLS
from pydantic import create_model


GITHUB_SYSTEM_PROMPT = SystemMessage(
    content="""
You are a helpful assistant that can investigate, create, modify, and delete GitHub issues and Comments.

IMPORTANT: This system now uses the GitHub MCP Server for most operations. 
- Most tools are now MCP-based and provide better integration with GitHub's API
- Some comment operations (update/delete) still use GraphQL as they're not available in MCP
- All issue and label operations use MCP server tools

When working with GitHub resources, prefer using the MCP-based tools for better reliability and consistency.
"""
)


GRAPHQL_URL = "https://api.github.com/graphql"


def get_mcp_client(token: str):
    return MultiServerMCPClient(
        {
            "github": {
                "transport": "http",
                "url": "https://api.githubcopilot.com/mcp/",
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    )


def create_method_specific_tools(
    mcp_tools: List[BaseTool],
) -> Tuple[List[StructuredTool], List[StructuredTool], List[StructuredTool]]:
    """
    Create method-specific variants of multi-method MCP tools with inherited schemas.
    
    Args:
        mcp_tools: List of MCP tools to process.
        
    Returns:
        Tuple of (issue_tools, comment_tools, label_tools) lists.
    """
    issue_read_tool = next(
        (tool for tool in mcp_tools if tool.name == "issue_read"), None
    )

    if not issue_read_tool:
        return [], [], []

    original_schema = issue_read_tool.args_schema
    IssueReadWithoutMethod = None

    if original_schema:
        fields_without_method = {
            name: (field.type_, field.default if field.default is not ... else ...)
            for name, field in original_schema.__fields__.items()
            if name != "method"
        }

        IssueReadWithoutMethod = create_model(
            "IssueReadWithoutMethod", **fields_without_method
        )

    def create_method_wrapper(
        method_name: str, tool_name: str, description: str
    ) -> StructuredTool:
        """
        Create a wrapper function that pre-sets the method parameter.
        
        Args:
            method_name: The method name to pre-set.
            tool_name: The name for the new tool.
            description: Description for the new tool.
            
        Returns:
            A StructuredTool instance with the method pre-set.
        """

        async def wrapper(**kwargs: Any) -> Any:
            kwargs["method"] = method_name
            return await issue_read_tool.ainvoke(kwargs)

        return StructuredTool.from_function(
            func=wrapper,
            name=tool_name,
            description=description,
            args_schema=IssueReadWithoutMethod,
        )

    issue_tool = create_method_wrapper(
        "get",
        "get_issue_details",
        "Get detailed information about a specific GitHub issue",
    )

    comments_tool = create_method_wrapper(
        "get_comments",
        "get_issue_comments",
        "Get all comments for a specific GitHub issue",
    )

    labels_tool = create_method_wrapper(
        "get_labels",
        "get_issue_labels",
        "Get all labels assigned to a specific GitHub issue",
    )

    return [issue_tool], [comments_tool], [labels_tool]


def get_issue_agent(
    mcp_tools: List[BaseTool], specialized_issue_tools: List[StructuredTool]
) -> Any:
    """
    Creates an issue agent with appropriate tools and interrupt configuration.
    
    Args:
        mcp_tools: List of MCP tools available.
        specialized_issue_tools: List of specialized issue tools.
        
    Returns:
        Configured agent instance for issue operations.
    """
    base_tools = [tool for tool in mcp_tools if tool.name in GITHUB_MCP_ISSUE_TOOLS]

    all_tools = base_tools + specialized_issue_tools

    return create_agent(
        name="issue_agent",
        tools=all_tools,
        interrupt_before={
            "get_issue_details": False,
            "list_issues": False,
            "search_issues": False,
            "issue_write": True,
            "sub_issue_write": True,
        },
    )


def get_comment_agent(
    mcp_tools: List[BaseTool], specialized_comment_tools: List[StructuredTool]
) -> Any:
    """
    Creates a comment agent with appropriate tools and interrupt configuration.
    
    Args:
        mcp_tools: List of MCP tools available.
        specialized_comment_tools: List of specialized comment tools.
        
    Returns:
        Configured agent instance for comment operations.
    """
    base_tools = [tool for tool in mcp_tools if tool.name in GITHUB_MCP_COMMENT_TOOLS]

    graphql_only_tools = [update_comment_graphql, delete_comment_graphql]
    all_tools = base_tools + specialized_comment_tools + graphql_only_tools

    return create_agent(
        name="comment_agent",
        tools=all_tools,
        interrupt_before={
            "get_issue_comments": False,
            "add_issue_comment": True,
            "update_comment": True,
            "delete_comment": True,
        },
    )


def get_label_agent(
    mcp_tools: List[BaseTool], specialized_label_tools: List[StructuredTool]
) -> Any:
    """
    Creates a label agent with appropriate tools and interrupt configuration.
    
    Args:
        mcp_tools: List of MCP tools available.
        specialized_label_tools: List of specialized label tools.
        
    Returns:
        Configured agent instance for label operations.
    """
    base_tools = [tool for tool in mcp_tools if tool.name in GITHUB_MCP_LABEL_TOOLS]

    all_tools = base_tools + specialized_label_tools

    return create_agent(
        name="label_agent",
        tools=all_tools,
        interrupt_before={
            "get_label": False,
            "list_label": False,
            "get_issue_labels": False,
            "label_write": True,
        },
    )


async def get_github_sub_agents(token: str) -> List[CompiledSubAgent]:
    """
    Creates and returns all GitHub sub-agents configured with MCP tools.
    
    Args:
        token: GitHub authentication token.
        
    Returns:
        List of configured CompiledSubAgent instances.
    """
    mcp_client = get_mcp_client(token)
    mcp_tools = await mcp_client.get_tools()

    specialized_issue_tools, specialized_comment_tools, specialized_label_tools = (
        create_method_specific_tools(mcp_tools)
    )

    return [
        CompiledSubAgent(
            name="issue_agent",
            description="Manage GitHub issues - get issue details, create, update issues and sub-issues",
            runnable=get_issue_agent(mcp_tools, specialized_issue_tools),
        ),
        CompiledSubAgent(
            name="comment_agent",
            description="Manage GitHub issue comments - get comments, add via MCP, update/delete via GraphQL",
            runnable=get_comment_agent(mcp_tools, specialized_comment_tools),
        ),
        CompiledSubAgent(
            name="label_agent",
            description="Manage GitHub labels - get issue labels, manage repository labels",
            runnable=get_label_agent(mcp_tools, specialized_label_tools),
        ),
    ]
