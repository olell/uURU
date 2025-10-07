"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from app.models.asterisk import PSAor, PSAuth, PSEndpoint, IAXFriend
from app.models.user import Invite, User
from app.models.extension import Extension, TemporaryExtensions
from app.models.federation import Peer, IncomingPeeringRequest, OutgoingPeeringRequest
from app.models.media import ExtensionMedia, Media

tables = [
    User,
    Extension,
    TemporaryExtensions,
    Invite,
    Peer,
    IncomingPeeringRequest,
    OutgoingPeeringRequest,
    Media,
    ExtensionMedia,
]
asterisk_tables = [PSAor, PSAuth, PSEndpoint, IAXFriend]
