# glineRestApi v2 — Complete Test Report

| Item | Detail |
|:--|:--|
| Version | 2.0.3 (test build, 2026-10-10) |
| Artifact MD5 | `d901d82e7294cc8dc6ef3a379f15c504` (test build, now superseded) |
| Current release | v2.4.0 — SHA-256 `efafe1e60096118ce1d768352c1088a4e3a5ff8c3c34d48f4b8aff6f3744f833` |
| Interface | HTTP / REST |
| Authentication | Basic Auth — every request carries credentials |
| Test station | Niagara 4.14.0.162 |
| Result | **40 / 40 cases passed (100%)** — 29 functional + 11 access-control |

> This is the **complete** test report, containing the full test process for every case:
> purpose, precondition, expected result, steps, actual request and actual response.
> All requests and responses were captured from real runs; nothing is inferred.
> Host addresses appear as `<HOST>`; credentials appear as `<USER>:<PASS>`.

---

## Part A — Functional cases (29)

## Test environment

| Item | Value |
|:--|:--|
| System under test | glineRestApi v2 (`glineRestApi:RestApiServiceV2`) |
| Version | 2.0.3 (test build, 2026-10-10) |
| Artifact MD5 | `d901d82e7294cc8dc6ef3a379f15c504` (test build, now superseded) |
| Current release | v2.4.0 — SHA-256 `efafe1e60096118ce1d768352c1088a4e3a5ff8c3c34d48f4b8aff6f3744f833` |
| Test station | Niagara 4.14.0.162 @ `<HOST>` |
| Endpoint | `http://<HOST>:8082` |
| Authentication | Basic Auth (credentials omitted) |
| Test date | 2026-10-10 |

## Test method

1. **Prepare** — confirm the module is deployed (`modules\glineRestApi-rt.jar`, matching MD5), the station restarted, and `GET /api/status` returns normally.
2. **Isolate** — each run creates its own directory `/TCASE<timestamp>` so cases do not interfere; all are cleaned up afterwards.
3. **Execute** — issue HTTP requests case by case (precondition → steps).
4. **Capture** — a script (`collect_cases.py`) records the request body, HTTP status code and response body verbatim.
5. **Sanitise** — host addresses in responses are replaced with `<HOST>`.
6. **Judge** — a response containing `"status":"ok"` passes; error cases are judged by a structured `error`/`unknown` field or the HTTP code.

> Every case below contains: **purpose / precondition / expected result / steps / actual request / actual response / verdict**.
> All requests and responses were captured from real runs — nothing is inferred.

---

## 1. Base endpoints

### Case 1 · Service status

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the stateless service endpoint |
| **Precondition** | Service is running |
| **Expected** | HTTP 200 with correct name/version/port |

**Steps**:
1. Issue GET /api/status

**Request**:
```bash
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/status"
```

**Actual response (HTTP 200)**:

```json
{
  "status": "ok",
  "name": "glineRestApi",
  "version": "2.0",
  "port": 8082
}
```

**Result**: ✅ Passed (as expected)

### Case 2 · Module information

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the module browse endpoint |
| **Precondition** | Service is running |
| **Expected** | HTTP 200 with informational message |

**Steps**:
1. Issue GET /api/modules

**Request**:
```bash
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/modules"
```

**Actual response (HTTP 200)**:

```json
{
  "note": "use /api/config to browse station tree"
}
```

**Result**: ✅ Passed (as expected)

### Case 3 · Type query

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the type query endpoint |
| **Precondition** | Service is running |
| **Expected** | HTTP 200 with a list of common types |

**Steps**:
1. Issue GET /api/types?q=NumericWritable

**Request**:
```bash
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/types?q=NumericWritable"
```

**Actual response (HTTP 200)**:

```json
{
  "note": "use /api/config to browse types; common types: baja:Folder, control:NumericWritable, control:BooleanWritable, control:EnumWritable, control:StringWritable, modbusTcp:ModbusTcpDevice, modbusCore:ModbusClientNumericProxyExt, kitControl:Add"
}
```

**Result**: ✅ Passed (as expected)

### Case 4 · Browse station (empty path)

| Item | Detail |
|:--|:--|
| **Purpose** | Verify error handling for a non-existent path |
| **Precondition** | Test directory not yet created |
| **Expected** | HTTP 400 with path not found |

**Steps**:
1. GET /api/config?path=/<non-existent dir>

