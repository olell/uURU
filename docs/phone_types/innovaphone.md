# Innovaphone

Support for

- `Innovaphone IP241`
- `Innovaphone IP112`
- `Innovaphone IP200a`

## Prerequesites

Add `innovaphone` to the list of enabled flavors in your config.

### DHCP

To use auto provisioning of Innovaphone devices add the following
snippet to your `dnsmasq.conf`:

```
dhcp-option=vendor:1.3.6.1.4.1.6666,215,"http://${UURU_WEB_HOST}/telephoning/innovaphone/update?mac=#m&localip=#i"
dhcp-option=vendor:1.3.6.1.4.1.6666,216,1
```

\_replace `${UURU_WEB_HOST}` accordingly

## Usage

Create extensions with the type of your innovaphone and enter the MAC
address in the format `aa-bb-cc-00-11-22`.

!!! info
    The letters must be lowercase and the bytes seperated by a hyphen!

