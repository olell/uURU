"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
from pydantic import BaseModel
from sqlmodel import Session, delete, select

from app.models.asterisk import DialPlanEntry, PSAor, PSAuth, PSEndpoint
from app.models.crud import CRUDNotAllowedException
from app.models.extension import Extension
from app.models.user import User, UserRole
from app.telephoning.main import Telephoning

logger = getLogger(__name__)


class AsteriskExtension(BaseModel):
    extension: str
    password: str
    type: str


def create_asterisk_extension(
    session_asterisk: Session,
    extension: str,
    extension_name: str,
    password: str,
    type: str,
    context="pjsip_internal",
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
        flavor = Telephoning.get_flavor_by_type(type)
        codec = (
            flavor.SUPPORTED_CODEC
            if isinstance(flavor.SUPPORTED_CODEC, str)
            else flavor.SUPPORTED_CODEC[type]
        )

        ps_endpoint = PSEndpoint(
            id=extension,
            transport="transport-udp",
            aors=ps_aor.id,
            auth=ps_auth.id,
            context=context,
            disallow="all",
            allow=codec,
            callerid=f"{extension_name} <{extension}>",
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


def update_asterisk_extension(
    session_asterisk: Session, extension: Extension, autocommit=True
):
    ps_endpoint = session_asterisk.exec(
        select(PSEndpoint).where(PSEndpoint.id == extension.extension)
    ).first()
    if not ps_endpoint:
        raise ValueError("no such endpoint in asterisk db")

    try:
        ps_endpoint.callerid = f"{extension.name} <{extension.extension}>"
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


def delete_asterisk_extension(
    session_asterisk: Session, extension: Extension, autocommit=True
) -> None:
    try:
        for cls in [PSEndpoint, PSAuth, PSAor]:
            session_asterisk.exec(delete(cls).where(cls.id == extension.extension))

    except Exception as e:
        logger.exception("Couldn't delete extension in asterisk DB")
        if autocommit:
            session_asterisk.rollback()
        raise e

    if autocommit:
        session_asterisk.commit()

    logger.info(
        f"Deleted extension {extension.name} <{extension.extension}> in asterisk DB"
    )


def create_or_update_asterisk_dialplan_entry(
    session_asterisk: Session, entry: DialPlanEntry, autocommit=True
) -> DialPlanEntry:
    try:
        session_asterisk.add(entry)
        if autocommit:
            session_asterisk.commit()
            session_asterisk.refresh(entry)
    except:
        if autocommit:
            session_asterisk.rollback()
        raise

    return entry


def create_or_update_asterisk_dialplan_callgroup(
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

    participants = extension.get_flavor_model.participants_list
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

    dialplan = session_asterisk.exec(
        select(DialPlanEntry).where(DialPlanEntry.exten == extension.extension)
    ).first()
    if not dialplan:
        dialplan = DialPlanEntry(
            exten=extension.extension,
            priority=1,
            app="Dial",
            appdata="&".join(
                [f"${{PJSIP_DIAL_CONTACTS({e.extension})}}" for e in extensions]
            ),
        )
    else:
        dialplan.appdata = "&".join(
            [f"${{PJSIP_DIAL_CONTACTS({e.extension})}}" for e in extensions]
        )

    logger.info(
        f"Created callgroup at {extension.extension} with participants: {participants}"
    )

    return create_or_update_asterisk_dialplan_entry(
        session_asterisk, dialplan, autocommit
    )


def delete_asterisk_dialplan_entry(
    session_asterisk: Session, extension: Extension, user: User, autocommit=True
):
    if not (user.role == UserRole.ADMIN or extension.user.id == user.id):
        raise CRUDNotAllowedException(
            "You're not permitted to delete this dialplan entry"
        )

    entry = session_asterisk.exec(
        select(DialPlanEntry).where(DialPlanEntry.exten == extension.extension)
    ).first()
    if entry is None:
        raise CRUDNotAllowedException("Extension not found in dialplan database")

    try:
        session_asterisk.delete(entry)
        if autocommit:
            session_asterisk.commit()
    except:
        if autocommit:
            session_asterisk.rollback()
        raise