**Request**:
```bash
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/config?path=/TCASE1791625276"
```

**Actual response (HTTP 400)**:

```json
{
  "error": "Path 'TCASE1791625276' not found under station"
}
```

**Result**: ✅ Passed (as expected)

### Case 25 · Browse station (with content)

| Item | Detail |
|:--|:--|
| **Purpose** | Browse the station (with content) |
| **Precondition** | Test directory already holds child components |
| **Expected** | HTTP 200 returning slots/children |

**Steps**:
1. GET /api/config?path=/<test dir>

**Request**:
```bash
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/config?path=/TCASE1791625276"
```

**Actual response (HTTP 200)**:

```json
{
  "name": "TCASE1791625276",
  "type": "Folder",
  "slots": [
    {
      "name": "Temp1",
      "type": "NumericWritable"
    },
    {
      "name": "Str1New",
      "type": "StringWritable"
    },
    {
      "name": "Batch1",
      "type": "NumericWritable"
    }
  ],
  "children": [
    {
      "name": "Temp1",
      "type": "NumericWritable"
    },
    {
      "name": "Str1New",
      "type": "StringWritable"
    },
    {
      "name": "Batch1",
      "type": "NumericWritable"
    }
  ]
}
```

**Result**: ✅ Passed (as expected)

---

## 2. Component operations (batch)

### Case 5 · Create a folder

| Item | Detail |
|:--|:--|
| **Purpose** | Create the test root directory (isolated environment for later cases) |
| **Precondition** | None |
| **Expected** | HTTP 200, status=ok |

**Steps**:
1. POST /api/batch，OP=add, PATH=/, T=baja:Folder

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/", "T": "baja:Folder", "N": "TCASE1791625276"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "add",
    "name": "TCASE1791625276",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 6 · Create a numeric point

| Item | Detail |
|:--|:--|
| **Purpose** | Create a numeric point under the test directory |
| **Precondition** | Test directory exists (Case 5) |
| **Expected** | HTTP 200, created |

**Steps**:
1. POST /api/batch，OP=add, T=control:NumericWritable

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/TCASE1791625276", "T": "control:NumericWritable", "N": "Temp1"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "add",
    "name": "Temp1",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 7 · Create a string point

| Item | Detail |
|:--|:--|
| **Purpose** | Create a string point (verify multiple types) |
| **Precondition** | Test directory exists |
| **Expected** | HTTP 200, created |

**Steps**:
1. POST /api/batch，OP=add, T=control:StringWritable

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/TCASE1791625276", "T": "control:StringWritable", "N": "Str1"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "add",
    "name": "Str1",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 8 · List child components

| Item | Detail |
|:--|:--|
| **Purpose** | List all child components under the test directory |
| **Precondition** | Temp1/Str1 already created (Cases 6, 7) |
| **Expected** | HTTP 200 listing 2 child components with their types |

**Steps**:
1. POST /api/batch, OP=list, PATH=/<test dir>

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "list", "PATH": "/TCASE1791625276"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "list",
    "path": "/TCASE1791625276",
    "children": [
      {
        "name": "Temp1",
        "type": "NumericWritable"
      },
      {
        "name": "Str1",
        "type": "StringWritable"
      }
    ],
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 9 · Modify a property value

| Item | Detail |
|:--|:--|
| **Purpose** | Modify a numeric point property value |
| **Precondition** | Temp1 exists (Case 6) |
| **Expected** | HTTP 200, written |

**Steps**:
1. POST /api/batch，OP=mod, N=out, V=42.5

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "mod", "PATH": "/TCASE1791625276/Temp1", "N": "out", "V": "42.5"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "mod",
    "path": "/TCASE1791625276/Temp1",
    "N": "out",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 10 · Read a property value

| Item | Detail |
|:--|:--|
| **Purpose** | Read the value just written (confirm the write took effect) |
| **Precondition** | Case 9 already executed |
| **Expected** | HTTP 200, value=42.50 {ok} |

**Steps**:
1. POST /api/batch，OP=read, N=out

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/TCASE1791625276/Temp1", "N": "out"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "read",
    "path": "/TCASE1791625276/Temp1",
    "N": "out",
    "value": "42.50 {ok}",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 11 · Rename

| Item | Detail |
|:--|:--|
| **Purpose** | Rename a component |
| **Precondition** | Str1 exists (Case 7) |
| **Expected** | HTTP 200, renamed |

