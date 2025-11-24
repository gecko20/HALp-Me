import importlib
import pkgutil
from typing import List
from core.types import ToolSpec

def load_tools(working_directory: str) -> List[ToolSpec]:
    tools: List[ToolSpec] = []
    pkg = "functions"

    for _, modname, _ in pkgutil.iter_modules([pkg]):
        mod = importlib.import_module(f"{pkg}.{modname}")

        if hasattr(mod, "build_tool"):
            tools.append(mod.build_tool(working_directory))

    return tools
