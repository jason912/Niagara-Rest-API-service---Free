# Part 2 — Consuming points: building a client that collects

This part is the other direction. The station is now the **client**: it opens a driver
network, builds a device object for a field controller, adds points whose proxy extension
knows how to reach that controller, and then confirms that the values are arriving.

The objects built here read the servers described in
[`../part1-server/`](../part1-server/) — a Modbus TCP slave, a BACnet/IP device, an oBIX
server — or any real field controller in the same shape.

Every protocol in this part follows the same four-step shape:

| Step | What it means |
|:--|:--|
| 1 · Network | a driver network object of the client flavour (`modbusTcp:ModbusTcpNetwork`, `bacnet:BacnetNetwork`, …), enabled |
| 2 · Device | one object per field controller, carrying address, port, and unit id |
| 3 · Points | one point per value, each created with the **proxy extension** that knows the address |
| 4 · Proof | the poll counter climbs **and** an outside client reads the same value |

Step 3 is where the chain is decided: `PROXY` is passed on the `add` itself, because
`proxyExt` is a protected slot that cannot be attached after creation.

## Documents

| Document | Protocol | What it answers |
|:--|:--|:--|
| [`niagara-client-collection.md`](./niagara-client-collection.md) | Modbus TCP, SNMP, BACnet, oBIX clients | The four-step chain as REST calls, the proxy slots per protocol, the two readings that confirm collection, and a worked SNMP pair |
| [`part2-collecting-points.pdf`](./part2-collecting-points.pdf) | all | 9-page deck: building the chain over the API, the client object chain per protocol, the proxy-extension requirement, the counters, and the outside-drive test |

Verified rows are marked in [`../VERIFIED.md`](../VERIFIED.md); rows left blank there are not
claimed anywhere in these documents.

## The client chain, per protocol

| | Modbus TCP | BACnet/IP | SNMP | oBIX |
|:--|:--|:--|:--|:--|
| Network type | `modbusTcp:ModbusTcpNetwork` | `bacnet:BacnetNetwork` | `nSnmp:SnmpNetwork` | `obix:ObixNetwork` |
| Device object | `ModbusTcpDevice` | `BacnetDevice` | `SnmpDevice` | oBIX device |
| Address slots | `ipAddress`, `port`, `deviceAddress` | `address` (`BacnetAddress`) | `ipAddress`, `port`, `community` | URL path |
| Proxy extension | `ModbusClientNumericProxyExt` | `BacnetNumericProxyExt` | `SnmpNumericProxyExt` | `ObixNumericProxyExt` |
| Polling control | `devicePollConfig`, `pollScheduler` | `pollFrequency`, COV | `pollScheduler` | poll rate |
| Outside client | Modbus master FC03/FC06 | BACnet ReadProperty | `snmpget` | oBIX GET |

## Building a client point correctly

The proxy extension carries the addressing slots, so the three values to set on every point
are these:

| Slot | Set it to | Read-back rendering |
|:--|:--|:--|
| `proxyExt/dataType` | the register width (`integerType`, `floatType`, …) | `Integer Type` |
| `proxyExt/dataAddress` | the register / OID / object reference | `Modbus:40002`, `Modbus:0001` |
| `proxyExt/byteOrder` | the device's byte order | `Big Endian` |

A `cp` copy inherits all three from the source point, so re-read them on the new point after
every copy and set them for the new address.

## The two readings that confirm collection

| Reading | What it shows |
|:--|:--|
| `pollScheduler.totalPolls` rising between two reads | the network is dispatching polls |
| an outside client returning the same value as the point | the driver, the proxy and the point agree with the field |

Both are in the collection document, with the SNMP pair that was read on both sides.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
