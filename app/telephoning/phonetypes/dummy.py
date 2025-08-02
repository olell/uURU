from app.telephoning.flavor import PhoneFlavor


class Dummy(PhoneFlavor):
    PHONE_TYPES = ["Dummy"]
    PREVENT_SIP_CREATION = True
    IS_SPECIAL = True