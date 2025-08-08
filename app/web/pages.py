"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from logging import getLogger
import os
from app.core.config import settings

logger = getLogger(__name__)


def available(listing=False) -> bool:
    if not settings.ENABLE_PAGES:
        return False

    if not os.path.exists("pages/"):
        return False

    files = os.listdir("pages/")
    md_files = list(filter(lambda f: f.endswith(".md"), files))
    if not listing:
        return len(md_files) > 0
    return md_files


def get_all() -> list[str]:
    files = available(True)
    if not files:
        return []

    return [f.split(".md")[0] for f in files]
