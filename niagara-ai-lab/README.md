# Niagara AI Automation Lab

Hands-on notes from driving a Niagara 4 station **entirely through machine-facing
interfaces** — no Workbench clicks, no desktop session. Everything here was reproduced
against a live station (Niagara `4.14.0.162`) and confirmed from the outside with
independent Modbus, BACnet and SNMP clients.

**What is proven:** the checklist below marks every capability that was driven over the API
and confirmed off-station. Blank rows are not claimed anywhere in this lab.

## Verified checklist

[`VERIFIED.md`](./VERIFIED.md) · [`VERIFIED.pdf`](./VERIFIED.pdf) — **26 of 32 capabilities
verified**, 6 left blank.

A tick means the capability was driven over the API and then observed from **outside** the
station: an outside protocol client, or a counter delta across a known interval. A blank cell
is not verified, and nothing in these documents claims it.

### Part 1 — the station publishes points · 18 / 21

| # | Capability | Protocol | ✓ |
|:--|:--|:--|:--:|
| 1.1 | Enable the driver network | BACnet/IP | ✓ |
| 1.2 | Enable the IP port | BACnet/IP | ✓ |
| 1.3 | Bind the port link to a real NIC | BACnet/IP | ✓ |
| 1.4 | Server answers a Who-Is from another host | BACnet/IP | ✓ |
| 1.5 | Create an export descriptor | BACnet/IP | ✓ |
| 1.6 | Write `pointOrd` (a `BOrd` slot) | BACnet/IP | ✓ |
| 1.7 | Write `objectId` and let the component rename | BACnet/IP | ✓ |
| 1.8 | Create an export point | oBIX | ✓ |
| 1.9 | Write the `point` slot (a `BOrd` slot) | oBIX | ✓ |
| 1.10 | Read the export from outside | oBIX | ✓ |
| 1.11 | Create a slave point | Modbus TCP slave | ✓ |
| 1.12 | Bind the register | Modbus TCP slave | ✓ |
| 1.13 | Read the register from outside | Modbus TCP slave | ✓ |
| 1.14 | Write the register from outside | Modbus TCP slave | ✓ |
| 1.15 | Component create / copy / rename / remove | all | ✓ |
| 1.16 | Multi-operation edits in one request | all | ✓ |
| 1.17 | Facet edit and read-back | all | ✓ |
| 1.18 | Program source upload and compile | all | ✓ |
| 1.19 | Read the exported object with ReadProperty | BACnet/IP |   |
| 1.20 | Write through an oBIX export (`<value>/set/`) | oBIX |   |
| 1.21 | SNMP agent exports | SNMP |   |

### Part 2 — the station collects points · 8 / 11

| # | Capability | Protocol | ✓ |
|:--|:--|:--|:--:|
| 2.1 | Create a client network | Modbus TCP | ✓ |
| 2.2 | Create a client device | Modbus TCP | ✓ |
| 2.3 | Set address, port and unit id | Modbus TCP | ✓ |
| 2.4 | Create a point with its proxy extension | Modbus TCP | ✓ |
| 2.5 | Set the register data type | Modbus TCP | ✓ |
| 2.6 | Point carries a structured address | Modbus TCP | ✓ |
| 2.7 | Scheduler is running | SNMP | ✓ |
| 2.8 | Point value matches an outside read | SNMP | ✓ |
| 2.9 | Point value matches an outside read | Modbus TCP |   |
| 2.10 | Point collected and driven from outside | BACnet/IP |   |
| 2.11 | Point collected from an oBIX server | oBIX |   |

## Two halves, opposite directions

The material is split by direction, because the two directions use different objects:

| | Part 1 — the station is the **server** | Part 2 — the station is the **client** |
|:--|:--|:--|
| Question | how do station points become BACnet, oBIX and Modbus objects? | how does the station poll devices and hold their values? |
| Objects | export descriptors, slave points | driver network, device, point + proxy extension |
| Key step | binding the source (`BOrd`, enum slots) | the proxy extension and the register decode |
| Proof | an outside client reads the published point | an outside client reads the same value the point holds |
| Folder | [`part1-server/`](./part1-server/) | [`part2-client/`](./part2-client/) |

Each part has its own README, its own deck, and its own documents.

## Two channels, one station

