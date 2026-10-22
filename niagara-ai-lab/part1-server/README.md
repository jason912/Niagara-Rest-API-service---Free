# Part 1 — Publishing station points as a server

This part covers one direction only: **station point → protocol object that an outside
client can read or write**. The station is the server; something else is the client.

Every protocol in this part follows the same three-step shape, and the step that usually
fails is the second one:

| Step | BACnet export | oBIX export | Modbus TCP slave |
|:--|:--|:--|:--|
| 1 · Create the object | REST `add` | REST `add` | REST `cp` (not `add`) |
| 2 · Bind the source or address | `pointOrd` → **oBIX PUT** | `point` → **oBIX PUT** | `dataAddress` → **REST mod** |
| 3 · Assign public identity | `objectId` → REST mod | binding is the identity | binding is the identity |

Two rows in step 2 are `BOrd` slots, and `BOrd` is the one type the REST encoder cannot
express: it rejects the string with `BString cannot be cast to BOrd`. That single fact is
why a server-side workflow needs two channels instead of one.

## Documents

| Document | Protocol | What it answers |
|:--|:--|:--|
| [`niagara-bacnet-server-points.md`](./niagara-bacnet-server-points.md) | BACnet/IP | Three-layer enable order, `exportTable`, the three slots split across two channels, and the rename that happens the moment `objectId` is written |
| [`niagara-obix-server-points.md`](./niagara-obix-server-points.md) | oBIX | The `point` slot only oBIX can write, `<value>/set/` for writes, and the operations this interface cannot perform at all |
| [`niagara-modbus-server-points.md`](./niagara-modbus-server-points.md) | Modbus TCP slave | Why `add` produces a point with a `NullProxyExt`, `dataAddress` versus `address`, and where the slave network differs from a client network |
| [`part1-publishing-points.pdf`](./part1-publishing-points.pdf) | all three | 9-page deck: capability matrix, the three-step pattern, per-protocol traps, fault reference |

## What is common to all three

- **A disabled parent makes every child inert.** The driver network itself must be
  enabled before a port, a device, or an export object means anything.
- **A bound descriptor still faults while the source holds `null`.** The binding is
  correct; there is simply nothing to publish yet.
- **The station's own read-back is not proof.** The point is published only when an
  independent client, on another host, returns the value.

## What differs

- BACnet needs a network-level enable chain (`network` → `ipPort` → real NIC in `link`)
  before any descriptor can answer; oBIX and Modbus slave do not.
- Modbus slave objects cannot be created with `add` — the created point carries a
  `NullProxyExt` and no `dataAddress` slot at all.
- Only BACnet renames the object behind your back (`objectId` write → new component
  name); the other two keep the name you gave them.
- Only oBIX publishes history and alarm queries; only REST can create, copy, rename, or
  remove the component in the first place.

The client direction — building devices and points that poll *these* servers — is in
[`../part2-client/`](../part2-client/).

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
