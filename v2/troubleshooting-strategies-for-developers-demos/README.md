# Troubleshooting Strategies for Developers - Demos

Progressive demos from buggy code to structured incident response.

| Demo | Topic | Complexity |
|------|-------|-----------|
| demo01_buggy_app | App with intentional bugs to find | Naive |
| demo02_structured_logging | Structured logging with correlation IDs | Intermediate |
| demo03_hypothesis_driven_debug | Systematic hypothesis-test debugging loop | Intermediate |
| demo04_observability_triage | RED/USE metrics and observability | Advanced |
| demo05_incident_response | Playbooks, postmortem, and on-call | Real-world |

## Setup

```bash
pip install structlog
```

## Running

```bash
cd demo01_buggy_app
python main.py
```