| Channel | Endpoint | Best at |
|---|---|---|
| **REST API v2** | `/api/config`, `/api/batch` (`v2.42.0`) | creating, copying, renaming and removing components; atomic multi-op edits; facet and program edits |
| **oBIX** | `/obix/config/...` | `BOrd` slots and enum slots, which the REST encoder cannot carry |

A working deployment uses both, and every claim is confirmed from outside the station.

## Which action goes through which channel

| Action | Channel | Confirmation |
|---|---|---|
| Create, copy, rename, remove components | **REST v2** — `add` / `cp` / `rename` / `remove` | the object appears in the parent's slot list |
| Multi-step edits in one request | **REST v2** — `/api/batch` | one POST, one result per operation, in order |
| Facets (`units`, `precision`, `min`, `max`) | **REST v2** — `mod` with `N=facets` | the value renders with the new facet |
| `objectName`, `objectId` on an export point | **REST v2** — `mod` | the slot read-back changes, and the component self-renames |
| Program source and compile | **REST v2** — `/api/program/*` | compile response |
| `BOrd` slots — `pointOrd`, `point`, link targets | **oBIX** — `PUT` of a `<uri>` | the slot read-back returns the ord |
| Enum slots — `dataType`, `adapter`, `adapterId` | **oBIX** — `PUT` of the escaped name from `~range` | the slot read-back returns the enum |
| Proving a point is exposed or collected | **Outside the station** — Modbus FC03/FC06, BACnet Who-Is plus ReadProperty, SNMP GET | an independent client sees the same value |

Rule of thumb: **build with REST, bind with oBIX, prove with an outside client.**

## Documents

| Document | What it answers |
|---|---|
| [`VERIFIED.md`](./VERIFIED.md) | The checklist: every capability in this lab, ticked when it was confirmed off-station, blank when it was not |
| [`VERIFIED.pdf`](./VERIFIED.pdf) | The same checklist as a 2-page A4 document, for review or print |
| [`part1-server/README.md`](./part1-server/README.md) | Part 1 overview: the three-step publish pattern, what is common to all three protocols, what differs |
| [`part1-server/part1-publishing-points.pdf`](./part1-server/part1-publishing-points.pdf) | 9-page deck: object trees, the three-layer BACnet enable, the slots split across two channels, the Modbus slave `PROXY` step |
| [`part1-server/niagara-bacnet-server-points.md`](./part1-server/niagara-bacnet-server-points.md) | Exposing station points as BACnet objects: the enable chain, `exportTable`, the three slots split across two channels, the rename after `objectId` |
| [`part1-server/niagara-obix-server-points.md`](./part1-server/niagara-obix-server-points.md) | Exposing station points as oBIX points: the `point` slot, `/set/` writes, and which channel writes which step |
| [`part1-server/niagara-modbus-server-points.md`](./part1-server/niagara-modbus-server-points.md) | Exposing station points as Modbus registers: `PROXY` at creation, `dataAddress`, `dataType`, and the working register exchange |
| [`part2-client/README.md`](./part2-client/README.md) | Part 2 overview: the four-step client chain per protocol, the proxy-extension requirement, the slots to set on every point |
| [`part2-client/part2-collecting-points.pdf`](./part2-client/part2-collecting-points.pdf) | 9-page deck: building the chain over the API, the client chain per protocol, the proxy slots, the two confirmation readings |
| [`part2-client/niagara-client-collection.md`](./part2-client/niagara-client-collection.md) | Collecting from field devices: the four REST steps, the proxy slots per protocol, the two readings that confirm collection |

Commands are copy-paste ready except for `<HOST>`, `<USER>` and `<PASS>`.

## Verification style

A value appearing in the station is not evidence. Every ticked row in
[`VERIFIED.md`](./VERIFIED.md) is backed by one of:

- an **outside client** reading the same point independently (Modbus FC03/FC06, BACnet
  Who-Is plus ReadProperty, SNMP GET), or
- a **poll counter delta** across a known interval (`pollScheduler.totalPolls`), or
- a **state change caused externally** that the station then followed.

## Scope and caveats

- Station paths are examples; substitute your own ord and component names.
- Vendor identifiers appear only where a protocol frame or a class path requires them (for
  example `vendor 36` in a BACnet I-Am, or a Java package name).
- Hosts, credentials and internal addresses are placeholders throughout.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
