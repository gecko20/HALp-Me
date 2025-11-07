import argparse
import os
import sys
from dotenv import load_dotenv
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file
from google import genai
from google.genai import types
from importlib import import_module

# Command line arguments
cli_parser = argparse.ArgumentParser()
cli_parser.add_argument("prompt", help="The prompt being sent to the underlying LLM")
cli_parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
cli_parser.add_argument("-w", "--working-directory", help="The working directory to use", default="./calculator")

# Load environment vars
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

# Create the Gemini client
client = genai.Client(api_key=api_key)
# TODO: Move to config
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Write or overwrite files
- Execute and run Python files with optional arguments. If no arguments are provided, execute the function without passing arguments. Never ask for arguments yourself.

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons. Always assume that paths are relative to the working directory.

If your plan involves writing new code or changing existing code, make sure that you run the program afterwards and check whether your changes had the desired effects.

When you think you have completed all the individual points of your plan, create your final response which should always contain the phrase "Job's done. If something doesn't work now, it can only be attributable to human error.". Your final response should also contain a summary of what you did.
"""
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)

# Messages history
messages: list[types.Content] = []


# Calls a function for the LLM
def call_function(function_call_part, working_directory="./calculator", verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    # Inject the working directory into the function call's args
    args = function_call_part.args.copy()
    args['working_directory'] = working_directory

    # Get the function via introspection / reflection
    module = import_module(f"functions.{function_call_part.name}")
    func = getattr(module, function_call_part.name, None)

    if func is None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ]
        )

    result = func(**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": result},
            )
        ]
    )

def main():
    args = cli_parser.parse_args()

    prompt = args.prompt
    working_directory = args.working_directory

    messages.append(
        types.Content(role="user", parts=[types.Part(text=prompt)])
    )

    # Agent feedback loop
    # TODO: Accumulate token counts (in/out) and move the prints out of the loop
    final_response = None
    for i in range(20):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=messages,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    tools=[available_functions],
                ),
            )

            # Add the generated response candidates to the messages list
            for candidate in response.candidates:
                messages.append(candidate.content)

            # TODO: Move out of loop?
            if args.verbose:
                print(f"User prompt: {prompt}")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

            # Check whether the current response returned the response.text property;
            # if it did, break out of the feedback loop.
            # The first iteration should yield the LLM's plan.
            if response.text and "Job's done." in response.text:
                final_response = response
                break

            if response.function_calls:
                for call in response.function_calls:
                    result = call_function(call, working_directory=working_directory, verbose=args.verbose)
                    if not result.parts[0].function_response.response:
                        raise Exception(f"Fatal: A call to {call.name} failed")

                    if args.verbose:
                        print(f"-> {result.parts[0].function_response.response}")

                    # Convert the function call's resposne to a message and append it to messages
                    new_message = types.Content(
                        role="user",
                        parts=result.parts,
                    )
                    messages.append(new_message)
        # TODO: Graceful error handling
        except Exception as e:
            print(f"Exception raised, quitting: {e}")
            break
    else:
        print(f"Max iterations exhausted... no final response obtained")
        # TODO: Format messages so that they are more readable for humans
        print(f"Conversation history: {messages}")
        sys.exit(1)

    print(f"Response: {final_response.text}")

    sys.exit(0)


if __name__ == "__main__":
    main()
