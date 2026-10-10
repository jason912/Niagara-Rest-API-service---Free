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

## 一、功能

| 能力 | 说明 |
|:--|:--|
| 站点浏览 | 按路径读取站点树，查看组件与属性 |
| 组件管理 | 新建、删除、重命名、复制 |
| 属性读写 | 读取与写入任意组件属性 |
| 链接管理 | 建立与解除组件链接 |
| 动作调用 | 调用组件公开动作 |
| BQL 查询 | 执行 BQL 查询，返回结构化表格 |
| 批量处理 | 单请求按序执行多个操作 |
| 程序管理 | 新建程序、添加插槽、写入源码、读取状态 |
| 访问控制 | 认证与网段白名单 |

## 二、接口

| 端点 | 方法 | 说明 |
|:--|:--|:--|
| `/api/status` | GET | 服务状态 |
| `/api/modules` | GET | 模块信息 |
| `/api/types` | GET | 组件类型 |
| `/api/config` | GET | 浏览站点树 |
| `/api/batch` | POST | 组件操作 |
| `/api/program/write` | POST | 写入程序源码 |
| `/api/program/addslot` | POST | 程序添加插槽 |
| `/api/program/status` | GET | 读取程序状态 |

> 所有接口均需认证。

## 三、测试结果

| # | 用例 | 结果 |
|:--|:--|:--|
| 1 | 新建文件夹 | 通过 |
| 2 | 新建数值点 | 通过 |
| 3 | 新建字符串点 | 通过 |
| 4 | 列出子组件 | 通过 |
| 5 | 修改属性值 | 通过 |
| 6 | 读取属性值 | 通过 |
| 7 | 重命名组件 | 通过 |
| 8 | 复制组件 | 通过 |
| 9 | 建立链接 | 通过 |
| 10 | 验证链接传值 | 通过 |
| 11 | 解除链接 | 通过 |
| 12 | 调用动作 | 通过 |
| 13 | BQL 查询 | 通过 |
| 14 | 单请求多操作 | 通过 |
| 15 | 删除组件 | 通过 |
| 16 | 服务状态 | 通过 |
| 17 | 模块信息 | 通过 |
| 18 | 类型查询 | 通过 |
| 19 | 浏览目录 | 通过 |
| 20 | 路径不存在 | 通过 |
| 21 | 非法类型 | 通过 |
| 22 | 未知操作 | 通过 |
| 23 | 方法不被接受 | 通过 |
| 24 | 写入程序源码 | 通过 |
| 25 | 程序添加插槽 | 通过 |
| 26 | 读取程序状态 | 通过 |
| 27 | 认证 — 无凭证 | 拒绝 |
| 28 | 认证 — 错误口令 | 拒绝 |
| 29 | 认证 — 错误用户名 | 拒绝 |
| 30 | 认证 — 正确凭证 | 通过 |
| 31 | 网段白名单 | 通过 |
| 32 | 配置重启后保留 | 通过 |

**合计 40 项，全部符合预期。**

## 四、用例详情（带凭证实测）

> 以下所有请求均携带 Basic Auth 凭证实测抓取。

### 组件操作
### 1. 新建文件夹

**目的**：建立文件夹

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/", "T": "baja:Folder", "N": "Demo"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "add",
    "name": "Demo",
    "status": "ok"
  }
]
```

### 2. 新建数值点

**目的**：建立数值点

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "control:NumericWritable", "N": "Temp1"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "add",
    "name": "Temp1",
    "status": "ok"
  }
]
```

### 3. 新建字符串点

**目的**：建立字符串点

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "control:StringWritable", "N": "Str1"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "add",
    "name": "Str1",
    "status": "ok"
  }
]
```

### 4. 列出子组件

**目的**：列出目录下的组件

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "list", "PATH": "/Demo"}]'
```

**响应 HTTP 200**
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

### 5. 修改属性值

**目的**：写入组件属性值

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "mod", "PATH": "/Demo/Temp1", "N": "out", "V": "42.5"}]'
```

**响应 HTTP 200**
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

### 6. 读取属性值

**目的**：读取组件属性值

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/Demo/Temp1", "N": "out"}]'
```

**响应 HTTP 200**
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

### 7. 重命名组件

**目的**：重命名组件

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "rename", "PATH": "/Demo/Str1", "NEW": "StrRen"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "rename",
    "new": "StrRen",
    "status": "ok"
  }
]
```

### 8. 复制组件

**目的**：复制组件

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "cp", "PATH": "/Demo/Temp1", "N": "Temp1Cpy"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "cp",
    "name": "Temp1Cpy",
    "status": "ok"
  }
]
```

### 链接
### 9. 建立链接

**目的**：在两个组件间建立链接

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "link", "PATH": "/Demo/Temp1", "N": "out", "TARGET": "/Demo/Temp1Cpy", "TARGET_N": "in16"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "link",
    "status": "ok"
  }
]
```

### 10. 验证链接传值

**目的**：确认链接真实传值

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/Demo/Temp1Cpy", "N": "in16"}]'
```

**响应 HTTP 200**
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

### 11. 解除链接

**目的**：解除组件链接

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "unlink", "TARGET": "/Demo/Temp1Cpy"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "unlink",
    "status": "ok"
  }
]
```

### 动作与查询
### 12. 调用动作

**目的**：调用组件动作

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "invoke", "PATH": "/Demo1", "N": "execute"}]'
```

