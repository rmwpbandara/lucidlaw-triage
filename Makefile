.PHONY: help install backend frontend test lint format up

help:
	@echo "install   Install backend (dev) and frontend dependencies"
	@echo "backend   Run the FastAPI backend (http://localhost:8000)"
	@echo "frontend  Run the Next.js frontend (http://localhost:3000)"
	@echo "test      Run the offline backend test suite"
	@echo "lint      Lint and format-check the backend"
	@echo "up        Run both services with Docker Compose"

install:
	cd backend && pip install -r requirements-dev.txt
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest

lint:
	cd backend && ruff check app tests && ruff format --check app tests

up:
	docker compose up --build