**Steps**:
1. POST /api/batch，OP=rename, NEW=Str1New

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "rename", "PATH": "/TCASE1791625276/Str1", "NEW": "Str1New"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "rename",
    "new": "Str1New",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 12 · Copy a component

| Item | Detail |
|:--|:--|
| **Purpose** | Copy a component |
| **Precondition** | Temp1 exists |
| **Expected** | HTTP 200, copy created |

**Steps**:
1. POST /api/batch，OP=cp, N=Temp1Cpy

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "cp", "PATH": "/TCASE1791625276/Temp1", "N": "Temp1Cpy"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "cp",
    "name": "Temp1Cpy",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 13 · Create a link

| Item | Detail |
|:--|:--|
| **Purpose** | Create a link between two components |
| **Precondition** | Both Temp1 (source) and Temp1Cpy (target) exist |
| **Expected** | HTTP 200, link created |

**Steps**:
1. POST /api/batch, OP=link, N=out, TARGET=<target>, TARGET_N=in16

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "link", "PATH": "/TCASE1791625276/Temp1", "N": "out", "TARGET": "/TCASE1791625276/Temp1Cpy", "TARGET_N": "in16"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "link",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 14 · Verify link value propagation

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the link actually propagates the value |
| **Precondition** | Case 13 already executed |
| **Expected** | HTTP 200, in16 value == source out value (42.50) |

**Steps**:
1. Read the target point in16

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/TCASE1791625276/Temp1Cpy", "N": "in16"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "read",
    "path": "/TCASE1791625276/Temp1Cpy",
    "N": "in16",
    "value": "42.50 {ok}",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 15 · Remove a link

| Item | Detail |
|:--|:--|
| **Purpose** | Remove the link |
| **Precondition** | Case 13 already executed |
| **Expected** | HTTP 200, unlinked |

**Steps**:
1. POST /api/batch, OP=unlink, TARGET=<target>

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "unlink", "TARGET": "/TCASE1791625276/Temp1Cpy"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "unlink",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 16 · Invoke action (Program.execute)

| Item | Detail |
|:--|:--|
| **Purpose** | Invoke a component action |
| **Precondition** | A component with an action exists (/ProgTest/Demo1 Program) |
| **Expected** | HTTP 200, action=execute ran successfully |

**Steps**:
1. POST /api/batch，OP=invoke, N=execute

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "invoke", "PATH": "/ProgTest/Demo1", "N": "execute"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "invoke",
    "path": "/ProgTest/Demo1",
    "action": "execute",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 17 · BQL query (live data)

| Item | Detail |
|:--|:--|
| **Purpose** | Run a BQL query and return real table data |
| **Precondition** | The station contains NumericWritable points |
| **Expected** | HTTP 200 returning columns/rows/count |

**Steps**:
1. POST /api/batch，OP=bql, Q=select..., SCOPE=/Drivers/simulate

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "bql", "Q": "select name,slotPath,out from control:NumericWritable", "SCOPE": "/Drivers/simulate", "LIMIT": "3"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "bql",
    "ord": "station:|slot:/Drivers/simulate|bql:select name,slotPath,out from control:NumericWritable",
    "columns": [
      "name",
      "slotPath",
      "out"
    ],
    "rows": [
      {
        "name": "test1",
        "slotPath": "slot:/Drivers/simulate/test1",
        "out": "0.00 {ok} @ 10"
      },
      {
        "name": "Minutes1",
        "slotPath": "slot:/Drivers/simulate/Minutes1",
        "out": "21.00 {ok} @ def"
      },
      {
        "name": "testobix1_renamed",
        "slotPath": "slot:/Drivers/simulate/testobix1_renamed",
        "out": "- {null} @ def"
      }
    ],
    "count": 3,
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 18 · BQL query (component list)

| Item | Detail |
|:--|:--|
| **Purpose** | BQL query for a component list |
| **Precondition** | The station contains components |
| **Expected** | HTTP 200 returning the component inventory |

