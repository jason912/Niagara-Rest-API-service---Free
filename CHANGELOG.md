# Changelog

All notable changes to **glineRestApi (v2)** are documented here.

> **Note on editions.** This repository ships **v1 (`niagaraRestApi`)** only.
> The **v2 (`glineRestApi`)** module is a separate module distributed on request —
> see [Getting v2](README.md#getting-v2). This changelog is published so customers
> can see what each v2 release adds before requesting a build.

Versions correspond to `META-INF/module.xml` `vendorVersion` and to the `version`
field returned by `GET /api/status`.

---

## v2.5.0 — 2026-10-15

**Alarm & history extension automation — attach, configure, and activate over REST.**

### Added
- **Alarm & history extension setup via `batch`.** Extensions are ordinary components, so
  v2 can now drive the full capture setup over HTTP — no Workbench required.
  - `{"OP":"add","PATH":"/pt","T":"history:NumericCovHistoryExt","N":"he"}`
  - `{"OP":"mod","PATH":"/pt/he","N":"enabled","V":true}` → extension reports
    `active=true` (collection live)
  - `{"OP":"add","PATH":"/pt","T":"alarm:AlarmSourceExt","N":"ae"}`
  - `{"OP":"mod","PATH":"/pt/ae","N":"alarmClass","V":"/AlarmClass"}`
- Verified live on a Niagara 4.14 station: extension attached, slot written, and the
  extension activated and read back through the API.

### Notes
- Extension types: `alarm:AlarmSourceExt`; `history:Numeric|Boolean|Enum|StringCovHistoryExt`;
  `history:NumericIntervalHistoryExt`.
- `timeDelay` (`RelTime`) is written as a **raw millisecond number** (`5000`), not `"5s"`.
- `historyName` / `toOffnormalText` (`BFormat`) and `alarmEnable` (`AlarmTransitionBits`)
  are **not** writable via `MOD` — a property-type limit, not an API limit.

### Documentation
- README: new **Alarm & History Extensions via REST** section with copy-paste `curl`
  examples and a `MOD`-writable-slot table.
- REST API Guide / User Guide: new chapter on extension setup, plus the companion
  chapter on reading the collected data through the station's **Web Box** feature.

---

## v2.4.0 — 2026-10-15

**Facet handling reworked: enum ranges, ordered facets, slot-facet reads.**

### Added
- **Enum facets (`range=`)** — `MOD` with `V="facets:range=A,B,C"` writes a
  `BEnumRange` (`{A=0,B=1,C=2}`); the indexed form `range=0:Low,1:Mid,2:High`
  is also accepted (`{Low=0,Mid=1,High=2}`).
- **Slot-facet read** — `READ` accepts an optional `SLOT` to read a specific slot's
  facets: `{"OP":"read","PATH":"/SomePoint","SLOT":"out"}` → `{"facets":"..."}`.

### Fixed
- Facet spec splitting is now **`;`-first**: `range=` values may contain commas
  without being torn apart. (Previously the spec was split on `[;,]`, which broke
  multi-value enums.)
- Facets are now built as **key/value arrays** (`BFacets.make(keys, vals)`) instead of a
  flattened argument list — deterministic key/value pairing.
- Writing facets on a slot resolves the **slot's** type for coercion (instead of the
  component's), so typed slots coerce correctly.
- A bare `V="A,B,C"` with no `key=` is now treated as an enum `range`.

### Compatibility
- No operation was removed or renamed. All v2.3 operations and behaviours are intact
  (verified live: ADD / LINK / UNLINK / RENAME / CP / MOD / READ / LIST / BQL / INVOKE /
  FACET / FILE).

---

## v2.3.0 — 2026-10-15

**Authentication restored; link operations and lifecycle actions reconciled.
Baseline "secure + link" build.**

### Added
- **`OP=facet`** — read back a component's facets.
- **`OP=file`** — read text / base64 / directory listings under a configured
  `fileRoot`, with a **canonical-path containment check** (rejects `../` escapes).

### Fixed
- **`/api/config` authentication regression** — the endpoint is authenticated again.
- **`restart` / `applyConfig` actions** restored.
- **`changed()` auto-restart** behaviour restored.

### Notes
- `module.xml` `vendorVersion` moved **2.0.0 → 2.3.0**; `GET /api/status` reports
  `"version":"2.3"`; module description is `Gline REST API v2.3`.
- Reconciles the v2.2-era branch that had dropped authentication and lifecycle actions.

---

## v2.2 — 2026-10-12

**Link operations (interim branch).**

### Added
- `LINK` / `UNLINK` with improved link-target resolution (`linkTo`).

### Known issue
- This interim branch omitted the `/api/config` authentication check and the
  `restart` / `applyConfig` actions. **Superseded by v2.3**, which restores them.

---

## v2.1 — 2026-10-12

**Automatic property-value coercion for typed slots.**

### Added
- `setPropAuto()` — `MOD` accepts human-readable values for typed slots and coerces
  them on the server:
  - `baja:RelTime` — `V="60000"` (ms) → `1 minute`
  - `history:CollectionInterval` — `V="false:3600000"`
  - `history:Capacity` — `V="5000"` / `"5000 records"` / `"unlimited"`

### Notes
- `module.xml` gained a dependency on `history-rt` (Niagara 4.14).

---

## v2.0 — 2026-10-10

**First v2 release. v1 + authentication + access control + BQL + program management.**

### Added
- **Basic Auth** on every request (username/password configurable at runtime).
- **CIDR allow-list** to restrict access to trusted network segments.
- **Configuration persistence** across station restarts (no external reverse proxy).
- **BQL query → structured JSON table**
  (`{"OP":"bql","columns":[...],"rows":[...],"count":N}`).
- **Program management** — `POST /api/program/write`, `POST /api/program/addslot`,
  `GET /api/program/status`.
- All **11 batch operations** from v1 (ADD / LINK / RENAME / DUPLICATE / CP / MOD /
  UNLINK / REMOVE / READ / LIST / INVOKE), plus `BQL` and `INVOKE`.

### Security behaviour
- Missing or wrong credentials → **HTTP 401**.
- Requests from outside the allow-list → **HTTP 403**.
- `GET /api/status` is exempt from auth (for liveness probes).

### Verified
- **40 test cases passed** — 29 functional + 11 access-control. Full report:
  [`docs/glineRestApi-v2-Test-Report.md`](docs/glineRestApi-v2-Test-Report.md).

### Notes
- Runs on port **8082** (v1 runs on 8081; both can run side by side).
- Module name inside the jar: `glineRestApi` (type `glineRestApi:RestApiServiceV2`).

---

## v1 — 2026-06 (in this repository)

**`niagaraRestApi-rt.jar` — the free edition.**

- 11 batch operations via a single `POST /api/batch`.
- Port **8081**, Niagara 4.14.
- **No built-in authentication** — deploy on a trusted network segment.
- Internal version `1.0.1.4.14`.

See [ABOUT_THIS_JAR.md](ABOUT_THIS_JAR.md).
