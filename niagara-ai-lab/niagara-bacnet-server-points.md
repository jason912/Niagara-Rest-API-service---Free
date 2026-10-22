# Exposing station points as BACnet objects

**Applies to** Niagara N4 (verified on 4.14.0.162) with `BACnetNetwork` present.
**Companion:** [BACnet/IP server enablement](#prerequisite-the-server-must-be-running) below —
a correctly built export object still reads as `{fault}` if the server itself is not up.

This document covers one direction only: **station point → BACnet object visible to an
external BACnet client**. Reading BACnet devices into a station is a different driver
(`BACnetNetwork` device objects) and is not covered here.

---

## Prerequisite: the server must be running

Three layers must all be enabled. Enabling only `ipPort` produces `status={ok}` on that
component while nothing answers on the wire.

| Layer | Path | Failure mode when off |
|:--|:--|:--|
| Driver network | `/Drivers/BacnetNetwork` | whole network `{disabled}`, every child inert |
| Network port | `/Drivers/BacnetNetwork/bacnetComm/network/ipPort` | `{disabled,fault}` |
| Link | `.../ipPort/link` | `BACnet/IP adapter not ready! Check cable connections.` |

The `link` holds three `DynamicEnum` slots (`adapter`, `adapterId`, `ipAddress`).
They **cannot be written over REST** — REST rejects them with
`BEnumRange cannot be cast to BEnum`, and rejects the display name with `Illegal name`.
The only working channel is an `oBIX PUT` of the **escaped** name taken from the slot's
`~range`. The escape table is in the capability deck (`niagara-protocol-capability-matrix.pdf`).

```
GET  <obix>/config/Drivers/BacnetNetwork/bacnetComm/network/ipPort/link/adapter/~range
PUT  <obix>/config/Drivers/BacnetNetwork/bacnetComm/network/ipPort/link/adapter/
     <enum val="Intel$28R$29$20PRO$2f1000$20MT$20Desktop$20Adapter$20$232"/>
```

Setting `adapter` to the real NIC makes `adapterId` and `ipAddress` follow automatically
(`eth6` / the station's own address in the verified run). A debug or virtual adapter is a
common wrong value and yields `adapter not ready`.

Completion: `BacnetNetwork.status = {ok}`, `ipPort.status = {ok}`, `faultCause` empty,
`localDevice.status = {ok}`, `localDevice.systemStatus = Operational`.

Verify from outside with a **unicast** Who-Is to UDP 47808 — a global broadcast
(NPDU `0xff`) sent from the same host is frequently dropped:

```python
import socket
def bvlc(npdu): return bytes([0x81, 0x0A]) + (4 + len(npdu)).to_bytes(2, 'big') + npdu
pkt = bvlc(bytes([0x01, 0x00, 0x10, 0x08]))          # NPDU 01 00 + APDU 10 08 (Who-Is)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(5)
s.connect(('<HOST>', 47808)); s.send(pkt); print(s.recv(2048).hex()); s.close()
# 810a001401001000c4020004582205c491002124  → device,1112 / maxAPDU 1476 / vendor 36
```

---

## Where export objects live

```
/Drivers/BacnetNetwork/localDevice/exportTable
```

Every object below this table is a *descriptor*: it points at one station point and
publishes it under one BACnet object identifier.

---

## 1. Choose the descriptor type

| Source point | Descriptor type |
|:--|:--|
| `control:NumericPoint` (read-only) | `bacnet:BacnetAnalogInputDescriptor` |
| Numeric, value semantics | `bacnet:BacnetAnalogValueDescriptor` |
| Numeric, output semantics (writable) | `bacnet:BacnetAnalogOutputDescriptor` |
| `control:BooleanPoint` | `bacnet:BacnetBinaryInputDescriptor` |
| Boolean, value semantics | `bacnet:BacnetBinaryValueDescriptor` |
| `control:EnumPoint` | `bacnet:BacnetEnumDescriptor` |
| String | `bacnet:BacnetCharacterStringDescriptor` |

```json
[{"OP":"add","PATH":"/Drivers/BacnetNetwork/localDevice/exportTable",
  "N":"demo_av100","T":"bacnet:BacnetAnalogValueDescriptor"}]
```

A fresh descriptor reads:

```
objectId   = analogValue:-1        (unassigned)
objectName = ""
pointOrd   = null
status     = {fault}
```

---

## 2. Fill three slots — over two different channels

| Slot | Type | Channel | Notes |
|:--|:--|:--|:--|
| `objectName` | String | **REST** | must be globally unique on the network |
| `pointOrd` | `BOrd` | **oBIX PUT only** | REST rejects: `BString cannot be cast to BOrd` |
| `objectId` | `BBacnetObjectIdentifier` | **REST** | e.g. `analogValue:100`; oBIX also works but may answer `BadUriErr` while succeeding |

`pointOrd` over oBIX:

```bash
curl -X PUT "http://<HOST>/obix/config/Drivers/BacnetNetwork/localDevice/exportTable/demo_av100/pointOrd/" \
  -u "<USER>:<PASS>" \
  -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><uri val="station:|slot:/Demo/Temp1" xmlns="http://obix.org/ns/schema/1.0"/>'
```

Rules that bite:

- A `#` inside the source path must be escaped as `$23`.
- `objectName` must be unique across the whole network — a duplicate yields
  `{fault}` / `Duplicate Object Name`.
- One source point can back **exactly one** descriptor. A second binding faults.
- Writing `pointOrd` over oBIX may return `BadUriErr` and still have taken effect —
  always confirm by reading the slot back, never by the response code.

REST for the other two:

```json
[{"OP":"mod","PATH":"/Drivers/BacnetNetwork/localDevice/exportTable/demo_av100","N":"objectName","V":"Demo_Temp1"},
 {"OP":"mod","PATH":"/Drivers/BacnetNetwork/localDevice/exportTable/demo_av100","N":"objectId","V":"analogValue:100"}]
```

---

## 3. The component renames itself

The moment `objectId` is written, the descriptor's own name becomes
`<object-type>_<instance>`:

```
demo_av100  →  analogValue_100
```

Retrieve it with `list` after the write. Looking it up by the name you typed will fail,
and a subsequent `add` under that name silently creates a second object.

---

## 4. The source point must hold a value

With a `null` source the descriptor stays `{fault}`:

```
faultCause: Invalid value for BACnet Object:- {null} @ def
```

Give the source a real value and it flips to `{ok}` immediately — no restart needed.

---

## 5. Verify from outside

```bash
python3 bacnet_scan.py read -t <HOST> -d <DEVICE_INSTANCE> \
  --objtype 2 --objinst 100 --prop 85
```

| `--objtype` | Object |
|:--:|:--|
| 0 | analogInput |
| 1 | analogOutput |
| 2 | analogValue |
| 3 | binaryInput |
| 4 | binaryOutput |
| 5 | binaryValue |
| 8 | device |
| 40 | characterStringValue |

| `--prop` | Property |
|:--:|:--|
| 85 | present-value |
| 77 | object-name |

Do not accept the station's own read-back as proof. The point is published only when an
independent BACnet client returns the value.

---

## Fault reference

| `faultCause` | Cause | Fix |
|:--|:--|:--|
| `Invalid Object ID` | `pointOrd` bound but `objectId` unassigned | REST `mod objectId` |
| `Cannot find exported point` | wrong `pointOrd` path, or `#` not escaped | rewrite `pointOrd`, `#` → `$23` |
| `Duplicate Object Name` | `objectName` empty or reused | assign a unique name |
| `Invalid value ... {null}` | source point has no value | write a value to the source |
| `BACnet/IP adapter not ready!` | `link` bound to a virtual/debug NIC, or `0.0.0.0` | rebind `adapter` to the real NIC |
| network `{disabled}` | `BacnetNetwork.enabled = false` | enable the driver network, not just `ipPort` |
| descriptor not found by name | it renamed itself after `objectId` | `list` the export table |

---

## Worked end-to-end chain (verified)

The value path crosses three protocols in one run:

```
external Modbus master writes HR[1] = 1234  →  station point reads 1234.00
                                            →  BACnet analogInput:101 present-value = 1234.0
```

That single check proves the export object is wired to a live point *and* that the
BACnet server is answering off-station.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
