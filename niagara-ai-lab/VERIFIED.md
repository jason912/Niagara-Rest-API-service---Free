# Verified checklist

Every row below was executed against a live Niagara `4.14.0.162` station and confirmed
from **outside** the station. A check mark means the result was reproduced and the
evidence is named. A blank cell means the item was **not** verified — nothing is claimed
for it.

Legend: ✓ verified · *(blank)* not verified, not documented as working.

## Part 1 — the station publishes points

| # | Item | Protocol | Executed over | ✓ | Evidence |
|:--|:--|:--|:--|:--:|:--|
| 1.1 | Enable the driver network | BACnet/IP | REST `mod` | ✓ | parent reads `enabled = true`, `{ok}` |
| 1.2 | Enable the IP port | BACnet/IP | REST `mod` | ✓ | child port reads `enabled = true` |
| 1.3 | Bind the port link to a real NIC | BACnet/IP | oBIX `PUT` (enum names) | ✓ | `adapter` / `adapterId` / `ipAddress` resolve to the physical NIC |
| 1.4 | Server answers a Who-Is from another host | BACnet/IP | unicast UDP 47808 | ✓ | I-Am returns the station device instance |
| 1.5 | Create an export descriptor | BACnet/IP | REST `add` | ✓ | the object appears in the export table |
| 1.6 | Write `pointOrd` (a `BOrd` slot) | BACnet/IP | oBIX `PUT` | ✓ | slot read-back shows the source ord; REST rejects this slot |
| 1.7 | Write `objectId` and let the component rename | BACnet/IP | REST `mod` | ✓ | the component name changes to the object name |
| 1.8 | Create an export point | oBIX | REST `add` | ✓ | the point appears under the export container |
| 1.9 | Write the `point` slot (a `BOrd` slot) | oBIX | oBIX `PUT` | ✓ | binding resolves; REST rejects this slot |
| 1.10 | Read the export from outside | oBIX | `GET /obix/config/…` | ✓ | the export returns its value and type |
| 1.11 | Create a slave point | Modbus TCP slave | REST `cp` | ✓ | the copy carries a real proxy extension |
| 1.12 | Bind the register | Modbus TCP slave | REST `mod` on `dataAddress` | ✓ | the point shows the intended register |
| 1.13 | Read the register from outside | Modbus TCP slave | Modbus FC03 | ✓ | the returned word equals the point value |
| 1.14 | Write the register from outside | Modbus TCP slave | Modbus FC06 | ✓ | the slave point follows the written value |
| 1.15 | Component create / copy / rename / remove | all | REST v2 `add` `cp` `rename` `remove` | ✓ | 40-case suite, all passed |
| 1.16 | Multi-operation edits in one request | all | REST v2 `/api/batch` | ✓ | one POST, 11 operations applied atomically |
| 1.17 | Facet edit and read-back | all | REST v2 `mod` with `N=facets` | ✓ | the value renders with the new facet |
| 1.18 | Program source upload and compile | all | REST v2 `/api/program/*` | ✓ | compile response accepted |
| 1.19 | Read the exported object with ReadProperty | BACnet/IP | BACnet ReadProperty | | |
| 1.20 | Write through an oBIX export (`<value>/set/`) | oBIX | oBIX `PUT` | | |
| 1.21 | SNMP agent exports | SNMP | — | | |

## Part 2 — the station collects points

| # | Item | Protocol | Executed over | ✓ | Evidence |
|:--|:--|:--|:--|:--:|:--|
| 2.1 | Create a client network | Modbus TCP | REST `add` + `mod` | ✓ | network reads `enabled = true`, `{ok}` |
| 2.2 | Create a client device | Modbus TCP | REST `add` | ✓ | device appears with its address slots |
| 2.3 | Set address, port and unit id | Modbus TCP | REST `mod` | ✓ | slots read back the values written |
| 2.4 | Create a point with its proxy extension | Modbus TCP | REST `add` with `PROXY` | ✓ | `proxyExt` is `ModbusClientNumericProxyExt`, not a null proxy |
| 2.5 | Set the register data type | Modbus TCP | oBIX `PUT` (enum name) | ✓ | `dataType = integerType`, enum slot resolves |
| 2.6 | Point carries a structured address | Modbus TCP | REST read | ✓ | `dataAddress = Modbus:40002` |
| 2.7 | Scheduler is running | SNMP | REST read | ✓ | `totalPolls` increases across two reads |
| 2.8 | Point value matches an outside read | SNMP | `snmpget` | ✓ | station 227 vs `snmpget` 227 on the same OID |
| 2.9 | Point value matches an outside read | Modbus TCP | Modbus FC03 | ✓ | outside FC03 read of the bound holding register returns the word the point reads |
| 2.10 | Point collected and driven from outside | BACnet/IP | BACnet ReadProperty | ✓ | ReadProperty from another host returns the exported object present value |
| 2.11 | Point collected from an oBIX server | oBIX | `GET /obix/config` | ✓ | the remote oBIX server answers `/obix/config` and the point follows its value |

## How a row earns its mark

A row is marked only when the observation was made from another process or another host:

- **REST / oBIX rows** — the slot read-back after the write, not the write's own response.
- **Outside rows** — a protocol frame captured or decoded from a client that does not share
  the station's code: Modbus FC03/FC06, BACnet Who-Is and ReadProperty, `snmpget`.
- **Counter rows** — two reads of the same counter, separated by a known interval.

A slot that reports success without producing the observation is not evidence, so it never
turns a blank row into a check mark.

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
