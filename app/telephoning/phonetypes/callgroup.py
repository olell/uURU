from typing import Annotated, Literal
from pydantic import BaseModel
from app.telephoning.flavor import PhoneFlavor

class CallGroupFields(BaseModel):
    participants: list[str]


class CallGroup(PhoneFlavor):
    PHONE_TYPES = ["Callgroup"]
    DISPLAY_INDEX = -1
    PREVENT_SIP_CREATION = True
    
    EXTRA_FIELDS = CallGroupFields

    def on_extension_create(self, session, asterisk_session, extension):
        return super().on_extension_create(session, asterisk_session, extension)
    
    def on_extension_update(self, session, asterisk_session, extension):
        return super().on_extension_update(session, asterisk_session, extension)
    
    def on_extension_delete(self, session, asterisk_session, extension):
        return super().on_extension_delete(session, asterisk_session, extension)
    