"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from app.telephoning.flavor import PhoneFlavor


class SIP(PhoneFlavor):
    PHONE_TYPES = ["SIP"]
    DISPLAY_INDEX = 1000
    IS_SPECIAL = False
