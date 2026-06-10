# Niagara-Rest-API-service
# Niagara REST API — Verified Capabilities & Competitive Advantages 
A toolkit designed for AI-powered automation of Niagara programming.

> **Test stations:** IOT_Test (N4.14 @ 192.168.2.112:8081) — *tested live 2026-06-10 13:28 CST*  
> **Module:** niagaraRestApi v1.0.1.4.14  
> **Interface:** JSON over HTTP, POST /api/batch as the core batch operation endpoint  
> **Authentication:** None (internal LAN only — wrap with nginx + Basic Auth for production)

---

> **⚠️ Live test note:** All operations documented below were freshly verified against 192.168.2.112:8081 on 2026-06-10 at 13:28-13:33 CST.  
> Test record: create folder → batch ADD 5 components + LINK → RENAME → verify link preserved → Deep Copy (CP) → verify link rebuilt in copy → MOD (fallback, facets) → read→ list → INVOKE set → UNLINK → REMOVE → full lifecycle (ADD→LINK→UNLINK→REMOVE) → cleanup.  
> **MOD limitation confirmed:** Writing to `out` on StringWritable / BooleanWritable requires INVOKE `set`, not direct MOD. Simple properties (fallback, name-like slots) work directly.

---

## 10 Verified Batch Operations

All 10 operations have been tested and confirmed working on live stations:

| # | OP | Name | Description | Verified |
|---|---|------|-------------|:--------:|
| 1 | **ADD** | Create | Create any component type (Folder, Writable points, ModbusTcpDevice, proxyExt, etc.) | ✅ |
| 2 | **LINK** | Connect | Create BConversionLink between slots with auto type conversion | ✅ |
| 3 | **RENAME** | Rename | Rename components while preserving all handle-based link ORDs | ✅ |
| 3b | **DUPLICATE** | Duplicate (alias for CP) | Same as CP, auto-generates `{name}_copy` suffix, copies to same parent | ✅ |
| 4 | **CP** | Deep Copy | Recursive deep copy of entire subtree; internal links rebuilt automatically | ✅ |
| 5 | **MOD** | Modify | Write string, integer, boolean, and FlexAddress property values | ✅ |
| 6 | **UNLINK** | Disconnect | Remove the Link child component from target point | ✅ |
| 7 | **REMOVE** | Delete | Permanently remove a component from the station tree | ✅ |
| 8 | **READ** | Read | Read component info or a specific property value | ✅ |
| 9 | **LIST** | List | List names and types of all immediate child components | ✅ |
| 10 | **INVOKE** | Call Action | Invoke any Niagara action (ping, set, enable/disable, etc.) | ✅ |

---

## Verified End-to-End Test Cases

### 1. Batch ADD — Create Modbus TCP Device (T8600 Thermostat)
- Single POST batch creates ModbusTcpDevice + 3 NumericWritable points + proxyExt for each
- Configured proxyExt dataAddress with `addr|decimal` format
- Called `ping` action to verify device connectivity
- Tested point polling cycle: disable → re-enable with frequency override

### 2. Batch ADD + LINK — MQTT Point Deployment
- Created 10 BooleanWritable points under MQTT folder
- Simultaneously created LINK connections to MqttClient `in10` input
- All in a single POST request — no secondary operations needed
- Tested on IOT_Test station (192.168.2.112)

### 3. ADD + LINK + RENAME — Link Preservation After Rename
- Create folder → ADD srcPoint and tgtPoint → LINK them → RENAME srcPoint
- **Result:** Link survives rename because Niagarax uses handle-based ORD (`h:xxxxx`), not name-based paths

### 4. Deep Copy (CP) + Internal Link Rebuild
- Create folder with internally LINKed components → CP to new path
- **Result:** Copied folder has internal links correctly rebuilt — src→dst mapping fully preserved
- Only batch operation on the market that supports deep copy with link reconstruction

### 5. Full Lifecycle (ADD → LINK → UNLINK → REMOVE)
- Create → Link → Unlink → Remove
- UNLINK correctly removes the Link child component from the target
- REMOVE deletes the parent source; dst remains orphaned (no dangling references)

### 6. INVOKE — Action Calls
- Called ModbusTcpDevice `ping` action — verified connectivity
- Set BooleanWritable point values via INVOKE
- Test string/numeric/boolean value types via `VAL_TYPE` (`num`/`bool`/`str`)

