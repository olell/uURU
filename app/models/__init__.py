from app.models.asterisk import PSAor, PSAuth, PSEndpoint
from app.models.user import User
from app.models.extension import Extension, TemporaryExtensions

tables = [User, Extension, TemporaryExtensions]
asterisk_tables = [PSAor, PSAuth, PSEndpoint]
