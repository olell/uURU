from pydantic import BaseModel, Field
from app.telephoning.flavor import PhoneFlavor

class GrandstreamExtraFields(BaseModel):
    mac: str = Field(pattern="^([0-9a-f]{2}-){5}[0-9a-f]{2}$")

class Grandstream(PhoneFlavor):

    PHONE_TYPES = ["Grandstream WP810"]
    IS_SPECIAL = True
    EXTRA_FIELDS = GrandstreamExtraFields
    SUPPORTED_CODEC = "g722"

    def generate_routes(self, router):
        pass