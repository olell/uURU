"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field
from app.core.db import SessionDep
from app.models.crud.extension import get_extension_by_extra_field
from app.telephoning.templates import templates
from app.telephoning.flavor import PhoneFlavor

logger = getLogger(__name__)


class SnomExtraFields(BaseModel):
    mac: str = Field(pattern="^([0-9a-f]{2}-){5}[0-9a-f]{2}$")


class Snom(PhoneFlavor):
    PHONE_TYPES = ["Snom 300"]
    EXTRA_FIELDS = SnomExtraFields
    SUPPORTED_CODEC = "g722"
    IS_SPECIAL = True

    def generate_routes(self, router):
        ########################################################################
        @router.get("/snom-{mac}")
        def get_config(request: Request, session: SessionDep, mac: str):

            mac = "-".join([mac.lower()[i : i + 2] for i in range(0, len(mac) - 1, 2)])

            extension = get_extension_by_extra_field(session, "mac", mac)
            if not extension:
                raise HTTPException(404, f"no extension found for mac {mac}")

            logger.info(f"Send provisioning data to Snom 300 @ {mac}")

            return templates.TemplateResponse(
                request, "snom.j2.xml", {"extension": extension}
            )
