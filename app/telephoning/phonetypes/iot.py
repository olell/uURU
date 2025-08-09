"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Literal
from fastapi import HTTPException, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from dicttoxml import dicttoxml
from app.core.db import SessionDep
from app.models.crud.extension import get_extension_by_extra_field
from app.telephoning.flavor import PhoneFlavor
from app.core.config import settings


class IoTFields(BaseModel):
    secret: str


class IoT(PhoneFlavor):
    PHONE_TYPES = ["IoT"]
    IS_SPECIAL = True
    EXTRA_FIELDS = IoTFields

    def generate_routes(self, router):

        @router.get("/{secret}")
        def get_sip_credentials(
            session: SessionDep,
            secret: str,
            format: Literal["json", "csv", "xml"] = "json",
        ):
            ext = get_extension_by_extra_field(session, "secret", secret)
            if ext is None:
                raise HTTPException(status_code=404, detail="Extension not found")

            data = {
                "server": settings.ASTERISK_HOST,
                "transport": "udp",
            }
            data.update(ext.model_dump())

            if format == "json":
                return data
            elif format == "xml":
                data["user_id"] = str(data["user_id"])
                return Response(
                    dicttoxml(data, attr_type=False),
                    media_type="application/xml",
                )
            else:
                response = ",".join(map(str, data.keys())) + "\n"
                response += ",".join(map(str, data.values())) + "\n"
                return PlainTextResponse(response)
