# Grandstream

This flavor adds suport for Grandstream phones

- `Grandstream WP810` (WiFi phone)
- `Grandstream GXP2160`

## Prerequesites

Add `grandstream` to the list of enabled flavors in your config.

### Configuration

If you want to use automatic WiFi provisioning for the `WP810` you
have to set some config keys:

| Key                          | Description              |
| ---------------------------- | ------------------------ |
| UURU_GRANDSTREAM_WIFI_SSID   | SSID of your network     |
| UURU_GRANDSTREAM_WIFI_PASSWD | Password of your network |


## Usage

Create extensions with the type of your grandstream and enter the MAC
address in the format `aa-bb-cc-00-11-22`.

!!! info
    The letters must be lowercase and the bytes seperated by a hyphen!
