import importlib
import pkgutil
from fastapi import APIRouter, FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.telephoning.flavor import PhoneFlavor

def load_phone_flavors() -> list[PhoneFlavor]:
    """
    loads all classes which inherit PhoneFlavor and are located in
    "app/telephoning/phonetypes/*" and returns them as a list
    """
    package = importlib.import_module("app.telephoning.phonetypes")
    
    phone_flavors = []

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
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
        self.router = APIRouter(prefix=settings.TELEPHONING_PREFIX, tags=["telephoning"])

        self.flavor_classes = load_phone_flavors()
        self.flavors = {}

    def start(self, app: FastAPI):
        
        for cls in self.flavor_classes:
            # 1st: create instance
            flavor_name = cls.__name__.lower()
            if flavor_name in self.flavors:
                raise RuntimeError("Flavor classes must have unique names!")

            flavor = cls()

            # 2nd: create routes
            router = APIRouter(prefix=f"/{flavor_name}")
            flavor.generate_routes(router)
            self.router.include_router(router)

            # 3rd: initiate job
            try:
                flavor.job()
            except NotImplementedError:
                pass # do not schedule job
            else:
                self.scheduler.add_job(flavor.job, "interval", seconds=flavor.JOB_INTERVAL)

            self.flavors.update({flavor_name: flavor})
        
        # start scheduler and include router
        self.scheduler.start()
        app.include_router(self.router)


    def stop(self):
        # stop all jobs
        self.scheduler.shutdown()

    def get_flavor_by_type(self, phone_type: str) -> PhoneFlavor | None:
        """
        returns the instance of the PhoneFlavor which supports the given
        phone_type, if there isn't such instance, it returns None
        """
        for flavor in self.flavors.values():
            if phone_type in flavor.PHONE_TYPES:
                return flavor
        return None
    
    def get_all_phone_types(self) -> list[str]:
        """
        returns a list of all supported phone types
        """
        types = []
        for flavor in self.flavors.values():
            types.extend(flavor.PHONE_TYPES)

        return types