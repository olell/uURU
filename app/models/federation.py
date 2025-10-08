"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Literal
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, String
import uuid


class IncomingRequestStatus(BaseModel):
    accept: bool

    # required only if accepted
    prefix: str | None = None

    # required only if not accepted
    local_only: bool = False


class OutgoingRequestStatus(BaseModel):
    accept: bool
    secret: str

    # required only if accepted
    extension_length: int | None = None
    partner_iax_host: str | None = None
    partner_uuru_host: str | None = None


class PeerTeardownData(BaseModel):
    name: str
    secret: str


class PeerBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # iaxfriend
    name: str
    codec: Literal["g722", "alaw", "ulaw", "g726", "gsm", "lpc10"] = Field(
        "g722", sa_type=String
    )

    # dialplan
    prefix: str
    partner_extension_length: int

    # network
    partner_iax_host: str
    partner_uuru_host: str


class Peer(PeerBase, table=True):
    # iaxfriend
    secret: str


class OutgoingPeeringRequestBase(SQLModel):
    name: str
    partner_uuru_host: str
    prefix: str
    codec: Literal["g722", "alaw", "ulaw", "g726", "gsm", "lpc10"] = Field(
        "g722", sa_type=String
    )


class OutgoingPeeringRequestPublic(OutgoingPeeringRequestBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class OutgoingPeeringRequest(OutgoingPeeringRequestPublic, table=True):
    secret: str


class IncomingPeeringRequestBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    codec: Literal["g722", "alaw", "ulaw", "g726", "gsm", "lpc10"] = Field(
        "g722", sa_type=String
    )
    partner_uuru_host: str
    partner_iax_host: str
    partner_extension_length: int


class IncomingPeeringRequest(IncomingPeeringRequestBase, table=True):
    secret: str
