# Micro User Registration Utility

Minimal phone extension self registration utility for asterisk.
Additional features:

* `Innovaphone` provisioning

Build with shiny stuff like FastAPI and SQLModel.

## Architecture

This project is based on two components:

* `uuru` (+ database)
* `asterisk` (+ database)

`uuru` configure `asterisk` via the database integration.

## Get Started

### Requirements

To deploy `uuru` you need

* `docker compose` [Installation Instructions](https://docs.docker.com/compose/install/)
* `uv` [Installation Instructions](https://docs.astral_.sh/uv/getting-started/installation/) (if you want to develop)

### Production

```
docker compose up --build
```

### Development

```
cp -av .env.sample .env
docker compose -f docker-compose-base.yml up --build -d
uv run fastapi dev
```

### ports

* app: `127.0.0.1:8000`
* mariadb app: `127.0.0.1:3307`
* mariadb asterisk: `127.0.0.1:3306`