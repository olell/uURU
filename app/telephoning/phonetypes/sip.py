"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from pydantic import BaseModel

from app.core.config import settings
from app.models.asterisk import MusicOnHold
from app.models.crud.asterisk import (
    create_music_on_hold,
    create_sip_account,
    delete_music_on_hold,
    delete_sip_account,
    get_music_on_hold_by_name,
    update_music_on_hold,
    update_sip_account,
)
from app.models.crud.dialplan import Dial, Dialplan
from app.models.media import AudioFormat, MediaType
from app.telephoning.flavor import CODEC, MediaDescriptor, PhoneFlavor


class SIPFields(BaseModel):
    codec: CODEC = "g722"


class SIP(PhoneFlavor):
    PHONE_TYPES = ["SIP"]
    IS_SPECIAL = False
    DISPLAY_INDEX = 1000
    EXTRA_FIELDS = SIPFields

    MEDIA = {
        "moh": MediaDescriptor(
            media_type=MediaType.AUDIO,
            required=False,
            label="Ringback Tone / Music on Hold",
            out_format=AudioFormat(
                out_type="mp3", samplerate=44100, channels=1, bitdepth=16
            ),
        )
    }

    def on_extension_create(self, session, asterisk_session, user, extension):
        super().on_extension_create(session, asterisk_session, user, extension)
        create_sip_account(
            asterisk_session,
            extension=extension.extension,
            extension_name=extension.name,
            password=extension.password,
            codec=self.get_codec(extension),
            autocommit=False,
        )
        create_music_on_hold(asterisk_session, extension, autocommit=False)

    def on_extension_update(self, session, asterisk_session, user, extension):
        super().on_extension_update(session, asterisk_session, user, extension)
        update_sip_account(
            asterisk_session,
            extension,
            autocommit=False,
        )
        update_music_on_hold(asterisk_session, extension, autocommit=False)

    def on_extension_delete(self, session, asterisk_session, user, extension):
        super().on_extension_delete(session, asterisk_session, user, extension)
        delete_sip_account(
            asterisk_session,
            extension.extension,
            autocommit=False,
        )
        delete_music_on_hold(asterisk_session, extension, autocommit=False)

    def get_codec(self, extension) -> CODEC:
        """
        if an extra field "codec" exists, it returns that, otherwise
        it uses the value from SUPPORTED_CODEC
        """
        if extension is None:
            return super().get_codec(extension)

        codec = extension.get_extra_field("codec")
        if codec is not None:
            return codec

        return super().get_codec(extension)
