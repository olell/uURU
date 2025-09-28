"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.core.db import SessionAsteriskDep, SessionDep
from app.models.crud import CRUDNotAllowedException, federation
from app.models.federation import (
    IncomingPeeringRequest,
    IncomingPeeringRequestBase,
    IncomingRequestStatus,
    OutgoingPeeringRequestBase,
    OutgoingPeeringRequestPublic,
    OutgoingRequestStatus,
)
from app.models.user import UserRole

router = APIRouter(prefix="/federation", tags=["federation"])
logger = getLogger(__name__)


@router.post("/outgoing/request")
def create_outgoing_peering_request(
    session: SessionDep, user: CurrentUser, data: OutgoingPeeringRequestBase
) -> OutgoingPeeringRequestBase:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to create peering requests!",
        )

    try:
        return federation.create_outgoing_peering_request(
            session, user, data.name, data.partner_uuru_host, data.prefix
        )
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/outgoing/request", status_code=status.HTTP_204_NO_CONTENT)
def revoke_outgoing_peering_request(
    session: SessionDep, user: CurrentUser, request_id: str
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your are not permitted to revoke peering requests!",
        )

    try:
        request = federation.get_outgoing_peering_request_by_id(session, request_id)
        federation.revoke_outgoing_peering_request(session, user, request)
        return {"status": "OK"}
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/outgoing/requests")
def get_outgoing_peering_requests(
    session: SessionDep, user: CurrentUser
) -> list[OutgoingPeeringRequestPublic]:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to get peering requests!",
        )

    try:
        requests = federation.get_outgoing_peering_requests(session, user)
        return requests
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/incoming/requests")
def get_incoming_peering_requests(
    session: SessionDep, user: CurrentUser
) -> list[IncomingPeeringRequestBase]:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to get peering requests!",
        )

    try:
        requests = federation.get_incoming_peering_requests(session, user)
        return requests
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/incoming/request/{request_id}")
def set_incoming_peering_request_status(
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    user: CurrentUser,
    request_id: str,
    request_status: IncomingRequestStatus,
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not permitted to accept peering requests!",
        )

    if request_status.accept and request_status.prefix is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="prefix is required"
        )

    request = federation.get_incoming_peering_request_by_id(session, request_id)
    try:
        if request_status.accept:
            federation.accept_incoming_peering_request(
                session, session_asterisk, user, request, prefix=request_status.prefix
            )
        else:
            federation.decline_incoming_peering_request(session, user, request)
        return {"status": "OK"}
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/incoming/request")
def create_incoming_peering_request(
    session: SessionDep, request: IncomingPeeringRequest
):
    try:
        federation.create_incoming_peering_request(session, request)
        return {"status": "OK"}
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/incoming/request/{request_id}")
def revoke_incoming_peering_request(session: SessionDep, request_id: str, secret: str):
    try:
        federation.revoke_incoming_peering_request(session, request_id, secret)
        return {"status": "OK"}
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put("/outgoing/request/{request_id}")
def set_outgoing_peering_request_status(
    session: SessionDep,
    session_asterisk: SessionAsteriskDep,
    request_id: str,
    request_status: OutgoingRequestStatus,
):
    if request_status.accept and (
        request_status.extension_length is None
        or request_status.partner_iax_host is None
        or request_status.partner_uuru_host is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields"
        )

    try:
        if request_status.accept:
            federation.accept_outgoing_peering_request(
                session,
                session_asterisk,
                request_id,
                request_status.secret,
                request_status.extension_length,
                request_status.partner_iax_host,
                request_status.partner_uuru_host,
            )
        else:
            federation.decline_outgoing_peering_request(
                session, request_id, request_status.secret
            )
        return {"status": "OK"}
    except CRUDNotAllowedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
