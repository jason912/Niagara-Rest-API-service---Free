# Exposing station points as oBIX points

**Applies to** Niagara N4 (verified on 4.14.0.162).
Covers **station → oBIX**: the station publishes its own points over oBIX so an external
oBIX client can read — and, for writable exports, write — them.

Consuming an external oBIX server into a station (`ObixNetwork` device) is the opposite
direction and is not covered here.

---

## Where the objects live

```
/Drivers/ObixNetwork                 type obixDriver:ObixNetwork
└── exports                          the export table
    └── <export point>               type obixDriver:ObixExport
```

Note the module prefix: the type is **`obixDriver:ObixExport`**. Writing
`obix:ObixExport` returns a type-not-found error.

---

## 1. Create the export point (REST)

```json
[{"OP":"add","PATH":"/Drivers/ObixNetwork/exports",
  "N":"demo_num1","T":"obixDriver:ObixExport"}]
```

Immediately after creation:

```
point  = null
status = {fault}        ← expected; nothing is bound yet
```

`{fault}` here is not a failure of the `add`. It means the export has no source.

---

## 2. Bind the source point — oBIX only

`point` is a `BOrd` slot. Three channels were tried against it:

| Channel | Result |
|:--|:--|
| REST `mod` with `V="station:\|slot:/Demo/Temp1"` | `javax.baja.sys.BString cannot be cast to javax.baja.naming.BOrd` |
| box `set({slot:'point', value: baja.Ord.make(...)})` | returns OK, **value stays null** — silent failure |
| **oBIX `PUT` `<uri>`** | **succeeds** |

```bash
curl -X PUT "http://<HOST>/obix/config/Drivers/ObixNetwork/exports/demo_num1/point/" \
  -u "<USER>:<PASS>" \
  -H "X-Requested-With: XMLHttpRequest" -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><uri val="station:|slot:/Demo/Temp1" xmlns="http://obix.org/ns/schema/1.0"/>'
```

That is the whole binding step: once `point` resolves to a live component, `status`
becomes `{ok}` with no restart and no further action.

Confirm by reading the slot back:

```
GET <obix>/config/Drivers/ObixNetwork/exports/demo_num1/point/
→ <uri val="station:|slot:/Demo/Temp1" .../>
```

Never trust the `PUT` response body alone — the channel has been observed to answer
`BadUriErr` on writes that in fact took effect.

---

## 3. Two fault rules observed

| Situation | Result | Meaning |
|:--|:--|:--|
| Two exports bound to the **same** source point | second one `{fault}` | one source point backs exactly one export |
| Export bound to a read-only `control:NumericPoint` | `{fault}` | the export declares itself `obix:WritablePoint`; the source is expected to be writable (**single observation, inference unconfirmed**) |

The first rule is firm and reproducible. The second is a hypothesis from one run — treat
it as a diagnostic hint, not a guarantee, and confirm against your own station before
building a workflow on it.

---

## 4. Verify from outside

```bash
curl -u "<USER>:<PASS>" "http://<HOST>/obix/config/Drivers/ObixNetwork/exports/demo_num1/"
```

A healthy numeric export returns the point object with the live value:

```xml
<real val="42.5" href="..." is="obix:WritablePoint obix:Point" status="ok"/>
```

The export appears under the same tree an external oBIX client already browses, so no
separate port or service is needed — the oBIX server that serves `/obix/config` is the
one that serves the export.

---

## Writing through an export

An export publishes the source point; writing the export writes the source. Use the
`set` action node, not the point object itself:

```
POST <obix>/config/Drivers/ObixNetwork/exports/demo_num1/set/
Content-Type: text/xml

<real val="25.5"/>
```

Posting to the export object without `/set/` returns `BadUriErr`.

---

## What oBIX cannot do

| Attempt | Result |
|:--|:--|
| Create a component (`POST` parent with a type object, `/obix/def/<type>`, `PUT` a child path) | `BadUriErr` — every variant, on two independent stations |
| Add an extension (history, alarm) | `BadUriErr` |
| Write a proxied point's value | the `set` node exists but the value does not change; `PUT <point>/out/` returns `Cannot translate` |
| Clear a priority slot to null (`<real null="true"/>`) | `Cannot translate` |

So oBIX owns three things in this workflow: **binding `BOrd` slots**, **DynamicEnum
writes**, and **reading history/alarm data**. Point and extension *creation* belongs to
REST.

---

## Pitfalls

- **`/set/` sits under the point root, not under `in16`.** `POST <point>/in16/set/`
  returns `BadUriErr`.
- **A proxied point's `set` node is inert.** The node is published, the write is accepted,
  the value does not move. This is an oBIX mapping limitation for proxied points, not an
  authentication problem — a normal point written with the same credentials works.
- **`<real null="true"/>` is rejected.** oBIX cannot clear a priority slot; only the box
  channel can (see the box document).
- **`#` in a path must be escaped as `$23`**, and other reserved characters follow the
  `$xx` convention used by DynamicEnum names.

---

## Summary of the three-step pattern

Every "publish a point to an external protocol" workflow in this series has the same
shape, and each step may require a different channel:

| Step | BACnet export | oBIX export | Modbus slave |
|:--|:--|:--|:--|
| 1. Create object | REST `add` | REST `add` | REST `cp` |
| 2. Bind source / address | `pointOrd` → **oBIX** | `point` → **oBIX** | `dataAddress` → REST |
| 3. Assign public identity | `objectId` → REST | *(binding is enough)* | *(binding is enough)* |

---

Shanghai Gline Net Co. · @jason912 · jason.zhang@gline-net.com
