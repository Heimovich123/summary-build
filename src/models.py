from pydantic import BaseModel, Field
from typing import List, Optional

class Task(BaseModel):
    description: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    status: str = Field(description="E.g., 'New', 'In Progress', 'Completed'")
    source_message_ids: List[int] = Field(description="IDs of the messages where this task was discussed")
    source_chat_id: int = Field(description="ID of the chat")

class Decision(BaseModel):
    description: str
    context: Optional[str] = None
    source_message_ids: List[int] = Field(description="IDs of the messages where this decision was made")
    source_chat_id: int

class UnresolvedDiscussion(BaseModel):
    topic: str
    participants: List[str]
    current_status: str
    source_message_ids: List[int]
    source_chat_id: int

class ChangedDecision(BaseModel):
    old_decision: str
    new_decision: str
    reason: Optional[str] = None
    source_message_ids: List[int]
    source_chat_id: int

class ObjectReport(BaseModel):
    object_name: str
    tasks: List[Task] = []
    decisions: List[Decision] = []
    unresolved_discussions: List[UnresolvedDiscussion] = []
    changed_decisions: List[ChangedDecision] = []

class DailyReport(BaseModel):
    date: str
    objects: List[ObjectReport]
