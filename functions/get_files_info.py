import os
from functools import reduce
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    working_directory_abs = os.path.abspath(working_directory)

    if not os.path.isabs(directory):
        directory_abs = os.path.realpath(os.path.abspath(os.path.join(working_directory_abs, directory)))
    else:
        directory_abs = os.path.realpath(os.path.abspath(directory))

    if os.path.commonpath([working_directory_abs, directory_abs]) != working_directory_abs:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    try:
        if not os.path.isdir(directory_abs):
            return f'Error: "{directory}" is not a directory'

        dir_contents = os.listdir(directory_abs)
    except Exception as e:
        return f"Error reading directory contents: {e}"

    def handle_entry(acc, entry):
        entry_path = directory_abs + "/" + entry
        is_dir = os.path.isdir(entry_path)
        file_size = os.path.getsize(entry_path)
        return acc + f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}\n"

    try:
        result = reduce(handle_entry, dir_contents, "")
    except Exception as e:
        return f"Error reading directory contents: {e}"

    return result
