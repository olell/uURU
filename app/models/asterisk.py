from typing import Optional
from sqlmodel import Field, SQLModel


class PSEndpoint(SQLModel, table=True):

    __tablename__ = "ps_endpoints"

    id: str = Field(primary_key=True)
    transport: str
    aors: str
    auth: str
    context: str
    disallow: str
    allow: str
    direct_media: str = "0"


class PSAor(SQLModel, table=True):

    __tablename__ = "ps_aors"

    id: str = Field(primary_key=True)
    max_contacts: int = 1


class PSAuth(SQLModel, table=True):

    __tablename__ = "ps_auths"

    id: str = Field(primary_key=True)
    auth_type: str = "userpass"
    password: str
    username: str
