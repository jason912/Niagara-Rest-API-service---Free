# Exposing station points as Modbus registers

**Applies to** Niagara N4 (verified on 4.14.0.162).
This document covers **station → Modbus TCP slave**: the station answers as a Modbus
server and an external master reads and writes its registers.

Reading a field device into the station (Modbus TCP *client*) is the opposite direction and is
covered in [`../part2-client/`](../part2-client/).

Verified rows are marked in [`../VERIFIED.md`](../VERIFIED.md).

---

## Where the objects live

```
/Drivers/<slave network>            type modbusTcpSlave:ModbusTcpSlaveNetwork
└── <device>                        type modbusTcpSlave:ModbusSlaveDevice
    └── points
        └── <point>                 proxyExt = ModbusServerNumericProxyExt
```

The slave network is a **separate object** from a `ModbusTcpNetwork` client. Both may
coexist in one station; they do not share a port.

---

## 1. Create the point with its proxy extension

`PROXY` on the `add` is what gives the point a register address slot. This is the same rule
as on the client side: the proxy extension is passed at creation because `proxyExt` is a
protected slot that cannot be attached, replaced or given a child afterwards.

```json
[{"OP":"add","PATH":"/Drivers/<net>/<device>/points",
  "N":"Srv_Reg1","T":"control:NumericPoint",
  "PROXY":"modbusTcpSlave:ModbusServerNumericProxyExt"}]
```

The second option, when the proxy type is already present on a reference point, is a copy:

```json
[{"OP":"cp",
  "PATH":"/Drivers/<net>/<device>/points/Ref_Reg1",
  "N":"Srv_Reg2",
  "TARGET_PATH":"/Drivers/<net>/<device>/points"}]
```

The copy carries the proxy type, `outOfServiceExt`, and every slot of the source — including
`dataType`, `dataAddress` and `byteOrder`. Read those three back on the new point and set
them for the new register.

## 2. Bind the register

The slot is named `dataAddress` on the proxy extension:

```json
[{"OP":"mod","PATH":"/Drivers/<net>/<device>/points/<point>/proxyExt",
  "N":"dataAddress","V":"0001"}]
```

| Slot | Example value | Read-back rendering |
|:--|:--|:--|
| `dataAddress` | `0001` | `Hex:0001` |
| `regType` | `holding` / `input` | `Holding` / `Input` |
| `dataType` | `integerType` | `Integer Type` |
| `byteOrder` | `bigEndian` | `Big Endian` |

`dataAddress` is a `FlexAddress` and takes a hexadecimal string over REST. `dataType` is an
enum, so it is written over oBIX with the escaped value name:

```
PUT <obix>/config/Drivers/<net>/<device>/points/<point>/proxyExt/dataType/
    <enum val="integerType"/>
```

Set `dataType` to match the register width before the first poll: an integer holding
register is `integerType` (one register), a float pair is `floatType` (two registers).
Polling begins on the next cycle and needs no restart.

## 3. Confirm from outside

The confirmation is a Modbus master on another host, not the station's own read-back:

```python
import socket, struct

def mb(host, pdu, unit=1, port=502, timeout=6):
    s = socket.create_connection((host, port), timeout=timeout)
    s.sendall(struct.pack('>HHHB', 0x1234, 0, len(pdu) + 1, unit) + pdu)
    r = s.recv(512); s.close()
    return r

# FC06 write HR[1] = 7777
mb('<HOST>', struct.pack('>BHH', 6, 0x01, 7777))
# FC03 read HR[0..1]
mb('<HOST>', struct.pack('>BHH', 3, 0x00, 2))
```

The verified exchange on the test station:

```
req  FC06  12 34 00 00 00 06 01 06 00 01 1e 61
resp  FC06  12 34 00 00 00 06 01 06 00 01 1e 61     ← accepted, 0x1e61 = 7777

req  FC03  12 34 00 00 00 07 01 03 04 04 d2 1e 61
resp  FC03  12 34 00 00 00 07 01 03 04 04 d2 1e 61  ← HR[0] = 1234, HR[1] = 7777
```

And the station point behind HR[1]:

```
GET /api/config?path=/Drivers/<net>/<device>/points/Srv_Reg1
→ out = 7777.0 {ok}
```

That is the full loop: an external master wrote a register, the station point took the value,
and a second external read returned the same number.

## 4. Point direction

A slave-side point published to an external master is normally readable from outside and
writable from inside. An external write goes through the proxy into the point's priority
array, so publish a point whose `in16` (lowest priority) is free when the external master is
meant to control it. Read `out` and the priority array to see which slot is currently
driving the value.

---

## Slave and client, side by side

| | Slave (this document) | Client |
|:--|:--|:--|
| Network type | `modbusTcpSlave:ModbusTcpSlaveNetwork` | `modbusTcp:ModbusTcpNetwork` |
| Device type | `modbusTcpSlave:ModbusSlaveDevice` | `modbusTcp:ModbusTcpDevice` |
| Proxy ext | `ModbusServerNumericProxyExt` | `ModbusClientNumericProxyExt` |
| Address slot | `dataAddress` (FlexAddress) | `dataAddress` (FlexAddress) |
| Who initiates | external master | station |
| Polling config | none — the slave answers | `devicePollConfig/*` + network `pollScheduler` |

A slave network has no `pollScheduler`: it answers, it does not poll. `totalPolls` belongs to
the client side only.

---

## Type discovery

`/api/types` and `/api/modules` do not enumerate component types — they return a single
note. To confirm a class exists on a station, list the module jar:

```
modbusTcpSlave-rt.jar → com/tridium/modbusTcpSlave/BModbusServerNumericProxyExt.class
```

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
