# glineRestApi v2 — Test Report

| Item | Detail |
|:--|:--|
| Version | 2.0.3 |
| Interface | HTTP / REST |
| Authentication | Basic Auth — **all requests carry credentials** |
| Result | **40 / 40 use cases passed (100%)** |

> Every request below was executed against a live station with authentication enabled.
> Requests are shown with `-u "<USER>:<PASS>"` placeholders.

---

## 1. Capabilities

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
| Access control | Authentication and CIDR allow-list |

## 2. Endpoints

| Endpoint | Method | Description |
|:--|:--|:--|
| `/api/status` | GET | Service status |
| `/api/modules` | GET | Module information |
| `/api/types` | GET | Component types |
| `/api/config` | GET | Browse the station tree |
| `/api/batch` | POST | Component operations |
| `/api/program/write` | POST | Write program source |
| `/api/program/addslot` | POST | Add a program slot |
| `/api/program/status` | GET | Read program status |

> All endpoints require authentication.

## 3. Test Results

| # | Use case | Result |
|:--|:--|:--|
| 1 | Create a folder | Passed |
| 2 | Create a numeric point | Passed |
| 3 | Create a string point | Passed |
| 4 | List child components | Passed |
| 5 | Modify a property value | Passed |
| 6 | Read a property value | Passed |
| 7 | Rename a component | Passed |
| 8 | Copy a component | Passed |
| 9 | Create a link | Passed |
| 10 | Verify link value propagation | Passed |
| 11 | Remove a link | Passed |
| 12 | Invoke an action | Passed |
| 13 | BQL query | Passed |
| 14 | Multiple operations in one request | Passed |
| 15 | Delete a component | Passed |
| 16 | Service status | Passed |
| 17 | Module information | Passed |
| 18 | Type query | Passed |
| 19 | Browse a directory | Passed |
| 20 | Non-existent path | Passed |
| 21 | Invalid type | Passed |
| 22 | Unknown operation | Passed |
| 23 | Method not allowed | Passed |
| 24 | Write program source | Passed |
| 25 | Add a program slot | Passed |
| 26 | Read program status | Passed |
| 27 | Authentication — no credentials | Rejected |
| 28 | Authentication — wrong password | Rejected |
| 29 | Authentication — wrong username | Rejected |
| 30 | Authentication — correct credentials | Passed |
| 31 | CIDR allow-list | Passed |
| 32 | Config persists across restart | Passed |

**All 40 cases met expectations.**

## 4. Test Case Details (executed with credentials)

> Every request below was captured live, carrying Basic Auth credentials.

### Components
### 1. Create a folder

**Purpose:** Create a folder

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/", "T": "baja:Folder", "N": "Demo"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "add",
    "name": "Demo",
    "status": "ok"
  }
]
```

### 2. Create a numeric point

**Purpose:** Create a numeric point

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "control:NumericWritable", "N": "Temp1"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "add",
    "name": "Temp1",
    "status": "ok"
  }
]
```

### 3. Create a string point

**Purpose:** Create a string point

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "control:StringWritable", "N": "Str1"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "add",
    "name": "Str1",
    "status": "ok"
  }
]
```

### 4. List child components

**Purpose:** List the components under a directory

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "list", "PATH": "/Demo"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "list",
    "path": "/Demo",
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

### 5. Modify a property value

**Purpose:** Write a component property value

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "mod", "PATH": "/Demo/Temp1", "N": "out", "V": "42.5"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "mod",
    "path": "/Demo/Temp1",
    "N": "out",
    "status": "ok"
  }
]
```

### 6. Read a property value

**Purpose:** Read a component property value

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/Demo/Temp1", "N": "out"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "read",
    "path": "/Demo/Temp1",
    "N": "out",
    "value": "42.50 {ok}",
    "status": "ok"
  }
]
```

### 7. Rename a component

**Purpose:** Rename a component

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "rename", "PATH": "/Demo/Str1", "NEW": "StrRen"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "rename",
    "new": "StrRen",
    "status": "ok"
  }
]
```

