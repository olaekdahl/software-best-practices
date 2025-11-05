
#!/usr/bin/env bash
set -euo pipefail
uvicorn kafka_version.producer_api:app --reload --port 8001
