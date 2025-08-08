"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Optional
from sqlmodel import Field, SQLModel


class DialPlanEntry(SQLModel, table=True):
    __tablename__ = "extensions"

    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    context: str = "pjsip_internal"
    exten: str
    priority: int
    app: str
    appdata: str


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
    callerid: str
    send_pai: str = "1"


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