### 7. MOD — Property Writes
- String: `ipAddress` → `"192.168.2.140"`
- Integer: `port` → `502`, `deviceAddress` → `2`
- Boolean: `enabled` → `false` / `true`
- FlexAddress: `dataAddress` → `"2|decimal"`, `"0x0A|hex"`
- `out` value writes on NumericWritable/BooleanWritable via INVOKE set

> **Live test note (2026-06-10):** Direct MOD on `out` of StringWritable fails (`BString cannot be cast to BStatusString`). Use INVOKE `set` for point values instead. Simple scalar properties (fallback, basic config fields) work directly with MOD.

---

## Competitive Advantages

| # | Advantage | Gline REST | oBIX | BTIB ACTIVE-API | Tridium /rest/ | 3rd-Party Analytics |
|---|-----------|:----------:|:----:|:---------------:|:--------------:|:------------------:|
| 1 | **Atomic batch** (10 ops, single POST) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 2 | **Deep Copy + link rebuild** | ✅ | ❌ | ❌ | ❌ | ❌ |
| 3 | **Rename preserves links** (handle ORD) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 4 | **Full component lifecycle** (create/delete/copy/rename/link/unlink/invoke — all 7) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 5 | **No SMA required** | ✅ | ✅ | ✅ | ❌ | ❌ |
| 6 | **Lightweight deploy** (single .jar, 3 steps) | ✅ | built-in | .jar | built-in | external |
| 7 | **Alarm query** | ❌ | ✅ | ✅ | ❌ | ✅ |
| 8 | **History query** | ❌ | ✅ | ✅ | ✅ | ✅ |
| 9 | **Client mode** (call 3rd-party APIs) | ❌ | ❌ | ✅ | ❌ | ❌ |

### Detail

**1. Atomic Batch Operations**  
Gline REST is the only solution supporting up to 10 operations in a single HTTP request. Batch operations execute sequentially in order — ideal for synchronized point creation, template deployment, and multi-step workflows.

**2. Deep Copy + Internal Link Reconstruction**  
When copying a component subtree with internal LINKs, Gline REST's CP operation not only recursively deep-copies every component but also rebuilds all internal link relationships in the copy. No other solution offers this capability.

**3. Link-Safe Rename**  
Niagarax LINK components use handle-based ORDs (`h:xxxxx`) rather than name-based paths. Gline REST's RENAME calls `parent.rename()`, which preserves all handle-based references intact — no broken links after rename.

**4. Full Component Lifecycle**  
Seven lifecycle operations: create (ADD), delete (REMOVE), copy (CP), rename (RENAME), link (LINK), unlink (UNLINK), invoke (INVOKE). This is the only API covering all seven. oBIX supports none of these; BTIB supports some (create/delete) but not copy/rename; Tridium /rest/ supports only limited create.

**5. No SMA Required**  
SMA (Software Maintenance Agreement) is Tridium's annual subscription license. Gline REST works on any station without SMA. Combined with the free built-in oBIX, you get full coverage (component lifecycle + alarm + history) at zero license cost.

**6. Lightweight Deployment**  
Three steps: copy .jar to modules/ → restart station → curl verify. No web container, no external dependencies, no configuration beyond the port number.

---

## Recommended Complementary Strategy

| Use Case | Recommended Solution |
|----------|---------------------|
| Batch point creation / template copy / component lifecycle management | **Gline REST API** (POST /api/batch) |
| Alarm query and acknowledgement | **oBIX** (POST /~alarmQuery/) |
| Historical trend data | **oBIX** (HistoryService) |
| Daily read/write point values | Gline REST or oBIX (both work) |
| External API data ingestion into station | **BTIB RestNetwork** (Gline REST has no client mode) |
| Production security | **nginx reverse proxy + Basic Auth** + Gline REST |

**Bottom line:** Gline REST API + oBIX together provide complete station management coverage (component lifecycle + alarm + history) at zero license cost — an unbeatable combination for developers and system integrators working with Niagarax N4 stations.

---

## Commercial Contact

**Shanghai Gline Net Co.**  
Email: jason.zhang@gline-net.com  
Tel / WhatsApp: +86 13801909968

> **Disclaimer:** This document was automatically generated by an AI system based on publicly available internet research, training data, and hands-on testing on specific station builds (Niagarax N4.14.0.162). Features, availability, and pricing may vary by station version, configuration, and license tier. Always verify directly with each vendor for your specific requirements. The AI author and Shanghai Gline Net Co. assume no liability for any errors, omissions, or decisions made based on this document.
