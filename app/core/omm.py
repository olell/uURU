import random
import string
from typing import Annotated
import uuid
from fastapi import Depends
import mitel_ommclient2
import mitel_ommclient2.types
from sqlmodel import Session
from app.core.config import settings
from app.core.db import engine, engine_asterisk
from app.core.security import generate_extension_password
from app.models.crud.asterisk import create_asterisk_tmp_extension
from app.models.extension import TemporaryExtension


class OMM:
    _instance = None

    @staticmethod
    def get_instance():
        if OMM._instance is None:
            OMM._instance = OMM()

        return OMM._instance

    def __init__(self):
        if not settings.OMM_ENABLE:
            return

        self.ommclient = mitel_ommclient2.OMMClient2(
            host=settings.OMM_HOST,
            port=settings.OMM_PORT,
            username=settings.OMM_USER,
            password=settings.OMM_PASSWORD,
            ommsync=True,
        )

    @staticmethod
    def job():
        if not settings.OMM_ENABLE:
            return

        omm = OMM.get_instance()

        for device in omm.get_unbound_devices():
            tmp_ext_id = TemporaryExtension.generate_extension()
            password = generate_extension_password()

            user_id = omm.configure_user_on_device(
                tmp_ext_id, tmp_ext_id, password, (device.ppn)
            )

            tmp_ext = TemporaryExtension(
                extension=tmp_ext_id,
                password=password,
                uid=user_id,
                ppn=device.ppn,
            )

            with Session(engine) as session:
                session.add(tmp_ext)
                session.commit()

                with Session(engine_asterisk) as session_asterisk:
                    create_asterisk_tmp_extension(session_asterisk, tmp_ext)

    def get_unbound_devices(self):
        if not settings.OMM_ENABLE:
            return
        return self.ommclient.find_devices(
            lambda d: d.relType == mitel_ommclient2.types.PPRelTypeType("Unbound")
        )

    def configure_user_on_device(
        ext_name: str, ext_id: int, ext_password: str, device_ppn: int
    ) -> int:
        omm = OMM.get_instance()

        user = omm.ommclient.create_user(ext_name)
        omm.ommclient.set_user_sipauth(user.uid, ext_id, ext_password)
        omm.ommclient.set_user_name(user.uid, ext_name)
        omm.ommclient.attach_user_device(int(user.uid), device_ppn)

        return int(user.uid)

    def delete_user_from_device(user_id: int, device_ppn: int) -> None:
        omm = OMM.get_instance()

        omm.ommclient.detach_user_device(uid=user_id, ppn=device_ppn)
        omm.ommclient.delete_pp_user(id=user_id)


OMMDep = Annotated[OMM, Depends(OMM.get_instance)]
