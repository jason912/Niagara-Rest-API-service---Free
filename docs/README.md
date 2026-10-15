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
| [`v2/glineRestApi-v2-guide.pdf`](v2/glineRestApi-v2-guide.pdf) | Authentication, endpoints, 11 batch ops + BQL, program endpoints, facet editing, alarm/history extension setup, reading data via Web Box, limitations |
| [`v2/glineRestApi-v2-comparison.pdf`](v2/glineRestApi-v2-comparison.pdf) | v2 against the other channels, including the extension-automation capability |
| [`v2/glineRestApi-v2-whatsnew.pdf`](v2/glineRestApi-v2-whatsnew.pdf) | Release deck — what v2 adds over v1 |
| [`v2/glineRestApi-v2-Test-Report.md`](v2/glineRestApi-v2-Test-Report.md) | The 40 verified test cases (29 functional + 11 access-control) |

**v2 in one line:** v1 plus authentication, access control, BQL, program management, facet
editing, and alarm/history extension automation.

### v2.41 onwards

| Document | What it covers |
|:--|:--|
| [`v2/glineRestApi-v2.41-proxy-extensions.md`](v2/glineRestApi-v2.41-proxy-extensions.md) | Assembling a point's driver proxy extension at creation time with the `PROXY` field — the problem it solves, both operational notes (restart after creating the point, one SNMP network per station), the two SNMP network types, and a verified reference run with APC PDU OIDs |
| [`v2/glineRestApi-v2-signature-timestamp.md`](v2/glineRestApi-v2-signature-timestamp.md) | Signature timestamps — what "not timestamped" means, why it matters once the signing certificate expires, how to add and verify one, and why timestamping must be the last step (it changes the hashes) |

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
