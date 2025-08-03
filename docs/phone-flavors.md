# Implement custom phone flavors

uURU has a pluggable phone flavor system which can be used to implement
autoprovisioning or other functions for custom phone types.

Phone flavor classes are located in `/app/telephoning/phonetypes` and should
be called `{phone_flavor}.py`. In those file you must implement a class which
inherits `PhoneFlavor`.

The implemented classes are automatically discovered and enabled if the
`{phone_flavor}` is enabled in the configuration.

You can take a look at the `/app/telephoning/flavor.py` which contains the
base class to get more information about how to implement a new phone flavor.

## How does it work?

At application startup all classes inheriting `PhoneFlavor` are searched
and checked if enabled.
For enabled phone flavors then an instance will be created and stored. The will
be exactly one instance of every enabled phone flavor call at every time.

Then a router is created which is given to the class to implement custom http routes.
At last the job function of the flavor is called a first time to check if it
raises an `NotImplementedError`, if it does _not_, the job is scheduled with the defined
`JOB_INTERVAL` interval.



## How to implement?

Your class should be called like the phone type or brand your implementing
features for. The class must inherit `PhoneType`


```python filename="/app/telephoning/phonetypes/mitel_dect.py"
class DECT(PhoneFlavor):
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
# Supported codecs:
CODEC = Literal["g722", "alaw", "ulaw", "g726", "gsm", "lpc10"]
SUPPORTED_CODEC: CODEC | dict[str, CODEC] = "g722"

# If this flag is set to true, on creation of such a phone type no SIP
# account is created in the asterisk database
PREVENT_SIP_CREATION = False
``` 

And you can override some functions:
```python
def on_extension_create(self, session: Session, asterisk_session: Session, extension: "Extension")

on_extension_update(self, session: Session, asterisk_session: Session, extension: "Extension")

def on_extension_delete(self, session: Session, asterisk_session: Session, extension: "Extension")

def generate_routes(self, router: APIRouter)

def job(self)
```
