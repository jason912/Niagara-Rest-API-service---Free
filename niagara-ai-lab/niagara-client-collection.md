# Collecting data from field devices — how to tell it is working

**Applies to** Niagara N4 (verified on 4.14.0.162).
This is the **client** direction: the station polls external devices and holds their
values in station points. The opposite direction (publishing station points outward) is
covered by the BACnet / oBIX / Modbus server documents in this folder.

Everything here is about one question that is easy to get wrong: **is the point actually
being collected, or does it just look plausible?**

---

## Why the obvious checks are not enough

Four independent signals all report success on a point that never receives data:

| Signal | What it actually means | Why it misleads |
|:--|:--|:--|
| device `status = {ok}` | the device object is configured and the driver accepted it | says nothing about whether a poll fired |
| `health = Ok [timestamp]` | a PingMonitor read succeeded | runs on its own path, independent of the poll queue |
| `readValue = 0.00 {ok}` | a value object exists | the *status facet* is `ok`, the point is not refreshed |
| `readStatus = okNotActive` | the poll range is configured | "not active" is literal — nothing is scheduled |

And one failure report that looks like success:

```
out        = 0.00 {stale}
faultCause = ""          ← empty. No fault, no hint.
enabled    = true
```

An empty `faultCause` with a `{stale}` value is the normal appearance of a point that is
being polled but decoded wrongly, *and* of a point that is not polled at all. The two are
distinguishable only by counters and by an external value change.

---

## The two counters that settle it

### 1. `pollScheduler` — did any poll fire at all?

```
/drivers/<driver network>/pollScheduler
```

```
pollEnabled      = true
totalPolls       = N over Mms
normalCount      = current=1 average=0
statisticsStart  = <when the scheduler was (re)built>
```

Read it twice, ten seconds apart.

| Observation | Conclusion |
|:--|:--|
| `totalPolls` increases | the scheduler is running; the problem is downstream (decoding, mapping, device response) |
| `totalPolls` frozen, `normalCount = 0` | **no point has ever been registered** — the problem is upstream of polling |

`normalCount = 0` is the decisive one. It is not "polling failed"; it is "the queue is
empty". Comparing two networks side by side makes it obvious:

| Network | Scheduler class | `totalPolls` | `normalCount` |
|:--|:--|:--|:--|
| `SnmpNetwork1` | `NPollScheduler` | 122 over 17s | `current=1` |
| `ModbusTcpNetwork` | `BasicPollScheduler` | 0 over 0ms | **`current=0`** |

### 2. `devicePollConfig` — what is the driver told to read?

```
/drivers/<driver network>/<device>/devicePollConfig/Range_<start>_<end>
```

| Slot | Meaning |
|:--|:--|
| `startAddress` | first register of the range (`Hex:0000`) |
| `consecutivePointsToPoll` | how many points the range covers |
| `readGroupSize` | registers per request |
| `readStatus` | `okNotActive` / `0: ok` — **a range state, never proof of collection** |
| `dataType` | the register interpretation (`Holding Register`) |

`consecutivePointsToPoll` has been observed at `0` on a range that nonetheless spanned
one device's whole point table. Changing it to the point count, and deleting the range
entry entirely, both produced **zero** additional polls — so do not treat a non-zero value
here as a fix, and do not treat `0` alone as the root cause. Use it as a description of
intent, not as a diagnosis.

---

## The only reliable proof: change the value outside

Configure nothing, trust nothing, and drive the far end:

1. Find the device's real value with an independent client (Modbus master, `snmpget`,
   BACnet ReadProperty) from another host.
2. Change it at the source — write a distinctive number, or pick a quantity that moves.
3. Watch the station point.

The point must change to the new value with `{ok}`. This is the one test that cannot be
faked by status facets, health monitors, or copied values.

### Worked Modbus case

A slave network and one client point on the same station, pointed at the station's own
slave port, is the cheapest possible loop:

```
external Modbus master: FC06 write HR[1] = 5555  →  client point C1 = 5555.00 {ok}
external Modbus master: FC06 write HR[1] = 6666  →  client point C1 = 6666.00 {ok}
external Modbus master: FC06 write HR[1] = 4321  →  client point C1 = 4321.00 {ok}
```

Three distinct values, each reflected, with `totalPolls` climbing and the slave network's
`currentConnections = 1` throughout. That is a working client.

### Why a *copy* of a device proves nothing

Duplicating a working device and pointing the copy elsewhere produced a device that
appeared healthy — `socket = Opened`, `totalPolls` climbing — while every point kept the
values it had inherited from the source. Copied points carry copied values; a clone that
"has data" immediately after creation has nothing but the source's last write. Only an
external value change distinguishes a clone from a collection.

