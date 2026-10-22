# Exposing station points as oBIX points

**Applies to** Niagara N4 (verified on 4.14.0.162).
Covers **station → oBIX**: the station publishes its own points over oBIX so an external
oBIX client can read — and, for writable exports, write — them.

Consuming an external oBIX server into a station (`ObixNetwork` device) is the opposite
direction and is covered in [`../part2-client/`](../part2-client/).

---

## Where the objects live

```
/Drivers/ObixNetwork                 type obixDriver:ObixNetwork
└── exports                          the export table
    └── <export point>               type obixDriver:ObixExport
```

Note the module prefix: the type is **`obixDriver:ObixExport`**.

---

## 1. Create the export point (REST)

```json
[{"OP":"add","PATH":"/Drivers/ObixNetwork/exports",
  "N":"demo_num1","T":"obixDriver:ObixExport"}]
```

The export is created with an empty `point` slot; step 2 fills it.

## 2. Bind the source point (oBIX `PUT`)

`point` is a `BOrd` slot — a station ord, not a string. It is written as a `<uri>` over oBIX:

```bash
curl -X PUT "http://<HOST>/obix/config/Drivers/ObixNetwork/exports/demo_num1/point/" \
  -u "<USER>:<PASS>" \
  -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><uri val="station:|slot:/Demo/Temp1" xmlns="http://obix.org/ns/schema/1.0"/>'
```

Once `point` resolves to a live component, `status` becomes `{ok}` with no restart.

Confirm by reading the slot back:

```
GET <obix>/config/Drivers/ObixNetwork/exports/demo_num1/point/
→ <uri val="station:|slot:/Demo/Temp1" .../>
```

The read-back is the confirmation, not the `PUT` response body.

Escaping for the `val` attribute follows the oBIX `$xx` convention: `#` is `$23`, space is
`$20`, `.` is `$2e`, `/` is `$2f`. Farm out a path with a `#` in it as
`station:|slot:/Drivers/ModbusTcpNetwork/dev$23/points/reg1`.

## 3. Confirm from outside

```bash
curl -u "<USER>:<PASS>" "http://<HOST>/obix/config/Drivers/ObixNetwork/exports/demo_num1/"
```

A healthy numeric export returns the point object with the live value:

```xml
<real val="42.5" href="..." is="obix:WritablePoint obix:Point" status="ok"/>
```

The export appears under the same tree an external oBIX client already browses, so no
separate port or service is needed — the oBIX server that serves `/obix/config` is the one
that serves the export.

## 4. Write through an export

An export publishes the source point; writing the export writes the source. Use the `set`
action node, which sits under the point root:

```
POST <obix>/config/Drivers/ObixNetwork/exports/demo_num1/set/
Content-Type: text/xml

<real val="25.5"/>
```

Read the source point back over REST to confirm the write landed where the export points:

```
GET /api/config?path=/Demo/Temp1
→ out = 25.5 {ok}
```

---

## Which channel writes which step

Two channels, and each one owns a different slot type:

| Step | Channel | Why that channel |
|:--|:--|:--|
| Create the export | REST `add` | object creation belongs to the REST batch |
| Bind the source point | oBIX `PUT` `<uri>` | `point` is a `BOrd`; the batch encoder carries strings only |
| Write the value | oBIX `POST …/set/` | the action node is the oBIX write surface |
| Read anything back | REST `GET` or oBIX `GET` | both render the same slots |

The same split appears on the BACnet side: `objectId` and `objectName` are REST writes,
`pointOrd` is an oBIX `<uri>` write. DynamicEnum slots (a BACnet `adapter`, a proxy
`dataType`) are also oBIX writes, with the enum value given by its escaped name.

---

## Summary of the three-step pattern

Every "publish a point to an external protocol" workflow in this series has the same
shape, and each step may use a different channel:

| Step | BACnet export | oBIX export | Modbus slave |
|:--|:--|:--|:--|
| 1. Create object | REST `add` | REST `add` | REST `cp` |
| 2. Bind source / address | `pointOrd` → **oBIX** | `point` → **oBIX** | `dataAddress` → REST |
| 3. Assign public identity | `objectId` → REST | *(binding is enough)* | *(binding is enough)* |

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
