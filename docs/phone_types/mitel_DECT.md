# Mitel DECT

Register DECT phones using a Mitel OMM DECT setup.

## Prerequesites

Add `mitel_dect` to the list of enabled flavors in your config.

### Configuration

Configure following config keys:

| Key                  | Description                       |
| -------------------- | --------------------------------- |
| UURU_OMM_HOST        | Hostname or IP of the OMM         |
| UURU_OMM_PORT        | Port of the OMM                   |
| UURU_OMM_USER        | Username of the OMM admin user    |
| UURU_OMM_PASSWORD    | Password of the OMM admin user    |
| UURU_OMM_VERIFY_CERT | Should the https cert be verified |

### Configure the OMM

Todo!

## Usage

µURU automatically enables reigstration for the RFPs, so you can
directly connect your phone to the FP. Each new connected phone 
gets a temporary extension assigned which cannot be used to dial 
other users.

After creating an extension with the `DECT` type you can dial
the `token` displayed when you click on the key symbol in the
list of your extension. If the token was valid, the dect phone
will automatically be re-assigned to the actual extension and
can now be used to dial other extensions.


*[OMM]: Open Mobility Manager
*[FP]: Fixed Part - Dect Base Station