# Niagara-Rest-API-service---Free 🚀

[![Niagara 4.14+](https://img.shields.io/badge/Niagara-4.14%2B-blue)](https://www.tridium.com)
[![License: Free](https://img.shields.io/badge/License-Free-brightgreen)](LICENSE)
[![Contact](https://img.shields.io/badge/Contact-WhatsApp-brightgreen)](https://wa.me/8613801909968)

> **Passwordless REST API for Niagara 4 — batch operations, deep copy, link-safe rename, and full component lifecycle. Built for AI automation.**

---

## What Is It?

A lightweight, no-auth REST API module for Niagarax N4 stations. Expose a JSON-over-HTTP endpoint for **10 batch operations** — create, read, update, delete, copy, rename, link, unlink, list, and invoke — all through a single `POST /api/batch` call.

Designed for:
- **AI agents** to programmatically configure Niagara stations
- **CI/CD pipelines** for station deployment
- **Bulk point creation** during commissioning
- **Template-based station cloning**

---

## Quick Start

```bash
# 1. Add niagaraRestApi-rt.jar to your modules/ directory
# 2. Restart station
# 3. The REST API is now live on port 8081 (configurable)

# Test it:
curl -X POST http://your-station:8081/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"LIST","PATH":"Drivers"}]'
```

> **⚠️ No authentication by default.** For production, wrap with nginx reverse proxy + Basic Auth.

---

## 10 Verified Batch Operations

| # | OP | Name | Description |
|:--|:---|------|-------------|
| 1 | **ADD** | Create | Create any component type (Folder, Writable points, ModbusTcpDevice, proxyExt, etc.) |
| 2 | **LINK** | Connect | Create BConversionLink between slots with auto type conversion |
| 3 | **RENAME** | Rename | Rename components while preserving all handle-based link ORDs |
| 3b | **DUPLICATE** | Duplicate | Same as CP, auto-generates `{name}_copy` suffix |
| 4 | **CP** | Deep Copy | Recursive deep copy; internal links rebuilt automatically |
| 5 | **MOD** | Modify | Write string, integer, boolean, and FlexAddress property values |
| 6 | **UNLINK** | Disconnect | Remove the Link child component from target point |
| 7 | **REMOVE** | Delete | Permanently remove a component |
| 8 | **READ** | Read | Read component info or a specific property |
| 9 | **LIST** | List | List all immediate child components |
| 10 | **INVOKE** | Call Action | Invoke any Niagara action (ping, set, enable/disable) |

---

## Competitive Advantages

| Feature | Gline REST | oBIX | BTIB ACTIVE-API | Tridium /rest/ |
|---------|:----------:|:----:|:---------------:|:--------------:|
| Atomic batch (10 ops, single POST) | ✅ | ❌ | ❌ | ❌ |
| Deep Copy + link rebuild | ✅ | ❌ | ❌ | ❌ |
| Rename preserves links | ✅ | ❌ | ❌ | ❌ |
| Full lifecycle (7 operations) | ✅ | ❌ | ❌ | ❌ |
| No SMA required | ✅ | ✅ | ✅ | ❌ |
| Single .jar deployment | ✅ | built-in | .jar | built-in |

---

## Recommended Strategy

| Use Case | Recommended |
|----------|-------------|
| Batch point creation / template deployment | **Gline REST API** (`POST /api/batch`) |
| Alarm query and acknowledgement | **oBIX** (built-in) |
| Historical trend data | **oBIX** (HistoryService) |
| External API data ingestion | **BTIB RestNetwork** |
| Production security | **nginx + Basic Auth** + Gline REST |

**Bottom line:** Gline REST API + oBIX = full station management (component lifecycle + alarm + history) at zero license cost.

---

## Verified Test Cases

### Test 1: Batch ADD — Modbus TCP Device (T8600 Thermostat)

Single POST batch creates a ModbusTcpDevice + 3 NumericWritable points + proxyExt for each, configures dataAddress with `addr|decimal` format, and calls `ping` to verify connectivity.

### Test 2: Batch ADD + LINK — MQTT Point Deployment

Creates 10 BooleanWritable points under an MQTT folder with LINK connections to MqttClient `in10` input — all in a single POST request.

### Test 3: ADD + LINK + RENAME — Link Preservation

Link survives rename because Niagarax uses handle-based ORD (`h:xxxxx`), not name-based paths.

### Test 4: Deep Copy (CP) + Internal Link Rebuild

Copied folder has internal links correctly rebuilt — src→dst mapping fully preserved.

### Test 5: Full Lifecycle (ADD → LINK → UNLINK → REMOVE)

Complete lifecycle verified end-to-end. UNLINK correctly removes the Link child; REMOVE deletes the source without dangling references.

### Test 6: INVOKE — Action Calls

- `ping` on ModbusTcpDevice — connectivity verified
- `set` on BooleanWritable — value updated correctly
- Supports `VAL_TYPE`: `num` / `bool` / `str`

### Test 7: MOD — Property Writes

| Property | Type | Value |
|----------|------|-------|
| `ipAddress` | String | `"192.168.2.140"` |
| `port` | Integer | `502` |
| `enabled` | Boolean | `false` / `true` |
| `dataAddress` | FlexAddress | `"2|decimal"`, `"0x0A|hex"` |

> ⚠️ Direct MOD on `out` of StringWritable fails (`BString cannot be cast to BStatusString`). Use **INVOKE `set`** for point values.

---

## Requirements

| Component | Requirement |
|-----------|-------------|
| **Niagara** | 4.14 or later |
| **License** | None required |
| **Auth** | None (internal LAN) — wrap with nginx for production |
| **Port** | 8081 (configurable) |

---

## Documentation

| Manual | Description |
|--------|-------------|
| [REST API Guide](docs/Niagara_REST_API_Guide.pdf) | Complete API reference |
| [API Comparison](docs/Niagara_API_Comparison_English.pdf) | Gline REST vs oBIX vs BTIB vs Tridium |

---

## Support & Contact

- **Email**: [jason.zhang@gline-net.com](mailto:jason.zhang@gline-net.com)
- **WhatsApp**: [+86 138 0199 0968](https://wa.me/8613801909968)

**Shanghai Gline Net Co., Ltd.** — Your Partner in Smarter Automation

---

> **Disclaimer:** Features verified on Niagarax N4.14.0.162 (192.168.2.112). Capabilities may vary by station version and configuration.

© 2026 Shanghai Gline Net Co., Ltd. All rights reserved.
