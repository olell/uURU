from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, IPvAnyAddress
from pydantic_extra_types.mac_address import MacAddress

from app.models.crud.extension import get_extension_by_extra_field
from app.telephoning.templates import templates
from app.core.config import settings
from app.core.db import SessionDep

# from app.models.crud.extension import get_extension_by_mac
from app.telephoning.flavor import PhoneFlavor


class InnovaphoneFields(BaseModel):
    mac: str = Field(pattern="^([0-9a-f]{2}-){5}[0-9a-f]{2}$")


class Innovaphone(PhoneFlavor):

    PHONE_TYPES = ["Innovaphone 241", "Innovaphone 200a"]
    SUPPORTED_CODEC = {
        "Innovaphone 241": "g722",
        "Innovaphone 200a": "alaw"
    }
    EXTRA_FIELDS = InnovaphoneFields
    IS_SPECIAL = True

    def __init__(self):
        super().__init__()

        self.prometheus_sd_target: dict[str, tuple[dict, IPvAnyAddress]] = {}

    def on_extension_create(self, session, asterisk_session, extension):
        print(
            f"A new {extension.type} was created. My extra_fields are {extension.extra_fields}"
        )

    def update_sd_targets_by_mac(
        self, session: SessionDep, mac: MacAddress, last_ip: IPvAnyAddress
    ):
        extension = get_extension_by_extra_field(session, "mac", mac)
        if not extension:
            return

        extension = extension.model_dump()
        extension.update({"last_ip": last_ip})

        self.prometheus_sd_target.update({extension.get("extension"): extension})

    def generate_routes(self, router: APIRouter):

        ########################################################################
        @router.get("/update")
        def get_update(
            session: SessionDep, mac: str, localip: IPvAnyAddress
        ) -> PlainTextResponse:
            self.update_sd_targets_by_mac(session, mac, localip)
            return PlainTextResponse(
                f"mod cmd UP0 cfg http://{settings.WEB_HOST}{settings.TELEPHONING_PREFIX}/innovaphone/config?mac={mac} iresetn"
            )

        ########################################################################
        @router.get("/config")
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

        @router.get("/service-discovery")
        def get_service_discovery():
            result = list()

            for _, extension in self.prometheus_sd_target.items():
                target = {
                    "targets": [f"{extension.get("last_ip")}"],
                    "labels": {
                        "instance": f"{extension.get("name")} <{extension.get("extension")}>",
                        "__meta_model": f"{extension.get("type")}",
                    },
                }

                for metric, key in {
                    "__meta_location": "location_name",
                    "__meta_latitude": "lat_float",
                    "__meta_longitude": "lon_float",
                }.items():
                    value = extension.get(key, None)
                    if value:
                        target["labels"][metric] = value

                result.append(target)

            return result
