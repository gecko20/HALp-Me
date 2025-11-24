import os
from  typing import Dict, Any
from core.types import ToolSpec

MAX_CHARS = 10000


def get_file_content(working_directory: str, file_path: str) -> str:
    working_directory_abs = os.path.abspath(working_directory)

    if not os.path.isabs(file_path):
        file_path_abs = os.path.realpath(os.path.abspath(os.path.join(working_directory_abs, file_path)))
    else:
        file_path_abs = os.path.realpath(os.path.abspath(file_path))

    if os.path.commonpath([working_directory_abs, file_path_abs]) != working_directory_abs:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(file_path_abs):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    with open(file_path_abs, "r") as f:
        file_content_string = f.read(MAX_CHARS)

        if len(file_content_string) > MAX_CHARS:
            file_content_string += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'

        return file_content_string

def build_tool(working_directory: str) -> ToolSpec:
    def _fn(file_path: str) -> str:
        return get_file_content(working_directory=working_directory, file_path=file_path)

    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read from, relative to the working directory. Required.",
            }
        },
        "required": ["file_path"],
        "additionalProperties": False
    }

    return ToolSpec(
        name="get_file_content",
        description=f"Reads the content from the file located at the given file_path, constrained to the working directory, as a string truncated to {MAX_CHARS} characters.",
        parameters=schema,
        func=_fn,
    )