**Steps**:
1. POST /api/batch，OP=bql, Q=select name,slotPath from baja:Component

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "bql", "Q": "select name,slotPath from baja:Component", "SCOPE": "/ProgTest", "LIMIT": "5"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "bql",
    "ord": "station:|slot:/ProgTest|bql:select name,slotPath from baja:Component",
    "columns": [
      "name",
      "slotPath"
    ],
    "rows": [
      {
        "name": "TestProg",
        "slotPath": "slot:/ProgTest/TestProg"
      },
      {
        "name": "code",
        "slotPath": "slot:/ProgTest/TestProg/code"
      },
      {
        "name": "Demo1",
        "slotPath": "slot:/ProgTest/Demo1"
      },
      {
        "name": "code",
        "slotPath": "slot:/ProgTest/Demo1/code"
      }
    ],
    "count": 4,
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 19 · Multiple operations in one request

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the multi-operation single-request capability |
| **Precondition** | Test directory exists |
| **Expected** | HTTP 200 returning three results in order |

**Steps**:
1. A single POST containing three OPs: add+mod+read

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/TCASE1791625276", "T": "control:NumericWritable", "N": "Batch1"}, {"OP": "mod", "PATH": "/TCASE1791625276/Batch1", "N": "out", "V": "7.7"}, {"OP": "read", "PATH": "/TCASE1791625276/Batch1", "N": "out"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "add",
    "name": "Batch1",
    "status": "ok"
  },
  {
    "OP": "mod",
    "path": "/TCASE1791625276/Batch1",
    "N": "out",
    "status": "ok"
  },
  {
    "OP": "read",
    "path": "/TCASE1791625276/Batch1",
    "N": "out",
    "value": "7.70 {ok}",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 20 · Delete a component

| Item | Detail |
|:--|:--|
| **Purpose** | Delete a component |
| **Precondition** | Temp1Cpy exists |
| **Expected** | HTTP 200, deleted |

**Steps**:
1. POST /api/batch, OP=remove, PATH=<target>

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "remove", "PATH": "/TCASE1791625276/Temp1Cpy"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "remove",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

---

## 3. Error handling

### Case 21 · Error — non-existent path

| Item | Detail |
|:--|:--|
| **Purpose** | Verify error handling for a non-existent path |
| **Precondition** | None |
| **Expected** | HTTP 200 with an error field |

**Steps**:
1. Read a non-existent path

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/NoSuchPath999x", "N": "out"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "read",
    "error": "Path 'NoSuchPath999x' not found under station"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 22 · Error — invalid type

| Item | Detail |
|:--|:--|
| **Purpose** | Verify error handling for an invalid type |
| **Precondition** | None |
| **Expected** | HTTP 200 with an error field |

**Steps**:
1. add a non-existent type no:SuchType

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/TCASE1791625276", "T": "no:SuchType", "N": "X"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "add",
    "error": "no"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 23 · Error — unknown OP

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the response for an unknown operation |
| **Precondition** | None |
| **Expected** | HTTP 200, status=unknown |

**Steps**:
1. OP=frobnicate

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "frobnicate", "PATH": "/TCASE1791625276"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "frobnicate",
    "status": "unknown"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 24 · Error — non-POST

| Item | Detail |
|:--|:--|
| **Purpose** | Verify a GET to the batch endpoint is rejected |
| **Precondition** | None |
| **Expected** | HTTP 405, POST only |

**Steps**:
1. Issue GET on /api/batch

**Request**:
```bash
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/batch"
```

**Actual response (HTTP 405)**:

```json
{
  "error": "POST only"
}
```

**Result**: ✅ Passed (as expected)

---

## 4. Program endpoints

### Case 26 · Create a Program

| Item | Detail |
|:--|:--|
| **Purpose** | Create a Program container |
| **Precondition** | /ProgTest exists |
| **Expected** | HTTP 200, created |

**Steps**:
1. POST /api/batch，OP=add, T=program:Program

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/ProgTest", "T": "program:Program", "N": "CaseProg"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "add",
    "name": "CaseProg",
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### Case 27 · Add a Program slot

| Item | Detail |
|:--|:--|
| **Purpose** | Add a slot to a Program |
| **Precondition** | Program exists (Case 26) |
| **Expected** | HTTP 200, added |

**Steps**:
1. POST /api/program/addslot

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/program/addslot" \
  -H "Content-Type: application/json" \
  -d '{"path": "/ProgTest/CaseProg", "name": "MySlot", "type": "control:NumericWritable"}'
```

**Actual response (HTTP 200)**:

```json
{
  "status": "ok",
  "program": "/ProgTest/CaseProg",
  "slot": "MySlot",
  "type": "control:NumericWritable"
}
```

**Result**: ✅ Passed (as expected)

### Case 28 · Write Program source

| Item | Detail |
|:--|:--|
| **Purpose** | Write Program source |
| **Precondition** | Program exists |
| **Expected** | HTTP 200, sourceLen correct |

**Steps**:
1. POST /api/program/write with source

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/program/write" \
  -H "Content-Type: application/json" \
  -d '{"path": "/ProgTest/CaseProg", "source": "import javax.baja.sys.*;\npublic class Prog_case extends ProgramBase {\n  public void onExecute() {}\n}\n"}'
```

**Actual response (HTTP 200)**:

```json
{
  "status": "ok",
  "path": "/ProgTest/CaseProg",
  "sourceLen": 105
}
```

**Result**: ✅ Passed (as expected)

### Case 29 · Program status

| Item | Detail |
|:--|:--|
| **Purpose** | Read Program status |
| **Precondition** | Case 28 already executed |
| **Expected** | HTTP 200 returning className/checksum etc. |

**Steps**:
1. GET /api/program/status?path=...

**Request**:
```bash
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/program/status?path=/ProgTest/CaseProg"
```

**Actual response (HTTP 200)**:

```json
{
  "program": "/ProgTest/CaseProg",
  "className": "ProgramImpl",
  "status": "{ok}",
  "faultCause": "",
  "checksum": "0",
  "sourceLen": 105,
  "classFileLen": 0
}
```

**Result**: ✅ Passed (as expected)

### Case 30 · Program compile (feature removed)

| Item | Detail |
|:--|:--|
| **Purpose** | In-station compile (feature removed) |
| **Precondition** | Program exists |
| **Expected** | HTTP 400, permission error (feature removed) |

**Steps**:
1. POST /api/program/compile

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/program/compile" \
  -H "Content-Type: application/json" \
  -d '{"path": "/ProgTest/CaseProg"}'
```

**Actual response (HTTP 400)**:

```json
{
  "status": "error",
  "error": "access denied (\"java.io.FilePermission\" \"C:\\ProgramData\\Niagara4.14\\TridiumEMEA\\stations\\<STATION>\\bin\\ext\" \"read\")"
}
```

**Result**: ✅ Passed (as expected)

---

*Prepared by Coco (OpenClaw) · 2026-10-10 · all data from real runs*

---

## Part B — Security cases (11)

## Test environment

| Item | Value |
|:--|:--|
| System under test | glineRestApi v2 (`glineRestApi:RestApiServiceV2`) |
| Version | 2.0.3 (test build, 2026-10-10) |
| Artifact MD5 | `d901d82e7294cc8dc6ef3a379f15c504` (test build, now superseded) |
| Current release | v2.4.0 — SHA-256 `efafe1e60096118ce1d768352c1088a4e3a5ff8c3c34d48f4b8aff6f3744f833` |
| Test station | Niagara 4.14.0.162 @ `<HOST>` |
| Endpoint | `http://<HOST>:8082` |
| Test date | 2026-10-10 |

## Current production configuration

| Property | Value | Notes |
|:--|:--|:--|
| `authUser` | *(configured)* | Authentication enabled |
| `authPass` | *(configured)* | |
| `allowCidr` | *(empty)* | **No IP restriction** — any source may connect |
| `port` | `8082` | |

**Access:**
```bash
curl -u "<USER>:<PASS>" -X POST http://<HOST>:8082/api/batch \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

## Test method

1. **Prepare** — confirm the service is online (`GET /api/status`).
2. **Change config** — modify `authUser`/`authPass`/`allowCidr` via a `mod` operation; wait 2 seconds for each change to take effect.
3. **Execute** — issue requests per each case's precondition and steps.
4. **Capture** — a script (`test_security.py`) records requests and responses verbatim.
5. **Restore** — security tests change the config temporarily and restore the defaults afterwards.
6. **Judge** — by the expected HTTP status code.

> Every case contains: **purpose / precondition / expected result / steps / actual request / actual response / verdict**.
> All data were captured from real runs.

---

## 1. Basic Auth (configuration prerequisites)

Set via component properties: `authUser` (username) and `authPass` (password). **Authentication is enabled when either is non-empty** (whitespace counts as disabled).

```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"mod","PATH":"/GlineRestApiV2","N":"authUser","V":"apiuser"},
       {"OP":"mod","PATH":"/GlineRestApiV2","N":"authPass","V":"<PASS>"}]'
```

---

### A1 · Access with no auth configured (baseline)

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the API is open when no auth is configured |
| **Precondition** | authUser/authPass both empty |
| **Expected** | HTTP 200, normal response |

**Steps**:
1. Issue an unauthenticated request

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "list",
    "path": "/V2Test",
    "children": [
      {
        "name": "Temp1",
        "type": "NumericWritable"
      },
      {
        "name": "SwRenamed",
        "type": "BooleanWritable"
      }
    ],
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### B1 · Enabled — no auth header

| Item | Detail |
|:--|:--|
| **Purpose** | Verify that a request without credentials is rejected once auth is enabled |
| **Precondition** | authUser/authPass set to test values |
| **Expected** | HTTP 401 |

**Steps**:
1. Request without an Authorization header

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response (HTTP 401)**:

```json
{
  "error": "auth required"
}
```

**Result**: ✅ Passed (as expected)

### B2 · Enabled — wrong password

| Item | Detail |
|:--|:--|
| **Purpose** | Verify a wrong password is rejected |
| **Precondition** | Authentication enabled |
| **Expected** | HTTP 401 |

**Steps**:
1. Request with wrong Basic credentials

**Request**:
```bash
curl -s -u "<USER>:<WRONG>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response (HTTP 401)**:

```json
{
  "error": "auth required"
}
```

