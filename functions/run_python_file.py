import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description=f"Executes the Python file located at file_path, constrained to the working directory, passing the optional args to it.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file which will be executed, relative to the working directory. Required.",
            ),
            "args": types.Schema(
                type=types.Type.STRING,
                description="An optional list of arguments which are passed to the Python file. Defaults to [] if not specified."
            )
        },
    ),
)

def run_python_file(working_directory, file_path, args=[]):
    working_directory_abs = os.path.abspath(working_directory)

    if not os.path.isabs(file_path):
        file_path_abs = os.path.realpath(os.path.abspath(os.path.join(working_directory_abs, file_path)))
    else:
        file_path_abs = os.path.realpath(os.path.abspath(file_path))

    if os.path.commonpath([working_directory_abs, file_path_abs]) != working_directory_abs:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(file_path_abs):
        return f'Error: File "{file_path}" not found.'

    if not file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        cmd = ['python3', file_path_abs, *args] if args else ['python3', file_path_abs]
        completed_process = subprocess.run(
            cmd,
            capture_output=True,
            timeout=30,
        )

        if len(completed_process.stdout) == 0 and len(completed_process.stderr) == 0 and completed_process.returncode == 0:
            return f'No output produced'

        return_string = f'STDOUT: {completed_process.stdout.decode('utf-8')}\n'
        return_string += f'STDERR: {completed_process.stderr.decode('utf-8')}\n'

        if completed_process.returncode != 0:
            return_string += f'Process exited with return code {completed_process.returncode}'

        return return_string
    except Exception as e:
        return f'Error: executing Python file: {e}'
