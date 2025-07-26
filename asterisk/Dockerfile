FROM ubuntu:24.04

ARG ASTERISK_SOURCE_VERSION=20.15.0

# download needed packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    alembic \
    asterisk \
    unixodbc \
    unixodbc-dev \
    odbc-mariadb \
    gettext-base \
    ca-certificates \
    python3-mysqldb \
    && rm -rf /var/lib/apt/lists/*

# download asterisk source - extract alembic contrib - move into /etc/alembic
RUN wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_SOURCE_VERSION}.tar.gz \
    && tar -xvzf asterisk-${ASTERISK_SOURCE_VERSION}.tar.gz asterisk-${ASTERISK_SOURCE_VERSION}/contrib/ast-db-manage \
    && mv asterisk-${ASTERISK_SOURCE_VERSION}/contrib/ast-db-manage alembic \
    && mv alembic /etc/alembic \
    && rm -rf asterisk-${ASTERISK_SOURCE_VERSION}* alembic/

COPY etc/ /etc/

COPY entrypoint.sh /

ENTRYPOINT /entrypoint.sh