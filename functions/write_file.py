import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=f"Writes the given content to a file located at file_path, constrained to the working directory, overwriting existing contents of the file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory. Required.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file. Required."
            )
        },
    ),
)

def write_file(working_directory, file_path, content):
    working_directory_abs = os.path.abspath(working_directory)

    if not os.path.isabs(file_path):
        file_path_abs = os.path.realpath(os.path.abspath(os.path.join(working_directory_abs, file_path)))
    else:
        file_path_abs = os.path.realpath(os.path.abspath(file_path))

    if os.path.commonpath([working_directory_abs, file_path_abs]) != working_directory_abs:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    # Create the file path and the file if it does not exist yet
    if not os.path.exists(file_path_abs):
        try:
            os.makedirs(os.path.dirname(file_path_abs), exist_ok=True)
            open(file_path_abs, 'a').close()
        except Exception as e:
            return f'Error: Cannot create "{file_path}"; error: {e}'

    with open(file_path_abs, 'w') as f:
        f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'