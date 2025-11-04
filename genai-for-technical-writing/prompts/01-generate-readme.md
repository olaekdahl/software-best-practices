# Prompt: Generate a high-quality README for `Widgetizer`

Context:

- Code: {{code_root}} <!-- e.g., `src/widgetizer/` -->
- Seeds: {{seed_docs}} <!-- e.g., `docs/overview.md`, `docs/architecture.md` -->
- Examples: {{examples}} <!-- e.g., `examples/usage.py` -->

Task:

- Write a concise, friendly README that explains:
  - What the project is and why it exists
  - Quick start with a minimal example
  - Basic architecture and how the pieces fit
  - How to run the example
  - How to generate docs using the prompts
- Include one Mermaid diagram (optional) illustrating the simple data flow.

Constraints:

- Keep it under ~500 words.
- Use clear headings and an easy-to-scan structure.
- Prefer short sentences and active voice.

Output:

- Markdown README content only.
- No boilerplate badges; focus on substance.
