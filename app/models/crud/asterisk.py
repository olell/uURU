from pydantic import BaseModel
from sqlmodel import Session, delete, select

from app.models.asterisk import PSAor, PSAuth, PSEndpoint
from app.models.crud import CRUDNotAllowedException
from app.models.extension import Extension, TemporaryExtensions
from app.telephoning.main import Telephoning


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
        session_asterisk.rollback()
        print(f"exception {e}")
        raise CRUDNotAllowedException(f"could not configure endpoint in asterisk: {e}")

    if autocommit:
        session_asterisk.commit()
        session_asterisk.refresh(ps_aor)
        session_asterisk.refresh(ps_auth)
        session_asterisk.refresh(ps_endpoint)

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
        session_asterisk.rollback()
        raise e

    if autocommit:
        session_asterisk.commit()


def delete_asterisk_extension(
    session_asterisk: Session, extension: Extension, autocommit=True
) -> None:
    try:
        for cls in [PSEndpoint, PSAuth, PSAor]:
            session_asterisk.exec(delete(cls).where(cls.id == extension.extension))

    except Exception as e:
        session_asterisk.rollback()
        raise e

    if autocommit:
        session_asterisk.commit()
