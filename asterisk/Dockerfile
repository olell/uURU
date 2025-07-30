FROM ubuntu:24.04

ARG ASTERISK_SOURCE_VERSION=20.15.0

# download needed packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    alembic \
    asterisk \
    asterisk-mp3 \
    unixodbc \
    unixodbc-dev \
    odbc-mariadb \
    gettext-base \
    ca-certificates \
    python3-pip \
    python3-mysqldb \
    python3-requests \
    && rm -rf /var/lib/apt/lists/*

# download asterisk source - extract alembic contrib - move into /etc/alembic
RUN wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_SOURCE_VERSION}.tar.gz \
    && tar -xvzf asterisk-${ASTERISK_SOURCE_VERSION}.tar.gz asterisk-${ASTERISK_SOURCE_VERSION}/contrib/ast-db-manage \
    && mv asterisk-${ASTERISK_SOURCE_VERSION}/contrib/ast-db-manage alembic \
    && mv alembic /etc/alembic \
    && rm -rf asterisk-${ASTERISK_SOURCE_VERSION}* alembic/

# install pyst2 for AGI integration
RUN pip3 install pyst2 --break-system-packages

COPY etc/ /etc/
COPY usr/ /usr/

COPY entrypoint.sh /

ENTRYPOINT /entrypoint.sh