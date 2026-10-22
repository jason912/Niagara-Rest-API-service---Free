# Niagara AI Automation Lab

Hands-on notes from driving a Niagara 4 station **entirely through machine-facing
interfaces** — no Workbench clicks, no desktop session. Everything here was
reproduced against a live station (Niagara `4.14.0.162`) and verified from the
outside with independent Modbus, BACnet and SNMP clients.

The point of the exercise: find out which of the two station-side channels can
actually do a given job, where each one stops, and how to prove that a deployment
really works instead of trusting a green status icon.

## Two halves, opposite directions

The material is split by direction, because the two directions use different
objects and fail in different ways:

| | Part 1 — the station is the **server** | Part 2 — the station is the **client** |
|:--|:--|:--|
| Question | how do station points become BACnet, oBIX and Modbus objects? | how does the station poll devices and hold their values? |
| Objects | export descriptors, slave points | driver network, device, point + proxy extension |
| Fails at | binding the source (`BOrd`, enum slots) | the proxy extension and the register decode |
| Proof | an outside client reads the published point | an outside write appears in the station point |
| Folder | [`part1-server/`](./part1-server/) | [`part2-client/`](./part2-client/) |

Each part has its own README, its own deck, and its own documents. Read the part
that matches the direction you are building.

## Two channels, one station

| Channel | Endpoint | Best at |
|---|---|---|
| **oBIX** | `/obix/config/...` | Enum and slot writes REST cannot express; server-side export binding |
| **REST API v2** | `/api/config`, `/api/batch` (`v2.42.0`) | Creating components, atomic multi-op edits, program compile |

A working deployment usually needs both. The matrix below is the short
version of what was measured.

## Which action goes through which channel

The guides are API-driven, but they are **not REST-only**. Component creation,
copying, renaming, removal and facet edits all run over REST v2. Three kinds of
slot cannot be written that way, and every result is confirmed from outside the
station.

| Action | Channel | Evidence |
|---|---|---|
| Create, copy, rename, remove components | **REST v2** — `add` / `cp` / `rename` / `remove` | the object appears in the parent's slot list |
| Multi-step edits in one request | **REST v2** — `/api/batch`, 11 ops | one POST, all-or-nothing |
| Facet strings (`units`, `precision`, `min`, `max`) | **REST v2** — `mod` with `N=facets` | the value renders with the new facet |
| `objectName`, `objectId` on an export point | **REST v2** — `mod` | the slot read-back changes, and the component may self-rename |
| Program source and compile | **REST v2** — `/api/program/*` | compile response |
| Any `BOrd` slot — `pointOrd`, `point`, link targets | **oBIX only** — PUT | REST rejects with `BString cannot be cast to BOrd` |
| Any enum slot — `dataType`, `adapter`, `adapterId` | **oBIX only** — PUT of the escaped name from `~range` | REST rejects with both `BEnumRange cannot be cast to BEnum` and `Illegal name` |
| Proving a point is exposed or collected | **Outside the station** — Modbus FC03/FC06, BACnet Who-Is plus ReadProperty, SNMP GET | an independent client sees the same value |

Rule of thumb: **build with REST, bind with oBIX, prove with an outside client.**
A status slot inside the station is never the evidence. The four signals that report
success without delivering it are listed in the collection guide.

## Documents

| Document | What it answers |
|---|---|
| [`part1-server/README.md`](./part1-server/README.md) | Part 1 overview: the three-step publish pattern, what is common to all three protocols, what differs |
| [`part1-server/part1-publishing-points.pdf`](./part1-server/part1-publishing-points.pdf) | 9-page deck: object trees, the three-layer BACnet enable, the slots split across two channels, the Modbus slave trap, fault reference |
| [`part1-server/niagara-bacnet-server-points.md`](./part1-server/niagara-bacnet-server-points.md) | Exposing station points as BACnet objects: three-layer enable order, `exportTable`, the three slots split across two channels, and the rename that happens behind your back |
| [`part1-server/niagara-obix-server-points.md`](./part1-server/niagara-obix-server-points.md) | Exposing station points as oBIX points: the `point` slot is writable by one channel only, plus what the interface cannot do at all |
| [`part1-server/niagara-modbus-server-points.md`](./part1-server/niagara-modbus-server-points.md) | Exposing station points as Modbus registers: why `add` alone produces a broken point, `dataAddress` versus `address`, and the `dataType` copy trap |
| [`part2-client/README.md`](./part2-client/README.md) | Part 2 overview: the four-step client chain per protocol, the proxy-extension requirement, the slots to re-check on every copied point |
| [`part2-client/part2-collecting-points.pdf`](./part2-client/part2-collecting-points.pdf) | 9-page deck: building the chain over the API, the client chain per protocol, the four signals that lie, the two counters, the outside-drive test, the open case |
| [`part2-client/niagara-client-collection.md`](./part2-client/niagara-client-collection.md) | Collecting from field devices: four signals that lie, the two counters that settle it, and the only proof that counts |

Each protocol document follows the same shape: where the objects live, how to
create and bind them, how to verify from outside the station, and a fault
reference. Commands are copy-paste ready except for `<HOST>`, `<USER>` and
`<PASS>`.

## Verification style

A value appearing in the station is not evidence. Every claim in these documents
is backed by one of:

- an **outside client** reading or writing the same point independently
  (Modbus FC03/FC06, BACnet Who-Is plus ReadProperty, SNMP GET), or
- a **poll counter delta** observed across a known interval
  (`pollScheduler.totalPolls`, `pollScheduler.normalCount`), or
- a **state change caused externally** that the station then followed.

Anything that only looked correct in a status slot is called out as unproven.

## Scope and caveats

- Station paths are examples; substitute your own ord and component names.
- Vendor identifiers appear only where a protocol frame or a class path requires
  them (for example `vendor 36` in a BACnet I-Am, or a Java package name).
- Hosts, credentials and internal addresses are placeholders throughout.
- One case is left open on purpose: three field controllers that report every
  point stale while a freshly created equivalent device collects normally. The
  document records what was ruled out rather than guessing at a cause.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
