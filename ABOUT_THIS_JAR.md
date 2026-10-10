# About `niagaraRestApi-rt.jar`

**This jar is the v1 module (`niagaraRestApi`) — not v2.**

| Item | Value |
|:--|:--|
| Edition | **v1** |
| Module name | `niagaraRestApi-rt` (as declared inside `META-INF/module.xml`) |
| Internal version | `1.0.1.4.14` |
| Port | 8081 |
| Authentication | None (intended for trusted internal networks) |
| Niagara version | 4.14 |
| Signed | Yes (GLINE + NIAGARA4 signatures) |

## What v1 can do

11 batch operations through a single `POST /api/batch`:

`ADD` · `LINK` · `RENAME` · `DUPLICATE` · `CP` (deep copy) · `MOD` · `UNLINK` ·
`REMOVE` · `READ` · `LIST` · `INVOKE`

## What v1 does NOT do

| Capability | v1 | Where it lives |
|:--|:--:|:--|
| **BQL query** | ❌ returns `{"OP":"bql","status":"unknown"}` | **v2 only** |
| Built-in authentication | ❌ | **v2 only** |
| CIDR allow-list | ❌ | **v2 only** |
| Program management | ❌ | **v2 only** |

> **BQL is a v2 feature.** On v1, sending a BQL request returns `status:"unknown"`.
> Verified live on :8081 (v1) and :8082 (v2) with the same request.

## Why the file name has no "v1"

The file name is kept as `niagaraRestApi-rt.jar` **on purpose**, to match the module
name declared inside the jar (`niagaraRestApi-rt`). Niagara resolves modules by the
metadata inside the jar, and keeping the file name aligned with the module name
avoids any ambiguity during installation or upgrade.

**Do not rename the file** — install it exactly as `niagaraRestApi-rt.jar` in your
Niagara `modules/` directory.

## Install

1. Copy `niagaraRestApi-rt.jar` into your Niagara `modules/` directory.
2. Restart the station.
3. The REST API listens on port 8081 (configurable).

```bash
curl -X POST http://your-station:8081/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"LIST","PATH":"Drivers"}]'
```

## Getting v2 (with BQL, auth, program management)

v2 is a different module (`glineRestApi`, port 8082) and is **not distributed in this
repository**. See the "Getting v2" section of the main [README](README.md).
