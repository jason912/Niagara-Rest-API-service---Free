# About `niagaraRestApi-rt.jar`

**This jar is the v1 module (`niagaraRestApi`).**

| Item | Value |
|:--|:--|
| Edition | **v1** |
| Module name | `niagaraRestApi-rt` (as declared inside `META-INF/module.xml`) |
| Internal version | `1.0.1.4.14` |
| Port | 8081 |
| Authentication | None (intended for trusted internal networks) |
| Niagara version | 4.14 |
| Signed | Yes (GLINE + NIAGARA4 signatures) |

## Why the file name has no "v1"

The file name is kept as `niagaraRestApi-rt.jar` **on purpose**, to match the module
name declared inside the jar (`niagaraRestApi-rt`). Niagara resolves modules by the
metadata inside the jar, and keeping the file name aligned with the module name
avoids any ambiguity during installation or upgrade.

**Do not rename the file** — install it exactly as `niagaraRestApi-rt.jar` in your
Niagara `modules/` directory.

## What this is NOT

- This is **not** v2. v2 is a **different module** (`glineRestApi`, port 8082) with
  built-in authentication, BQL and program management. It is **not distributed in
  this repository** — see the "Getting v2" section of the main [README](README.md).

## Install

1. Copy `niagaraRestApi-rt.jar` into your Niagara `modules/` directory.
2. Restart the station.
3. The REST API listens on port 8081 (configurable).

```bash
curl -X POST http://your-station:8081/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"LIST","PATH":"Drivers"}]'
```
