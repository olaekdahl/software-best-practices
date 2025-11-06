# Prefect Demo (Orchestration)

This folder contains a minimal Prefect flow that mirrors the custom orchestrator:
`extract -> transform -> load -> train -> evaluate`.

## Setup

```bash
pip install prefect==2.*
```

Run locally:

```bash
python3 widget_pipeline_flow.py
```

Optionally, start the Prefect server/Orion UI:

```bash
prefect server start  # in another terminal
```

Then you can register and run flows with deployment features if desired.
