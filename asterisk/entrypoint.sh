#!/bin/bash

set -e

# set default values for AMI handling
UURU_ASTERISK_AMI_USER="${UURU_ASTERISK_AMI_USER:-uuru_ami_user}"
UURU_ASTERISK_AMI_PASS="${UURU_ASTERISK_AMI_PASS:-uuru_ami_secret}"
UURU_ASTERISK_AMI_ADDR="${UURU_ASTERISK_AMI_ADDR:-172.17.0.1}"
UURU_ASTERISK_AMI_PORT="${UURU_ASTERISK_AMI_ADDR:-5038}"

# execute alembic database migrations
cd /etc/alembic
envsubst < config.ini.tmpl > config.ini
alembic -c config.ini upgrade head

# execute asterisk
cd /
envsubst < /etc/odbc.ini.tmpl > /etc/odbc.ini
envsubst < /etc/asterisk/res_odbc.conf.tmpl > /etc/asterisk/res_odbc.conf
envsubst < /etc/asterisk/manager.conf.tmpl > /etc/asterisk/manager.conf
exec asterisk -f