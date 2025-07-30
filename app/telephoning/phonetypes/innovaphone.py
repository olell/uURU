from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from pydantic_extra_types.mac_address import MacAddress

from app.telephoning import templates
from app.core.config import settings
from app.core.db import SessionDep
#from app.models.crud.extension import get_extension_by_mac
from app.telephoning.flavor import PhoneFlavor


class InnovaphoneFields(BaseModel):
    mac: MacAddress

class Innovaphone(PhoneFlavor):

    PHONE_TYPES = ["Innovaphone 241", "Innovaphone 201a"]
    EXTRA_FIELDS = InnovaphoneFields
    IS_SPECIAL = True

    def generate_routes(self, router: APIRouter):

        ########################################################################
        @router.get("/update")
        def get_update(mac: MacAddress) -> PlainTextResponse:
            return PlainTextResponse(
                f"mod cmd UP0 cfg http://{settings.WEB_HOST}{settings.API_V1_STR}/provisioning/innovaphone/config?mac={mac} iresetn"
            )
        
        ########################################################################
        @router.get("/innovaphone/config")
        def get_config(
            request: Request, session: SessionDep, mac: MacAddress
        ) -> PlainTextResponse:
            extension = None #get_extension_by_mac(session, mac)
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