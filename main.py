import argparse
import os
from dotenv import load_dotenv
from core.agent import Agent
from core.registry import load_tools
from providers.provider import Provider
from providers.gemini_provider import GeminiProvider
from config import SYSTEM_PROMPT, DEFAULT_BACKEND

# Command line arguments
cli_parser = argparse.ArgumentParser()
cli_parser.add_argument("prompt", help="The prompt being sent to the underlying LLM")
cli_parser.add_argument("-v", "--verbose", help="Enable verbose output", action="store_true")
cli_parser.add_argument("--backend", choices=["gemini", "ollama"], default=DEFAULT_BACKEND)
cli_parser.add_argument("-w", "--working-directory", help="The working directory to use", default="./calculator")

# Load environment vars
load_dotenv()

def build_provider(backend: str) -> Provider:
    if backend == "gemini":
        return GeminiProvider(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            system_prompt=SYSTEM_PROMPT,
        )
    #elif backend == "ollama":
    #    return OpenAIProvider(
    #        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    #        model=os.getenv("OLLAMA_MODEL", "gpt-oss-20b"),
    #        system_prompt=SYSTEM_PROMPT,
    #    )
    else:
        raise ValueError(f"Unknown backend: {backend}")

def main():
    args = cli_parser.parse_args()

    # Load tool specs
    tools = load_tools(working_directory=args.working_directory)

    provider = build_provider(args.backend)
    agent = Agent(provider=provider, tools=tools, system_prompt=SYSTEM_PROMPT)

    out = agent.run(args.prompt, verbose=args.verbose)

    print(f"Final Response:\n{out}")


if __name__ == "__main__":
    main()
