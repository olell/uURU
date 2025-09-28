"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
import uuid
from requests import HTTPError
from sqlmodel import Session, or_, select

from app.api.client.federation import (
    call_create_incoming_peering_request,
    call_revoke_incoming_peering_request,
    call_set_outgoing_peering_request_status,
)
from app.models.crud import CRUDNotAllowedException
from app.models.crud.asterisk import (
    create_asterisk_iax_peer_and_dialplan,
    delete_asterisk_iax_peer_and_dialplan,
)
from app.models.federation import (
    OutgoingRequestStatus,
    Peer,
    OutgoingPeeringRequest,
    IncomingPeeringRequest,
)
from app.models.user import User, UserRole
from app.core.security import generate_peer_secret
from app.core.config import settings

logger = getLogger(__name__)


"""
Local Actions
"""


def get_outgoing_peering_request_by_id(
    session: Session, request_id: uuid.UUID
) -> OutgoingPeeringRequest | None:
    statement = select(OutgoingPeeringRequest).where(
        OutgoingPeeringRequest.id == uuid.UUID(request_id)
    )
    request = session.exec(statement).first()

    return request


def get_outgoing_peering_requests(
    session: Session, user: User
) -> list[OutgoingPeeringRequest]:
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")
    return list(session.exec(select(OutgoingPeeringRequest)).all())


def create_outgoing_peering_request(
    session: Session,
    user: User,
    name: str,
    partner_uuru_host: str,
    prefix: str,
    autocommit=True,
) -> OutgoingPeeringRequest:
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")

    ex = session.exec(
        select(Peer).where(
            or_(Peer.name == name, Peer.partner_uuru_host == partner_uuru_host)
        )
    ).first()
    if ex is not None:
        raise CRUDNotAllowedException(
            "There is already a peer with this name or partner"
        )

    ex = session.exec(
        select(OutgoingPeeringRequest).where(
            or_(
                OutgoingPeeringRequest.name == name,
                OutgoingPeeringRequest.partner_uuru_host == partner_uuru_host,
            )
        )
    ).first()
    if ex is not None:
        raise CRUDNotAllowedException(
            "Peering with this instance is already requested!"
        )

    secret = generate_peer_secret()

    db_obj = OutgoingPeeringRequest(
        name=name, secret=secret, partner_uuru_host=partner_uuru_host, prefix=prefix
    )

    request = IncomingPeeringRequest(
        id=str(db_obj.id),
        name=name,
        partner_uuru_host=settings.FEDERATION_UURU_HOST,
        partner_iax_host=settings.FEDERATION_IAX2_HOST,
        partner_extension_length=settings.EXTENSION_DIGITS,
        secret=secret,
    )
    try:
        call_create_incoming_peering_request(partner_uuru_host, request)
    except HTTPError:
        raise CRUDNotAllowedException(
            f"Failed to request peering with {partner_uuru_host}"
        )

    try:
        session.add(db_obj)
        if autocommit:
            session.commit()
        logger.info(
            f"Requested peering '{db_obj.name}' with {db_obj.partner_uuru_host}"
        )
    except:
        if autocommit:
            session.rollback()
        raise

    return db_obj


def revoke_outgoing_peering_request(
    session: Session, user: User, request: OutgoingPeeringRequest, autocommit=True
):
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")

    try:
        call_revoke_incoming_peering_request(
            request.partner_uuru_host, str(request.id), request.secret
        )
    except HTTPError:
        raise CRUDNotAllowedException(
            f"Failed to revoke peering request at {request.partner_uuru_host}"
        )

    try:
        session.delete(request)
        if autocommit:
            session.commit()

        logger.info(
            f"Revoked peering request '{request.name}' with {request.partner_uuru_host}"
        )
    except:
        if autocommit:
            session.rollback()
        raise


def get_incoming_peering_request_by_id(
    session: Session, request_id: uuid.UUID
) -> IncomingPeeringRequest | None:
    statement = select(IncomingPeeringRequest).where(
        IncomingPeeringRequest.id == uuid.UUID(request_id)
    )
    request = session.exec(statement).first()

    return request


def get_incoming_peering_requests(session: Session, user: User) -> list[Peer]:
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")

    return list(session.exec(select(IncomingPeeringRequest)).all())


def accept_incoming_peering_request(
    session: Session,
    session_asterisk: Session,
    user: User,
    request: IncomingPeeringRequest,
    prefix: str,
    autocommit=True,
):
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")

    status = OutgoingRequestStatus(
        accept=True,
        secret=request.secret,
        extension_length=settings.EXTENSION_DIGITS,
        partner_iax_host=settings.FEDERATION_IAX2_HOST,
        partner_uuru_host=settings.FEDERATION_UURU_HOST,
    )
    try:
        call_set_outgoing_peering_request_status(
            request.partner_uuru_host, str(request.id), status
        )
    except HTTPError:
        raise CRUDNotAllowedException(
            f"Failed to tell {request.partner_uuru_host} that the request was accepted"
        )

    peer = Peer(
        name=request.name,
        prefix=prefix,
        partner_extension_length=request.partner_extension_length,
        secret=request.secret,
        partner_iax_host=request.partner_iax_host,
        partner_uuru_host=request.partner_uuru_host,
    )

    try:
        create_asterisk_iax_peer_and_dialplan(session_asterisk, peer, autocommit)

        session.delete(request)
        session.add(peer)
        session.delete(request)
        if autocommit:
            session.commit()

        logger.info(f"Accepted peering {peer.name} with {peer.partner_uuru_host}")

    except:
        if autocommit:
            session.rollback()
        raise


