
#!/usr/bin/env bash
set -euo pipefail
uvicorn sync_http.app:app --reload --port 8000
