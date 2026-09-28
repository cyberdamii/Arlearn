# ARLearn

Cloud-based practical and skills-based learning platform. This first build contains the simulation engine, accounts, scoring, and a web client. The AR client (Unity with AR Foundation) will consume the same API.

## Structure

    backend/    FastAPI service: auth, simulations, attempts, scoring
    content/    Simulation definitions as JSON, separate from code
    web/        Web client served by the backend
    Dockerfile, docker-compose.yml, .github/workflows/ci.yml

## Run locally

    cd backend
    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://localhost:8000. API documentation is at http://localhost:8000/docs.

## Test

    cd backend
    pytest

## Run with Docker

    docker compose up --build

## Environment variables

    SECRET_KEY      signing key for tokens, required in production
    DATABASE_URL    default is a local SQLite file
    TOKEN_MINUTES   token lifetime, default 720

## Push to GitHub

    git init
    git add .
    git commit -m "Initial scaffold"
    git branch -M main
    git remote add origin https://github.com/<username>/arlearn.git
    git push -u origin main

## Deploy

The Dockerfile runs on any container host such as Render, Railway, or Fly.io. Set SECRET_KEY, and attach persistent storage or switch DATABASE_URL to PostgreSQL before using it with real users.

## Adding a simulation

Add a JSON file to content/simulations following cpr-adult.json. Each step names the action that must be performed, and steps are scored in order. Every simulation must be reviewed by a subject-matter expert before use with learners.
