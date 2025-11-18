# Grandstream

This flavor adds suport for some SNOM phones.

- `SNOM 3xx`

## Prerequesites

Add `snom` to the list of enabled flavors in your config.


### DHCP

Set DHCP option 66 to `{UURU_HOST}/telephoning/snom/snom`

## Usage

Create extensions with the type of your SNOM and enter the MAC
address in the format `aa-bb-cc-00-11-22`.

!!! info
    The letters must be lowercase and the bytes seperated by a hyphen!
