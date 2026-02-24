# Software Design Principles and Architecture Fundamentals - Demos

Progressive demos illustrating design principles, patterns, and architecture.

| Demo | Topic | Complexity |
|------|-------|-----------|
| demo01_no_principles | Anti-pattern: no design principles | Naive |
| demo02_solid_principles | SOLID principles applied | Intermediate |
| demo03_design_patterns | Strategy, Adapter, Observer | Intermediate |
| demo04_api_design | REST API with OpenAPI and error contracts | Advanced |
| demo05_modular_architecture | Modular monolith with clean layers | Real-world |

## Running

Each demo is self-contained. Run with:

```bash
cd demo01_no_principles
python main.py
```

For demo04 (API), install dependencies first:

```bash
pip install fastapi uvicorn pydantic
cd demo04_api_design
uvicorn app:app --reload
```
