# Niagara-Rest-API-service---Free 🚀

**📦 This repository ships the v1 module only — [`niagaraRestApi-rt.jar`](niagaraRestApi-rt.jar).**
**v2 (`glineRestApi`) is not distributed here — see [Getting v2](#getting-v2).**
See [ABOUT_THIS_JAR.md](ABOUT_THIS_JAR.md) if you are unsure which edition you have.

[![Niagara 4.14+](https://img.shields.io/badge/Niagara-4.14%2B-blue)](https://www.tridium.com)
[![License: Free](https://img.shields.io/badge/License-Free-brightgreen)](LICENSE)
[![Author](https://img.shields.io/badge/Author-jason912-blue)](https://github.com/jason912)
[![Contact](https://img.shields.io/badge/Contact-WhatsApp-brightgreen)](https://wa.me/8613801909968)

> **REST API for Niagara 4 — batch operations, deep copy, link-safe rename, and full component lifecycle. Built for AI automation.**
>
> **Two editions:** **v1 · niagaraRestApi** (lightweight, free) · **v2 · glineRestApi** (built-in authentication, BQL, program management — available on request)

---

## Two Editions

| | **v1 · niagaraRestApi** | **v2 · glineRestApi** |
|:--|:--|:--|
| **Availability** | ✅ In this repo | 🔒 **On request** |
| **Access Control** | — | ✅ CIDR allow-list |
| **BQL Query** | — | ✅ Structured JSON tables |
| **Program Management** | — | ✅ Create / addslot / write / status |
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
| **Access-control hardening (401 on bad credentials)** | ❌ | ✅ |
| Port | 8081 | 8082 |

In short: **v2 = v1 + authentication + access control + BQL + program management.**

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

#### 🆕 Built-in Security (v2 only)

Basic Auth (username + password, configurable at runtime) plus a CIDR allow-list to restrict access to trusted network segments. Configuration persists across restarts, so no external reverse proxy is required.

#### 🆕 Access-control hardening (v2 only)

Missing or wrong credentials are rejected with **HTTP 401**; requests from outside the allow-list are rejected with **HTTP 403**.

---

## Getting v2

**v2 is distributed on request** so we can match you with the right build and support.

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

Full report: [docs/glineRestApi-v2-Test-Report.md](docs/glineRestApi-v2-Test-Report.md)

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

## Competitive Advantages

| Feature | Gline REST | oBIX | BTIB ACTIVE-API | Tridium /rest/ |
|---------|:----------:|:----:|:---------------:|:--------------:|
| Atomic batch (11 ops, single POST) | ✅ | ❌ | ❌ | ❌ |
| Deep Copy + link rebuild | ✅ | ❌ | ❌ | ❌ |
| Rename preserves links | ✅ | ❌ | ❌ | ❌ |
| Full component lifecycle (create → modify → link → rename → copy → delete) | ✅ | ❌ | ❌ | ❌ |
| No SMA required | ✅ | ✅ | ✅ | ❌ |
| Single .jar deployment | ✅ | built-in | .jar | built-in |
| Built-in auth *(v2)* | ✅ | ✅ | ❌ | ✅ |
| BQL to JSON table *(v2)* | ✅ | ❌ | ❌ | ❌ |

---

## Recommended Strategy

| Use Case | Recommended |
|----------|-------------|
| Batch point creation / template deployment | **Gline REST API** (`POST /api/batch`) |
| Alarm query and acknowledgement | **oBIX** (built-in) |
| Historical trend data | **oBIX** (HistoryService) |
| External API data ingestion | **BTIB RestNetwork** |
| Production security | **v2** (built-in Basic Auth + CIDR allow-list) — no reverse proxy needed |

**Bottom line:** Gline REST API + oBIX = full station management (component lifecycle + alarm + history) at zero license cost.

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
| [REST API Guide](docs/Niagara_REST_API_Guide.pdf) | Complete API reference |
| [API Comparison](docs/Niagara_API_Comparison_English.pdf) | Gline REST vs oBIX vs BTIB vs Tridium |
| [v2 Test Report](docs/glineRestApi-v2-Test-Report.md) | v2 — 40/40 use cases passed |

---

## Support & Contact

- **Author**: [@jason912](https://github.com/jason912)
- **Email**: [jason.zhang@gline-net.com](mailto:jason.zhang@gline-net.com)
- **WhatsApp**: [+86 138 0199 0968](https://wa.me/8613801909968)

**Shanghai Gline Net Co., Ltd.** — Your Partner in Smarter Automation

---

> **Disclaimer:** Features verified on Niagara N4.14. Capabilities may vary by station version and configuration.

© 2026 Shanghai Gline Net Co., Ltd. All rights reserved.