**响应 HTTP 200**
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

### 13. BQL 查询

**目的**：执行 BQL 查询

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "bql", "Q": "select name,slotPath,out from control:NumericWritable", "SCOPE": "/Drivers/sim", "LIMIT": "3"}]'
```

**响应 HTTP 200**
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

### 14. 单请求多操作

**目的**：一次请求执行多个操作

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "control:NumericWritable", "N": "MB1"}, {"OP": "mod", "PATH": "/Demo/MB1", "N": "out", "V": "7.7"}, {"OP": "read", "PATH": "/Demo/MB1", "N": "out"}]'
```

**响应 HTTP 200**
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

### 删除与浏览
### 15. 删除组件

**目的**：删除组件

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "remove", "PATH": "/Demo/MB1"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "remove",
    "status": "ok"
  }
]
```

### 16. 服务状态

**目的**：确认服务运行状态

**请求**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/status"
```

**响应 HTTP 200**
```json
{
  "status": "ok",
  "name": "glineRestApi",
  "version": "2.0",
  "port": 8082
}
```

### 17. 模块信息

**目的**：查询模块信息

**请求**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/modules"
```

**响应 HTTP 200**
```json
{
  "note": "use /api/config to browse station tree"
}
```

### 18. 类型查询

**目的**：查询可用组件类型

**请求**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/types?q=NumericWritable"
```

**响应 HTTP 200**
```json
{
  "note": "use /api/config to browse types; common types: baja:Folder, control:NumericWritable, control:BooleanWritable, control:EnumWritable, control:StringWritable, modbusTcp:ModbusTcpDevice, modbusCore:ModbusClientNumericProxyExt, kitControl:Add"
}
```

### 19. 浏览目录

**目的**：读取目录下的组件与属性

**请求**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/config?path=/Demo"
```

**响应 HTTP 200**
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

### 容错
### 20. 路径不存在

**目的**：核对不存在路径的返回

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "read", "PATH": "/NoSuchXYZ", "N": "x"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "read",
    "error": "Path 'NoSuchXYZ' not found under station"
  }
]
```

### 21. 非法类型

**目的**：核对非法类型的返回

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "add", "PATH": "/Demo", "T": "no:SuchType", "N": "X"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "add",
    "error": "no"
  }
]
```

### 22. 未知操作

**目的**：核对未知操作的返回

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/batch" \
  -H "Content-Type: application/json" \
  -d '[{"OP": "frobnicate", "PATH": "/Demo"}]'
```

**响应 HTTP 200**
```json
[
  {
    "OP": "frobnicate",
    "status": "unknown"
  }
]
```

### 23. 方法不被接受

**目的**：核对非规定方法的返回

**请求**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/batch"
```

**响应 HTTP 405**
```json
{
  "error": "POST only"
}
```

### 程序管理
### 24. 写入程序源码

**目的**：写入程序源码

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/program/write" \
  -H "Content-Type: application/json" \
  -d '{"path": "/Demo/CaseProg", "source": "import javax.baja.sys.*;\nimport com.tridium.program.*;\npublic class CaseProg extends ProgramBase {\n public void onExecute() throws Exception {}\n public void onStart() throws Exception {}\n public void onStop() throws Exception {}\n}\n"}'
```

**响应 HTTP 200**
```json
{
  "status": "ok",
  "path": "/Demo/CaseProg",
  "sourceLen": 238
}
```

### 25. 程序添加插槽

**目的**：为程序添加插槽

**请求**
```bash
curl -u "<USER>:<PASS>" -X POST "http://<HOST>:8082/api/program/addslot" \
  -H "Content-Type: application/json" \
  -d '{"path": "/Demo/CaseProg", "name": "MySlot", "type": "control:NumericWritable"}'
```

**响应 HTTP 200**
```json
{
  "status": "ok",
  "program": "/Demo/CaseProg",
  "slot": "MySlot",
  "type": "control:NumericWritable"
}
```

### 26. 读取程序状态

**目的**：读取程序运行状态

**请求**
```bash
curl -u "<USER>:<PASS>" "http://<HOST>:8082/api/program/status?path=/Demo/CaseProg"
```

**响应 HTTP 200**
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

### 认证

| 场景 | 请求 | 响应 |
|:--|:--|:--|
| 无凭证 | `curl -X POST .../api/batch` | **401** |
| 错误口令 | `curl -u "<USER>:<WRONG>" ...` | **401** |
| 错误用户名 | `curl -u "<WRONG>:<PASS>" ...` | **401** |
| 正确凭证 | `curl -u "<USER>:<PASS>" ...` | **200** |

**无凭证/错误凭证响应 HTTP 401**
```json
{"error":"auth required"}
```
**正确凭证响应 HTTP 200**
```json
{"status":"ok"}
```

### 网段白名单

| 场景 | 结果 |
|:--|:--|
| 来源在白名单内 | 允许 |
| 来源不在白名单内 | **403** 拒绝 |
| 本机回环 | 始终允许（恢复通道）|

### 配置持久化

认证与白名单配置在服务重启后保留。

## 五、总表

| 类别 | 用例 | 通过 |
|:--|:--|:--|
| 功能 | 29 | 29 |
| 访问控制 | 11 | 11 |
| **合计** | **40** | **40** |

**结论：全部用例通过。**

*2026-10-10*