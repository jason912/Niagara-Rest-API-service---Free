# Exposing station points as BACnet objects

**Applies to** Niagara N4 (verified on 4.14.0.162) with `BACnetNetwork` present.

This document covers one direction only: **station point → BACnet object visible to an
external BACnet client**. Reading BACnet devices into a station is the client direction and
is covered in [`../part2-client/`](../part2-client/).

The verified rows of this document are marked in [`../VERIFIED.md`](../VERIFIED.md).

---

## Step 0: bring the server up

Three layers are enabled, in this order. Each layer is confirmed by a read-back before the
next one is touched.

| Layer | Path | Working read-back |
|:--|:--|:--|
| Driver network | `/Drivers/BacnetNetwork` | `status = {ok}`, `enabled = true` |
| Network port | `/Drivers/BacnetNetwork/bacnetComm/network/ipPort` | `status = {ok}`, `enabled = true` |
| Link | `.../ipPort/link` | `adapterId` = physical NIC, `ipAddress` = station address |

```json
[{"OP":"mod","PATH":"/Drivers/BacnetNetwork","N":"enabled","V":"true"},
 {"OP":"mod","PATH":"/Drivers/BacnetNetwork/bacnetComm/network/ipPort","N":"enabled","V":"true"}]
```

The `link` holds three `DynamicEnum` slots (`adapter`, `adapterId`, `ipAddress`). They are
written over oBIX, using the escaped name taken from the slot's own `~range`:

```
GET  <obix>/config/Drivers/BacnetNetwork/bacnetComm/network/ipPort/link/adapter/~range
PUT  <obix>/config/Drivers/BacnetNetwork/bacnetComm/network/ipPort/link/adapter/
     <enum val="Intel$28R$29$20PRO$2f1000$20MT$20Desktop$20Adapter$20$232"/>
```

Setting `adapter` to the physical NIC makes `adapterId` and `ipAddress` follow on their own
(`eth6` and the station's own address on the verified run). The escape table is in the part
deck (`part1-publishing-points.pdf`): space `$20`, `.` `$2e`, `/` `$2f`, `(` `$28`, `)` `$29`,
`#` `$23`, digits `$31`–`$39`.

Confirm the server answers off-station with a **unicast** Who-Is to UDP 47808:

```python
import socket
def bvlc(npdu): return bytes([0x81, 0x0A]) + (4 + len(npdu)).to_bytes(2, 'big') + npdu
pkt = bvlc(bytes([0x01, 0x00, 0x10, 0x08]))          # NPDU 01 00 + APDU 10 08 (Who-Is)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(5)
s.connect(('<HOST>', 47808)); s.send(pkt); print(s.recv(2048).hex()); s.close()
# 810a001401001000c4020004582205c491002124  → device,1112 / maxAPDU 1476 / vendor 36
```

The I-Am body carries the local device instance, the max APDU and the vendor id — the same
three values the station reports under `localDevice`.

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

A fresh descriptor reports `objectId = analogValue:-1` (unassigned), `objectName = ""`,
`pointOrd = null`. The three slots below fill it in.

---

## 2. Fill three slots — over two channels

| Slot | Type | Channel | Value on the verified run |
|:--|:--|:--|:--|
| `objectName` | String | **REST** | unique on the network |
| `objectId` | `BBacnetObjectIdentifier` | **REST** | `analogValue:100` |
| `pointOrd` | `BOrd` | **oBIX `PUT`** | `station:\|slot:/<source point>` |

`pointOrd` is a station ord, so it goes through oBIX as a `<uri>`:

```bash
curl -X PUT "http://<HOST>/obix/config/Drivers/BacnetNetwork/localDevice/exportTable/demo_av100/pointOrd/" \
  -u "<USER>:<PASS>" \
  -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><uri val="station:|slot:/Demo/Temp1" xmlns="http://obix.org/ns/schema/1.0"/>'
```

`objectName` and `objectId` go through the REST batch:

```json
[{"OP":"mod","PATH":"/Drivers/BacnetNetwork/localDevice/exportTable/demo_av100","N":"objectName","V":"Demo_Temp1"},
 {"OP":"mod","PATH":"/Drivers/BacnetNetwork/localDevice/exportTable/demo_av100","N":"objectId","V":"analogValue:100"}]
```

Paths that contain `#` are escaped in the `val` attribute: `$23`. The rest of the escape set
is the same one the DynamicEnum names use.

Read every slot back after writing — that is the confirmation for both channels:

```
GET /api/config?path=/Drivers/BacnetNetwork/localDevice/exportTable/<descriptor>
→ objectName = Demo_Temp1   objectId = analogValue:100   pointOrd = station:|slot:/Demo/Temp1
→ status = {ok}
```

---

## 3. The component renames itself

The moment `objectId` is written, the descriptor's own name becomes
`<object-type>_<instance>`:

```
demo_av100  →  analogValue_100
```

So `list` the export table after the write and address the object by its new name:

```json
[{"OP":"list","PATH":"/Drivers/BacnetNetwork/localDevice/exportTable"}]
```

One source point backs exactly one descriptor, and one name identifies one object on the
network — the export table is the single place where both are decided.

---

## 4. Confirming with an outside read

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

The value the outside client returns is the confirmation: the descriptor is bound, the object
is published, and the BACnet server answered a request that did not come from the station.

---

## Configuration reference

The working values on the verified run, for comparison against a fresh build:

| Slot | Working value | Read-back rendering |
|:--|:--|:--|
| `BacnetNetwork.enabled` | `true` | `{ok}` |
| `ipPort.enabled` | `true` | `{ok}`, `localDevice.systemStatus = Operational` |
| `link/adapter` | the physical NIC, escaped name | `adapterId = eth6`, `ipAddress` = station address |
| `pointOrd` | `station:\|slot:/<path>` | `<uri val="station:\|slot:/<path>"/>` |
| `objectName` | unique across the network | one object per name |
| `objectId` | `analogValue:100` | descriptor renamed to `analogValue_100` |

---

## Worked chain (verified)

One descriptor built over both channels, then read from another host:

```
REST add      bacnet:BacnetAnalogValueDescriptor          → descriptor in exportTable
REST mod      objectName / objectId                       → renamed to analogValue_100
oBIX PUT      pointOrd = station:|slot:/<source point>    → status {ok}
outside call  Who-Is (unicast, UDP 47808)                 → I-Am, device 1112
```

The Who-Is reply proves the server answers off-station; the descriptor proves the object is
published. Together they are the confirmation that the export is live.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
