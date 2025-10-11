"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from app.models.crud.dialplan import Answer, ConfBridge, Dialplan, Hangup
from app.telephoning.flavor import PhoneFlavor


class Conference(PhoneFlavor):
    PHONE_TYPES = ["Conference"]
    IS_SPECIAL = True

    def on_extension_create(self, session, asterisk_session, user, extension):
        plan = Dialplan(asterisk_session, extension.extension)
        plan.add(Answer(), 1)
        plan.add(ConfBridge(conference=extension.extension), 2)
        plan.add(Hangup(), 3)
        plan.store(False)

    def on_extension_delete(self, session, asterisk_session, user, extension):
        plan = Dialplan(asterisk_session, extension.extension)
        plan.delete(False)