def decline_incoming_peering_request(
    session: Session, user: User, request: IncomingPeeringRequest, autocommit=True
):
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")

    status = OutgoingRequestStatus(
        accept=False,
        secret=request.secret,
    )
    try:
        call_set_outgoing_peering_request_status(
            request.partner_uuru_host, str(request.id), status
        )
    except HTTPError:
        raise CRUDNotAllowedException(
            f"Failed to tell {request.partner_uuru_host} that the request was declined"
        )

    try:
        session.delete(request)
        if autocommit:
            session.commit()

        logger.info(f"Declined peering {request.name} with {request.partner_uuru_host}")
    except:
        if autocommit:
            session.rollback()
        raise


def get_peers(session: Session) -> Peer:
    return list(session.exec(select(Peer)).all())


def teardown_peer(
    session: Session, session_asterisk: Session, user: User, peer: Peer, autocommit=True
):
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")

    # TODO: Sent teardown request to other instance

    try:
        delete_asterisk_iax_peer_and_dialplan(session_asterisk, peer, autocommit)

        session.delete(Peer)
        if autocommit:
            session.commit()

        logger.info(f"Teared down peering {peer.name} with {peer.partner_uuru_host}")
    except:
        if autocommit:
            session.rollback()
        raise


"""
Inter-Instance Actions
"""


def get_incoming_peering_requests(
    session: Session, user: User
) -> list[IncomingPeeringRequest]:
    if user.role != UserRole.ADMIN:
        raise CRUDNotAllowedException("Admin only!")

    return list(session.exec(select(IncomingPeeringRequest)).all())


def get_incoming_peering_request_by_id(
    session: Session, request_id: uuid.UUID
) -> IncomingPeeringRequest | None:
    statement = select(IncomingPeeringRequest).where(
        IncomingPeeringRequest.id == uuid.UUID(request_id)
    )
    return session.exec(statement).first()


def create_incoming_peering_request(
    session: Session, request: IncomingPeeringRequest, autocommit=True
):
    ex = session.exec(
        select(Peer).where(
            or_(
                Peer.name == request.name,
                Peer.partner_uuru_host == request.partner_uuru_host,
            )
        )
    ).first()
    if ex is not None:
        raise CRUDNotAllowedException("We are already peering or the name is invalid!")

    try:
        request.id = uuid.UUID(request.id)
        session.add(request)
        if autocommit:
            session.commit()
    except:
        if autocommit:
            session.rollback()
        raise


def revoke_incoming_peering_request(
    session: Session, request_id: uuid.UUID, secret: str, autocommit=True
):
    request = get_incoming_peering_request_by_id(session, request_id)
    if request is None:
        raise CRUDNotAllowedException("Unknown request!")

    if request.secret != secret:
        raise CRUDNotAllowedException("Invalid secret!")

    try:
        session.delete(request)
        if autocommit:
            session.commit()
    except:
        if autocommit:
            session.rollback()
        raise


def accept_outgoing_peering_request(
    session: Session,
    session_asterisk: Session,
    request_id: uuid.UUID,
    secret: str,
    extension_length: int,
    partner_iax_host: str,
    partner_uuru_host: str,
    autocommit=True,
):
    request = get_outgoing_peering_request_by_id(session, request_id)
    if request is None:
        raise CRUDNotAllowedException("Unknown request!")

    if request.secret != secret:
        raise CRUDNotAllowedException("Invalid secret!")

    peer = Peer(
        name=request.name,
        prefix=request.prefix,
        partner_extension_length=extension_length,
        secret=secret,
        partner_iax_host=partner_iax_host,
        partner_uuru_host=partner_uuru_host,
    )

    try:
        session.delete(request)
        session.add(peer)
        create_asterisk_iax_peer_and_dialplan(session_asterisk, peer, autocommit)

        if autocommit:
            session.commit()
    except:
        if autocommit:
            session.rollback()
        raise


def decline_outgoing_peering_request(
    session: Session, request_id: uuid.UUID, secret: str, autocommit=True
):
    request = get_outgoing_peering_request_by_id(session, request_id)
    if request is None:
        raise CRUDNotAllowedException("Unknown request!")

    if request.secret != secret:
        raise CRUDNotAllowedException("Invalid secret!")

    try:
        session.delete(request)
        if autocommit:
            session.commit()
    except:
        if autocommit:
            session.rollback()
        raise


def request_peer_teardown(
    session: Session, session_asterisk: Session, name: str, secret: str, autocommit=True
):
    peer = session.exec(
        select(Peer).where(Peer.name == name).where(Peer.secret == secret)
    ).first()

    if peer is None:
        raise CRUDNotAllowedException("Unknown peer!")

    try:
        delete_asterisk_iax_peer_and_dialplan(session_asterisk, peer, autocommit)
        session.delete(peer)
        if autocommit:
            session.commit()
    except:
        if autocommit:
            session.rollback()
        raise
