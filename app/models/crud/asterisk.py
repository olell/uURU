from sqlmodel import Session, delete, select

from app.models.asterisk import PSAor, PSAuth, PSEndpoint
from app.models.crud import CRUDNotAllowedException
from app.models.extension import Extension


def create_asterisk_extension(
    session_asterisk: Session, extension: Extension
) -> tuple[PSAor, PSAuth, PSEndpoint]:

    try:
        ps_aor = PSAor(id=extension.extension)
        ps_auth = PSAuth(
            id=extension.extension,
            username=extension.extension,
            password=extension.password,
        )
        # TODO: fix hard coded context
        # TODO: fix hard coded transport
        # TODO: fix hard coded codec
        ps_endpoint = PSEndpoint(
            id=extension.extension,
            transport="transport-udp",
            aors=ps_aor.id,
            auth=ps_auth.id,
            context="pjsip_internal",
            disallow="all",
            allow="g722",
        )
        session_asterisk.add(ps_aor)
        session_asterisk.add(ps_auth)
        session_asterisk.add(ps_endpoint)
        session_asterisk.commit()
        session_asterisk.refresh(ps_aor)
        session_asterisk.refresh(ps_auth)
        session_asterisk.refresh(ps_endpoint)
    except Exception as e:
        print(f"exception {e}")
        raise CRUDNotAllowedException(f"could not configure endpoint in asterisk: {e}")

    return [ps_aor, ps_auth, ps_endpoint]


def delete_asterisk_extension(session_asterisk: Session, extension: Extension) -> None:
    try:
        for cls in [PSEndpoint, PSAuth, PSAor]:
            session_asterisk.exec(delete(cls).where(cls.id == extension.extension))

    except Exception as e:
        session_asterisk.rollback()
        raise e

    session_asterisk.commit()
