from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Callable

Role = Literal["system", "user", "assistant", "tool"]

@dataclass
class Message:
    """
    A class that represents a message in the conversation with the LLM

    Attributes:
        role: The role this message belongs to
        content: The content of the message
        tool_call_id: (OpenAI): the tool call's id if there is any tool call in this message
        name: Optional tool/function name
    """
    role: Role
    content: str
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

@dataclass
class ToolSpec:
    """
    A class describing a tool the LLM is able to use

    Attributes:
        name: The name of the tool
        description: The description of the tool
        parameters: A Dict describing the parameters of the tool
        func: The actual Python implementation of the tool
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]

@dataclass
class ToolCall:
    """
    A class describing a tool call

    Attributes:
        id: (OpenAI): An optional ID of the tool call; Gemini might not use one
        name: The name of the called tool
        arguments: A Dict describing the parameters passed to the tool
    """
    id: Optional[str]
    name: str
    arguments: Dict[str, Any]

@dataclass
class Response:
    """
    A class describing a response from the LLM

    Attributes:
        assistant_text: The generated text of the response
        tool_calls: A list of the tool calls the assistant intends to use
        usage: Token usage statistics for this response
    """
    assistant_text: str
    tool_calls: List[ToolCall]
    usage: TokenUsage | None

@dataclass
class TokenUsage:
    """
    A class describing used input/output tokens for a given response

    Attributes:
        input_count: The count of input tokens
        output_count: The count of output tokens
    """
    input_count: int
    output_count: int
