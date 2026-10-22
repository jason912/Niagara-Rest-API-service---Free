# Documentation

This folder is split by **module edition**. Each edition has its own directory — the two
never share a document, so there is no risk of reading v1 behaviour as a v2 behaviour (or
the reverse).

```
docs/
├── README.md                          ← you are here
├── v1/                                ← niagaraRestApi (free, unauthenticated, port 8081)
│   ├── niagaraRestApi-v1-guide.pdf
│   └── niagaraRestApi-v1-comparison.pdf
└── v2/                                ← glineRestApi (on request, authenticated, port 8082)
    ├── glineRestApi-v2-guide.pdf
    ├── glineRestApi-v2-comparison.pdf
    ├── glineRestApi-v2-whatsnew.pdf
    ├── glineRestApi-v2-Test-Report.md
    ├── glineRestApi-v2.41-proxy-extensions.md
    ├── glineRestApi-v2-facets.md
    ├── glineRestApi-v2-facets.pdf
    └── glineRestApi-v2-signature-timestamp.md
```

## Which edition am I running?

Query the station's status endpoint — it names the module directly.

| Edition | Status response | Auth | Default port |
|:--|:--|:--|:--:|
| **v1** | `{"status":"ok","name":"niagaraRestApi","port":8081}` | none | 8081 |
| **v2** | `{"status":"ok","name":"glineRestApi","version":"2.x","port":8082}` | Basic Auth on every request | 8082 |

The two are **independent modules** and can run side by side on the same station — which is
why every document is scoped to exactly one edition.

## v1 — niagaraRestApi

| Document | What it covers |
|:--|:--|
| [`v1/niagaraRestApi-v1-guide.pdf`](v1/niagaraRestApi-v1-guide.pdf) | Overview, architecture, the 10 batch operations, endpoint reference, deployment, limitations |
| [`v1/niagaraRestApi-v1-comparison.pdf`](v1/niagaraRestApi-v1-comparison.pdf) | v1 against the other ways to talk to a station (built-in XML, built-in REST, third-party, analytics) |

**v1 in one line:** free, single `.jar`, no authentication, 10 batch component operations, real
`/api/modules` and `/api/types` listings. No BQL, no facet editing, no program endpoints,
no alarm/history query.

## v2 — glineRestApi

| Document | What it covers |
|:--|:--|
| [`v2/glineRestApi-v2-guide.pdf`](v2/glineRestApi-v2-guide.pdf) | Authentication, endpoints, 11 batch ops + BQL, program endpoints, facet editing, alarm/history extension setup, reading data over oBIX, limitations |
| [`v2/glineRestApi-v2-comparison.pdf`](v2/glineRestApi-v2-comparison.pdf) | v2 against the other channels, including the extension-automation capability |
| [`v2/glineRestApi-v2-whatsnew.pdf`](v2/glineRestApi-v2-whatsnew.pdf) | Release deck — what v2 adds over v1 |
| [`v2/glineRestApi-v2-Test-Report.md`](v2/glineRestApi-v2-Test-Report.md) | The 40 verified test cases (29 functional + 11 access-control) |

**v2 in one line:** v1 plus authentication, access control, BQL, program management, facet
editing, and alarm/history extension automation.

### v2.41 onwards

| Document | What it covers |
|:--|:--|
| [`v2/glineRestApi-v2.41-proxy-extensions.md`](v2/glineRestApi-v2.41-proxy-extensions.md) | Assembling a point's driver proxy extension at creation time with the `PROXY` field — the problem it solves, both operational notes (restart after creating the point, one SNMP network per station), the two SNMP network types, and a verified reference run with APC PDU OIDs |
| [`v2/glineRestApi-v2-facets.md`](v2/glineRestApi-v2-facets.md) · [PDF](v2/glineRestApi-v2-facets.pdf) | Editing facets over REST — the facet string, the two traps (`;` is the separator, a unit must be a `BUnit` not text), the unit names that resolve, and how to verify a facet write by its rendering |
| [`v2/glineRestApi-v2-signature-timestamp.md`](v2/glineRestApi-v2-signature-timestamp.md) | Signature timestamps — what "not timestamped" means, why it matters once the signing certificate expires, how to add and verify one, and why timestamping must be the last step (it changes the hashes) |

