run-api:
	uvicorn --app-dir src app:app --reload

demo-sql-vuln:
	python src/sql_injection_vulnerable.py

demo-sql-safe:
	python src/sql_injection_safe.py

demo-deser-insecure:
	python src/insecure_deserialization.py --pickle sample.pkl

demo-deser-safe:
	python src/safe_deserialization.py --json sample.json

demo-validate:
	python src/input_validation.py

.PHONY: run-api demo-sql-vuln demo-sql-safe demo-deser-insecure demo-deser-safe demo-validate