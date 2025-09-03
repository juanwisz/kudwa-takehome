run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-init:
	python -m scripts.load_data

test:
	pytest -v

format:
	black app tests scripts

lint:
	flake8 app tests scripts
