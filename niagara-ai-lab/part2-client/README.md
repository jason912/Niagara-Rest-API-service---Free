# Part 2 — Consuming points: building a client that collects

This part is the other direction. The station is now the **client**: it opens a driver
network, builds a device object for a field controller, adds points whose proxy
extension knows how to reach that controller, and then has to prove that the values are
actually arriving.

The objects built here are the ones that read the servers described in
[`../part1-server/`](../part1-server/) — a Modbus TCP slave, a BACnet/IP device, an oBIX
server — or any real field controller in the same shape.

Every protocol in this part follows the same four-step shape:

| Step | What it means |
|:--|:--|
| 1 · Network | a driver network object of the client flavour (`modbusTcp:ModbusTcpNetwork`, `bacnet:BacnetNetwork`, …), enabled |
| 2 · Device | one object per field controller, carrying address, port, and poll settings |
| 3 · Points | one point per value, each with a **proxy extension** that knows the address |
| 4 · Proof | the poll counters move **and** the value changes when driven from outside |

Step 3 is where a client build breaks silently. A point created without its proxy
extension reads `0.00 {fault,stale}` forever, and the point still looks like a point.

## Documents

| Document | Protocol | What it answers |
|:--|:--|:--|
| [`niagara-client-collection.md`](./niagara-client-collection.md) | Modbus TCP, SNMP, BACnet, oBIX clients | Four status signals that lie, the two counters that settle "is it collecting", and the only proof that counts |
| [`part2-collecting-points.pdf`](./part2-collecting-points.pdf) | all | 9-page deck: building the chain over the API, the client object chain per protocol, the proxy-extension requirement, the counters, the outside-drive test, and the open case |

## The client chain, per protocol

| | Modbus TCP | BACnet/IP | SNMP | oBIX |
|:--|:--|:--|:--|:--|
| Network type | `modbusTcp:ModbusTcpNetwork` | `bacnet:BacnetNetwork` | `nSnmp:SnmpNetwork` | `obix:ObixNetwork` |
| Device object | `ModbusTcpDevice` | `BacnetDevice` | `SnmpDevice` | oBIX device |
| Address slots | `ipAddress`, `port`, `deviceAddress` | `address` (`BacnetAddress`) | `ipAddress`, `port`, `community` | URL path |
| Proxy extension | `ModbusClientNumericProxyExt` | `BacnetNumericProxyExt` | `SnmpNumericProxyExt` | `ObixNumericProxyExt` |
| Polling control | `devicePollConfig`, `pollScheduler` | `pollFrequency`, COV | `pollScheduler` | poll rate |
| Polls from outside | Modbus master FC03/FC06 | BACnet ReadProperty | `snmpget` | oBIX GET |

## Building a client point correctly

`add` alone does not produce a working client point. The shortcut that works is `cp`
from a point that already carries the right proxy extension — but `cp` copies the
extension's settings too, including `dataType`. An integer register copied from a float
point decodes as one IEEE-754 value and reads `0.00 {stale}` with an empty `faultCause`.

The three slots to check on every copied point:

| Slot | Typical wrong value | Symptom |
|:--|:--|:--|
| `proxyExt/dataType` | `Float Type` on an integer register | `0.00 {stale}`, no fault |
| `proxyExt/dataAddress` | inherited from the source device | reads a plausible but wrong number |
| `proxyExt/byteOrder` | inherited | large integers come back wrong |

## The four signals that are not evidence

| Signal | What it actually proves |
|:--|:--|
| device `status = {ok}` | the configuration was accepted |
| `health = Ok [timestamp]` | a ping succeeded, on a separate path |
| `readValue = 0.00 {ok}` | a value object exists |
| `readStatus = okNotActive` | a poll range is configured, nothing scheduled |

None of them is a measurement of collection. The counters and an external value change
are, and both are in the collection document.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
