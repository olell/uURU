from logging import getLogger
from pydantic import BaseModel
from datetime import datetime

from sqlmodel import Session

from app.core.security import generate_extension_password
from app.models.crud.asterisk import (
    create_asterisk_extension,
    delete_asterisk_extension,
)
from app.models.user import User
from app.core.config import settings

logger = getLogger(__name__)


class WebSIPExtension(BaseModel):
    aor: str
    extension: str
    auth_user: str
    auth_pass: str
    display_name: str
    created_at: datetime


class WebSIPManager(object):
    _instance = None

    @staticmethod
    def instance():
        if WebSIPManager._instance is None:
            WebSIPManager._instance = WebSIPManager()

        return WebSIPManager._instance

    def __init__(self):
        self.active_extensions: list[WebSIPExtension] = []

    def teardown(self, session_asterisk: Session):
        # deletes all websip extensions
        for extension in self.active_extensions:
            self.delete_extension(session_asterisk, extension)

    def get_extension(self, extension: str):
        ext = [e for e in self.active_extensions if e.extension == extension]
        if len(ext) != 1:
            raise AttributeError("Unknown extension")
        return ext[0]

    def delete_extension(self, session_asterisk: Session, extension: WebSIPExtension):
        try:
            delete_asterisk_extension(session_asterisk, extension.extension)
            self.active_extensions.pop(self.active_extensions.index(extension))
        except Exception as e:
            logger.error(
                f"Failed to delete WebSIP extension from asterisk DB: {str(e)}"
            )
            raise

    def create_extension(self, session_asterisk: Session, user: User | None = None):
        free_extension = None
        for i in range(
            settings.WEBSIP_EXTENSION_RANGE[0], settings.WEBSIP_EXTENSION_RANGE[1] + 1
        ):
            exts = [e for e in self.active_extensions if e.extension == str(i)]
            if len(exts) == 0:
                free_extension = str(i)
                break

        if free_extension is None:
            raise Exception("No free extension found in WebSIP range")
        free_extension = str(free_extension)

        pwd = generate_extension_password()
        name = f"{user.username if user else 'Anonymous'} (Web)"

        ext = WebSIPExtension(
            aor=f"sip:{free_extension}@{settings.ASTERISK_HOST}",
            extension=free_extension,
            auth_user=free_extension,
            auth_pass=pwd,
            display_name=name,
            created_at=datetime.now(),
        )

        try:
            create_asterisk_extension(
                session_asterisk,
                free_extension,
                name,
                pwd,
                "SIP",
                set_websip_fields=True,
            )
        except Exception as e:
            logger.error(f"Failed to create WebSIP extension in asterisk DB: {str(e)}")
            raise

        self.active_extensions.append(ext)

        return ext
