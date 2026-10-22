# Collecting points from field devices — the working chain

**Applies to** Niagara N4 (verified on 4.14.0.162).
This is the **client** direction: the station polls an external device and holds the values
in station points. The opposite direction (publishing station points outward) is covered by
the BACnet / oBIX / Modbus server documents in [`../part1-server/`](../part1-server/).

The whole build is four REST calls plus one proxy slot. Follow them in order and the chain
polls. The verified status of every row is in [`../VERIFIED.md`](../VERIFIED.md).

---

## The chain in one table

| Step | Object | Created over | The field that decides it |
|:--|:--|:--|:--|
| 1 · Network | driver network of the client flavour | REST `add` + `mod enabled` | `enabled = true` |
| 2 · Device | one object per field controller | REST `add` + `mod` address slots | `ipAddress`, `port`, `deviceAddress` |
| 3 · Point | point carrying its proxy extension | REST `add` with `PROXY` | `PROXY` at creation time |
| 4 · Proxy slots | register type and register address | oBIX `PUT` | `dataType`, `dataAddress` |
| 5 · Confirm | counters, then an outside read | REST `GET` + protocol client | two readings that agree |

---

## 1. Driver network

```json
[{"OP":"add","PATH":"/Drivers","N":"ModbusTcpNetwork","T":"modbusTcp:ModbusTcpNetwork"},
 {"OP":"mod","PATH":"/Drivers/ModbusTcpNetwork","N":"enabled","V":"true"}]
```

The network is the polling owner: it holds `pollScheduler`, and every device under it
inherits its enabled state. Create it first, enable it, then build devices.

## 2. Device

```json
[{"OP":"add","PATH":"/Drivers/ModbusTcpNetwork","N":"<device>","T":"modbusTcp:ModbusTcpDevice"},
 {"OP":"mod","PATH":"/Drivers/ModbusTcpNetwork/<device>","N":"ipAddress","V":"<HOST>"},
 {"OP":"mod","PATH":"/Drivers/ModbusTcpNetwork/<device>","N":"port","V":"502"},
 {"OP":"mod","PATH":"/Drivers/ModbusTcpNetwork/<device>","N":"deviceAddress","V":"1"}]
```

`deviceAddress` is the unit id on the field bus, not the station's ord. Read the device back
after the writes — the three slots are the entire addressing model:

```
GET /api/config?path=/Drivers/ModbusTcpNetwork/<device>
→ ipAddress = <HOST>   port = 502   deviceAddress = 1
```

BACnet devices take one `address` slot holding a `BacnetAddress`; that slot is written over
oBIX, in the same way the export side writes `pointOrd` (see
[`../part1-server/niagara-bacnet-server-points.md`](../part1-server/niagara-bacnet-server-points.md)).

## 3. Point, with its proxy extension

```json
[{"OP":"add","PATH":"/Drivers/ModbusTcpNetwork/<device>/points",
  "N":"<point>","T":"control:NumericPoint",
  "PROXY":"modbusCore:ModbusClientNumericProxyExt"}]
```

`PROXY` is what connects the point to the protocol. It is passed at creation because
`proxyExt` is a protected slot: it cannot be attached afterwards, removed, or given a child.
A batch that creates points for a client device carries `PROXY` on every point.

The proxy extension type per protocol:

| Protocol | Proxy extension |
|:--|:--|
| Modbus TCP client | `modbusCore:ModbusClientNumericProxyExt` |
| BACnet client | `bacnet:BacnetNumericProxyExt` |
| SNMP | `snmp:SnmpNumericProxyExt` (nDriver form: `nSnmp:SnmpNumericProxyExt`) |
| oBIX client | `obix:ObixNumericProxyExt` |

## 4. Proxy extension slots

Two slots carry the register:

| Slot | Type | Written over |
|:--|:--|:--|
| `dataType` | enum (`integerType`, `floatType`, …) | oBIX `PUT`, escaped enum name |
| `dataAddress` | `FlexAddress` | REST `mod` or oBIX `PUT` |

```bash
curl -X PUT "http://<HOST>/obix/config/Drivers/ModbusTcpNetwork/<device>/points/<point>/proxyExt/dataType/" \
  -u "<USER>:<PASS>" \
  -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><enum val="integerType" xmlns="http://obix.org/ns/schema/1.0"/>'
```

Read the slot back to confirm; the `PUT` response body is not the confirmation:

```
GET <obix>/config/Drivers/ModbusTcpNetwork/<device>/points/<point>/proxyExt/dataType/
→ <enum val="integerType"/>
```

