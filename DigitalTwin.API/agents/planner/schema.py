from pydantic import BaseModel
from typing import List


class Task(BaseModel):
    id: int
    agent: str
    action: str
    description: str
    depends_on: List[int] = []


class Plan(BaseModel):
    goal: str
    tasks: List[Task]
