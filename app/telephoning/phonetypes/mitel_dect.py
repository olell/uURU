from logging import getLogger
from fastapi import HTTPException
from fastapi import status
from fastapi.responses import PlainTextResponse
import mitel_ommclient2
from sqlmodel import Session
from threading import Lock

from app.core.security import generate_extension_password
from app.models.crud.asterisk import (
    create_asterisk_extension,
)
from app.models.crud.extension import (
    delete_tmp_extension,
    get_extension_by_token,
    get_tmp_extension_by_id,
)
from app.models.extension import TemporaryExtensions
from app.telephoning.flavor import PhoneFlavor
from app.core.config import settings
from app.core.db import (
    SessionAsteriskDep,
    SessionDep,
    engine,
    engine_asterisk,
)

logger = getLogger(__name__)

class MitelDECT(PhoneFlavor):
    PHONE_TYPES = ["DECT"]
    DISPLAY_INDEX = 1001
    IS_SPECIAL = False

    SUPPORTED_CODEC = "alaw"

    JOB_INTERVAL = 10

    def __init__(self):
        self.lock = Lock()
        self.ommclient = mitel_ommclient2.OMMClient2(
            host=settings.OMM_HOST,
            port=settings.OMM_PORT,
            username=settings.OMM_USER,
            password=settings.OMM_PASSWORD,
            ommsync=True,
        )
        logger.info("Created OMM client")

    def generate_routes(self, router):
        @router.post("/")
        def dect_registration(
            session: SessionDep,
            session_asterisk: SessionAsteriskDep,
            data: dict,
        ) -> PlainTextResponse:
            logger.info(
                f"registration attempt from tmp extension {data['tmp_extension']} via token {data['token']}"
            )

            extension = get_extension_by_token(session, data["token"])
            if not extension:
                logger.error("unknown extension")
                raise HTTPException(
                    detail="could not find matching extension for token",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            tmp_extension = get_tmp_extension_by_id(session, data["tmp_extension"])
            if not tmp_extension:
                logger.error("unknown tmp extension")
                raise HTTPException(
                    detail="could not identify temporary extension from caller",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # detach temporary user from device
            self.delete_user_from_device(
                user_id=tmp_extension.uid, device_ppn=tmp_extension.ppn
            )

            # atach real user to device
            self.configure_user_on_device(
                extension.name,
                extension.extension,
                extension.password,
                tmp_extension.ppn,
            )

            # delete tmp_extension
            delete_tmp_extension(session, session_asterisk, tmp_extension)

    def job(self):
        self.enable_subscription_mode()

        for device in self.get_unbound_devices():
            tmp_ext_id = TemporaryExtensions.generate_extension()
            password = generate_extension_password()
            
            logger.info(f"OMM: new unbound device: {device.ppn} @ {tmp_ext_id}")

            user_id = self.configure_user_on_device(
                tmp_ext_id, tmp_ext_id, password, (device.ppn)
            )

            tmp_ext = TemporaryExtensions(
                extension=tmp_ext_id,
                password=password,
                uid=user_id,
                ppn=device.ppn,
            )

            with Session(engine) as session:
                session.add(tmp_ext)
                session.commit()

                with Session(engine_asterisk) as session_asterisk:
                    create_asterisk_extension(
                        session_asterisk,
                        extension=tmp_ext_id,
                        extension_name="DECT TMP",
                        password=password,
                        type="DECT",
                        context="pjsip_dect_tmp",
                    )

    def enable_subscription_mode(self):
        with self.lock:
            mode = self.ommclient.get_subscription_mode()
            if mode != "Configured":
                logger.info("enabled dect subscription mode")
                self.ommclient.set_subscription_mode("Configured")

    def get_unbound_devices(self):
        with self.lock:
            return self.ommclient.find_devices(
                lambda d: d.relType == mitel_ommclient2.types.PPRelTypeType("Unbound")
            )

    def get_user_by_extension(self, extension: str):
        with self.lock:
            users = list(self.ommclient.find_users(lambda u: u.num == extension))

        if len(users) != 1:
            raise RuntimeError(
                f"found {len(users)} for extension {extension.extension} in OMM"
            )
        return users[0]

    def configure_user_on_device(
        self, ext_name: str, ext_id: int, ext_password: str, device_ppn: int
    ) -> int:
        user = self.ommclient.create_user(str(ext_id))
        with self.lock:
            self.ommclient.set_user_sipauth(user.uid, str(ext_id), ext_password)
            self.ommclient.set_user_name(user.uid, str(ext_name))
            self.ommclient.attach_user_device(int(user.uid), device_ppn)

        return int(user.uid)

    def delete_user_from_device(self, user_id: int, device_ppn: int) -> None:
        with self.lock:
            self.ommclient.detach_user_device(uid=user_id, ppn=device_ppn)
            self.ommclient.delete_pp_user(id=user_id)

    def on_extension_delete(self, session, asterisk_session, _, extension):
        user = self.get_user_by_extension(extension.extension)
        with self.lock:
            self.ommclient.detach_user_device_by_user(user.uid)
            self.ommclient.delete_pp_user(user.uid)

    def on_extension_update(self, session, asterisk_session, _, extension):
        user = self.get_user_by_extension(extension.extension)
        with self.lock:
            self.ommclient.set_user_name(user.uid, extension.name)