## AI automation lab

Worked through the API only — no desktop session — against a live station. Each guide ends in
an outside-client verification, so a claim can be re-tested instead of trusted.

| Document | What it covers |
|:--|:--|
| [`../niagara-ai-lab/README.md`](../niagara-ai-lab/README.md) | Index, the two-channel summary, the split into a server part and a client part, and the verification rules used throughout |
| [`../niagara-ai-lab/part1-server/README.md`](../niagara-ai-lab/part1-server/README.md) | **Part 1 — publishing.** Station point → protocol object: the three-step pattern, what all three protocols share, what differs |
| [`../niagara-ai-lab/VERIFIED.md`](../niagara-ai-lab/VERIFIED.md) | The checklist: every capability in the lab, ticked when it was built over the API and confirmed off-station, blank when it was not claimed |
| [`../niagara-ai-lab/part1-server/part1-publishing-points.pdf`](../niagara-ai-lab/part1-server/part1-publishing-points.pdf) | 9-page deck — object trees per protocol, the three-layer BACnet enable, the slots split across two channels, the Modbus slave `PROXY` step |
| [`../niagara-ai-lab/part1-server/niagara-bacnet-server-points.md`](../niagara-ai-lab/part1-server/niagara-bacnet-server-points.md) | Publishing station points as BACnet objects — enable order, `exportTable`, the three slots split across two channels, and the rename that follows an `objectId` write |
| [`../niagara-ai-lab/part1-server/niagara-obix-server-points.md`](../niagara-ai-lab/part1-server/niagara-obix-server-points.md) | Publishing station points over oBIX — the `point` slot, `/set/` writes, and which channel writes which step |
| [`../niagara-ai-lab/part1-server/niagara-modbus-server-points.md`](../niagara-ai-lab/part1-server/niagara-modbus-server-points.md) | Publishing station points as Modbus registers — `PROXY` at creation, `dataAddress`, `dataType`, and the working register exchange |
| [`../niagara-ai-lab/part2-client/README.md`](../niagara-ai-lab/part2-client/README.md) | **Part 2 — collecting.** The four-step client chain per protocol, the proxy-extension requirement, the slots to set on every point |
| [`../niagara-ai-lab/part2-client/part2-collecting-points.pdf`](../niagara-ai-lab/part2-client/part2-collecting-points.pdf) | 9-page deck — building the chain over the API, the client objects per protocol, the proxy slots, the two confirmation readings |
| [`../niagara-ai-lab/part2-client/niagara-client-collection.md`](../niagara-ai-lab/part2-client/niagara-client-collection.md) | Collecting from field devices — the four REST steps, the proxy slots per protocol, the two readings that confirm collection |

## A note on the two editions' differences

The editions differ in ways that matter when reading documentation, so they are never mixed:

| Behaviour | v1 | v2 |
|:--|:--|:--|
| `/api/modules` | Real module list with type counts | Informational stub — use `/api/config` |
| `/api/types` | Real type enumeration | Informational stub — use `/api/config` or BQL |
| `/api/config` `slots` member | Object keyed by slot name | Array of `{name, type}` |
| `/api/batch` without credentials | HTTP 200 | HTTP 401 |
| `/api/program/*` | HTTP 404 (does not exist) | Present |
| BQL | Not supported | Supported, returns a JSON table |
| Facet editing | Not supported | Supported (v2.4) |
| Batch operations | 10 | 11 + BQL |

## Support

Commercial customization, integration, or deployment support:

**Shanghai Gline Net Co.** · jason.zhang@gline-net.com · WhatsApp +86 138 0199 0968
