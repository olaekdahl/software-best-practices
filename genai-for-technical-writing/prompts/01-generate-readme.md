# Prompt: Generate a high-quality README for `Widgetizer`

Context:

- Root:{{project_root}}
- Code: {{code_root}} <!-- e.g., `src/widgetizer/` -->
- Seeds: {{seed_docs}} <!-- e.g., `docs/overview.md`, `docs/architecture.md` -->
- Examples: {{examples}} <!-- e.g., `examples/usage.py` -->
- Folders_to_exclude: {{list of folders to exclude}}
- Vale_ini_location: {{}}

Task:

- Write a concise, friendly README that explains:
  - What the project is and why it exists
  - Quick start with a minimal example
  - Basic architecture and how the pieces fit
  - How to run the example
  - How to generate docs using the prompts
- Include one Mermaid diagram illustrating the simple data flow.

Constraints:

- Keep it under ~500 words.
- Use clear headings and an easy-to-scan structure.
- Prefer short sentences and active voice.

Output:

- Create a new README.md file if none exists or update if one is already present in root folder.
- Markdown README content only.
- No boilerplate badges; focus on substance.
- If unsure, stop and ask clarifying question.

Linting:

- Use Vale to lint the generated README
- Use Vale lint output and fix suggestions, warnings, and errors.
- Vale_ini_location specifies the location for .vale.ini
