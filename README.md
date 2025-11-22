# Micro User Registration Utility

µURU is a telephone self registration utility based on asterisk 
intended for small events and communities.


## 🚀 Get Started

To see how to get started with setting up µURU and how to configure
it take a look at the

**Documentation:** https://olell.github.io/uURU/

## ⚡️ Features:

- Pluggable Phone-Flavor system, currently supporting
  - Basic SIP extensions
  - Innovaphone IP241, IP200A, IP112
  - Mitel DECT OMM integration
  - Grandstream WP810 WiFi Phones
  - SNOM 300
  - Dummy extensions
  - IoT extensions
- Callgroups
- Conferences
- Federation between µURU instances
- WebSIP to initiate calls directly from the browser
- Originate calls via physical phones from the browser
- LDAP Phonebook
- Rendering of Markdown for (Help-)Pages
- Managing of images, audio files and other media
- Prometheus HTTP Service-Discovery (**currently only for Innovaphones**)
- Super-Simplified deployment of the whole PBX by using docker compose



## 🏗️ Architecture

This project is based on multiple components:

- `uuru` which is the frontend
- `asterisk` which is the actual PBX
- `openldap` for the phonebook

`uuru` configures the `asterisk` via the database integration. 
Additionally `uuru` has an own database and creates an `ldap`
directory.

Due to pluggable phone-flavors it is pretty simple to build
integration for new telephone types. See the [docs](https://olell.github.io/uURU/phone-flavors/)
how to implement such a flavor.

## 🔑 License

`uURU` is released under the `MIT` license - see `LICENSE` for more information.

Javascript / CSS files in `/frontend` may be released under different
licenses. Please refer to the file's header for more information.
