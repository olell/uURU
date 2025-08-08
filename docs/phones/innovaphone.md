# Innovaphone Autoprovisioning

## Enable flavor

Add `innovaphone` to the list of enable flavors in your config.

## DHCP

`uuru` supports auto provisioning of Innovaphone devices (currently `IP241` & `IP200a`).
To activate add the following snippet to your `dnsmasq.conf`:

```
dhcp-option=vendor:1.3.6.1.4.1.6666,215,"http://${UURU_WEB_HOST}/telephoning/innovaphone/update?mac=#m&localip=#i"
dhcp-option=vendor:1.3.6.1.4.1.6666,216,1
```

\_replace `${UURU_WEB_HOST}` accordingly
