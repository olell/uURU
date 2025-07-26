#!/bin/bash

set -e

# execute alembic database migrations
cd /etc/alembic
envsubst < config.ini.tmpl > config.ini
alembic -c config.ini upgrade head

# execute asterisk
cd /
envsubst < /etc/odbc.ini.tmpl > /etc/odbc.ini
envsubst < /etc/asterisk/res_odbc.conf.tmpl > /etc/asterisk/res_odbc.conf
exec asterisk -f