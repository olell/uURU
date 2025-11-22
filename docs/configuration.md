# Configuration

uURU is configured via environment variables or an .env file. This should
give you an overview about the supported config keys.

### Default credentials

The credentials for the first created account are configured by

| Key                        | Description | Default    |
| -------------------------- | ----------- | ---------- |
| UURU_DEFAULT_ROOT_USER     | Username    | root       |
| UURU_DEFAULT_ROOT_PASSWORD | Password    | rootpasswd |

### Security

| Key                              | Description                            | Default           |
| -------------------------------- | -------------------------------------- | ----------------- |
| UURU_SECRET_KEY                  | Secret key used to sign session tokens | random (32 chars) |
| UURU_ACCESS_TOKEN_EXPIRE_MINUTES | Minutes until a login expires          | 8 days (11520)    |
| UURU_BACKEND_CORS_ORIGINS        | A list of allowed CORS origins         | `[]`              |

### HTTP routing

!!! warning
Do not change those values, currently uURU contains some hardcoded links
which will break otherwise!

| Key                     | Description                             | Default      |
| ----------------------- | --------------------------------------- | ------------ |
| UURU_WEB_PREFIX         | Prefix after `/` for web routes         | empty        |
| UURU_API_V1_STR         | Prefix after `/` for api routes         | /api/v1      |
| UURU_TELEPHONING_PREFIX | Prefix after `/` for telephoning routes | /telephoning |

### Network

| Key                | Description                          | Default        |
| ------------------ | ------------------------------------ | -------------- |
| UURU_WEB_HOST      | Hostname / ip + port of the web host | 127.0.0.1:8000 |
| UURU_ASTERISK_HOST | Hostname / ip + port of the asterisk | 127.0.0.1      |

### Federation

| Key                       | Description                                              | Default               |
| ------------------------- | -------------------------------------------------------- | --------------------- |
| UURU_FEDERATION_IAX2_HOST | The hostname or ip-address of your asterisk server       | 127.0.0.1             |
| UURU_FEDERATION_UURU_HOST | The web-address of your µURU instance including protocol | http://127.0.0.1:8000 |

### Application Database

| Key                    | Description                                                  | Default  |
| ---------------------- | ------------------------------------------------------------ | -------- |
| UURU_DATABASE_TYPE     | Type of database for the application ("mysql" or "postgres") | postgres |
| UURU_DATABASE_SERVER   | Host of the application database                             |          |
| UURU_DATABASE_PORT     | Port for the application database                            | 5432     |
| UURU_DATABASE_USER     | User for the application database                            |          |
| UURU_DATABASE_PASSWORD | Password for the application database                        |          |
| UURU_DATABASE_DB       | Database for the application database                        |          |

### Asterisk Database

The database must be a mariadb / mysql db

| Key                             | Description                        | Default |
| ------------------------------- | ---------------------------------- | ------- |
| UURU_ASTERISK_DATABASE_SERVER   | Host of the asterisk database      |         |
| UURU_ASTERISK_DATABASE_PORT     | Port for the asterisk database     | 3306    |
| UURU_ASTERISK_DATABASE_USER     | User for the asterisk database     |         |
| UURU_ASTERISK_DATABASE_PASSWORD | Password for the asterisk database |         |
| UURU_ASTERISK_DATABASE_DB       | Database for the asterisk database |         |

### LDAP

| Key                            | Description                       | Default              |
| ------------------------------ | --------------------------------- | -------------------- |
| UURU_LDAP_SERVER               | LDAP server connection string     | ldap://localhost:389 |
| UURU_LDAP_BASE_DN              | Base DN of the ldap server        | dc=uuru              |
| UURU_LDAP_USER                 | Admin user of the ldap server     | cn=admin,dc=uuru     |
| UURU_LDAP_PASSWORD             | Password of the admin user        |                      |
| UURU_LDAP_PUBLIC_HOST          | IP or Hostname of the LDAP server | 127.0.0.1            |
| UURU_LDAP_PUBLIC_BIND_USER     | User for public connections       | cn=public,dc=uuru    |
| UURU_LDAP_PUBLIC_BIND_PASSWORD | Password for public connections   | public               |

### Application Behavior

| Key                     | Description                                                 | Default |
| ----------------------- | ----------------------------------------------------------- | ------- |
| UURU_LOGLEVEL           | One of CRITICAL, FATAL, ERROR, WARNING, INFO, DEBUG         | INFO    |
| UURU_LIFESPAN_DROP_DB   | (For dev!) drop the database after application shutdown     | False   |
| UURU_LEGACY_FRONTEND    | Enable legacy UI                                            | False   |
| UURU_LIMIT_REGISTRATION | Limit registrations by requiring an invite code to register | False   |

