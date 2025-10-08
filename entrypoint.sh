#!/bin/bash

set -e
cd /app

# execute alembic database migrations
uv run alembic upgrade head

# execute app
uvicorn app.main:app --workers 1 --host 0.0.0.0