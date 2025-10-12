"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import ClassVar, Literal, Optional, Self

from pydantic import BaseModel, PrivateAttr


class BaseDialplanApp(BaseModel):
    """
    This is a baseclass for dialplan apps
    """

    DOC_URL: ClassVar = ""
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


class Answer(BaseDialplanApp):
    # TODO: Answer has options https://docs.asterisk.org/Latest_API/API_Documentation/Dialplan_Applications/Answer/#synopsis
    COMPATIBLE_APP: ClassVar = "Answer"

    @staticmethod
    def parse(_, appdata):
        return Answer()

    def assemble(self):
        return self.COMPATIBLE_APP, ""


class Hangup(BaseDialplanApp):
    COMPATIBLE_APP: ClassVar = "Dial"
    causecode: Optional[str] = None

    @staticmethod
    def parse(_, appdata):
        if appdata is not None and len(appdata) > 0:
            return Hangup(causecode=appdata)
        return Hangup()

    def assemble(self):
        causecode = "" if self.causecode is None else self.causecode
        return self.COMPATIBLE_APP, causecode


class Goto(BaseDialplanApp):
    COMPATIBLE_APP: ClassVar = "Goto"

    context: Optional[str] = None
    extension: Optional[str] = None
    priority: Optional[str] = None

    @staticmethod
    def parse(_, appdata):
        args = appdata.split(",")
        if len(args) == 3:
            return Goto(context=args[0], extension=args[1], priority=args[2])
        elif len(args) == 2:
            return Goto(extension=args[0], priority=args[1])
        else:
            return Goto(priority=args[0])

    def assemble(self):
        appdata = ""
        if self.context is not None and self.extension is not None:
            appdata += f"{self.context},{self.extension},"
        elif self.extension is not None:
            appdata += f"{self.extension},"
        appdata += self.priority
        return self.COMPATIBLE_APP, appdata


class Set(BaseDialplanApp):
    COMPATIBLE_APP: ClassVar = "Set"

    name: str
    value: str
    inherit_mode: Literal["none", "inherit", "inherit_children"] = "none"

    @staticmethod
    def parse(_, appdata: str):
        name, value = appdata.split("=")
        inherit_mode = "none"
        if name.startswith("__"):
            name = name[2:]
            inherit_mode = "inherit_children"
        elif name.startswith("_"):
            name = name[1:]
            inherit_mode = "inherit"
        return Set(name=name, value=value, inherit_mode=inherit_mode)

    def assemble(self):
        prefix = (
            "_"
            if self.inherit_mode == "inherit"
            else "__" if self.inherit_mode == "inherit_children" else ""
        )
        return self.COMPATIBLE_APP, f"{prefix}{self.name}={self.value}"


class ConfBridge(BaseDialplanApp):
    COMPATIBLE_APP: ClassVar = "ConfBridge"

    conference: str
    # TODO: There are more options: https://docs.asterisk.org/Latest_API/API_Documentation/Dialplan_Applications/ConfBridge/#description

    @staticmethod
    def parse(_, appdata):
        return ConfBridge(conference=appdata)

    def assemble(self):
        return self.COMPATIBLE_APP, self.conference


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
