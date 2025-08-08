"""
uURU - Micro User Registration Utility

Copyright (c) Ole Lange, Gregor Michels and contributors. All rights reserved.
Licensed under the MIT license. See LICENSE file in the project root for details.
"""

import importlib
import pkgutil
from fastapi import APIRouter, FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import json
from logging import getLogger

from app.core.config import settings
from app.telephoning.flavor import PhoneFlavor

logger = getLogger(__name__)


def load_phone_flavors() -> list[PhoneFlavor]:
    """
    loads all classes which inherit PhoneFlavor and are located in
    "app/telephoning/phonetypes/*" and returns them as a list
    """
    package = importlib.import_module("app.telephoning.phonetypes")

    phone_flavors = []

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if module_name not in settings.ENABLED_PHONE_FLAVORS:
            continue
        module = importlib.import_module(f"app.telephoning.phonetypes.{module_name}")

        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            if (
                isinstance(attr, type)
                and issubclass(attr, PhoneFlavor)
                and attr is not PhoneFlavor
            ):
                phone_flavors.append(attr)

    return phone_flavors


class Telephoning(object):
    _instance = None

    @staticmethod
    def instance():
        if Telephoning._instance is None:
            Telephoning._instance = Telephoning()

        return Telephoning._instance

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.router = APIRouter(prefix=settings.TELEPHONING_PREFIX, tags=["phones"])

        self.flavor_classes = load_phone_flavors()
        self.flavors: dict[str, PhoneFlavor] = {}

        self.flavor_by_type = {}
        self.all_types = []

    def start(self, app: FastAPI):

        for cls in self.flavor_classes:
            # 1st: create instance
            flavor_name = cls.__name__.lower()
            if flavor_name in self.flavors:
                raise RuntimeError("Flavor classes must have unique names!")

            logger.info(f"Discovered phone flavor: {flavor_name}")

            flavor: PhoneFlavor = cls()

            # 2nd: create routes
            router = APIRouter(prefix=f"/{flavor_name}")
            flavor.generate_routes(router)
            self.router.include_router(router)

            # 3rd: initiate job
            try:
                flavor.job()
            except NotImplementedError:
                pass  # do not schedule job
            else:
                self.scheduler.add_job(
                    flavor.job, "interval", seconds=flavor.JOB_INTERVAL
                )

            logger.debug(f"Initiated router and job for {flavor_name}")

            self.flavors.update({flavor_name: flavor})
            self.flavor_by_type.update(
                {phone_type: flavor for phone_type in flavor.PHONE_TYPES}
            )

        # create list of all phone types
        flavors = list(self.flavors.values())
        flavors.sort(key=lambda f: -f.DISPLAY_INDEX)
        for flavor in flavors:
            self.all_types.extend(flavor.PHONE_TYPES)

        logger.info(f"Supported phone types are {', '.join(self.all_types)}")

        # start scheduler and include router
        self.scheduler.start()
        app.include_router(self.router)

    def stop(self):
        # stop all jobs
        self.scheduler.shutdown()

    @staticmethod
    def get_flavor_by_type(phone_type: str) -> PhoneFlavor | None:
        """
        returns the instance of the PhoneFlavor which supports the given
        phone_type, if there isn't such instance, it returns None
        """
        return Telephoning.instance().flavor_by_type.get(phone_type)

    @staticmethod
    def get_all_phone_types() -> list[str]:
        """
        returns a list of all supported phone types
        """
        return Telephoning.instance().all_types

    @staticmethod
    def get_schemas(as_json=True) -> dict[str, dict] | str:
        """
        returns a dict containing all json schemas
        """
        self = Telephoning.instance()
        schemas = {}

        for phone_type in self.all_types:
            flavor: PhoneFlavor = self.flavor_by_type[phone_type]
            schema = flavor.get_schema()
            if schema is not None:
                schemas.update({phone_type: schema})
        return schemas if not as_json else json.dumps(schemas)
