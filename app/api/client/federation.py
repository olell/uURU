"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

import requests
from logging import getLogger

from app.models.federation import OutgoingRequestStatus
from app.models.federation import IncomingPeeringRequest

logger = getLogger(__name__)


def call_create_incoming_peering_request(host: str, request: IncomingPeeringRequest):
    response = requests.post(
        host.rstrip("/") + "/api/v1/federation/incoming/request",
        json=request.model_dump(exclude_unset=True),
    )
    response.raise_for_status()
    logger.info(f"Created incoming peering request '{request.name}' at {host}")


def call_revoke_incoming_peering_request(host: str, request_id: str, secret: str):
    response = requests.delete(
        host.rstrip("/") + f"/api/v1/federation/incoming/request/{request_id}",
        params={"secret": secret},
    )
    response.raise_for_status()
    logger.info(f"Revoked incoming peering request at {host}")


def call_set_outgoing_peering_request_status(
    host: str, request_id: str, status: OutgoingRequestStatus
):
    response = requests.put(
        host.rstrip("/") + f"/api/v1/federation/outgoing/request/{request_id}",
        json=status.model_dump(exclude_unset=True, exclude_none=True),
    )
    response.raise_for_status()
    logger.info(
        f"Updated outgoing peering status to {'accepted' if status.accept else 'declined'} at {host}"
    )
