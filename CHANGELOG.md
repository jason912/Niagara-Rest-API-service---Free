# Changelog

All notable changes to **glineRestApi (v2)** are documented here.

> **Note on editions.** This repository ships **v1 (`niagaraRestApi`)** only.
> The **v2 (`glineRestApi`)** module is a separate module distributed on request —
> see [Getting v2](README.md#getting-v2). This changelog is published so customers
> can see what each v2 release adds before requesting a build.

Versions correspond to `META-INF/module.xml` `vendorVersion` and to the `version`
field returned by `GET /api/status`.

---

## v2.41.3 — 2026-10-16

**Facet `units` are written as real units, not text.**

### Fixed
- `mod` on `facets` now stores the `units` facet as a `javax.baja.units.BUnit` object
  instead of a string. Storing it as text left a value that crashed Workbench when it
  rendered the point:
  ```
  java.lang.ClassCastException: javax.baja.sys.BString cannot be cast to javax.baja.units.BUnit
      at javax.baja.sys.BDouble.toString(BDouble.java:393)
      at com.tridium.wiresheet.PropertyBarGlyph.updateValueString(PropertyBarGlyph.java:60)
  ```
  `units` is now resolved from the station's unit database by name (`volt`, `ampere`,
  `watt`, `volt ampere`, `kilowatt hour`, …). A name that does not resolve is rejected
  with a clear error rather than stored. `units=null` (or omitting `units`) clears the
  unit.

### Notes
- Fields in the facet string are separated by **`;`**; a comma is not a separator.
- A correctly stored unit reads back as its **symbol** (`units=V`), not the name written
  (`volt`).

See [`docs/v2/glineRestApi-v2-facets.md`](docs/v2/glineRestApi-v2-facets.md) for the
facet string reference, the unit names that resolve, and how to verify a write.

---

## v2.41.1 — 2026-10-15

**Re-release of v2.41.0 with a signed timestamp. Use this instead of v2.41.0.**

### Fixed
- The jar's signature now carries an RFC 3161 timestamp
  (`-tsa http://timestamp.digicert.com`). v2.41.0 was signed without one, so
  Workbench reported it as **"not timestamped"** and its signature would have
  stopped validating when the signing certificate expires.

### Notes
- Functionally identical to v2.41.0. The timestamp is the only change — and it
  is why the hashes differ from v2.41.0.
- Timestamping rewrites `META-INF/` inside the jar, so the MD5/SHA-256 change.
  Timestamping is the last step before release.

See [`docs/v2/glineRestApi-v2-signature-timestamp.md`](docs/v2/glineRestApi-v2-signature-timestamp.md)
for what "not timestamped" means and how to check any deployed jar.

---

## v2.41.0 — 2026-10-15

**Proxy extensions can be assembled at point creation.**

### Added
- **`PROXY` on `add`** — attach a driver proxy extension to the point's protected
  `proxyExt` slot in the same operation that creates the point. Optional
  `PROXY_SLOT` names a different slot (default `proxyExt`).
  ```json
  {"OP":"add","PATH":"/Drivers/SnmpNetwork1/PDU_AP8858_180/points",
   "T":"control:NumericWritable","N":"Phase1_Voltage",
   "PROXY":"nSnmp:SnmpNumericProxyExt"}
  ```
  Previously the proxy slot could not be filled at all: `remove` was rejected as
  protected and `add` was rejected because the slot already existed. The resulting
  point read `0.00 {fault,stale}` permanently.

### Fixed
- `/api/status` reports the version read from the module's own
  `META-INF/module.xml`. It was a hardcoded literal that had drifted to `2.4`.

### Notes
- **Restart the station after creating the point.** The proxy does not poll until
  then; before the restart the point reports
  `faultCause = "Read fault: Illegal Object Identifier"`. Re-setting the OID does
  not substitute for the restart.
- For SNMP, build the network as `T="nSnmp:SnmpNetwork"` (the nDriver type). The
  legacy `snmp:SnmpNetwork` type has no `sendConfig`/`receiveConfig`/`trapConfig`
  slots and its devices fault regardless of the point configuration.

See [`docs/v2/glineRestApi-v2.41-proxy-extensions.md`](docs/v2/glineRestApi-v2.41-proxy-extensions.md)
for the full write-up and the
verified reference run.

### Compatibility
- No operation was removed or renamed. All v2.4 operations and behaviours are
  intact. Omitting `PROXY` preserves the previous `add` behaviour exactly.

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

### Usage notes — alarm & history extensions

No new operation was needed for this; it uses the `ADD` / `MOD` that v2 has always had.
Recorded here because it is the documented way to drive capture setup over HTTP —
**no Workbench required**:

```json
{"OP":"add","PATH":"/pt","T":"history:NumericCovHistoryExt","N":"he"}
{"OP":"mod","PATH":"/pt/he","N":"enabled","V":true}
{"OP":"add","PATH":"/pt","T":"alarm:AlarmSourceExt","N":"ae"}
{"OP":"mod","PATH":"/pt/ae","N":"alarmClass","V":"/AlarmClass"}
```

- Extension types: `alarm:AlarmSourceExt`; `history:Numeric|Boolean|Enum|StringCovHistoryExt`;
  `history:NumericIntervalHistoryExt`.
- `timeDelay` (`RelTime`) is written as a **raw millisecond number** (`5000`), not `"5s"`.
- `historyName` / `toOffnormalText` (`BFormat`) and `alarmEnable` (`AlarmTransitionBits`)
  are **not** writable via `MOD` — a property-type limit, not an API limit.
- Reading the collected *data* back is a separate topic: it is queried over **oBIX**
  (`/obix/config/...`) — see the guide.

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