---

## Per-protocol notes

### Modbus TCP client

- **`dataType` is copied with the point and is the first thing to check.** An
  integer register read through `Float Type` yields `0.00 {stale}` with an empty
  `faultCause`. Set `dataType = integerType` over oBIX and polling starts on the next
  cycle — no restart.
- A `cp` from a point on another device is the normal way to get a
  `ModbusClientNumericProxyExt`, but it also imports that device's register type and
  scaling. Verify `dataType`, `dataAddress`, and `byteOrder` after every copy.
- `devicePollConfig` ranges are created by the driver, not by copying points; a new point
  does not automatically appear in a new range.
- If the far end is unreachable, the point goes `{stale}` **and** the device's `health`
  timestamp stops advancing. A health timestamp that keeps moving while points stay
  stale means the far end answers the ping address but not the point addresses — compare
  `pingAddress` against the points' `dataAddress` values.

### SNMP client

The most direct to verify, because `snmpget` speaks the same protocol from outside:

```bash
snmpget -v2c -c <community> <device> <OID>
```

| Niagara point | OID | Niagara | `snmpget` |
|:--|:--|:--|:--|
| Phase1_Voltage | `1.3.6.1.4.1.318.1.1.26.6.3.1.6.1` | 227.00 `{ok}` | INTEGER: 227 |
| Phase1_Current | `1.3.6.1.4.1.318.1.1.26.6.3.1.5.1` | 5.00 `{ok}` | INTEGER: 5 |
| PDU_Power | `1.3.6.1.4.1.318.1.1.26.4.3.1.5.1` | 8.00 `{ok}` | INTEGER: 8 |

A subset of points staying `{stale}` on an otherwise healthy device usually means the
OIDs are absent on that model — the OID table is written for a family, not for one unit.
Confirm with `snmpget` before touching the station.

Use the nDriver network type (`nSnmp:SnmpNetwork`), not the legacy `snmp:SnmpNetwork`,
and keep **one** SNMP network per station. Both traps are covered in
`glineRestApi-v2.41-proxy-extensions.md`.

### BACnet client

- A device in `{disabled,down}` with a `health` timestamp months old has not been
  participating; enabling it is the only way to learn anything. Do not read a stale
  `TransactionTimeoutException` as a current fault.
- Verification is ReadProperty from outside, the same call used for exported objects —
  but with the *device instance of the field device*, not the station's.
- BACnet collects on COV subscriptions as well as polling, so an empty `normalCount` on a
  BACnet network is not automatically wrong. Check whether COV is enabled before drawing
  conclusions from the scheduler.

### oBIX client

`ObixNetwork` devices read an external oBIX server. The export-side rules in
`niagara-obix-server-points.md` apply in reverse: a `{fault}` on the imported point
usually means the far server does not expose the path, not that the station is broken.

---

## Diagnostic sequence

Use this order; each step removes a whole class of causes.

| # | Check | If it fails |
|:--|:--|:--|
| 1 | Is the **driver network** `enabled` and `{ok}`? | enable the network — a disabled parent makes every child inert |
| 2 | Is `pollScheduler.totalPolls` increasing? | if frozen with `normalCount = 0`: no point is registered (see step 3) |
| 3 | Do the points appear in `devicePollConfig`, with a sane range and `dataType`? | fix the range; verify the point's own `proxyExt/dataType` |
| 4 | Does the device `health` timestamp advance? | far end unreachable on the ping address |
| 5 | **Change the value at the far end** — does the point follow? | this is the only real failure that survives steps 1–4 |

Steps 1–4 are all readable over REST with no side effects. Step 5 requires access to the
field device or a peer station.

---

## Known open case

Three Modbus client devices pointed at the same gateway, on the same network and at the
same moment as a working client device, held 29–30 points `{stale}` while the working
device beside them collected normally. Ruled out by measurement: far-end reachability
(TCP open from the station, real values read from outside), addressing (`deviceAddress`,
base address, range, `dataType` all correct and identical to the working device's
configuration), `enabled` state, range size, and full station restart. Their per-range
`readStatus` reached `0: ok` while points stayed stale.

Two conclusions are safe: the driver as a whole works (proven by the working device in the
same second), and the fault is specific to those three device objects. Resolving it
further needs in-station inspection (Workbench driver threads) or reconstruction of the
device objects — not more REST probing.

The lesson generalises: **a working neighbour is the most valuable diagnostic.** When one
device collects and another does not under identical network conditions, the network,
the driver module, and the protocol are all exonerated in one step.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