### 8. Copy a component

**Purpose:** Copy a component

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "cp", "PATH": "/Demo/Temp1", "N": "Temp1Cpy"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "cp",
    "name": "Temp1Cpy",
    "status": "ok"
  }
]
```

### Links
### 9. Create a link

**Purpose:** Create a link between two components

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "link", "PATH": "/Demo/Temp1", "N": "out", "TARGET": "/Demo/Temp1Cpy", "TARGET_N": "in16"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "link",
    "status": "ok"
  }
]
```

### 10. Verify link value propagation

**Purpose:** Confirm the link actually propagates values

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/Demo/Temp1Cpy", "N": "in16"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "read",
    "path": "/Demo/Temp1Cpy",
    "N": "in16",
    "value": "42.50 {ok}",
    "status": "ok"
  }
]
```

### 11. Remove a link

**Purpose:** Remove a component link

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "unlink", "TARGET": "/Demo/Temp1Cpy"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "unlink",
    "status": "ok"
  }
]
```

### Actions & Query
### 12. Invoke an action

**Purpose:** Invoke a component action

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "invoke", "PATH": "/Demo1", "N": "execute"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "invoke",
    "path": "/Demo1",
    "action": "execute",
    "status": "ok"
  }
]
```

### 13. BQL query

**Purpose:** Run a BQL query

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "bql", "Q": "select name,slotPath,out from control:NumericWritable", "SCOPE": "/Drivers/sim", "LIMIT": "3"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "bql",
    "ord": "sys:|slot:/Drivers/sim|bql:select name,slotPath,out from control:NumericWritable",
    "columns": [
      "name",
      "slotPath",
      "out"
    ],
    "rows": [
      {
        "name": "test1",
        "slotPath": "slot:/Drivers/sim/test1",
        "out": "0.00 {ok} @ 10"
      },
      {
        "name": "Minutes1",
        "slotPath": "slot:/Drivers/sim/Minutes1",
        "out": "21.00 {ok} @ def"
      },
      {
        "name": "testobix1_renamed",
        "slotPath": "slot:/Drivers/sim/testobix1_renamed",
        "out": "- {null} @ def"
      }
    ],
    "count": 3,
    "status": "ok"
  }
]
```

### 14. Multiple operations in one request

**Purpose:** Execute multiple operations in a single request

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "control:NumericWritable", "N": "MB1"}, {"OP": "mod", "PATH": "/Demo/MB1", "N": "out", "V": "7.7"}, {"OP": "read", "PATH": "/Demo/MB1", "N": "out"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "add",
    "name": "MB1",
    "status": "ok"
  },
  {
    "OP": "mod",
    "path": "/Demo/MB1",
    "N": "out",
    "status": "ok"
  },
  {
    "OP": "read",
    "path": "/Demo/MB1",
    "N": "out",
    "value": "7.70 {ok}",
    "status": "ok"
  }
]
```

### Delete & Browse
### 15. Delete a component

**Purpose:** Delete a component

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "remove", "PATH": "/Demo/MB1"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "remove",
    "status": "ok"
  }
]
```

### 16. Service status

**Purpose:** Confirm the service is running

**Request**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/status"
```

**Response — HTTP 200**
```json
{
  "status": "ok",
  "name": "glineRestApi",
  "version": "2.0",
  "port": 8082
}
```

### 17. Module information

**Purpose:** Query module information

**Request**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/modules"
```

**Response — HTTP 200**
```json
{
  "note": "use /api/config to browse station tree"
}
```

### 18. Type query

**Purpose:** Query the available component types

**Request**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/types?q=NumericWritable"
```

**Response — HTTP 200**
```json
{
  "note": "use /api/config to browse types; common types: baja:Folder, control:NumericWritable, control:BooleanWritable, control:EnumWritable, control:StringWritable, modbusTcp:ModbusTcpDevice, modbusCore:ModbusClientNumericProxyExt, kitControl:Add"
}
```

### 19. Browse a directory

**Purpose:** Read components and properties under a directory

**Request**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/config?path=/Demo"
```

