# GitHub Copilot instructions for this folder

This guide shows how to use GitHub Copilot Chat to generate documentation from the example project in this folder.

## Before you start

- Open this workspace in VS Code.
- Ensure the Copilot Chat extension is installed and signed in.
- Skim `README.md` in this folder to understand the structure.

## Using the prompt templates

1. Open a prompt file under `prompts/` (for example, `01-generate-readme.md`).
2. Select the entire prompt text and send it to Copilot Chat.
3. When the prompt references placeholders like `{{code_root}}` or `{{examples}}`, replace them with paths from this repo.
4. If the model asks for more context, paste the relevant code or doc snippets (or use the Add Context button in Chat).

## Good context to provide

- The code in `src/widgetizer/` (small enough to paste).
- The seed docs in `docs/`.
- The usage sample in `examples/usage.py`.

Tip: For larger repos, prefer linking to files or using selection-based prompts over pasting entire files.

## Keeping outputs tidy

- Ask Copilot to restrict output to a single Markdown block when you want a copy-paste ready result.
- If the output is long, ask for a summary at the top with anchor links.
- If something is off, respond with: "Revise only the XYZ section, keep everything else."

## Diagram generation

- The `03-generate-architecture-diagram.md` prompt suggests including a Mermaid diagram.
- You can paste the resulting diagram block into the `software-diagramming/` area or render it with your preferred plugin.

## Quality checks (optional)

- Use the Vale example in `technical-writing-and-knowledge-sharing/vale-example` to lint Markdown.
- Keep headings, lists, and code blocks clean to satisfy linters.

## Common issues

- Missing context: If Copilot asks for clarification, provide code snippets or file paths.
- Path sensitivity: If the linter complains about certain words (e.g., a folder name), rephrase or wrap terms in backticks.
- Too much boilerplate: Ask Copilot to focus on substance and remove badges or placeholder sections.

