# uURU Configuration

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

### HTTP routing

> [!IMPORTANT]  
> Do not change those values, currently uURU contains some hardcoded links
> which will break otherwise!

| Key                     | Description                             | Default      |
| ----------------------- | --------------------------------------- | ------------ |
| UURU_WEB_PREFX          | Prefix after `/` for web routes         | empty        |
| UURU_API_V1_STR         | Prefix after `/` for api routes         | /api/v1      |
| UURU_TELEPHONING_PREFIX | Prefix after `/` for telephoning routes | /telephoning |

### Network

| Key                | Description                          | Default        |
| ------------------ | ------------------------------------ | -------------- |
| UURU_WEB_HOST      | Hostname / ip + port of the web host | 127.0.0.1:8000 |
| UURU_ASTERISK_HOST | Hostname / ip + port of the asterisk | 127.0.0.1      |

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

| Key                | Description                   | Default              |
| ------------------ | ----------------------------- | -------------------- |
| UURU_LDAP_SERVER   | LDAP server connection string | ldap://localhost:389 |
| UURU_LDAP_BASE_DN  | Base DN of the ldap server    | dc=uuru              |
| UURU_LDAP_USER     | Admin user of the ldap server | cn=admin,dc=uuru     |
| UURU_LDAP_PASSWORD | Password of the admin user    |                      |

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
