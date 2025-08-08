from app.telephoning.flavor import PhoneFlavor


class SIP(PhoneFlavor):
    PHONE_TYPES = ["SIP"]
    DISPLAY_INDEX = 1000
    IS_SPECIAL = False
