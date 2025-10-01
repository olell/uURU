"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

import requests
from logging import getLogger

from app.models.extension import Extension, ExtensionBase

logger = getLogger(__name__)


def call_get_phonebook(host: str):
    response = requests.get(
        host.rstrip("/") + "/api/v1/extension/phonebook",
    )
    response.raise_for_status()

    raw_extensions = response.json()
    extensions: list[ExtensionBase] = []
    for e in raw_extensions:
        extensions.append(ExtensionBase.model_validate(e))

    return extensions
