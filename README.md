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

### Prepare

```
cp -av .env.sample .env
# edit .env file
# UURU_WEB_HOST
# UURU_WEB_HOST
# UURU_SECRET_KEY $(pwgen -1 30)
```

### Production

```
docker compose up --build
```

### Development

```
docker compose -f docker-compose-base.yml up --build -d
uv run fastapi dev
```

### ports

* app: `127.0.0.1:8000`
* mariadb app: `127.0.0.1:3307`
* mariadb asterisk: `127.0.0.1:3306`

## Auto Provisioning

`uuru` supports auto provisioning of Innovaphone devices (currently only `IP241`).
To activate add the following snippet to your `dnsmasq.conf`:
```
dhcp-option=vendor:1.3.6.1.4.1.6666,215,"http://${UURU_WEB_HOST}/api/v1/provisioning/innovaphone/update?mac=#m&localip=#i"
dhcp-option=vendor:1.3.6.1.4.1.6666,216,1
```

_replace `${UURU_WEB_HOST}` accordingly