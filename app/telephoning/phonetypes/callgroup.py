from typing import Annotated, Literal
from pydantic import BaseModel, Field, computed_field
from app.core.config import settings
from app.models.crud.asterisk import (
    create_or_update_asterisk_dialplan_callgroup,
    delete_asterisk_dialplan_entry,
)
from app.telephoning.flavor import PhoneFlavor


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
    PREVENT_SIP_CREATION = True

    EXTRA_FIELDS = CallGroupFields

    def on_extension_create(self, session, asterisk_session, user, extension):
        create_or_update_asterisk_dialplan_callgroup(
            session, asterisk_session, user, extension
        )

    def on_extension_update(self, session, asterisk_session, user, extension):
        create_or_update_asterisk_dialplan_callgroup(
            session, asterisk_session, user, extension
        )

    def on_extension_delete(self, session, asterisk_session, user, extension):
        delete_asterisk_dialplan_entry(asterisk_session, extension, user)
