# Niagara AI Automation Lab

Hands-on notes from driving a Niagara 4 station **entirely through machine-facing
interfaces** — no Workbench clicks, no desktop session. Everything here was
reproduced against a live station (Niagara `4.14.0.162`) and verified from the
outside with independent Modbus, BACnet and SNMP clients.

The point of the exercise: find out which of the three station-side channels can
actually do a given job, where each one stops, and how to prove that a deployment
really works instead of trusting a green status icon.

## Three channels, one station

| Channel | Endpoint | Best at |
|---|---|---|
| **box** | `POST /box/` (HTMX partials) | UI-shaped reads: slot lists, facets, alarm/log pages |
| **Built-in XML API** | `/obix/config/...` | Enum and slot writes REST cannot express; server-side export binding |
| **Built-in REST** | `/api/config`, `/api/batch` (`v2.42.0`) | Creating components, atomic multi-op edits, program compile |

A working deployment usually needs all three. The matrix below is the short
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
| Any `BOrd` slot — `pointOrd`, `point`, link targets | **Built-in XML API only** — PUT | REST rejects with `BString cannot be cast to BOrd` |
| Any enum slot — `dataType`, `adapter`, `adapterId` | **Built-in XML API only** — PUT of the escaped name from `~range` | REST rejects with both `BEnumRange cannot be cast to BEnum` and `Illegal name` |
| Slot lists, facets, alarm and log pages in UI shape | **box** — `POST /box/` | partial HTML |
| Proving a point is exposed or collected | **Outside the station** — Modbus FC03/FC06, BACnet Who-Is plus ReadProperty, SNMP GET | an independent client sees the same value |

Rule of thumb: **build with REST, bind with the XML API, prove with an outside client.**
A status slot inside the station is never the evidence. The four signals that report
success without delivering it are listed in the collection guide.

## Documents

| Document | What it answers |
|---|---|
| [`niagara-protocol-capability-matrix.pdf`](./niagara-protocol-capability-matrix.pdf) | 10-page deck: capability matrix for all three channels, the three-step publish flow per protocol, the two traps that cost the most time, and how to prove collection is live |
| [`niagara-bacnet-server-points.md`](./niagara-bacnet-server-points.md) | Exposing station points as BACnet objects: three-layer enable order, `exportTable`, the three slots split across two channels, and the rename that happens behind your back |
| [`niagara-modbus-server-points.md`](./niagara-modbus-server-points.md) | Exposing station points as Modbus registers: why `add` alone produces a broken point, `dataAddress` versus `address`, and the `dataType` copy trap |
| [`niagara-obix-server-points.md`](./niagara-obix-server-points.md) | Exposing station points as XML-API points: the `point` slot is writable by one channel only, plus what the interface cannot do at all |
| [`niagara-client-collection.md`](./niagara-client-collection.md) | Collecting from field devices: four signals that lie, the two counters that settle it, and the only proof that counts |

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

## Build

The deck is generated from source, so the PDF can be regenerated after an edit:

```bash
pip install reportlab pymupdf
python3 build_deck.py     # writes niagara-protocol-capability-matrix.pdf
```

Fonts: the script uses DejaVu for Latin text and falls back to a CJK-capable
font for the few glyphs that need it. Both are resolved from standard Linux font
paths; adjust the constants at the top of the script for other systems.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
