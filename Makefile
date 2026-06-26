.PHONY: install run-backend run-frontend seed docker-up docker-down lint clean

install:
	pip install -r requirements.txt

run-backend:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	streamlit run frontend/app.py --server.port=8501

seed:
	python backend/seed_db.py

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

lint:
	ruff check backend/ frontend/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete
