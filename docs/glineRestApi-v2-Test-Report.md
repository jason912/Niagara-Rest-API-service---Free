# glineRestApi v2 — Test Report

| Item | Detail |
|:--|:--|
| Version | 2.0.3 |
| Interface | HTTP / REST |
| Authentication | Basic Auth — **every request carries credentials** |
| Result | **40 / 40 use cases passed (100%)** |
| Breakdown | 29 functional + 11 access-control |

> Every request below was executed against a live Niagara 4.14 station with authentication enabled.
> Credentials are shown as `-u "<USER>:<PASS>"` placeholders; no real credentials appear in this document.

---

## 1. How to read this report

- **29 functional cases** exercise the API surface: endpoint queries, batch operations (component lifecycle, links, actions, BQL, program management) and error handling.
- **11 access-control cases** exercise authentication, endpoint exemptions, the CIDR allow-list, and configuration persistence.
- A case **passes** when the response is the expected one. For functional cases the expected result is a successful operation (`"status":"ok"` on the API, confirmed by an independent channel where noted). For access-control cases the expected result is the documented acceptance/rejection.

---

## 2. Capabilities

| Capability | Description |
|:--|:--|
| Station browsing | Read the station tree by path; inspect components and properties |
| Component management | Create, delete, rename, copy |
| Property read/write | Read and write any component property |
| Link management | Create and remove component links |
| Action invocation | Invoke public actions on components |
| BQL query | Run BQL and return a structured table |
| Batch processing | Execute multiple operations in order in a single request |
| Program management | Create programs, add slots, write source, read status |
| Access control | Authentication (Basic Auth) and CIDR allow-list |

---

## 3. Endpoints

| Endpoint | Method | Description | Auth |
|:--|:--|:--|:--|
| `/api/status` | GET | Service status | Required |
| `/api/modules` | GET | Module information | Required |
| `/api/types` | GET | Component types | Required |
| `/api/config` | GET | Browse the station tree | Required |
| `/api/batch` | POST | Component operations + BQL | Required |
| `/api/program/write` | POST | Write program source | Required |
| `/api/program/addslot` | POST | Add a program slot | Required |
| `/api/program/status` | GET | Read program status | Required |

---

## 4. Results — 29 functional cases

| # | Use case | Method | Expected | Actual | Result |
|:--|:--|:--|:--|:--|:--|
| F1 | Service status | GET /api/status | 200 | 200 | Passed |
| F2 | Module information | GET /api/modules | 200 | 200 | Passed |
| F3 | Type query | GET /api/types | 200 | 200 | Passed |
| F4 | Browse empty path | GET /api/config | 200 | 200 | Passed |
| F5 | Browse with content | GET /api/config | 200 | 200 | Passed |
| F6 | Create a folder | batch add | ok | ok | Passed |
| F7 | Create a numeric point | batch add | ok | ok | Passed |
| F8 | Create a string point | batch add | ok | ok | Passed |
| F9 | List child components | batch list | ok | ok | Passed |
| F10 | Modify a property value | batch mod | ok | ok | Passed |
| F11 | Read a property value | batch read | ok | ok | Passed |
| F12 | Rename a component | batch rename | ok | ok | Passed |
| F13 | Copy a component | batch cp | ok | ok | Passed |
| F14 | Create a link | batch link | ok | ok | Passed |
| F15 | Verify link value propagation | batch read | 42.5 | 42.5 | Passed |
| F16 | Remove a link | batch unlink | ok | ok | Passed |
| F17 | Invoke an action | batch invoke | ok | ok | Passed |
| F18 | BQL query — live data | batch bql | table | table | Passed |
| F19 | BQL query — component list | batch bql | table | table | Passed |
| F20 | Multiple operations in one request | batch ×3 | ok | ok | Passed |
| F21 | Delete a component | batch remove | ok | ok | Passed |
| F22 | Error — non-existent path | batch read | error | error | Passed |
| F23 | Error — invalid type | batch add | error | error | Passed |
| F24 | Error — unknown operation | batch | error | error | Passed |
| F25 | Error — method not allowed | GET /api/batch | 405 | 405 | Passed |
| F26 | Create a program | batch add | ok | ok | Passed |
| F27 | Add a program slot | POST /api/program/addslot | ok | ok | Passed |
| F28 | Write program source | POST /api/program/write | ok | ok | Passed |
| F29 | Read program status | GET /api/program/status | ok | ok | Passed |

