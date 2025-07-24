# Micro User Registration Utility

Minimal phone extension self registration utility. Build with shiny stuff like FastAPI and SQLModel.

## Get Started (Dev Server)

To run the devserver on your machine you need to install `uv`. Please
follow the steps [from these instructions](https://docs.astral.sh/uv/getting-started/installation/).

Once you have `uv` installed, you can simply run the development server
using this command:

```bash
uv run fastapi dev
```

## Get Started (Docker)

**production environment**:
```
docker compose up
```

**development environment**:
```
docker compose up -f docker-compose.yml -f docker-compose.dev.yml
```

## Run tests

To run the test use this command

```bash
coverage run --source=app -m pytest
```
