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

    # Fields required for websip
    dtls_auto_generate_cert: str = "0"
    webrtc: str = "0"


class PSAor(SQLModel, table=True):

    __tablename__ = "ps_aors"

    id: str = Field(primary_key=True)
    max_contacts: int = 5


class PSAuth(SQLModel, table=True):

    __tablename__ = "ps_auths"

    id: str = Field(primary_key=True)
    auth_type: str = "userpass"
    password: str
    username: str


class IAXFriend(SQLModel, table=True):

    __tablename__ = "iaxfriends"

    id: int = Field(
        primary_key=True, nullable=False, sa_column_kwargs={"autoincrement": True}
    )
    type: str = "friend"
    context: str = "pjsip_internal"
    trunk: str = "yes"
    encryption: str = "yes"

    name: str
    username: str
    secret: str
    host: str

    disallow: str = ""
    allow: str = ""
