# Instance Federation

µURU supports federation between instances using asterisks IAX2 protocol and
some inter-instance communication between µURU instances.

## Setup peering with another instance

To setup a peering connection with another instance first of all both instances
need to have a peer-to-peer network connection. If the two instances are not
in the same physical network, you may want to use a wireguard tunnel or something
similar, but thats up to you since it currently is out of scope for µURU.

After setting up a network connection you can navigate to `Admin -> Federation`
in the webinterface. Here you can see a list of peers and outgoing/incoming
peering requests.
To create a new peering requests with an other instace click the little plus-sign
on the `Outgoing Peering Requests` heading and enter a name for the peering
(the same name will be shown on the partner instance). The host must be the
web-address including protocol and if necessary port.

After sending your peering requests the other instance will see the request and
may now accept or decline the peering request. If you accept a peering request
all you have to do is to enter a prefix for your side.

To tear down the peering you can simply click the trash icon on the list of peers.

## Configuration

You have to set two configuration keys to setup peering:

### Configuration

| Key                       | Description                                                                      |
| ------------------------- | -------------------------------------------------------------------------------- |
| UURU_FEDERATION_IAX2_HOST | The hostname or ip-address of your asterisk server                               |
| UURU_FEDERATION_UURU_HOST | The web-address of your µURU instance including protocol (and if necessary port) |

The addresses for those config keys may differ from the web host / asterisk
address you've already configured. The reason for this is that you can use different
networks for peering and your telephony network (for example if you build your
peering using wireguard tunnels).

## Technical details

This is a step-by-step flow of what happens when setting up a peering:

1. Instance A -> Send peering request to partner instance
   - The outgoing request on your side is stored in the database
   - On the other side a incoming peering request is created, using an ID,
     the peering name, your µURU web and asterisk address, your extension
     length and a secret
2. Instance B -> Receive peering request
   - The incoming data is stored as an incoming peering request in the database
3. Instance B -> Admin accepts request
   - The incoming peering request is deleted and a IAX2 friend and dialplan entry
     in the asterisk database is created. The peer is also stored in the µURU
     database
   - The other side gets notified that you've accepted the request
4. Instance A -> Accept notification receive
   - Once Instance B accepted the request the outgoing request is deleted
     from the database and a IAX2 friend dialplan entry are stored in the
     asterisk database. The peer is stored in the µURU database.
5. Now that Instance A and B have IAX2 friends created for each other you can
   call each other using the selected prefix
