"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import Annotated, Literal
from pydantic import BaseModel, Field, computed_field
from app.core.config import settings
from app.models.crud.asterisk import (
    create_music_on_hold,
    create_or_update_callgroup,
    delete_music_on_hold,
    update_music_on_hold,
)
from app.telephoning.dialplan import Dialplan
from app.models.media import AudioFormat, MediaType
from app.telephoning.flavor import MediaDescriptor, PhoneFlavor


class CallGroupFields(BaseModel):
    # todo, were expecting the user to enter a string of comma seperated extensions
    # this is due to frontend limitations. When doing the frontend rewrite, it shall
    # use a properly typed list[str]
    participants: str = Field(
        pattern=rf"^\d{{{settings.EXTENSION_DIGITS}}}(\s*,\s*\d{{{settings.EXTENSION_DIGITS}}})*$"
    )

    @computed_field
    @property
    def participants_list(self) -> list[str]:
        return [p.strip() for p in self.participants.split(",")]


class CallGroup(PhoneFlavor):
    PHONE_TYPES = ["Callgroup"]
    DISPLAY_INDEX = -1

    EXTRA_FIELDS = CallGroupFields

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
        create_music_on_hold(asterisk_session, extension, autocommit=False)
        dialplan_options = {}
        if extension.get_assigned_media("moh"):
            dialplan_options.update({"m": f"moh_{extension.extension}"})

        create_or_update_callgroup(
            session, asterisk_session, user, extension, dialplan_options
        )

    def on_extension_update(self, session, asterisk_session, user, extension):
        update_music_on_hold(asterisk_session, extension, autocommit=False)
        dialplan_options = {}
        if extension.get_assigned_media("moh"):
            dialplan_options.update({"m": f"moh_{extension.extension}"})

        create_or_update_callgroup(
            session, asterisk_session, user, extension, dialplan_options
        )

    def on_extension_delete(self, session, asterisk_session, user, extension):
        delete_music_on_hold(asterisk_session, extension, autocommit=False)
        Dialplan.from_db(asterisk_session, extension.extension).delete(asterisk_session)
