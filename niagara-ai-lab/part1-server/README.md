# Part 1 — Publishing station points as a server

This part covers one direction only: **station point → protocol object that an outside
client can read or write**. The station is the server; something else is the client.

Every protocol in this part follows the same three-step shape:

| Step | BACnet export | oBIX export | Modbus TCP slave |
|:--|:--|:--|:--|
| 1 · Create the object | REST `add` | REST `add` | REST `add` with `PROXY`, or `cp` from a built point |
| 2 · Bind the source or address | `pointOrd` → **oBIX PUT** | `point` → **oBIX PUT** | `dataAddress` → **REST mod** |
| 3 · Assign public identity | `objectId` → REST mod | binding is the identity | binding is the identity |

Two rows in step 2 are `BOrd` slots — a station ord, not a string — so they are written as
`<uri>` over oBIX. Everything else in the table goes through the REST batch.

## Documents

| Document | Protocol | What it answers |
|:--|:--|:--|
| [`niagara-bacnet-server-points.md`](./niagara-bacnet-server-points.md) | BACnet/IP | Three-layer enable order, `exportTable`, the three slots split across two channels, and the rename that happens the moment `objectId` is written |
| [`niagara-obix-server-points.md`](./niagara-obix-server-points.md) | oBIX | The `point` slot, `<value>/set/` for writes, and which channel writes which step |
| [`niagara-modbus-server-points.md`](./niagara-modbus-server-points.md) | Modbus TCP slave | `PROXY` at creation, `dataAddress`, `dataType`, and where the slave network differs from a client network |
| [`part1-publishing-points.pdf`](./part1-publishing-points.pdf) | all three | 9-page deck: the three-step pattern, per-protocol walkthroughs, the channel table |

Every row that was reproduced on the test station is marked in
[`../VERIFIED.md`](../VERIFIED.md). Rows left blank there are not claimed anywhere in these
documents.

## What is common to all three

- **The parent must be enabled first.** The driver network is enabled before a port, a
  device, or an export object means anything; each layer is confirmed by a read-back.
- **The source must hold a value.** With a `null` source the export object has nothing to
  publish; give the source a value and it reports `{ok}` without a restart.
- **The outside client is the confirmation.** The point is published when an independent
  client, on another host, returns the value.

## What differs

- BACnet needs a network-level enable chain (`network` → `ipPort` → real NIC in `link`)
  before any descriptor can answer; oBIX and Modbus slave do not.
- Only BACnet renames the object (`objectId` write → new component name); the other two keep
  the name you gave them.
- oBIX publishes history and alarm queries; REST creates, copies, renames and removes the
  component in the first place.
- A Modbus slave network answers and does not poll, so it has no `pollScheduler` — that
  belongs to the client side.

The client direction — building devices and points that poll *these* servers — is in
[`../part2-client/`](../part2-client/).

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
