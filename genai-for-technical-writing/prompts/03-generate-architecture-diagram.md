# Prompt: Generate an architecture note and diagram

Context:

- Code context: {{code_root}} <!-- e.g., `src/widgetizer/` -->
- Seed docs: {{seed_docs}} <!-- e.g., `docs/architecture.md` -->

Task:

- Produce a short architecture note (200–300 words) summarizing components and data flow.
- Include one Mermaid diagram (flowchart or sequence) illustrating key interactions.
- If helpful, list 2–3 assumptions explicitly.

Constraints:

- Keep it readable by an engineer skimming the repo.
- Prefer concrete nouns and verbs; avoid fluff.

Output:

- A single Markdown section with a heading, text, and a Mermaid code block.
