# Prompt: Generate a CHANGELOG snippet

Context:

- Git history: {{git_range}} <!-- e.g., `v0.1.0..HEAD` -->
- Code context: {{code_root}}

Task:

- Create a CHANGELOG entry with sections: Added, Changed, Fixed, Removed.
- Group items logically and keep bullets concise.

Constraints:

- Use semantic versioning language but do not invent a version number.
- If there are no changes in a section, omit the section.

Output:

- A Markdown snippet suitable for insertion into CHANGELOG.md.
