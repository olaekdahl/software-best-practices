# Demo 01 - Basic Diagrams: PlantUML and Mermaid

## Purpose

Show how diagrams-as-code works using the two most popular tools: PlantUML and Mermaid. Each diagram is stored as a plain-text source file that can be version-controlled, diffed, and reviewed in pull requests.

## Instructor Notes

- Open each file in VS Code with the appropriate preview extension installed
- PlantUML files (`.puml`) render with the **PlantUML** extension (jebbs.plantuml)
- Mermaid files (`.mmd`) render with the **Mermaid Editor** extension or the built-in GitHub/GitLab preview
- Emphasize that these files are diffable in PRs - show a side-by-side diff
- Point out the standard header/init lines used for consistent styling

## Files

| File | Format | Diagram Type | What It Shows |
|------|--------|--------------|---------------|
| `c4-c1-context.puml` | PlantUML | C4 Level 1 | System context - actors and external systems |
| `c4-c1-context.mmd` | Mermaid | C4 Level 1 | System context (Mermaid equivalent) |
| `c4-c2-container.puml` | PlantUML | C4 Level 2 | Containers - major runtime building blocks |
| `c4-c2-container.mmd` | Mermaid | C4 Level 2 | Containers (Mermaid equivalent) |
| `c4-c3-component.puml` | PlantUML | C4 Level 3 | Components - internal structure of one container |
| `c4-c3-component.mmd` | Mermaid | C4 Level 3 | Components (Mermaid equivalent) |
| `c4-c4-code.puml` | PlantUML | C4 Level 4 | Code - classes and interfaces inside one component |
| `c4-c4-code.mmd` | Mermaid | C4 Level 4 | Code - class diagram (Mermaid equivalent) |
| `sequence-order-flow.puml` | PlantUML | Sequence diagram | Order processing with alt/else branching |
| `class-order-domain.puml` | PlantUML | Class diagram | SOLID design with interfaces and relationships |
| `state-order-lifecycle.puml` | PlantUML | State machine | Order status transitions |
| `activity-code-review.puml` | PlantUML | Activity diagram | Code review workflow with decision points |
| `flowchart-cicd-pipeline.mmd` | Mermaid | Flowchart | CI/CD pipeline with pass/fail branches |
| `er-order-system.mmd` | Mermaid | ER diagram | Database entity relationships |
| `sequence-auth-flow.mmd` | Mermaid | Sequence diagram | Authentication flow with token validation |
| `gantt-sprint-plan.mmd` | Mermaid | Gantt chart | Sprint planning timeline |

## How to Render

### PlantUML

```bash
# CLI rendering (requires Java + plantuml.jar)
java -jar plantuml.jar sequence-order-flow.puml

# Or use the VS Code extension: Alt+D to preview
```

### Mermaid

```bash
# CLI rendering
npx @mermaid-js/mermaid-cli mmdc -i flowchart-cicd-pipeline.mmd -o pipeline.png

# Or use VS Code extension, GitHub renders .mmd natively in PRs
```

## Key Takeaways

1. **Diagrams-as-code** - store alongside source, version in Git, review in PRs
2. **PlantUML** - best for formal UML (class, sequence, state, activity)
3. **Mermaid** - lighter weight, renders natively in GitHub, GitLab, Notion, and many docs tools
4. **Keep diagrams focused** - one concept per diagram
5. **Use consistent styling** - shared headers/themes across the team
6. **Update diagrams in the same PR** as the code changes they describe
