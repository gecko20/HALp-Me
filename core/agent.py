from typing import List, Dict, Any
from core.types import Message, Response, ToolSpec, ToolCall, TokenUsage
from providers.provider import Provider

class Agent:
    def __init__(self, provider: Provider, tools: List[ToolSpec], system_prompt: str = ""):
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools

    def run(self, user_prompt: str, max_steps: int = 20, done_phrase: str = "Job's done.", verbose: bool = False) -> str:
        messages: List[Message] = []
        input_token_count  = 0
        output_token_count = 0

        # Start by injecting the system prompt as well as the user's prompt
        if self.system_prompt:
            messages.append(
                Message(role="system", content=self.system_prompt)
            )
        messages.append(
            Message(role="user", content=user_prompt)
        )

        # Agent feedback loop
        final_response = ""
        for i in range(max_steps):
            response = self.provider.chat(messages=messages, tools=self.tools)

            # Update usage statistics
            if response.usage is not None:
                input_token_count  += response.usage.input_count
                output_token_count += response.usage.output_count

            if verbose:
                print(f"({i} {self.provider.model}): Input tokens: {response.usage.input_count}; Output tokens: {response.usage.output_count}")

            # Extract assistant text and tool calls
            #assistant_text = response.get("assistant_text", "")
            #tool_calls: List[ToolCall] = response.get("tool_calls", [])
            assistant_text = response.assistant_text
            tool_calls = response.tool_calls

            if assistant_text:
                if verbose:
                    print(f"    ({i} {self.provider.model}): {assistant_text}")

                messages.append(
                    Message(role="assistant", content=assistant_text)
                )
                final_response = assistant_text
                if done_phrase in final_response:
                    return final_response

            # Execute any tool calls if present
            for tool_call in tool_calls:
                if verbose:
                    print(f"    Calling {tool_call.name}...")

                tool = next((t for t in self.tools if t.name == tool_call.name), None)
                if not tool:
                    # Return error as a tool message
                    messages.append(Message(
                        role="tool",
                        name=tool_call.name,
                        tool_call_id=tool_call.id,
                        content=f'{{"error": "Unknown function: {tool_call.name}"}}'
                    ))
                    continue

                # Inject arguments into the Python function
                out = tool.func(**tool_call.arguments)

                # Send the result back as a tool message
                messages.append(Message(
                    role="tool",
                    name=tool_call.name,
                    tool_call_id=tool_call.id,
                    content=__import__("json").dumps({"result": out})
                ))

        if verbose:
            print(f"({self.provider.model}): Total input tokens: {input_token_count}; Total output tokens: {output_token_count}")

        return final_response