`dataAddress` renders as `Modbus:40002` for holding-register offset 1, unit 1. Both slots
read over REST as well (`GET /api/config?path=…/proxyExt`), so a script can verify the proxy
without touching oBIX again.

A point copied with `cp` inherits the whole proxy, including `dataType`, `dataAddress` and
`byteOrder`. After a copy, re-read those three slots and set them for the new register.

## 5. Confirm collection

Two readings, taken in this order, confirm that the point is being collected.

**a. The scheduler is running.** Read `pollScheduler` twice, ten seconds apart:

```
GET /api/config?path=/Drivers/<driver network>/pollScheduler
pollEnabled     = true
totalPolls      = <n> over <ms>
normalCount     = current=<n>
```

`totalPolls` must increase between the two reads. A climbing counter means polls are being
dispatched by the network.

**b. The value agrees with an independent read.** Read the point, then read the same
quantity with a client that does not share the station's code:

| Protocol | Outside client | Verified pair |
|:--|:--|:--|
| SNMP | `snmpget -v2c -c <community> <HOST> <OID>` | point `227.00 {ok}` · `snmpget` `227` |
| Modbus TCP | master FC03 on the same register | *(see VERIFIED.md)* |
| BACnet/IP | ReadProperty `--prop 85` | *(see VERIFIED.md)* |
| oBIX | `GET <obix>/config/…` | *(see VERIFIED.md)* |

A row marked in [`../VERIFIED.md`](../VERIFIED.md) is a pair that was actually read on both
sides. Rows left blank there are not claimed anywhere in this document.

The SNMP case in full:

```bash
snmpget -v2c -c <community> <HOST> 1.3.6.1.4.1.318.1.1.26.6.3.1.6.1
# INTEGER: 227
```

```
station point /Drivers/<network>/<device>/points/Phase1_Voltage
→ 227.00 {ok}
```

Two independent readers returning the same number is the confirmation: the driver opened the
socket, the proxy decoded the OID, and the point holds the field value.

---

## Per-protocol notes

### Modbus TCP client

- Create the network, device and points as above; `dataType` and `dataAddress` are the two
  slots that map a point onto a register.
- `devicePollConfig` entries are built by the driver from the points' `dataAddress` values.
  A point added later joins the table; read
  `/…/<device>/devicePollConfig/Range_<start>_<end>` to see the range the driver built.
- `consecutivePointsToPoll` describes how many registers the range covers. Read it as a
  description of the range, not as a polling setting to tune.

### SNMP

`nSnmp:SnmpNetwork` is the nDriver form; keep one SNMP network per station. The OID lives on
the proxy extension, so a point is one OID. Units, precision and min/max are set as facets on
the point and render with the value.

### BACnet/IP

A BACnet client device carries its device instance in the `address` slot; import the object
list, then create points with `bacnet:BacnetNumericProxyExt`. BACnet collects on COV
subscriptions as well as polling, so `pollScheduler` is only part of the picture — read
`pollFrequency` on the point and the object's COV settings alongside it.

### oBIX

`ObixNetwork` devices read an external oBIX server. The export-side path rules in
[`../part1-server/niagara-obix-server-points.md`](../part1-server/niagara-obix-server-points.md)
apply in reverse: the point's `dataAddress` is the path on the far server, and the export's
`is` type tells you what kind of value to expect.

---

## Scripting a whole device

One batch creates the device and its points in a single request:

```json
[{"OP":"add","PATH":"/Drivers/ModbusTcpNetwork","N":"<device>","T":"modbusTcp:ModbusTcpDevice"},
 {"OP":"mod","PATH":"/Drivers/ModbusTcpNetwork/<device>","N":"ipAddress","V":"<HOST>"},
 {"OP":"mod","PATH":"/Drivers/ModbusTcpNetwork/<device>","N":"port","V":"502"},
 {"OP":"mod","PATH":"/Drivers/ModbusTcpNetwork/<device>","N":"deviceAddress","V":"1"},
 {"OP":"add","PATH":"/Drivers/ModbusTcpNetwork/<device>/points","N":"<point1>",
  "T":"control:NumericPoint","PROXY":"modbusCore:ModbusClientNumericProxyExt"},
 {"OP":"add","PATH":"/Drivers/ModbusTcpNetwork/<device>/points","N":"<point2>",
  "T":"control:NumericPoint","PROXY":"modbusCore:ModbusClientNumericProxyExt"}]
```

Post it to `/api/batch` and read the response array — one result per operation, in order.
Then set the proxy slots over oBIX and confirm with the two readings above.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
