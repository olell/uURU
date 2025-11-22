---
title: Home
---
# µURU Documentation

The Micro User Registration Utility

## What is µURU

µURU is a PBX solution based on Asterisk[^1]. µURU focuses on user self-registration
to allow users to create their own extension and register various kinds of phones
to the exchange.

The systems is primarly intended for use at small events or community locations
(like hackspaces) where people want to bring and use their own phones. µURU is designed
to be easily extendable and has a very straight-forward deployment process using
docker-compose.

## Feature Overview

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

## Example Workflow

If a user has brought a telephone with them and wants to register it on the system,
the workflow is roughly as follows:

1. The user registers an account
2. The user creates a new extension, for which the following information is required
    - Type of telephone (e.g., SIP or DECT)
    - Name of the extension
    - Desired telephone number
    - Any additional information depending on the type of telephone

Once the entries have been saved, the corresponding extension is created and the phone can
be registered. For example, the SIP access data can be entered for a softphone, or a DECT
phone can be registered to a DECT antenna and automatically linked by calling a registration token.

The µURU supports a growing number of phone types. You can find out exactly how these can
be integrated and registered in the [phone documentation](todo).

*[PBX]: Private Branch Exchange
*[SIP]: Session Initiation Protocol
[^1]: [Asterisk](https://www.asterisk.org/): Open source private branch exchange software