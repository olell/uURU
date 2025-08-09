# Micro User Registration Utility

Telephone extension self registration utility for asterisk.

## ⚡️ Features:

- Pluggable Phone-Flavor system, currently supporting
  - Basic SIP extensions
  - Innovaphone IP241, IP200A, IP112
  - Mitel DECT OMM integration
  - Grandstream WP810 WiFi Phones
  - SNOM 300
  - Dummy extensions
  - IoT extensions
- LDAP Phonebook
- Callgroups
- [Rendering of Markdown for (Help-)Pages](/docs/pages.md)
- Prometheus HTTP Service-Discovery (**currently only for Innovaphones**)
- Super-Simplified deployment of the whole PBX by using docker compose
- Build with shiny stuff like FastAPI and SQLModel.

## 🏗️ Architecture

This project is based on two components:

- `uuru` (+ database)
- `asterisk` (+ database)

`uuru` configure `asterisk` via the database integration.

Due to pluggable phone-flavors it is pretty simple to build
integration for new telephone types. See the [Phone Flavor Docs](/docs/phone-flavors.md) how to
implement such a flavor.

## 🚀 Get Started

### Requirements

To deploy `uuru` you need

- `docker compose` [Installation Instructions](https://docs.docker.com/compose/install/)
- `uv` [Installation Instructions](https://docs.astral_.sh/uv/getting-started/installation/) (**only if you want use the dev setup**)

### Prepare

- Take a look at the configuration documentation [here](/docs/configuration.md)

```
cp -av .env.sample .env
# edit .env file

# -> Required are at least
# UURU_WEB_HOST <your_ip>:8000
# UURU_ASTERISK_HOST <your_ip>
# UURU_SECRET_KEY $(pwgen -1 30)
```

### Production

> [!WARNING]
> Set the LDAP admin password in your config and the docker-compose-base.yml file
> to something secure! The LDAP server will be exposed to the public.

```
docker compose up --build
```

### Development

```
docker compose -f docker-compose-base.yml up --build -d
uv run fastapi dev
```

### ports

- app: `0.0.0.0:8000`
- mariadb app: `127.0.0.1:3307`
- mariadb asterisk: `127.0.0.1:3306`
- ldap server: `0.0.0.0:389`

## ☎️ Phone specific documentation

Read more about how to use uURU with the supported phone types here:

- [Innovaphone](/docs/phones/innovaphone.md)
- [Callgroups](/docs/phones/callgroup.md)
- [IoT](/docs/phones/iot.md)

## 🔑 License

`uURU` is released under the `MIT` license - see `LICENSE` for more information.

Javascript / CSS files in `/static/js` and `/static/css` may be released under different
licenses. Please refer to the file's header for more information.
