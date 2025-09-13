# WebSIP

µURU has an experimental WebSIP feature, this makes it possible to call phones
directly from a browser.

It works by creating temporary extensions ad-hoc when someone wants to call an
extension from the browser, the range for those extensions must be reserved
so that no other extensions can be registers in this range.

Once the extension was created signaling to the asterisk server is done via
websockets and media is transported via webrtc (using SIP.js). At the end of
the call the extension gets deleted again so that the range will hopefully never
be exhausted (of course depending on the size of the range).

To prevent problems with clients that do not unregister, µURU checks regulary
for orphaned/unused extensions. To keep extensions alive a client must send
at least every 3 minutes a keep alive request. All that is handled in the frontend.

### Please note

All modern browsers require webrtc to be transported securely, so you need to
use a reverse proxy with according certificates to enable secure transport for
at least the asterisk server.

### Configuration

| Key                         | Description                                              |
| --------------------------- | -------------------------------------------------------- |
| UURU_ENABLE_WEBSIP          | Enable websip (default is 1)                             |
| UURU_WEBSIP_PUBLIC          | If true (default) yo don't need an account to use websip |
| UURU_WEBSIP_WS_HOST         | External url where the asterisk websocket is reachable   |
| UURU_WEBSIP_EXTENSION_RANGE | Tuple of start and end of the range e.G. [9900, 9999]    |
