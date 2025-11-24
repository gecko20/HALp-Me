from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.types import Message, Response, ToolSpec, ToolCall, TokenUsage

class Provider(ABC):
    @abstractmethod
    def __init__(self, model: str, system_prompt: Optional[str] = None):
        self.model = model
        self.system_prompt = system_prompt

    @abstractmethod
    def chat(self, messages: List[Message], tools: List[ToolSpec]) -> Response:
        pass