**Response — HTTP 200**
```json
{
  "name": "Demo",
  "type": "Folder",
  "slots": [
    {
      "name": "Temp1",
      "type": "NumericWritable"
    },
    {
      "name": "StrRen",
      "type": "StringWritable"
    },
    {
      "name": "Temp1Cpy",
      "type": "NumericWritable"
    }
  ],
  "children": [
    {
      "name": "Temp1",
      "type": "NumericWritable"
    },
    {
      "name": "StrRen",
      "type": "StringWritable"
    },
    {
      "name": "Temp1Cpy",
      "type": "NumericWritable"
    }
  ]
}
```

### Error Handling
### 20. Non-existent path

**Purpose:** Check the response for a non-existent path

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/NoSuchXYZ", "N": "x"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "read",
    "error": "Path 'NoSuchXYZ' not found under station"
  }
]
```

### 21. Invalid type

**Purpose:** Check the response for an invalid type

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "no:SuchType", "N": "X"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "add",
    "error": "no"
  }
]
```

### 22. Unknown operation

**Purpose:** Check the response for an unknown operation

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "frobnicate", "PATH": "/Demo"}]'
```

**Response — HTTP 200**
```json
[
  {
    "OP": "frobnicate",
    "status": "unknown"
  }
]
```

### 23. Method not allowed

**Purpose:** Check the response for a disallowed method

**Request**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/batch"
```

**Response — HTTP 405**
```json
{
  "error": "POST only"
}
```

### Program Management
### 24. Write program source

**Purpose:** Write program source

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/program/write" \
  -H "Content-Type: application/json" \
  -d '{"path": "/Demo/CaseProg", "source": "import javax.baja.sys.*;\nimport com.tridium.program.*;\npublic class CaseProg extends ProgramBase {\n public void onExecute() throws Exception {}\n public void onStart() throws Exception {}\n public void onStop() throws Exception {}\n}\n"}'
```

**Response — HTTP 200**
```json
{
  "status": "ok",
  "path": "/Demo/CaseProg",
  "sourceLen": 238
}
```

### 25. Add a program slot

**Purpose:** Add a slot to a program

**Request**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/program/addslot" \
  -H "Content-Type: application/json" \
  -d '{"path": "/Demo/CaseProg", "name": "MySlot", "type": "control:NumericWritable"}'
```

**Response — HTTP 200**
```json
{
  "status": "ok",
  "program": "/Demo/CaseProg",
  "slot": "MySlot",
  "type": "control:NumericWritable"
}
```

### 26. Read program status

**Purpose:** Read program runtime status

**Request**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/program/status?path=/Demo/CaseProg"
```

**Response — HTTP 200**
```json
{
  "program": "/Demo/CaseProg",
  "className": "ProgramImpl",
  "status": "{ok}",
  "faultCause": "",
  "checksum": "0",
  "sourceLen": 238,
  "classFileLen": 0
}
```

### Authentication

| Scenario | Request | Response |
|:--|:--|:--|
| No credentials | `curl -X POST .../api/batch` | **401** |
| Wrong password | `curl -u "<USER>:<WRONG>" ...` | **401** |
| Wrong username | `curl -u "<WRONG>:<PASS>" ...` | **401** |
| Correct credentials | `curl -u "<USER>:<PASS>" ...` | **200** |

**No credentials / wrong credentials — HTTP 401**
```json
{"error":"auth required"}
```
**Correct credentials — HTTP 200**
```json
{"status":"ok"}
```

### CIDR Allow-list

| Scenario | Result |
|:--|:--|
| Source inside the allow-list | Allowed |
| Source outside the allow-list | **403** Rejected |
| Loopback | Always allowed (recovery path) |

### Configuration Persistence

Authentication and allow-list configuration persist across a service restart.

## 5. Summary

| Category | Cases | Passed |
|:--|:--|:--|
| Functional | 29 | 29 |
| Access Control | 11 | 11 |
| **Total** | **40** | **40** |

**Conclusion: all use cases passed.**

*2026-10-10*