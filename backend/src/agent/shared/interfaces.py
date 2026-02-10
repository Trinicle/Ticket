from typing import List
from pydantic import BaseModel, Field


class Issue(BaseModel):
    id: str = Field(description="The unique identifier for the issue")
    number: int = Field(description="The number of the issue")
    title: str = Field(description="The title of the issue")
    body: str = Field(description="The body of the issue")
    state: str = Field(description="The state of the issue")
    created_at: str = Field(description="The date and time the issue was created")
    updated_at: str = Field(description="The date and time the issue was last updated")
    closed_at: str = Field(description="The date and time the issue was closed")
    author: str = Field(description="The username of the author of the issue")
    assignees: List[str] = Field(description="The usernames of the assignees of the issue")
    labels: List[str] = Field(description="The names of the labels of the issue")
    milestone: str = Field(description="The name of the milestone of the issue")


class Comment(BaseModel):
    id: str = Field(description="The unique identifier for the comment")
    body: str = Field(description="The body of the comment")
    created_at: str = Field(description="The date and time the comment was created")
    updated_at: str = Field(description="The date and time the comment was last updated")


class Label(BaseModel):
    id: str = Field(description="The unique identifier for the label")
    name: str = Field(description="The name of the label")
    description: str = Field(description="The description of the label")
    color: str = Field(description="The color of the label")
    is_default: bool = Field(description="Whether the label is the default label")
    url: str = Field(description="The URL of the label")
