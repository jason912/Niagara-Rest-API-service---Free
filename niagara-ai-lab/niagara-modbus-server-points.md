# Exposing station points as Modbus registers

**Applies to** Niagara N4 (verified on 4.14.0.162).
This document covers **station → Modbus TCP slave**: the station answers as a Modbus
server and an external master reads/writes its registers.

Reading a field device into the station (Modbus TCP *client*) is the opposite direction
and behaves differently — see the client-side notes at the end.

---

## Where the objects live

```
/Drivers/<slave network>            created from type modbusTcpSlave:ModbusTcpSlaveNetwork
└── <device>                        created from type modbusTcpSlave:ModbusSlaveDevice
    └── points
        └── <point>                 proxyExt = ModbusServerNumericProxyExt
```

The slave network is a **separate object** from a `ModbusTcpNetwork` client. Both may
coexist in one station; they do not share a port.

---

## 1. Creating a point: `add` alone is not enough

`add` succeeds and returns `status: ok`, but the point it creates carries
`NullProxyExt` — there is no `dataAddress` slot, so there is no way to bind a register:

```
add  control:NumericPoint   →  status: ok
list                        →  children: [proxyExt: NullProxyExt]
```

Copy an existing point that already carries `ModbusServerNumericProxyExt`:

```json
[{"OP":"cp",
  "PATH":"/Drivers/<net>/<device>/points/Ref_Reg1",
  "N":"<new name>",
  "TARGET_PATH":"/Drivers/<net>/<device>/points"}]
```

The copy carries the proxy type, `outOfServiceExt`, and every slot of the source.
Always copy from a point of the **same data type** — see the trap below.

---

## 2. Bind the register

The slot is named `dataAddress`. Writing `address` fails with
`Property 'address' not found`.

```json
[{"OP":"mod","PATH":"/Drivers/<net>/<device>/points/<point>/proxyExt",
  "N":"dataAddress","V":"0010"}]
```

Read back as `Hex:0010`.

| Slot | Example value | Read-back rendering |
|:--|:--|:--|
| `dataAddress` | `0010` | `Hex:0010` |
| `regType` | `holding` / `input` | `Holding` / `Input` |
| `dataType` | `integerType` | `Integer Type` |
| `byteOrder` | `bigEndian` | `Big Endian` |

`dataAddress` is a `FlexAddress` and accepts a hexadecimal string over REST. By contrast
`BOrd` slots (see the BACnet and oBIX documents) reject REST strings entirely — the
distinction matters when you script a batch of point creation across driver families.

---

## 3. The copy trap: `dataType` travels with the point

This is the single most expensive mistake in this workflow.

A point copied from a float source keeps `dataType = Float Type`. Pointed at an integer
holding register, the proxy decodes two registers as one IEEE-754 float. The result is
not an error — the point reports **`0.00 {stale}`** and looks exactly like a driver that
is not polling.

Symptom set that misleads:

```
out          = 0.00 {stale}
readValue    = 0.00 {ok}
faultCause   = ""            ← empty, no hint
enabled      = true
```

Fix — set the type explicitly after the copy, over oBIX (REST cannot write an enum):

```
PUT <obix>/config/Drivers/<net>/<device>/points/<point>/proxyExt/dataType/
    <enum val="integerType"/>
```

Polling begins on the next cycle; no restart required. When this was applied to a live
test point, the value changed from `0.00 {stale}` to the register's real content within
one poll interval.

---

## 4. Verify from outside

Never accept the station's own read-back. Drive it from a Modbus master on another host:

```python
import socket, struct

def mb(host, pdu, unit=1, port=502, timeout=6):
    s = socket.create_connection((host, port), timeout=timeout)
    s.sendall(struct.pack('>HHHB', 0x1234, 0, len(pdu) + 1, unit) + pdu)
    r = s.recv(512); s.close()
    return r

# FC03 read HR[16], one register
mb('<HOST>', struct.pack('>BHH', 3, 0x10, 1))
# FC06 write HR[16] = 8888
mb('<HOST>', struct.pack('>BHH', 6, 0x10, 8888))
# FC03 read back → 8888 means the loop is closed
```

Completion criterion: write a distinctive value from outside, read it back from outside,
and confirm the station's point shows the same number with `{ok}`.

---

## 5. Point direction matters

A slave-side point published to an external master is normally **readable from outside
and writable from inside**. Writing it from outside goes through the proxy into the
priority array; if the point is also driven internally, the external write may be masked
by a higher priority slot. Check `out` for `{overridden}` before concluding the register
write was ignored.

If you need the external master to *control* a value, publish a point whose
`in16` (lowest priority) is free, or an output-semantic writable point.

---

## Related: the client direction is a different object type

| | Slave (this document) | Client |
|:--|:--|:--|
| Network type | `modbusTcpSlave:ModbusTcpSlaveNetwork` | `modbusTcp:ModbusTcpNetwork` |
| Device type | `modbusTcpSlave:ModbusSlaveDevice` | `modbusTcp:ModbusTcpDevice` |
| Proxy ext | `ModbusServerNumericProxyExt` | `ModbusClientNumericProxyExt` |
| Address slot | `dataAddress` (FlexAddress) | `dataAddress` (FlexAddress) |
| Who initiates | external master | station |
| Polling config | none | `devicePollConfig/*` + network `pollScheduler` |

A slave network has no `pollScheduler`: it answers, it does not poll. Seeing `totalPolls`
absent on a slave network is normal, not a fault.

---

## Fault reference

| Symptom | Cause | Fix |
|:--|:--|:--|
| point has only `NullProxyExt`, no `dataAddress` | created with `add` | `cp` from a point with the real proxy |
| `Property 'address' not found` | wrong slot name | use `dataAddress` |
| `Property 'X' not found` | guessed slot name | `GET /api/config?path=<path>` and read the real `slots` list |
| `0.00 {stale}`, empty `faultCause`, integer register | copied `dataType = Float Type` | set `dataType = integerType` over oBIX |
| `Illegal parent 'X' for child 'Y'` | right type, wrong parent | create the network/device first |
| station reads fine, external master times out | wrong TCP port, or the slave network is disabled | check the slave network's port and `enabled` |

`/api/types` and `/api/modules` do not enumerate types — they return a single note.
To confirm a class exists, list the module jar:

```
modbusTcpSlave-rt.jar → com/tridium/modbusTcpSlave/BModbusServerNumericProxyExt.class
```

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
