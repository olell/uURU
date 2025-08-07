from typing import Annotated
from fastapi import Depends
from ldap3 import Connection, Server

from app.core.config import settings


class LDAPClient:
    def __init__(self):
        self.server = Server(settings.LDAP_SERVER, get_info="ALL")
        self.connection = None

    def connect(self):
        self.connection = Connection(
            self.server,
            settings.LDAP_USER,
            settings.LDAP_PASSWORD,
            authentication="SIMPLE",
            auto_bind=True,
        )
        if not self.connection.bound:
            raise ConnectionError("Failed to connect to the ldap server")

    def unbind(self):
        if self.connection:
            self.connection.unbind()


def get_ldap():
    client = LDAPClient()
    client.connect()
    try:
        yield client.connection
    finally:
        client.unbind()


LDAPDep = Annotated[Connection, Depends(get_ldap)]
