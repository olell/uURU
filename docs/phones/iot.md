# IoT Phone Type

To enable autoprovisioning of IoT SIP devices you can exchange a secret for
information about the extension. To do so you can create an extension with type
`IoT` and set a secret, now you can request the details via http endpoint.

The url for this endpoint is `http[s]://{web host}/telephoning/iot/{your secret}`. You can optionally
append a `?format={format}` to receive the data in `csv` or `xml` it defaults
to `json`.

## Example response(s):

### json

```json
{
  "server": "192.168.42.254",
  "transport": "udp",
  "name": "Test IoT",
  "location_name": "",
  "lon": 114324760,
  "password": "1895",
  "public": true,
  "type": "IoT",
  "extension": "6562",
  "lat": 513765576,
  "token": "0199002940654",
  "info": "",
  "user_id": "2908dc6a-6658-4379-888b-c72f479221ae",
  "extra_fields": { "secret": "some-secret-string" }
}
```

### csv

```csv
server,transport,name,location_name,lon,password,public,type,extension,lat,token,info,user_id,extra_fields
192.168.42.254,udp,Test IoT,,114324760,1895,True,IoT,6562,513765576,0199002940654,,2908dc6a-6658-4379-888b-c72f479221ae,{'secret': 'some-secret-string'}
```

### xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<root>
    <server>192.168.42.254</server>
    <transport>udp</transport>
    <name>Test IoT</name>
    <location_name></location_name>
    <lon>114324760</lon>
    <password>1895</password>
    <public>true</public>
    <type>IoT</type>
    <extension>6562</extension>
    <lat>513765576</lat>
    <token>0199002940654</token>
    <info></info>
    <user_id>2908dc6a-6658-4379-888b-c72f479221ae</user_id>
    <extra_fields>
        <secret>some-secret-string</secret>
    </extra_fields>
</root>
```

## Further considerations

The IoT device should probably receive the endpoint (without the secret) via DHCP. If it's secure enough for you, you may use an unique identifier of your device like the MAC-Address as secret.
