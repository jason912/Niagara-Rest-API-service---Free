# Niagara-Rest-API-service---Free 🚀

[![Niagara 4.14+](https://img.shields.io/badge/Niagara-4.14%2B-blue)](https://www.tridium.com)
[![License: Free](https://img.shields.io/badge/License-Free-brightgreen)](LICENSE)
[![Author](https://img.shields.io/badge/Author-jason912-blue)](https://github.com/jason912)
[![Contact](https://img.shields.io/badge/Contact-WhatsApp-brightgreen)](https://wa.me/8613801909968)

> **REST API for Niagara 4 — batch operations, deep copy, link-safe rename, and full component lifecycle. Built for AI automation.**
>
> **Two editions:** **v1 · niagaraRestApi** (lightweight, no auth, free) · **v2 · glineRestApi** (built-in authentication, BQL, program management — available on request)

---

## Two Editions

| | **v1 · niagaraRestApi** | **v2 · glineRestApi** |
|:--|:--|:--|
| **Availability** | ✅ In this repo | 🔒 **On request** |
| **Authentication** | None | ✅ Basic Auth (required) |
| **Access Control** | — | ✅ CIDR allow-list |
| **BQL Query** | — | ✅ Structured JSON tables |
| **Program Management** | — | ✅ Create / addslot / write / status |
| **Batch Operations** | ✅ | ✅ |
| **Component Lifecycle** | ✅ | ✅ |
| **Port** | 8081 | 8082 |

Both editions are **independent modules** and can run side by side.

---

## What Is It?

A lightweight REST API module for Niagara N4 stations. **v1** exposes a JSON-over-HTTP endpoint for **11 batch operations** — create, read, update, delete, copy, rename, duplicate, link, unlink, list, and invoke — all through a single `POST /api/batch` call, with no authentication layer for fast internal use.

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

**In detail:**

- **Security** — Basic Auth (username + password, configurable at runtime) plus a CIDR allow-list to restrict access to trusted network segments. Configuration persists across restarts, so no external reverse proxy is required.
- **BQL Query** — run BQL directly over HTTP and receive **structured JSON tables** with columns, rows, and count — ready for reports, dashboards, and AI data pipelines.
- **Program Management** — create programs, add slots, write source, and read status, all through the API.

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

```bash
# 1. Add niagaraRestApi-rt.jar to your modules/ directory
# 2. Restart station
# 3. The REST API is now live on port 8081 (configurable)

# Test it:
curl -X POST http://your-station:8081/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"LIST","PATH":"Drivers"}]'
```

> **⚠️ v1 carries no authentication.** It is intended for trusted internal networks. For production exposure, wrap it with a reverse proxy, or use **v2**, which enforces authentication in the module itself.

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

**40 / 40 passed** — 29 functional + 11 access-control cases, executed live with credentials.
The table below lists the **batch operations** exercised (11 OPs), all reachable through a single `POST /api/batch`.
The remaining cases cover endpoints, error handling, program management, and access control — see [Test Results](#v2-test-results).

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

---

## Competitive Advantages

| Feature | Gline REST | oBIX | BTIB ACTIVE-API | Tridium /rest/ |
|---------|:----------:|:----:|:---------------:|:--------------:|
| Atomic batch (11 ops, single POST) | ✅ | ❌ | ❌ | ❌ |
| Deep Copy + link rebuild | ✅ | ❌ | ❌ | ❌ |
| Rename preserves links | ✅ | ❌ | ❌ | ❌ |
| Full lifecycle (7 operations) | ✅ | ❌ | ❌ | ❌ |
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

## v2 Test Results

**40 / 40 use cases passed — 100% pass rate**, executed against a live station with authentication enabled.

| Category | Cases | Passed |
|:--|:--:|:--:|
| Functional | 29 | 29 |
| Access Control | 11 | 11 |
| **Total** | **40** | **40** |

> Every request in the report carries credentials (`-u "<USER>:<PASS>"`).
> Full report: [docs/glineRestApi-v2-Test-Report.md](docs/glineRestApi-v2-Test-Report.md)

### Functional coverage (29)

| Group | Cases | What was verified |
|:--|:--|:--|
| **Components** | 8 | Create Folder / Numeric point / String point · List children · Read & write properties · Rename · Copy |
| **Links** | 3 | Create link · Verify value propagation through the link · Unlink |
| **Actions & Query** | 3 | Invoke action (`ping` / `set`) · **BQL query → JSON table** · Multi-operation single request |
| **Delete & Browse** | 4 | Delete component · Service status · Module info · Type query · Browse station tree |
| **Error handling** | 4 | Non-existent path · Invalid type · Unknown operation · Method not allowed |
| **Program management** | 3 | Write program source · Add program slot · Read program status |
| **Batch** | — | Multi-op ordering within one `POST /api/batch` |

### Access-control coverage (11)

| Case | Expected | Result |
|:--|:--|:--|
| No credentials | Rejected (401) | ✅ |
| Wrong password | Rejected (401) | ✅ |
| Wrong username | Rejected (401) | ✅ |
| Correct credentials | Accepted (200) | ✅ |
| CIDR allow-list enforcement | Blocked / allowed per segment | ✅ |
| Config persistence across restart | Retained | ✅ |

---

## Requirements

| Component | Requirement |
|-----------|-------------|
| **Niagara** | 4.14 or later |
| **License** | None required |
| **Auth** | v1: none (internal LAN) · **v2: built-in Basic Auth** |
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
