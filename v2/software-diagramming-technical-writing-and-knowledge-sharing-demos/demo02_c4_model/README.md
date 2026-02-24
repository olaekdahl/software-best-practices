# Demo 02 - C4 Model: Context, Container, Component

## Purpose

Demonstrate the C4 model for software architecture visualization. The C4 model provides four levels of zoom, each telling a different story to a different audience:

1. **Context** (Level 1) - Who uses the system and why? For stakeholders and new team members.
2. **Container** (Level 2) - What are the deployable units? For architects and DevOps.
3. **Component** (Level 3) - What are the major building blocks inside a container? For developers.
4. **Deployment** (Level 4) - Where does it run? For operations and infrastructure teams.

## Instructor Notes

- Walk through levels 1 through 4 in order, showing how each zooms in
- Point out that the Context diagram is the most important and most often skipped
- The Container diagram is the one teams use most day-to-day
- Component diagrams are only needed for complex services
- Ask the class: "Which level would you show to your VP? Your ops team? A new hire?"

## Files

| File | Format | C4 Level | What It Shows |
|------|--------|----------|---------------|
| `c4-level1-context.puml` | PlantUML | System Context | External users and systems interacting with the marketplace |
| `c4-level2-container.puml` | PlantUML | Container | Services, databases, queues, and frontends |
| `c4-level3-component.puml` | PlantUML | Component | Internal structure of the Order Service |
| `c4-level4-deployment.puml` | PlantUML | Deployment | Kubernetes cluster, cloud infrastructure |
| `c4-level1-context.mmd` | Mermaid | System Context | Same context diagram in Mermaid format |
| `c4-level2-container.mmd` | Mermaid | Container | Same container diagram in Mermaid format |

## System Under Design

All diagrams describe an **Online Marketplace** - a platform that connects buyers and sellers, handling product search, ordering, payment, and fulfillment.

## C4 Color Conventions

| Color | Meaning |
|-------|---------|
| Blue | User-facing applications (Web, Mobile) |
| Green | Backend services |
| Orange | Infrastructure adapters (DB repos, API clients) |
| Yellow | Domain/business logic |
| Gray | External systems (not owned by the team) |

## How to Render

```bash
# PlantUML
java -jar plantuml.jar c4-level1-context.puml

# Mermaid
npx @mermaid-js/mermaid-cli mmdc -i c4-level1-context.mmd -o context.png
```

## Key Takeaways

1. Start with Context - even for internal tools
2. Container diagram is the most commonly referenced level
3. Component diagrams only for complex services (avoid over-documenting)
4. Label arrows with **protocol** and **purpose** (e.g., "HTTPS / REST", "AMQP / Order Events")
5. Use trust boundaries to highlight security zones
6. Keep diagrams in the repo, update with code changes