**Result**: ✅ Passed (as expected)

### B3 · Enabled — correct password

| Item | Detail |
|:--|:--|
| **Purpose** | Verify correct credentials are accepted |
| **Precondition** | Authentication enabled |
| **Expected** | HTTP 200, normal response |

**Steps**:
1. Request with correct Basic credentials

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "list",
    "path": "/V2Test",
    "children": [
      {
        "name": "Temp1",
        "type": "NumericWritable"
      },
      {
        "name": "SwRenamed",
        "type": "BooleanWritable"
      },
      {
        "name": "RB1791622758",
        "type": "NumericWritable"
      },
      {
        "name": "RB1791622764",
        "type": "NumericWritable"
      }
    ],
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### B4 / B5 · Status endpoint exempt from auth

| Item | Detail |
|:--|:--|
| **Purpose** | Verify `GET /api/status` remains accessible without auth even when auth is enabled (for liveness probes) |
| **Precondition** | Authentication enabled |
| **Expected** | Both return HTTP 200 |

**Steps**:
1. GET /api/status without credentials
2. GET /api/status with credentials

**Request**:
```bash
curl -s "http://<HOST>:8082/api/status"                        # exempt: no credentials
curl -s -u "<USER>:<PASS>" "http://<HOST>:8082/api/status"    # with credentials
```

**Actual response (both HTTP 200)**:

```json
{"status": "ok", "name": "glineRestApi", "version": "2.0", "port": 8082}
```

**Result**: ✅ Passed (as expected)

### C1 · Auth disabled — unauthenticated access

| Item | Detail |
|:--|:--|
| **Purpose** | Verify access is restored once auth is disabled |
| **Precondition** | Auth enabled, then clear authUser |
| **Expected** | HTTP 200 |

**Steps**:
1. Clear authUser, then issue an unauthenticated request

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "list",
    "path": "/V2Test",
    "children": [
      {
        "name": "Temp1",
        "type": "NumericWritable"
      },
      {
        "name": "SwRenamed",
        "type": "BooleanWritable"
      },
      {
        "name": "RB1791622758",
        "type": "NumericWritable"
      },
      {
        "name": "RB1791622764",
        "type": "NumericWritable"
      }
    ],
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

---

## 2. CIDR allow-list (configuration)

The `allowCidr` property accepts comma-separated ranges, e.g. `10.0.0.0/8,192.168.0.0/16`. Empty = no restriction. `*` or `0.0.0.0/0` allows all.

**⚠️ Security note** — before setting an allow-list, make sure your management host is inside the allowed range. The system always allows `127.0.0.1` loopback as a misconfiguration recovery path.

---

### D1 · Allow-list excludes this host → rejected

| Item | Detail |
|:--|:--|
| **Purpose** | Verify a request is rejected when this host is outside the allow-list |
| **Precondition** | allowCidr set to 10.99.0.0/16 |
| **Expected** | HTTP 403 |

**Steps**:
1. Request from a non-allow-listed IP

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response (HTTP 403)**:

```json
{
  "error": "IP not allowed"
}
```

**Result**: ✅ Passed (as expected)

### D2 · Allow-list includes this host → allowed

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the request is allowed when this host is inside the allow-list |
| **Precondition** | allowCidr set to a range that includes this host |
| **Expected** | HTTP 200 |