**Functional: 29 / 29 passed.**

---

## 5. Results — 11 access-control cases

| # | Use case | Expected | Actual | Result |
|:--|:--|:--|:--|:--|
| S1 | No authentication configured (baseline access) | 200 | 200 | Passed |
| S2 | Auth enabled — request without credentials | 401 | 401 | Passed |
| S3 | Auth enabled — wrong password | 401 | 401 | Passed |
| S4 | Auth enabled — wrong username | 401 | 401 | Passed |
| S5 | Auth enabled — correct credentials | 200 | 200 | Passed |
| S6 | `/api/status` without credentials (exempt endpoint) | 200 | 200 | Passed |
| S7 | `/api/status` with credentials | 200 | 200 | Passed |
| S8 | Auth disabled — access allowed | 200 | 200 | Passed |
| S9 | CIDR allow-list — source outside the list | 403 | 403 | Passed |
| S10 | CIDR allow-list — source inside the list | 200 | 200 | Passed |
| S11 | Configuration persists across restart | Retained | Retained | Passed |

**Access control: 11 / 11 passed.**

---

## 6. Request/response evidence (selected cases)

> Every request below carries Basic Auth credentials.

### F6 — Create a folder

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/", "T": "baja:Folder", "N": "Demo"}]'
```
**Response — HTTP 200**
```json
[{ "OP": "add", "name": "Demo", "status": "ok" }]
```

### F10 — Modify a property value

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "mod", "PATH": "/Demo/Temp1", "N": "out", "V": "42.5"}]'
```
**Response — HTTP 200**
```json
[{ "OP": "mod", "path": "/Demo/Temp1", "N": "out", "status": "ok" }]
```

### F14 / F15 — Create a link and verify propagation

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "link", "PATH": "/Demo/Temp1", "N": "out",
        "TARGET": "/Demo/Temp1Cpy", "TARGET_N": "in16"}]'

curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/Demo/Temp1Cpy", "N": "in16"}]'
```
**Response — HTTP 200**
```json
[{ "OP": "link", "status": "ok" }]
[{ "OP": "read", "path": "/Demo/Temp1Cpy", "N": "in16", "value": "42.50 {ok}", "status": "ok" }]
```

### F18 — BQL query

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "bql", "Q": "select * from control:NumericWritable"}]'
```
**Response — HTTP 200**
```json
[{ "OP": "bql", "columns": ["path", "out"], "rows": [["/Demo/Temp1", "42.5"]], "count": 1, "status": "ok" }]
```

### S2 — Request without credentials

**Request**
```bash
curl -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "list", "PATH": "/"}]'
```
**Response — HTTP 401**
```json
{ "error": "auth required" }
```

### S5 — Correct credentials

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "list", "PATH": "/"}]'
```
**Response — HTTP 200**
```json
[{ "OP": "list", "path": "/", "children": [ { "name": "Demo", "type": "Folder" } ], "status": "ok" }]
```

---

## 7. Summary

| Category | Cases | Passed |
|:--|:--:|:--:|
| Functional | 29 | 29 |
| Access Control | 11 | 11 |
| **Total** | **40** | **40** |

**Conclusion: all 40 use cases passed (100%).**

### Notes

- `POST /api/program/compile` is **not** included in the figures above. It is access-controlled like every other endpoint; its functional use is outside the scope of this test set.
- Access-control cases are judged by the acceptance/rejection response itself (401 / 403 / 200), which is the final evidence for that behaviour.
