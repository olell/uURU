"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
from fastapi import HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from app.core.db import SessionDep
from app.models.crud.extension import get_extension_by_extra_field, filter_extensions_by_name
from app.telephoning.templates import templates
from app.telephoning.flavor import PhoneFlavor

logger = getLogger(__name__)


class GrandstreamExtraFields(BaseModel):
    mac: str = Field(pattern="^([0-9a-f]{2}-){5}[0-9a-f]{2}$")


class Grandstream(PhoneFlavor):

    PHONE_TYPES = ["Grandstream WP810"]
    IS_SPECIAL = True
    EXTRA_FIELDS = GrandstreamExtraFields
    SUPPORTED_CODEC = "g722"

    def generate_routes(self, router):
        ########################################################################
        @router.get("/cfg{mac}.xml")
        def get_config(request: Request, session: SessionDep, mac: str):

            mac = "-".join([mac.lower()[i : i + 2] for i in range(0, len(mac) - 1, 2)])

            extension = get_extension_by_extra_field(session, "mac", mac)
            if not extension:
                raise HTTPException(404, f"no extension found for mac {mac}")

            logger.info(f"Send provisioning data to WP810 @ {mac}")

            return templates.TemplateResponse(
                request, "grandstream_wp810.j2.xml", {"extension": extension}
            )

        @router.get("/phonebook.xml")
        def get_phonebook(request: Request, session: SessionDep):
            return templates.TemplateResponse(
                request, "grandstream_phonebook.j2.xml", {"extensions": filter_extensions_by_name(session, public=True)}
            )