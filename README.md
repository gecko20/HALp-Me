# HALp Me 6000
This project contains a rather simplified coding agent similar to Claude Code or OpenAI's Codex.

The coding agent currently supports and uses the following actions:
- List files and directories
- Read file contents
- Write to files
- Execute and run Python files with arguments

The agent is restricted to a working directory, currently hard-coded as "calculator".

It currently uses `gemini-2.5-flash` as the underlying LLM and needs a `GEMINI_API_KEY` supplied in a `.env` file.

WIP:
- Support for local LLMs served by Ollama
- Additional tools / functions for the agent
- More command line arguments

## Warning
While the agent is restricted to the given working directory, in theory it can break out of its prison and go completely rogue by executing arbitrary Python code (and even writing its own code for its escape if you don't treat your future AI overlords nicely...). You should run it inside a container. You have been warned.
This project started as a solution for the assignments of boot.dev's course on AI agents.
