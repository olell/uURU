"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from pydantic import BaseModel
from app.telephoning.flavor import CODEC, PhoneFlavor


class SIPFields(BaseModel):
    codec: CODEC = "g722"


class SIP(PhoneFlavor):
    PHONE_TYPES = ["SIP"]
    DISPLAY_INDEX = 1000
    IS_SPECIAL = False
    EXTRA_FIELDS = SIPFields

    def get_codec(self, extension) -> CODEC:
        if extension is None:
            return super().get_codec(extension)

        codec = extension.get_extra_field("codec")
        if codec is not None:
            return codec

        return "g722"
