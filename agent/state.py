from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Note:
    kind: Literal["finding", "gap", "conflict"]
    category: str
    description: str
    sources: list[str]


@dataclass
class InvestigationState:
    goal: str
    plan: list[dict] = field(default_factory=list)  # each item: {step, category, question, approach}
    current_step: int = 0
    notes: list[Note] = field(default_factory=list)
    documents_read: list[str] = field(default_factory=list)
    iterations: int = 0
    step_retries: dict = field(default_factory=dict)  # step_index -> retry_count
    concluded: bool = False
