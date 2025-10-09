"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import ClassVar, Literal, Optional, Self
from pydantic import BaseModel, PrivateAttr
from sqlmodel import Session, delete, select

from app.models.asterisk import DialPlanEntry


class BaseDialplanApp(BaseModel):
    """
    This is a baseclass for dialplan apps
    """

    COMPATIBLE_APP: ClassVar = ""

    _app: Optional[str] = PrivateAttr(None)
    _appdata: Optional[str] = PrivateAttr(None)

    @staticmethod
    def parse(app: str, appdata: str) -> Self:
        plan = BaseDialplanApp()
        plan._app = app
        plan._appdata = appdata
        return plan

    def assemble(self) -> tuple[str, str]:
        """
        returns values for app and appdata fields
        """
        return self._app, self._appdata


class Dial(BaseDialplanApp):
    """
    This abstracts the asterisk dial application it parses itself from appdata
    strings in the format

    device[&device[&...]][,timeout[,options]]
    """

    COMPATIBLE_APP: ClassVar = "Dial"

    devices: list[str]
    timeout: Optional[int] = None
    options: dict[str, str] = {}

    @staticmethod
    def parse(_, appdata):
        sections: list[str] = appdata.split(",")

        # devices are a list seperated by ampersands
        devices = sections[0].split("&")

        # timeout: integer of seconds or no value (for default)
        timeout = None
        if len(sections) > 1 and sections[1].isnumeric():
            timeout = int(sections[1])

        # options: list of characters with optionally parameters in paranthesis
        options = {}
        if len(sections) > 2:
            optstr = sections[2]
            while len(optstr):
                option = optstr[0]
                optstr = optstr[1:]
                params = None
                if len(optstr) > 0 and optstr[0] == "(":  # has params
                    end = optstr.find(")")
                    if end == -1:
                        raise RuntimeError(
                            f"Failed to parse options of dialplan application (missing closed paranthesis): {appdata}"
                        )
                    params = optstr[1:end]
                    if len(optstr) > end + 1:
                        optstr = optstr[end + 1 :]
                    else:
                        optstr = ""
                options.update({option: params})

        return Dial(devices=devices, timeout=timeout, options=options)

    def assemble(self):
        appdata = "&".join(self.devices)
        if self.timeout is None and self.options == {}:
            return self.COMPATIBLE_APP, appdata

        if self.timeout is None:
            appdata += ","
        else:
            appdata += f",{self.timeout}"

        if self.options != {}:
            appdata += ","
            for option in self.options.keys():
                appdata += option
                if self.options[option] is not None:
                    appdata += f"({self.options[option]})"

        return self.COMPATIBLE_APP, appdata


class Dialplan:

    def __init__(self, session_asterisk: Session, exten: str, context="pjsip_internal"):
        self.session = session_asterisk
        self.exten = exten
        self.context = context
        self.entries: dict[int, BaseDialplanApp] = {}

        self._load()

    def _parse(self, app: str, appdata: str) -> BaseDialplanApp:
        """
        Searches for a matching Dialplan App class and calls it's parse function
        if no match is found a BaseDialplanApp is returned
        """
        for subcls in BaseDialplanApp.__subclasses__():
            if subcls.COMPATIBLE_APP == app:
                return subcls.parse(app, appdata)
        return BaseDialplanApp.parse(app, appdata)

    def _load(self):
        """
        Loads existing dialplan entries from the database
        """

        entries = self.session.exec(
            select(DialPlanEntry)
            .where(DialPlanEntry.exten == self.exten)
            .where(DialPlanEntry.context == self.context)
        ).all()

        self.entries = {}
        for entry in entries:
            self.entries.update({entry.priority: self._parse(entry.app, entry.appdata)})

    def delete(self, autocommit=True):
        """
        Deletes the complete dialplan from the database
        """
        try:
            self.session.exec(
                delete(DialPlanEntry)
                .where(DialPlanEntry.exten == self.exten)
                .where(DialPlanEntry.context == self.context)
            )
            if autocommit:
                self.session.commit()
        except:
            if autocommit:
                self.session.rollback()
            raise

    def store(self, autocommit=True):
        """
        Deletes this dialplan and stores it again in the database
        """
        self.delete(autocommit)

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
                self.session.add(db_obj)
            if autocommit:
                self.session.commit()
        except:
            if autocommit:
                self.session.rollback()
            raise

        self._load()

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
