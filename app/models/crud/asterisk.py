"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
from pydantic import BaseModel
from sqlmodel import Session, delete, select

from app.core.config import settings
from app.models.asterisk import (
    IAXFriend,
    MusicOnHold,
    PSAor,
    PSAuth,
    PSEndpoint,
)
from app.models.crud import CRUDNotAllowedException
from app.models.crud.dialplan import Dial, Dialplan
from app.models.extension import Extension
from app.models.federation import Peer
from app.models.user import User, UserRole
from app.telephoning.flavor import CODEC
from app.telephoning.main import Telephoning

logger = getLogger(__name__)


def create_sip_account(
    session_asterisk: Session,
    extension: str,
    extension_name: str,
    password: str,
    codec: CODEC = "g722",
    context="pjsip_internal",
    set_websip_fields: bool = False,
    autocommit=True,
) -> tuple[PSAor, PSAuth, PSEndpoint]:

    try:
        ps_aor = PSAor(id=extension)
        ps_auth = PSAuth(
            id=extension,
            username=extension,
            password=password,
        )

        # TODO: fix hard coded transport
        ps_endpoint = PSEndpoint(
            id=extension,
            transport="transport-udp",
            aors=ps_aor.id,
            auth=ps_auth.id,
            context=context,
            disallow="all",
            allow=codec,
            callerid=f"{extension_name} <{extension}>",
            dtls_auto_generate_cert="1" if set_websip_fields else None,
            webrtc="1" if set_websip_fields else None,
        )
        session_asterisk.add(ps_aor)
        session_asterisk.add(ps_auth)
        session_asterisk.add(ps_endpoint)
    except Exception as e:
        if autocommit:
            session_asterisk.rollback()
        logger.exception("Couldn't configure endpoint in asterisk:")
        raise CRUDNotAllowedException(f"could not configure endpoint in asterisk: {e}")

    if autocommit:
        session_asterisk.commit()
        session_asterisk.refresh(ps_aor)
        session_asterisk.refresh(ps_auth)
        session_asterisk.refresh(ps_endpoint)

    logger.info(f"Created extension {extension_name} <{extension}> in asterisk DB")

    return [ps_aor, ps_auth, ps_endpoint]


def update_sip_account(
    session_asterisk: Session, extension: Extension, autocommit=True
):
    ps_endpoint = session_asterisk.exec(
        select(PSEndpoint).where(PSEndpoint.id == extension.extension)
    ).first()
    if not ps_endpoint:
        raise ValueError("no such endpoint in asterisk db")

    flavor = Telephoning.get_flavor_by_type(extension.type)
    codec = None
    if flavor is not None:
        codec = flavor.get_codec(extension)

    try:
        ps_endpoint.callerid = f"{extension.name} <{extension.extension}>"
        if codec is not None:
            ps_endpoint.allow = codec
        session_asterisk.add(ps_endpoint)
    except Exception as e:
        logger.exception("Couldn't update extension in asterisk DB")
        if autocommit:
            session_asterisk.rollback()
        raise e

    if autocommit:
        session_asterisk.commit()

    logger.info(
        f"Updated extension {extension.name} <{extension.extension}> in asterisk DB"
    )


def delete_sip_account(
    session_asterisk: Session, extension: str, autocommit=True
) -> None:
    try:
        for cls in [PSEndpoint, PSAuth, PSAor]:
            session_asterisk.exec(delete(cls).where(cls.id == extension))

    except Exception as e:
        logger.exception("Couldn't delete extension in asterisk DB")
        if autocommit:
            session_asterisk.rollback()
        raise e

    if autocommit:
        session_asterisk.commit()

    logger.info(f"Deleted extension <{extension}> in asterisk DB")


def create_or_update_callgroup(
    session: Session,
    session_asterisk: Session,
    creating_user: User,
    extension: Extension,
    autocommit=True,
):
    """
    this function expects that the Extension object is sanity checked before!
    """
    if extension.type != "Callgroup":
        raise CRUDNotAllowedException(
            "You cannot create a callgroup for this type of extension!"
        )

    participants = extension.get_flavor_model().participants_list
    if participants is None or len(participants) < 1:
        raise CRUDNotAllowedException("No participants found!")

    extensions = session.exec(
        select(Extension).where(Extension.extension.in_(participants))
    ).all()

    if not all(extensions):
        raise CRUDNotAllowedException("Unknown participants in list!")

    if creating_user.role == UserRole.USER and not all(
        [ext.user.id == creating_user.id for ext in extensions]
    ):
        raise CRUDNotAllowedException(
            "You may only create callgroups with extension you've created!"
        )

    plan = Dialplan(session_asterisk, extension.extension)
    plan.add(
        Dial(devices=[f"${{PJSIP_DIAL_CONTACTS({e.extension})}}" for e in extensions]),
        1,
    )
    plan.store()

    logger.info(
        f"Created callgroup at {extension.extension} with participants: {participants}"
    )


