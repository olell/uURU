from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.models.crud.extension import get_extension_by_extra_field
from app.telephoning import templates
from app.core.config import settings
from app.core.db import SessionDep
#from app.models.crud.extension import get_extension_by_mac
from app.telephoning.flavor import PhoneFlavor


class InnovaphoneFields(BaseModel):
    mac: str = Field(pattern="^([0-9a-f]{2}-){5}[0-9a-f]{2}$")

class Innovaphone(PhoneFlavor):

    PHONE_TYPES = ["Innovaphone 241", "Innovaphone 201a"]
    EXTRA_FIELDS = InnovaphoneFields
    IS_SPECIAL = True

    def on_extension_create(self, session, asterisk_session, extension):
        print(f"A new {extension.type} was created. My extra_fields are {extension.extra_fields}")

    def generate_routes(self, router: APIRouter):

        ########################################################################
        @router.get("/update")
        def get_update(mac: str) -> PlainTextResponse:
            return PlainTextResponse(
                f"mod cmd UP0 cfg http://{settings.WEB_HOST}/{settings.TELEPHONING_PREFIX}/innovaphone/config?mac={mac} iresetn"
            )
        
        ########################################################################
        @router.get("/innovaphone/config")
        def get_config(
            request: Request, session: SessionDep, mac: str
        ) -> PlainTextResponse:
            extension = get_extension_by_extra_field(session, "mac", mac)
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