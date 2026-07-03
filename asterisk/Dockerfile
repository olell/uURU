FROM ubuntu:noble-20260610

# install asterisk stack
RUN echo "path-include=/usr/share/doc/asterisk-doc/*" >> /etc/dpkg/dpkg.cfg.d/excludes \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        wget \
        alembic \
        asterisk \
        asterisk-doc \
        unixodbc \
        unixodbc-dev \
        odbc-mariadb \
        gettext-base \
        ca-certificates \
        python3-pip \
        python3-mysqldb \
        python3-requests \
        mpg123 \
    && rm -rf /var/lib/apt/lists/*

# install pyst2 for AGI integration
RUN pip3 install pyst2 --no-cache-dir --break-system-packages

COPY etc/ /etc/
COPY usr/ /usr/

COPY entrypoint.sh /

HEALTHCHECK --start-period=600s CMD curl http://127.0.0.1:8088/metrics

ENTRYPOINT /entrypoint.sh