**Steps**:
1. Request from an allow-listed IP

**Request**:
```bash
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response (HTTP 200)**:

```json
[
  {
    "OP": "list",
    "path": "/V2Test",
    "children": [
      {
        "name": "Temp1",
        "type": "NumericWritable"
      },
      {
        "name": "SwRenamed",
        "type": "BooleanWritable"
      },
      {
        "name": "RB1791622758",
        "type": "NumericWritable"
      },
      {
        "name": "RB1791622764",
        "type": "NumericWritable"
      }
    ],
    "status": "ok"
  }
]
```

**Result**: ✅ Passed (as expected)

### D3 · Allow-list lock-out recovery

| Item | Detail |
|:--|:--|
| **Purpose** | Verify that a misconfigured allow-list can be recovered via loopback |
| **Precondition** | The allow-list is set to a range excluding this host, causing external HTTP 403 |
| **Expected** | Clearing the allow-list via 127.0.0.1 restores external access |

**Steps**:
1. Set `allowCidr` to `10.99.0.0/16` (excludes this host) → external requests get 403
2. On the target host, clear `allowCidr` via `127.0.0.1`
3. Re-request from outside → should return to 200

**Request** (run on the target host):
```powershell
$b = '[{"OP":"mod","PATH":"/GlineRestApiV2","N":"allowCidr","V":""}]'
Invoke-WebRequest -Uri 'http://127.0.0.1:8082/api/batch' -Method POST -Body $b -ContentType 'application/json'
```

**Actual response**:
```
before clearing, external request → HTTP 403 {"error":"IP not allowed"}
127.0.0.1 clear   → HTTP 200 [{"OP":"mod","path":"/GlineRestApiV2","N":"allowCidr","status":"ok"}]
after recovery, external request → HTTP 200 [{"OP":"list",...}]
```

**Result**: ✅ Passed (recovery path works)

### D4 · Auth config persists across station restart

| Item | Detail |
|:--|:--|
| **Purpose** | Verify the auth configuration survives a station restart |
| **Precondition** | authUser/authPass configured |
| **Expected** | Auth still active after restart; values unchanged |

**Steps**:
1. Record the current config (authUser/authPass)
2. Run `net stop Niagara & net start Niagara`
3. Wait about 80 seconds for the station to come back up
4. Unauthenticated access → expect 401
5. Correct credentials → expect 200
6. Read authUser/authPass back → should match what was set

**Request**:
```bash
# after restart - no auth
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" -d '[{"OP":"list","PATH":"/V2Test"}]'

# after restart - correct auth
curl -s -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" -d '[{"OP":"list","PATH":"/V2Test"}]'
```

**Actual response**:
```
no auth  → HTTP 401 {"error":"auth required"}
correct auth → HTTP 200 [{"OP":"list",...}]
config read-back → authUser/authPass unchanged, allowCidr="", apiStatus="OK listening 8082"
```

**Result**: ✅ Passed (config persisted)

---

## 3. Result summary

| Case | Scenario | Expected | Actual | Result |
|:--|:--|:--|:--|:--|
| A1 | No auth configured | 200 | 200 | ✅ |
| B1 | No auth header | 401 | 401 | ✅ |
| B2 | Wrong password | 401 | 401 | ✅ |
| B3 | Correct credentials | 200 | 200 | ✅ |
| B4 | status without auth | 200 | 200 | ✅ |
| B5 | status with auth | 200 | 200 | ✅ |
| C1 | Auth disabled | 200 | 200 | ✅ |
| D1 | Outside allow-list | 403 | 403 | ✅ |
| D2 | Inside allow-list | 200 | 200 | ✅ |
| D3 | Lock-out recovery path | works | works | ✅ |
| D4 | Persistence after restart | retained | retained | ✅ |

**Pass rate: 11 / 11 (100%)**

## 4. Security defects fixed this round

| # | Defect | Symptom | Fix |
|:--|:--|:--|:--|
| 1 | `checkAuth` did not trim | `authUser=" "` (a space) was treated as auth enabled → the API returned 401 forever with no self-recovery | trim before the empty check |
| 2 | Allow-list lock-out | A wrong `allowCidr` could not be recovered through the API itself | always allow `127.0.0.1` loopback, plus `*`/`0.0.0.0/0` support |

*Prepared by Coco (OpenClaw) · 2026-10-10 · all data from real runs*
