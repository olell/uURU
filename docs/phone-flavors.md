# Implement custom phone flavors

µURU has a pluggable phone flavor system which can be used to implement
autoprovisioning or other functions for custom phone types.

Phone flavor classes are located in `/app/telephoning/phonetypes` and should
be called `{phone_flavor}.py`. In those file you must implement a class which
inherits `PhoneFlavor` or any other class inheriting `PhoneFlavor`.

The implemented classes are automatically discovered and enabled if the
`{phone_flavor}` is enabled in the configuration.

You can take a look at the `/app/telephoning/flavor.py` which contains the
base class to get more information about how to implement a new phone flavor.

## How does it work?

At application startup all classes inheriting `PhoneFlavor` are searched
and checked if enabled.
For enabled phone flavors then an instance will be created and stored. There will
be exactly one instance of every enabled phone flavor call at every time.

Then a router is created which is given to the class to implement custom http routes.
At last the job function of the flavor is called a first time to check if it
raises an `NotImplementedError`, if it does _not_, the job is scheduled with the defined
`JOB_INTERVAL` interval.

## How to implement?

Your class should be called like the phone type or brand your implementing
features for. The class must inherit `PhoneType` or another already existing
flavor. If you want to use an SIP-Account within your flavor you should
inherit your flavor from the `SIP` flavor which  can be imported `#!python from app.telephoning.phonetypes.sip import SIP`

```python
class ExamplePhone(SIP):
    ...
```

you can implement a constructor if you want to.

now your class can implement a variety of fields and functions to define its
behavor:

```python

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
# Supported codecs: "g722", "alaw", "ulaw", "g726", "gsm", "lpc10"
SUPPORTED_CODEC: CODEC | dict[str, CODEC] = "g722"

# This limits the maximum amount of characters for the extension name
MAX_EXTENSION_NAME_CHARS = 20

# This dict defines which media is required (or optional) for this phonetype
# take a look at the features/media documentation for more information.
MEDIA: dict[str, MediaDescriptor] = {}
```

And you can override some methods:
!!! Note
    If you inherit the SIP flavor for your phone, you must call the super method if you want to override the `on_extension_xyz` methods because thats the place
    where the SIP account is created.

    Like this: `#!python super().on_extension_update(session, asterisk_session, user, extension)`

```python
def on_extension_create(
    self,
    session: Session,
    asterisk_session: Session,
    user: "User",
    extension: "Extension",
):
    """
    This function is called after the user created the extension.
    """

def on_extension_update(
    self,
    session: Session,
    asterisk_session: Session,
    user: "User",
    extension: "Extension",
):
    """
    This function is called on any change to the extension.
    """

def on_extension_delete(
    self,
    session: Session,
    asterisk_session: Session,
    user: "User",
    extension: "Extension",
):
    """
    This function is called before the extension gets deleted.
    """

def generate_routes(self, router: APIRouter):
    """
    This method is called on application startup, here you can create routes
    using the standard FastAPI router interfaces.

    Routes from the router are prefixed with
    `/{settings.TELEPHONING_PREFIX}/{NAME OF THIS CLASS IN LOWERCASE}/`

    To obtain access to the Database Session / Asterisk DB Session use the
    dependencies from `app.core.db`

    Example for a route, created inside this function:
    ```
    @router.post("/")
    def do_something():
        pass
    ```
    """

def job(self):
    """
    This function may implement a job which runs regulary in the app
    background. The job is executed once on application start.

    If it raises an NotImplementedError it will not be scheduled.
    """

def get_codec(self, extension: "Extension | None"):
    """
    This function can modify how the codec for the SIP account is
    determined, normally you don't need to override it.
    """
```