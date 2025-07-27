from fastapi import HTTPException, Request
from fastapi import APIRouter
from fastapi import status
from fastapi.responses import PlainTextResponse
from pydantic_extra_types.mac_address import MacAddress

from app.core.config import settings
from app.api.templates import templates
from app.core.db import SessionDep
from app.models.crud.extension import get_extension_by_mac

router = APIRouter(prefix="/provisioning", tags=["provisioning"])


@router.get("/innovaphone/update")
def get_update(mac: MacAddress) -> PlainTextResponse:
    return PlainTextResponse(
        f"mod cmd UP0 cfg http://{settings.WEB_HOST}{settings.API_V1_STR}/provisioning/innovaphone/config?mac={mac} iresetn"
    )


@router.get("/innovaphone/config")
def get_config(
    request: Request, session: SessionDep, mac: MacAddress
) -> PlainTextResponse:
    extension = get_extension_by_mac(session, mac)
    if not extension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="found no extension for that mac",
        )

    return templates.TemplateResponse(
        request,
        "innovaphone.j2.cfg",
        {"settings": settings, "extension": extension},
    )