def create_iax_peer(session_asterisk: Session, peer: Peer, autocommit=True):
    # create iax peer
    friend = IAXFriend(
        name=peer.name,
        username=peer.name,
        secret=peer.secret,
        host=peer.partner_iax_host,
        disallow="all",
        allow=peer.codec,
    )

    # create dialplan entry
    try:
        session_asterisk.add(friend)

        plan = Dialplan(
            session_asterisk,
            exten=f"_{peer.prefix}{'X'*peer.partner_extension_length}",
        )
        plan.add(
            Dial(
                devices=[
                    f"IAX2/{peer.name}/${{EXTEN:-{peer.partner_extension_length}}}"
                ]
            ),
            1,
        )
        plan.store(autocommit)

        if autocommit:
            session_asterisk.commit()

        logger.info(
            f"Created IAX2Friend for peer {peer.name} and dialplan {plan.exten} in asterisk DB"
        )
    except:
        if autocommit:
            session_asterisk.rollback()

        raise


def delete_iax_peer(
    session_asterisk: Session,
    peer: Peer,
    autocommit=True,
):
    friend = session_asterisk.exec(
        select(IAXFriend)
        .where(IAXFriend.name == peer.name)
        .where(IAXFriend.secret == peer.secret)
    ).first()
    if friend is None:
        raise CRUDNotAllowedException("Unkown IAX2Friend")

    plan = Dialplan(
        session_asterisk,
        exten=f"_{peer.prefix}{'X'*peer.partner_extension_length}",
    )

    try:
        session_asterisk.delete(friend)
        plan.delete(autocommit)

        logger.info(
            f"Deleted IAX2Friend for {peer.name} and dialplan {plan.exten} from asterisk DB"
        )

        if autocommit:
            session_asterisk.commit()
    except:
        if autocommit:
            session_asterisk.rollback()
        raise


def get_music_on_hold_by_name(session_asterisk: Session, name: str) -> MusicOnHold:
    return session_asterisk.exec(
        select(MusicOnHold).where(MusicOnHold.name == name)
    ).first()


def create_music_on_hold(
    session_asterisk: Session, extension: Extension, media_name="moh", autocommit=True
):
    """
    creates a music on hold database entry for the extension if media is assigned
    at the given media name
    """
    if extension.get_assigned_media(media_name):  # check if the media is assigned
        moh = MusicOnHold(
            name=f"moh_{extension.extension}",
            mode="custom",
            application=f"/usr/bin/mpg123 -q -r 8000 -f 8192 --mono -s http://{settings.WEB_HOST}/api/v1/media/byextension/{extension.extension}/{media_name}",
        )
        try:
            session_asterisk.add(moh)
            if autocommit:
                session_asterisk.commit()
                session_asterisk.refresh(moh)
        except:
            if autocommit:
                session_asterisk.rollback()
            raise


def update_music_on_hold(
    session_asterisk: Session, extension: Extension, media_name="moh", autocommit=True
):
    assigned = extension.get_assigned_media(media_name)
    ex = get_music_on_hold_by_name(session_asterisk, f"moh_{extension.extension}")

    try:
        if assigned and not ex:  # newly assigned
            moh = MusicOnHold(
                name=f"moh_{extension.extension}",
                mode="custom",
                application=f"/usr/bin/mpg123 -q -r 8000 -f 8192 --mono -s http://{settings.WEB_HOST}/api/v1/media/byextension/{extension.extension}/{media_name}",
            )
            session_asterisk.add(moh)
            if autocommit:
                session_asterisk.commit()
                session_asterisk.refresh(moh)
        if assigned is None and ex:  # removed
            session_asterisk.delete(moh)
            if autocommit:
                session_asterisk.commit()

    except:
        if autocommit:
            session_asterisk.rollback()
        raise


def delete_music_on_hold(
    session_asterisk: Session, extension: Extension, autocommit=True
):
    moh = get_music_on_hold_by_name(session_asterisk, f"moh_{extension.extension}")
    if moh is None:
        return
    try:
        session_asterisk.delete(moh)
        if autocommit:
            session_asterisk.commit()
    except:
        if autocommit:
            session_asterisk.rollback()
        raise
