
#!/usr/bin/env bash
set -euo pipefail
python kafka_version/consumers/inventory_consumer.py &
python kafka_version/consumers/payment_consumer.py &
python kafka_version/consumers/email_consumer.py
