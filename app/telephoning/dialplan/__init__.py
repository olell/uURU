"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""


from typing import Literal, TypeVar, Union
from pydantic import Field
from sqlmodel import Session, delete, select

from app.models.asterisk import DialPlanEntry

# Import all applications here:
from app.telephoning.dialplan.applications import *

T = TypeVar("T", bound="BaseDialplanApp")


class Dialplan(BaseModel):

    exten: str
    context: str
    entries: dict[int, Union[BaseDialplanApp, T]] = Field(default_factory=dict)

    @staticmethod
    def from_db(session_asterisk: Session, exten: str, context="pjsip_internal"):
        plan = Dialplan(exten=exten, context=context)
        plan._load(session_asterisk)
        return plan

    @staticmethod
    def get_known_apps():
        return BaseDialplanApp.__subclasses__()

    def _parse(self, app: str, appdata: str) -> BaseDialplanApp:
        """
        Searches for a matching Dialplan App class and calls it's parse function
        if no match is found a BaseDialplanApp is returned
        """
        for subcls in Dialplan.get_known_apps():
            if subcls.COMPATIBLE_APP == app:
                return subcls.parse(app, appdata)
        return BaseDialplanApp.parse(app, appdata)

    def _load(self, session_asterisk: Session):
        """
        Loads existing dialplan entries from the database
        """

        entries = session_asterisk.exec(
            select(DialPlanEntry)
            .where(DialPlanEntry.exten == self.exten)
            .where(DialPlanEntry.context == self.context)
        ).all()

        self.entries = {}
        for entry in entries:
            self.entries.update({entry.priority: self._parse(entry.app, entry.appdata)})

    def delete(self, session_asterisk: Session, autocommit=True):
        """
        Deletes the complete dialplan from the database
        """
        try:
            session_asterisk.exec(
                delete(DialPlanEntry)
                .where(DialPlanEntry.exten == self.exten)
                .where(DialPlanEntry.context == self.context)
            )
            if autocommit:
                session_asterisk.commit()
        except:
            if autocommit:
                session_asterisk.rollback()
            raise

    def store(self, session_asterisk: Session, autocommit=True):
        """
        Deletes this dialplan and stores it again in the database
        """
        self.delete(session_asterisk, autocommit)

        try:
            for prio, entry in self.get_ordered_entries():
                app, appdata = entry.assemble()
                db_obj = DialPlanEntry(
                    context=self.context,
                    exten=self.exten,
                    priority=prio,
                    app=app,
                    appdata=appdata,
                )
                session_asterisk.add(db_obj)
            if autocommit:
                session_asterisk.commit()
        except:
            if autocommit:
                session_asterisk.rollback()
            raise

        self._load(session_asterisk)

    def add(self, app: BaseDialplanApp, prio: int | Literal["n"] = "n"):
        if prio == "n":
            prio = max(list(self.entries.keys()), default=0) + 1
        self.entries.update({prio: app})

    def remove(self, prio: int):
        if prio in self.entries.keys():
            del self.entries[prio]

    def get_ordered_entries(self) -> list[tuple[int, BaseDialplanApp]]:
        keys = list(self.entries.keys())
        keys.sort()
        return [(key, self.entries[key]) for key in keys]

    def __repr__(self):
        result = f"[{self.context}]\n"
        for prio, entry in self.get_ordered_entries():
            app, appdata = entry.assemble()
            result += f"exten => {self.exten},{prio},{app}({appdata})\n"
        return result[:-1]
