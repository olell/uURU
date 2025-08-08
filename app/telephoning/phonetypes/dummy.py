"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from pydantic import BaseModel
from app.telephoning.flavor import PhoneFlavor


class DummyExtraFields(BaseModel):
    displayname: str = ""


class Dummy(PhoneFlavor):
    PHONE_TYPES = ["Dummy"]
    PREVENT_SIP_CREATION = True
    IS_SPECIAL = True

    EXTRA_FIELDS = DummyExtraFields
