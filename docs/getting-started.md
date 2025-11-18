# Installation Instructions

µURU is published as a docker image and can be installed using `docker compose`. The git repo also
contains two docker compose yaml files (`docker-compose.yml` and `docker-compose-base.yml`) which
you can use as a starting point.

## Setup Instructions

### 1. Clone the repo
```
git clone https://github.com/olell/uuru
```

### 2. Prepare the setup
The git repo contains a file called `.env.sample`, copy this file and
edit the pre-defined configuration flags. Take a looks at the [configuration docs](configuration.md) to see which options are available.

```
cp -av .env.sample .env
# now edit the .env file
```

!!! info
    Required are at least the following flags

    - `UURU_WEB_HOST = <host_ip><:port>`
    - `UURU_ASTERISK_HOST = <host_ip>`
    - `UURU_SECRET_KEY = <some secret key>`

!!! warning
    In production you must configure the LDAP credentials in your configuration
    and in the `docker-compose-base.yml` to something secure. The LDAP server will
    be exposed to the public!

### 3. Start the system
```
docker compose up
```

!!! note
    At the first start this might take a while since the asterisk container
    populates the database and does some other housekeeping. If not changed
    the following ports are now open:

    - `0.0.0.0:8000` µURU
    - `0.0.0.0:389` LDAP
    - `0.0.0.0:8080` Asterisk HTTP
    - `0.0.0.0:5060` SIP

## Considerations for production
In production you should probably use a reverse-proxy like [traefik](https://github.com/traefik/traefik) to deploy the system with HTTPS and a valid certificate. An
example of how to do that will follow. Some features ([WebSIP](features/websip.md)) don't work without HTTPS.

Also you probably need control over the DHCP server in the network the µURU is deployed since some VoIP phones require special DHCP options to get their autoprovisioning information.