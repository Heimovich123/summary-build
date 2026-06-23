from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Literal

class ExtractedItem(BaseModel):
    task_summary: str
    room_or_zone: Optional[str] = None
    initiator: Optional[str] = None
    responsible: Optional[str] = None
    approver: Optional[str] = None
    approval_fact: bool = False
    deadline_text: Optional[str] = None
    deadline_date: Optional[str] = None
    deadline_status: Literal["В срок", "Просрочено", "Риск срыва", "Не определен"] = "Не определен"
    final_decision: Optional[str] = None
    change_history: Optional[str] = None
    status: Literal[
        "Согласовано, в работе", 
        "Обсуждается", 
        "Решение не принято", 
        "Ответственный не назначен", 
        "Дедлайн не установлен", 
        "Ожидает согласования", 
        "Просрочено", 
        "Решение изменено", 
        "Обсуждение без результата", 
        "Требует внимания руководителя"
    ] = "Обсуждается"
    next_action: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_chat_id: int
    source_message_ids: List[int]
    source_message_links: List[str] = []

    @model_validator(mode="after")
    def generate_links(self) -> 'ExtractedItem':
        if not self.source_message_links and self.source_message_ids:
            links = []
            str_chat_id = str(self.source_chat_id)
            if str_chat_id.startswith("-100"):
                clean_chat_id = str_chat_id.replace("-100", "")
                for msg_id in self.source_message_ids:
                    links.append(f"https://t.me/c/{clean_chat_id}/{msg_id}")
            self.source_message_links = links
        return self

class ObjectReport(BaseModel):
    object_name: str
    agreed_tasks: List[ExtractedItem] = []
    unresolved_discussions: List[ExtractedItem] = []
    missing_deadline: List[ExtractedItem] = []
    missing_responsible: List[ExtractedItem] = []
    changed_decisions: List[ExtractedItem] = []
    needs_manager_attention: List[ExtractedItem] = []

class DailyReport(BaseModel):
    date: str
    objects: List[ObjectReport]
