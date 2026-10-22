# Niagara-Rest-API-service---Free 🚀

**📦 This repository ships the v1 module only — [`niagaraRestApi-rt.jar`](niagaraRestApi-rt.jar).**
**v2 (`glineRestApi`) is not distributed here — see [Getting v2](#getting-v2).**
See [ABOUT_THIS_JAR.md](ABOUT_THIS_JAR.md) if you are unsure which edition you have.

![Niagara 4.14+](https://img.shields.io/badge/Niagara-4.14%2B-blue)
[![License: Free](https://img.shields.io/badge/License-Free-brightgreen)](LICENSE)
[![Author](https://img.shields.io/badge/Author-jason912-blue)](https://github.com/jason912)
[![Contact](https://img.shields.io/badge/Contact-WhatsApp-brightgreen)](https://wa.me/8613801909968)

> **REST API for Niagara 4 — batch operations, deep copy, link-safe rename, and full component lifecycle. Built for AI automation.**
>
> **Two editions:** **v1 · niagaraRestApi** (lightweight, free) · **v2 · glineRestApi** (built-in authentication, BQL, program management, facet editing — available on request)
>
> **Latest v2: [v2.4.0](CHANGELOG.md)** · see the [CHANGELOG](CHANGELOG.md) for per-version details.

---

## Two Editions

| | **v1 · niagaraRestApi** | **v2 · glineRestApi** |
|:--|:--|:--|
| **Availability** | ✅ In this repo | 🔒 **On request** |
| **Access Control** | — | ✅ CIDR allow-list |
| **BQL Query** | — | ✅ Structured JSON tables |
| **Program Management** | — | ✅ Create / addslot / write / status |
| **Facet Editing** | — | ✅ Write facets (incl. enum ranges), read slot facets |
| **Batch Operations** | ✅ | ✅ |
| **Component Lifecycle** | ✅ | ✅ |
| **Port** | 8081 | 8082 |

Both editions are **independent modules** and can run side by side.

---

## What Is It?

A lightweight REST API module for Niagara N4 stations. **v1** exposes a JSON-over-HTTP endpoint for **11 batch operations** — create, read, update, delete, copy, rename, duplicate, link, unlink, list, and invoke — all through a single `POST /api/batch` call.

**v2** adds a mandatory authentication layer plus query and program-management capabilities, for deployments that require controlled access.

Designed for:
- **AI agents** to programmatically configure Niagara stations
- **CI/CD pipelines** for station deployment
- **Bulk point creation** during commissioning
- **Template-based station cloning**

---

## What's New in v2 (vs. v1)

v2 keeps everything that made v1 useful, and adds a complete **security and query layer**.

| Capability | v1 · niagaraRestApi | v2 · glineRestApi |
|:--|:--:|:--:|
| 11 batch operations (ADD / LINK / RENAME / DUPLICATE / CP / MOD / UNLINK / REMOVE / READ / LIST / INVOKE) | ✅ | ✅ |
| **Basic Auth on every request** | ❌ | ✅ |
| **CIDR allow-list (network segment control)** | ❌ | ✅ |
| **Config persistence across restart** | — | ✅ |
| **BQL query → structured JSON table** | ❌ | ✅ |
| **Program management (write / addslot / status)** | ❌ | ✅ |
| **Facet editing (write facets; enum ranges; read slot facets)** | ❌ | ✅ |
| **Alarm & History extension setup (attach + configure + activate)** | ❌ | ✅ |
| **Access-control hardening (401 on bad credentials)** | ❌ | ✅ |
| Port | 8081 | 8082 |

In short: **v2 = v1 + authentication + access control + BQL + program management + facet editing + alarm/history extension automation.**

**In detail — what v2 adds:**

#### 🆕 BQL Query (v2 only)

Run BQL directly over HTTP and receive **structured JSON tables** with columns, rows, and count — ready for reports, dashboards, and AI data pipelines.

```bash
curl -u "<USER>:<PASS>" -X POST http://your-station:8082/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"bql","Q":"select * from control:NumericWritable"}]'
```

```json
[{"OP":"bql","columns":["slotPath","out"],"rows":[...],"count":100,"status":"ok"}]
```

> On **v1**, the same request returns `{"OP":"bql","status":"unknown"}` — BQL is a v2 feature. Verified live on both ports.

#### 🆕 Program Management (v2 only)

Create programs, add slots, write source, and read status — all through the API. On **v1** these endpoints do not exist (HTTP `404`).

| Endpoint | Method | Purpose |
|:--|:--|:--|
| `/api/program/write` | POST | Write program source |
| `/api/program/addslot` | POST | Add a program slot |
| `/api/program/status` | GET | Read class, status, checksum, source length |

#### 🆕 Alarm & History Extensions via REST (v2) — fully automated

**You do not need Workbench to set up data capture.** Alarm and history extensions are
ordinary components, so v2 can attach, configure, and *activate* them over HTTP —
verified live on a Niagara 4.14 station.

```bash
# Attach a history extension to a point and activate it
curl -u "<USER>:<PASS>" -X POST http://your-station:8082/api/batch \
  -H "Content-Type: application/json" -d '[
{"OP":"add","PATH":"/myFolder/pt","T":"history:NumericCovHistoryExt","N":"he"},
{"OP":"mod","PATH":"/myFolder/pt/he","N":"enabled","V":true}
]'
# → enabled=true, active=true  — history collection is live

# Attach an alarm extension and configure it
curl -u "<USER>:<PASS>" -X POST http://your-station:8082/api/batch \
  -H "Content-Type: application/json" -d '[
{"OP":"add","PATH":"/myFolder/pt","T":"alarm:AlarmSourceExt","N":"ae"},
{"OP":"mod","PATH":"/myFolder/pt/ae","N":"alarmClass","V":"/AlarmClass"},
{"OP":"mod","PATH":"/myFolder/pt/ae","N":"timeDelay","V":5000}
]'
```

| Extension type | Purpose |
|:--|:--|
| `alarm:AlarmSourceExt` | Alarm source extension |
| `history:NumericCovHistoryExt` | Numeric history, change-of-value |
| `history:BooleanCovHistoryExt` | Boolean history, change-of-value |
| `history:EnumCovHistoryExt` | Enum history, change-of-value |
| `history:StringCovHistoryExt` | String history, change-of-value |
| `history:NumericIntervalHistoryExt` | Numeric history, fixed interval |

**Writing slots — what works**

| Slot | Behaviour |
|:--|:--|
| `enabled` | Boolean — writable; activates a history extension |
| `alarmClass` | String — writable |
| `timeDelay` | `RelTime` — write a **raw millisecond number** (`5000`), not `"5s"` |
| `historyName` / `toOffnormalText` | `BFormat` — **not** writable via MOD |
| `alarmEnable` | `AlarmTransitionBits` — **not** writable via MOD |

Extensions created over REST stay fully visible and editable in Workbench.

**Reading the collected data** — the REST API has no alarm/history *query* endpoint by
design; that part is read through the station's **Web Box** feature
(`/wsbox/query/data/<ord>` and friends), which is automatable too. See the
[v2 REST API Guide](docs/v2/glineRestApi-v2-guide.pdf) for the full procedure.

#### 🆕 Facet Editing (v2.4)

Write **facets** on any property or point through `MOD`, and read a specific slot's
facets back:

```bash
# Write facets on a point — numeric, units, precision
curl -u "<USER>:<PASS>" -X POST http://your-station:8082/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"mod","PATH":"/Folder/Point","N":"facets","V":"min=0;max=100;units=degC;precision=2"}]'

# Enum facets — "range=A,B,C"  or indexed "range=0:Low,1:Mid,2:High"
curl -u "<USER>:<PASS>" -X POST http://your-station:8082/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"mod","PATH":"/Folder/Point","N":"facets","V":"range=Low,Mid,High"}]'

# Read the facets of a specific slot
curl -u "<USER>:<PASS>" -X POST http://your-station:8082/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"read","PATH":"/Folder/Point","SLOT":"out"}]'
```

Supported: numeric facets (`min` / `max` / `precision` / `fieldWidth`), `units`,
`trueText` / `falseText`, and enum **`range=`** in both plain (`A,B,C`) and indexed
(`0:A,1:B`) forms.

#### 🆕 Built-in Security (v2 only)

Basic Auth (username + password, configurable at runtime) plus a CIDR allow-list to restrict access to trusted network segments. Configuration persists across restarts, so no external reverse proxy is required.

#### 🆕 Access-control hardening (v2 only)

Missing or wrong credentials are rejected with **HTTP 401**; requests from outside the allow-list are rejected with **HTTP 403**.

---

## Getting v2

**v2 is distributed on request** so we can match you with the right build and support.
**Current v2 release: [v2.4.0](CHANGELOG.md)** — see the [CHANGELOG](CHANGELOG.md)
for what each v2 version adds.

Send us:

| Info | Example |
|:--|:--|
| Niagara version | 4.14 / 4.15 |
| Intended use | AI automation / commissioning / integration |
| Organization | (optional) |

**Contact:** [WhatsApp +86 138 0199 0968](https://wa.me/8613801909968) · [jason.zhang@gline-net.com](mailto:jason.zhang@gline-net.com)

We will send the latest build (`glineRestApi-rt.jar`) with installation notes.

---

## Quick Start

### v1 · niagaraRestApi (in this repo, port 8081)

**Download:** [`niagaraRestApi-rt.jar`](niagaraRestApi-rt.jar) — this is the **v1** module.

```bash
# 1. Add niagaraRestApi-rt.jar to your modules/ directory
# 2. Restart station
# 3. The REST API is now live on port 8081 (configurable)

# Test it:
curl -X POST http://your-station:8081/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"LIST","PATH":"Drivers"}]'
```

### v2 · glineRestApi (on request, port 8082)

```bash
# Every request is authenticated:
curl -u "USER:PASS" -X POST http://your-station:8082/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"LIST","PATH":"Drivers"}]'
```

> **v2 requires authentication on every request** (Basic Auth + optional CIDR allow-list), configurable in the station.

---

## 40 Verified Test Cases

**40 / 40 passed — 100% pass rate.** Executed live against a Niagara 4.14 station with authentication enabled. Every request carries credentials (`-u "<USER>:<PASS>"`).

| Category | Cases | Passed |
|:--|:--:|:--:|
| Functional | 29 | 29 |
| Access Control | 11 | 11 |
| **Total** | **40** | **40** |

Full report: [docs/v2/glineRestApi-v2-Test-Report.md](docs/v2/glineRestApi-v2-Test-Report.md)

### Functional cases (29)

| Group | # | Cases |
|:--|:--:|:--|
| **Endpoints** | 5 | Service status · Module info · Type query · Browse empty path · Browse with content |
| **Components** | 8 | Create folder · Create numeric point · Create string point · List children · Modify property · Read property · Rename · Copy |
| **Links** | 3 | Create link · Verify value propagation · Remove link |
| **Actions & Query** | 4 | Invoke action · BQL query (live data) · BQL query (component list) · Multiple operations in one request |
| **Delete** | 1 | Delete a component |
| **Error handling** | 4 | Non-existent path · Invalid type · Unknown operation · Method not allowed |
| **Program management** | 4 | Create program · Add program slot · Write program source · Read program status |
| | **29** | |

### Access-control cases (11)

| Group | # | Cases |
|:--|:--:|:--|
| **Baseline / toggle** | 4 | No auth configured · Auth disabled → allowed · `/api/status` without credentials · `/api/status` with credentials |
| **Basic Auth** | 4 | No credentials → 401 · Wrong password → 401 · Wrong username → 401 · Correct credentials → 200 |
| **CIDR allow-list** | 2 | Source outside list → 403 · Source inside list → 200 |
| **Persistence** | 1 | Configuration retained across restart |
| | **11** | |

### Batch operations (11 OPs, all via `POST /api/batch`)

| # | OP | Name | Description |
|:--|:---|------|-------------|
| 1 | **ADD** | Create | Create any component type (Folder, Writable points, ModbusTcpDevice, proxyExt, etc.) |
| 2 | **LINK** | Connect | Create BConversionLink between slots with auto type conversion |
| 3 | **RENAME** | Rename | Rename components while preserving all handle-based link ORDs |
| 4 | **DUPLICATE** | Duplicate | Same as CP, auto-generates `{name}_copy` suffix |
| 5 | **CP** | Deep Copy | Recursive deep copy; internal links rebuilt automatically |
| 6 | **MOD** | Modify | Write string, integer, boolean, and FlexAddress property values |
| 7 | **UNLINK** | Disconnect | Remove the Link child component from target point |
| 8 | **REMOVE** | Delete | Permanently remove a component |
| 9 | **READ** | Read | Read component info or a specific property |
| 10 | **LIST** | List | List all immediate child components |
| 11 | **INVOKE** | Call Action | Invoke any Niagara action (ping, set, enable/disable) |
| 12 | **BQL** | Query *(v2)* | Run BQL, return structured table |

> `POST /api/program/compile` is not counted above: it is access-controlled like every other endpoint, and its functional use is outside this test set.

---

## Comparison (by channel)

A capability overview across the common ways to talk to a station over HTTP.

| Feature | **Gline REST API** | Built-in XML API | Third-party connector | Built-in REST |
|---------|:------------------:|:----------------:|:---------------------:|:-------------:|
| Atomic batch (11 ops, single POST) | ✅ | ❌ | ❌ | ❌ |
| Deep Copy + link rebuild | ✅ | ❌ | ❌ | ❌ |
| Rename preserves links | ✅ | ❌ | ❌ | ❌ |
| Full component lifecycle (create → modify → link → rename → copy → delete) | ✅ | ❌ | ❌ | ❌ |
| **Alarm & history extension setup** | ✅ | ❌ | ❌ | ❌ |
| Facet editing *(v2.4)* | ✅ | ❌ | ❌ | ❌ |
| BQL to JSON table *(v2)* | ✅ | ❌ | ❌ | ❌ |
| Built-in auth *(v2)* | ✅ | ✅ | ❌ | ✅ |
| Single .jar deployment | ✅ | built-in | .jar | built-in |
| License fee | none | none | per station | none |

---

## Recommended Strategy

| Use Case | Recommended channel |
|----------|---------------------|
| Batch point creation / template deployment | **Gline REST API** (`POST /api/batch`) |
| Alarm & history extension setup (attach + activate) | **Gline REST API** (`POST /api/batch`) |
| Facet editing (units, ranges, precision) | **Gline REST API** (v2.4) |
| Component lifecycle automation | **Gline REST API** |
| Reading trend / alarm *data* | Built-in XML API, or Web Box (`/wsbox/query/data/`) |
| External API data ingestion | Third-party connector |
| Production security | **Gline REST API v2** (built-in auth + CIDR allow-list) — no reverse proxy needed |

**Bottom line:** Gline REST API covers the component lifecycle, queries, and facets over
HTTP with no license fee — and pairs with the built-in XML API for alarms and history.

---

## Requirements

| Component | Requirement |
|-----------|-------------|
| **Niagara** | 4.14 or later |
| **License** | None required |
| **Auth** | **v2:** built-in Basic Auth + CIDR allow-list |
| **Port** | 8081 (v1) · 8082 (v2) |

---

## Documentation

| Manual | Description |
|--------|-------------|
| [docs/](docs/README.md) | **Documentation index — split by edition** |
| [v1 Guide](docs/v1/niagaraRestApi-v1-guide.pdf) | niagaraRestApi v1 — complete reference |
| [v1 Comparison](docs/v1/niagaraRestApi-v1-comparison.pdf) | v1 vs the other channels |
| [v2 Guide](docs/v2/glineRestApi-v2-guide.pdf) | glineRestApi v2 — complete reference |
| [v2 Comparison](docs/v2/glineRestApi-v2-comparison.pdf) | v2 vs the other channels |
| [v2 What's New](docs/v2/glineRestApi-v2-whatsnew.pdf) | What v2 adds over v1 |
| [v2 Test Report](docs/v2/glineRestApi-v2-Test-Report.md) | v2 — 40/40 use cases passed |
| [AI automation lab](niagara-ai-lab/README.md) | Driving a station through the API only — capability deck, BACnet / Modbus / XML-API point publishing, and how collection is proven |
| [CHANGELOG](CHANGELOG.md) | What each v2 version adds (v2.0 → v2.4.0) |

---

## Support & Contact

- **Author**: [@jason912](https://github.com/jason912)
- **Email**: [jason.zhang@gline-net.com](mailto:jason.zhang@gline-net.com)
- **WhatsApp**: [+86 138 0199 0968](https://wa.me/8613801909968)

**Shanghai Gline Net Co., Ltd.** — Your Partner in Smarter Automation

---

> **Disclaimer:** Features verified on Niagara N4.14. Capabilities may vary by station version and configuration.

© 2026 Shanghai Gline Net Co., Ltd. All rights reserved.

---

## Commercial Support

This module is free of charge under the MIT License (see [LICENSE](LICENSE)).

For production deployments requiring warranty, priority support, or custom
development, commercial support is available.

- Email: jason.zhang@gline-net.com
- WhatsApp: +86 138 0199 0968
- Web: [www.glineweb.com](https://www.glineweb.com)

Shanghai Gline Net Co., Ltd.