### Telephoning

| Key                             | Description                                                         | Default      |
| ------------------------------- | ------------------------------------------------------------------- | ------------ |
| UURU_EXTENSION_DIGITS           | Required extension number length                                    | 4            |
| UURU_EXTENSION_PASSWORD_LENGTH  | Length of SIP password                                              | 20           |
| UURU_EXTENSION_PASSWORD_CHARS   | Charset from which the password is generated                        | digits (0-9) |
| UURU_EXTENSION_TOKEN_PREFIX     | Prefix for generated token                                          | 01990        |
| UURU_EXTENSION_TOKEN_LENGTH     | Number of digits after the prefix                                   | 8            |
| UURU_RESERVED_EXTENSIONS        | List of reserved extensions, e.G. [1234, [1000, 2000]]              | []           |
| UURU_RESERVED_NAME_PREFIXES     | List of prefixes which normal users may not use for extension names | []           |
| UURU_ALL_EXTENSION_TYPES_PUBLIC | May normal users create extension with all phone types              | False        |
| UURU_ENABLED_PHONE_FLAVORS      | A list of enabled phone flavors                                     | ["sip"]      |

### Site

| Key            | Description                                       | Default   |
| -------------- | ------------------------------------------------- | --------- |
| UURU_SITE_NAME | Name of your uURU setup                           | "Default" |
| UURU_SITE_LAT  | Optional latitude of your location, used for map  | 0         |
| UURU_SITE_LON  | Optional longitude of your location, used for map | 0         |

### Pages

| Key               | Description                           | Default |
| ----------------- | ------------------------------------- | ------- |
| UURU_ENABLE_PAGES | True / False                          | True    |
| UURU_PAGES_TITLE  | Title of the Pages dropdown in Navbar | Pages   |

### WebSIP

!!! note
The `UURU_WEBSIP_EXTENSION_RANGE` should be reserved via the `UURU_RESERVED_EXTENSIONS` key.

| Key                         | Description                                            | Default                |
| --------------------------- | ------------------------------------------------------ | ---------------------- |
| UURU_ENABLE_WEBSIP          | Enable websip                                          | True                   |
| UURU_WEBSIP_PUBLIC          | If true you don't need an account to use websip        | True                   |
| UURU_WEBSIP_WS_HOST         | External url where the asterisk websocket is reachable | ws://127.0.0.1:8088/ws |
| UURU_WEBSIP_EXTENSION_RANGE | Tuple of start and end of the range                    | [9900, 9999]           |

### Media

| Key                             | Description                                            | Default         |
| ------------------------------- | ------------------------------------------------------ | --------------- |
| UURU_MEDIA_PATH                 | Path to a directory where media files should be stored | ./uploads/      |
| UURU_MEDIA_MAX_SIZE_USER        | Maximum amount of bytes a user might upload            | 2097152 (2 MiB) |
| UURU_MEDIA_LIMIT_SIZE_ADMIN     | Apply the limit also for admin users                   | 0               |
| UURU_MEDIA_ALLOW_RAW            | Allow upload of raw files                              | 0               |
| UURU_MEDIA_IMAGE_STORAGE_FORMAT | Format in which images should be stored on disk        | png             |
| UURU_MEDIA_AUDIO_STORAGE_FORMAT | Format in which audio files should be stored on disk   | mp3             |

### Asterisk Manager Interface

!!! info
    Because the `asterisk` container is exposed via `--network=host` we have to bind the AMI interface to a specific (non 127.0.0.0/8) ip.
    We assume that your docker installation ships with `docker0` on `172.17.0.1` - change to your setup if needed.

!!! danger
    By default all other containers/processes on your machine can talk via `AMI` to the `asterisk`.
    We assume a trusted environment.
    Please generate a secure `UURU_ASTERISK_AMI_PASS` for production setups.


| Key                    | Description                                 | Default                    |
| ---------------------- | ------------------------------------------- | -------------------------- |
| UURU_ASTERISK_AMI_USER | Username for the asterisk manager interface | uuru_ami_user              |
| UURU_ASTERISK_AMI_PASS | Secret for the asterisk manager interface   | uuru_ami_secret            |
| UURU_ASTERISK_AMI_ADDR | Host of the asterisk manager interface      | 172.17.0.1 (Docker bridge) |
| UURU_ASTERSIK_AMI_PORT | Port of the asterisk manager interface      | 5038                       |
