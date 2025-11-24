from typing import List, Dict, Any, Optional
import json
from google import genai
from google.genai import types
from core.types import Message, Response, ToolSpec, ToolCall, TokenUsage
from providers.provider import Provider

def _to_gemini_messages(msgs: List[Message]) -> List[types.Content]:
    out: List[types.Content] = []

    for m in msgs:
        # Skip system messages (Gemini uses the parameter system_instruction in generate_content()
        if m.role == "system":
            continue

        # Map assistant -> model
        role = "model" if m.role == "assistant" else m.role

        # Convert text to text parts and tool results to function_response parts
        if role == "tool" and m.name:
            # Parse the JSON content back to a dict (agent.py JSON-dumps it as a string)
            try:
                response_dict = json.loads(m.content)
            except json.JSONDecodeError:
                # Fallback: Wrap raw content if it's not JSON
                response_dict = {"result": m.content}
            part = types.Part.from_function_response(name=m.name, response=response_dict)
            #out.append(types.Content(role="tool", parts=[part]))
            out.append(types.Content(role="user", parts=[part]))
        else:
            out.append(types.Content(role=role, parts=[types.Part(text=m.content)]))

    return out

def _to_gemini_tool(tool: ToolSpec) -> types.FunctionDeclaration:
    # Convert our provider-agnostic JSON schema from dict to a JSONSchema object
    json_schema_obj = types.JSONSchema.model_validate(tool.parameters)

    return types.FunctionDeclaration(
        name=tool.name,
        description=tool.description,
        parameters=types.Schema.from_json_schema(json_schema=json_schema_obj),
    )

class GeminiProvider(Provider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-001", system_prompt: Optional[str] = None):
        super().__init__(model=model, system_prompt=system_prompt)
        self.client = genai.Client(api_key=api_key)
        #self.model = model
        #self.system_prompt = system_prompt

    #def chat(self, messages: List[Message], tools: List[ToolSpec]) -> Dict[str, Any]:
    def chat(self, messages: List[Message], tools: List[ToolSpec]) -> Response:

        gemini_msgs  = _to_gemini_messages(messages)
        gemini_tools = [_to_gemini_tool(t) for t in tools]
        tool_bundle  = types.Tool(function_declarations=gemini_tools)

        response = self.client.models.generate_content(
            model=self.model,
            contents=gemini_msgs,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt or "",
                tools=[tool_bundle],
            )
        )

        # Convert response back
        assistant_text = response.text or ""
        tool_calls: List[ToolCall] = []
        if response.function_calls:
            for f in response.function_calls:
                tool_calls.append(ToolCall(id=None, name=f.name, arguments=dict(f.args or {})))

        usage_raw = getattr(response, "usage_metadata", None)
        usage = None
        if usage_raw:
            usage = TokenUsage(
                input_count=usage_raw.prompt_token_count or 0,
                output_count=usage_raw.candidates_token_count or 0,
            )
        return Response(
            assistant_text=assistant_text,
            tool_calls=tool_calls,
            usage=usage,
        )
        #return {
        #    "assistant_text": assistant_text,
        #    "tool_calls": tool_calls,
        #    "raw": response,
        #    "usage": usage,
        #}
