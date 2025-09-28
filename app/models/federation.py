"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from sqlmodel import SQLModel, Field
import uuid


class PeerBase(SQLModel):
    id = Field(default_factory=uuid.uuid4, primary_key=True)

    # iaxfriend
    name: str

    # dialplan
    prefix: str
    partner_extension_length: int


class Peer(PeerBase, table=True):
    # iaxfriend
    secret: str

    # network
    partner_iax_host: str
    partner_uuru_host: str


class OutgoingPeeringRequestBase(SQLModel):
    id = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    partner_uuru_host: str
    prefix: str


class OutgoingPeeringRequest(OutgoingPeeringRequestBase, table=True):
    secret: str


class IncomingPeeringRequestBase(SQLModel):
    id = Field(primary_key=True)
    name: str
    partner_uuru_host: str
    partner_iax_host: str
    partner_extension_length: str


class IncomingPeeringRequest(SQLModel, table=True):
    secret: str
