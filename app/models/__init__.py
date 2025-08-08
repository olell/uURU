"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from app.models.asterisk import PSAor, PSAuth, PSEndpoint
from app.models.user import User
from app.models.extension import Extension, TemporaryExtensions

tables = [User, Extension, TemporaryExtensions]
asterisk_tables = [PSAor, PSAuth, PSEndpoint]
