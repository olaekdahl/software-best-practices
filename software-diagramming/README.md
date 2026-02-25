# Software Diagramming

PlantUML and Mermaid diagrams for visualizing architecture, workflows, and system design.

## What's inside

### Core C4 diagrams (PlantUML)

- `c4-context.puml` / `c4-context.md` — C4 Level 1: System Context
- `c4-container.puml` / `c4-container.md` — C4 Level 2: Container
- `c4-component.puml` / `c4-component.md` — C4 Level 3: Component
- `c4-code.puml` / `c4-code.md` — C4 Level 4: Code

### Other diagrams

- `mermaid-simple.md` / `mermaid-starter.md` — Mermaid basics and syntax reference
- `webapp-flow.puml` / `webapp-flow.md` — Web application flow
- `microservice.puml` / `microservice.md` — Microservice architecture
- `puml-starter.puml` — PlantUML starter template
- `modeling-examples.md` — Various modeling examples
- `ref.md` — Quick UML reference

### Generated output

- `generated/` — Auto-generated architecture diagrams

## Additional diagrams

### `diagram-examples/` — Comprehensive Diagram Examples

A complete set of PlantUML and Mermaid diagrams covering multiple diagram types:

- **C4 diagrams** (L1–L4) in both `.puml` and `.mmd` formats
- **Sequence diagrams** — order processing flow
- **Class diagrams** — OOP relationships
- **State machine diagrams** — order lifecycle
- **Activity diagrams** — checkout workflow
- **Flowcharts** (Mermaid) — decision flows
- **ER diagrams** (Mermaid) — database relationships
- **Gantt charts** (Mermaid) — project timelines

```bash
# Open in VS Code with PlantUML / Mermaid preview extensions
code software-diagramming/diagram-examples/sequence-order-flow.puml
code software-diagramming/diagram-examples/flowchart-deployment.mmd
```

## Prerequisites

- **PlantUML preview:** VS Code extension `jebbs.plantuml` (requires Java)
- **Mermaid preview:** VS Code extension or GitHub/GitLab native rendering
