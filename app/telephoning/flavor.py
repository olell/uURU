"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.extension import Extension

from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import Session

from app.core.config import settings


class PhoneFlavor:
    """
    PhoneFlavor class:

    this class is a base class to implement custom phone flavors for uuru.
    To implement those flavors, first set the metadata attributes below. Then
    you can implement the methods, if you want to use a constructor, you can
    create one.

    All methods are instance methods, there will be always exactly one instance
    of your child class while the application runs. It is created on application
    start.

    The on_extension_create/update/delete methods are called if the user does
    one of those actions in the frontend (or by api calls). The methods are
    called AFTER the according action was executing, except the delete action,
    the on_extension_delete is called BEFORE the extension is actually deleted.

    To see an example of how to implement a phonetype, take a look at
    app/telephoning/phonetypes/innovaphone.py

    You don't have to worry about importing and registrating a new phone flavor
    somewhere in the app, flavors are discovered and created automatically as
    long as they're located in the app.telephoning.phonetypes module.

    """

    # A list of strings which are used to identify a phone type, those strings
    # are also used to display the user a dropdown selection when creating a new
    # extension
    PHONE_TYPES: list[str] = []
    # PhoneFlavors are ordered by this value before displayed to the user, the
    # higher the more on top
    DISPLAY_INDEX: int = 0

    # A pydantic model which describes which fields need to be configured by
    # the user when creating a new extension with this phone type
    EXTRA_FIELDS: BaseModel | None = None

    # Special types may only be created by admin users, this behavior
    # can be overwritten by configuring ALL_EXTENSION_TYPES_PUBLIC as true
    IS_SPECIAL: bool = False

    # Job interval in seconds
    JOB_INTERVAL: int = 60

    # When extensions are created the asterisk phonetype is configured based
    # on this value. If its a string, the value is applied for all phone types
    # in this flavor class. If it is a dict, it has to configure values for
    # all phone types from this class.
    # Supported codecs:
    CODEC = Literal["g722", "alaw", "ulaw", "g726", "gsm", "lpc10"]
    SUPPORTED_CODEC: CODEC | dict[str, CODEC] = "g722"

    # If this flag is set to true, on creation of such a phone type no SIP
    # account is created in the asterisk database
    PREVENT_SIP_CREATION = False

    def on_extension_create(
        self,
        session: Session,
        asterisk_session: Session,
        user: "User",
        extension: "Extension",
    ):
        pass

    def on_extension_update(
        self,
        session: Session,
        asterisk_session: Session,
        user: "User",
        extension: "Extension",
    ):
        pass

    def on_extension_delete(
        self,
        session: Session,
        asterisk_session: Session,
        user: "User",
        extension: "Extension",
    ):
        pass

    def generate_routes(self, router: APIRouter):
        """
        This method is called on application startup, here you can create routes
        using the standard FastAPI router interfaces.

        Routes from the router are prefixed with
        `/{settings.TELEPHONING_PREFIX}/{NAME OF THIS CLASS IN LOWERCASE}/`

        To obtain access to the Database Session / Asterik Session use the
        dependencies from `app.core.db`

        Example for a route, created inside this function:
        ```
        @router.post("/")
        def do_something():
            pass
        ```
        """
        pass

    def job(self) -> None:
        """
        This function may implement a job which runs regulary in the app
        background. The job is executed once on application start.

        If itraises an NotImplementedError it will not be scheduled.
        """
        raise NotImplementedError

    ## DO NOT OVERWRITE THOSE METHODS
    def is_public(self):
        return settings.ALL_EXTENSION_TYPES_PUBLIC or not self.IS_SPECIAL

    def get_schema(self):
        if self.EXTRA_FIELDS is None:
            return None

        return self.EXTRA_FIELDS.model_json_schema()
