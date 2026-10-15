# Assembling proxy extensions at point creation (`PROXY`)

**Applies to `glineRestApi` v2.41.0 and later.**

This document covers one thing: creating a point **with its driver proxy extension
already attached**, in a single `add` operation.

---

## The problem this solves

Driver points read and write through a *proxy extension* — the object that knows how
to talk to the field device. An SNMP point's `proxyExt` is a `SnmpNumericProxyExt`;
a Modbus point's is a `ModbusProxyExt`, and so on.

Before v2.41, `add` created the point but left `proxyExt` at its default
(`NullProxyExt`), and the slot could not be filled afterwards:

| Attempt | Result |
|:--|:--|
| `{"OP":"remove","PATH":".../points/Pt/proxyExt"}` | error — `proxyExt: control:AbstractProxyExt` (protected) |
| `{"OP":"add","PATH":".../points/Pt","N":"proxyExt","T":"snmp:SnmpNumericProxyExt"}` | error — `Slot 'proxyExt' already exists` |
| `{"OP":"add","PATH":".../points/Pt/proxyExt","T":"snmp:SnmpNumericProxyExt"}` | error — illegal child for parent |

The point existed, appeared in the tree, and read `0.00 {fault,stale}` forever.

---

## The `PROXY` field

`add` accepts two optional fields:

| Field | Default | Meaning |
|:--|:--|:--|
| `PROXY` | *(none)* | Type of the proxy extension to assemble, as `module:Type` |
| `PROXY_SLOT` | `proxyExt` | Which slot to write it into |

```json
{"OP":"add","PATH":"/Drivers/SnmpNetwork1/PDU_AP8858_180/points",
 "T":"control:NumericWritable",
 "N":"Phase1_Voltage",
 "PROXY":"nSnmp:SnmpNumericProxyExt"}
```

Response:

```json
{"OP":"add","name":"Phase1_Voltage","PROXY":"nSnmp:SnmpNumericProxyExt","status":"ok"}
```

The point now has a real proxy:

```
points/Phase1_Voltage
└── proxyExt  ->  SnmpNumericProxyExt
```

Then configure the proxy as you would any other component:

```json
{"OP":"mod","PATH":"/Drivers/SnmpNetwork1/PDU_AP8858_180/points/Phase1_Voltage/proxyExt",
 "N":"objectIdentifier","V":"1.3.6.1.4.1.318.1.1.26.6.3.1.6.1"}
```

Omitting `PROXY` keeps the pre-v2.41 behaviour exactly: a point with a null proxy.

---

## Two operational notes

### 1. Restart the station after creating the point

The proxy does not begin polling until the station restarts. Immediately after
`add` + `mod`, the point reports:

```
out        = 0.00 {fault,stale}
faultCause = "Read fault: Illegal Object Identifier"
```

This is not a configuration error. The proxy's `started()` hook validates the OID
before the freshly written slot is visible to the live object. Setting the OID again
does **not** substitute for the restart.

After `stop` / `start`:

```
out        = 0.00 {stale}       (stale only while the field device is unreachable)
faultCause = ""                 (no fault)
```

The point then behaves identically to one created in Workbench by hand.

### 2. Only one SNMP network per station

If two SNMP networks exist, every device on them faults:

```
Network fault: Only one SNMP Network is allowed per station.
Remove duplicate SNMP network(s) and restart station.
```

Delete the extra network(s) and restart.

---

## Choosing the right SNMP network type

A stock Niagara 4 install carries **two** network types both named `SnmpNetwork`:

| Type spec | Class | `sendConfig` / `receiveConfig` / `trapConfig` |
|:--|:--|:--|
| `snmp:SnmpNetwork` | `com.tridium.snmp.BSnmpNetwork` (legacy) | **absent** |
| `nSnmp:SnmpNetwork` | `com.tridium.nSnmp.BSnmpNetwork` (nDriver) | present |

Build SNMP networks with **`T="nSnmp:SnmpNetwork"`**. With the legacy type the
network's communication-configuration slots never materialise, so its devices fault
with `Illegal Object Identifier` regardless of how correct the point is — and the
fault looks like a point problem when it is not.

```json
{"OP":"add","PATH":"/Drivers","T":"nSnmp:SnmpNetwork","N":"SnmpNetwork1"}
{"OP":"add","PATH":"/Drivers/SnmpNetwork1","T":"nSnmp:SnmpDevice","N":"PDU_1"}
{"OP":"mod","PATH":"/Drivers/SnmpNetwork1/PDU_1","N":"ipAddress","V":"192.168.1.50"}
{"OP":"add","PATH":"/Drivers/SnmpNetwork1/PDU_1/points",
 "T":"control:NumericWritable","N":"Phase1_Voltage",
 "PROXY":"nSnmp:SnmpNumericProxyExt"}
```

---

## Verified reference

Confirmed live on a Niagara 4.14 station (2026-10-15), against an APC AP8858 rack
PDU, with `PROXY` set to `nSnmp:SnmpNumericProxyExt`:

| Check | Result |
|:--|:--|
| `add` response | `status: ok`, `PROXY` echoed |
| Point children | `proxyExt -> SnmpNumericProxyExt` |
| `proxyExt` type | `SnmpNumericProxyExt` (not `NullProxyExt`) |
| Proxy slot count | 11, identical to a Workbench-created point |
| `faultCause` after restart | empty |
| `objectIdentifier` | `1.3.6.1.4.1.318.1.1.26.6.3.1.6.1` read back intact |
| `out` | matches the equivalent hand-built point on the same device |

### APC AP8858 reference OIDs (PowerNet-MIB rPDU2)

Use the `...318.1.1.26.*` family:

| Point | OID |
|:--|:--|
| Phase1_Current | `1.3.6.1.4.1.318.1.1.26.6.3.1.5.1` |
| Phase1_Voltage | `1.3.6.1.4.1.318.1.1.26.6.3.1.6.1` |
| Phase1_Power | `1.3.6.1.4.1.318.1.1.26.6.3.1.7.1` |
| PDU_Power | `1.3.6.1.4.1.318.1.1.26.4.3.1.5.1` |
| PDU_Model | `1.3.6.1.4.1.318.1.1.26.2.1.8.1` |
| SysUpTime | `1.3.6.1.2.1.1.3.0` |

---

## Also in v2.41.0

`GET /api/status` now reports the version read from the module's own
`META-INF/module.xml`. It was previously a hardcoded literal that had drifted — it
returned `2.4` on a v2.4.0 build and would have kept returning it on this one.

```bash
curl -u "<USER>:<PASS>" http://<HOST>:8082/api/status
{"status":"ok","name":"glineRestApi","version":"2.41.0","port":8082}
```

---

Shanghai Gline Net Co. · jason.zhang@gline-net.com
