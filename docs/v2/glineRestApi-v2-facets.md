# Editing facets over REST

**Applies to `glineRestApi` v2.4 and later. Correct `units` handling requires v2.41.3 or later.**

This document covers one thing: writing a component's **facets** — units, precision,
range — from a single `mod` operation, and the two traps that make it fail.

---

## What facets are

`facets` is the slot that tells Niagara **how to display** a value: its unit, how many
decimal places, its allowed range. It is not the value itself, and it is not the
component's *device* facets (the ones on the proxy extension). It is the plain
`facets` slot present on any point.

```json
{"OP":"mod","PATH":"/Drivers/SnmpNetwork1/PDU_AP8858_180/points/Phase1_Voltage",
 "N":"facets",
 "V":"units=volt;precision=1;min=0;max=300"}
```

Response:

```json
{"OP":"mod","path":"/Drivers/SnmpNetwork1/PDU_AP8858_180/points/Phase1_Voltage","N":"facets","status":"ok"}
```

Read it back:

```json
{"OP":"read","PATH":"/Drivers/SnmpNetwork1/PDU_AP8858_180/points/Phase1_Voltage","N":"facets"}
```

```json
{"OP":"read","path":"/Drivers/SnmpNetwork1/PDU_AP8858_180/points/Phase1_Voltage","N":"facets",
 "value":"units=V,precision=1.00,min=0.00,max=300.00","status":"ok"}
```

Note the readback renders a **unit symbol** (`V`), not the name you wrote (`volt`).
That is the signature of a correctly-stored unit — see trap 1.

---

## The facet string

`V` is a `key=value` list. **Fields are separated by a semicolon (`;`).**

| Key | Type written | Accepted values |
|:--|:--|:--|
| `units` | `BUnit` | a Niagara unit name, e.g. `volt`, `ampere`, `watt`, `volt ampere`, `kilowatt hour`, `hertz`, `percent`, `celsius`, `day`, `hour`, `second` |
| `precision` | `BDouble` | decimal places, e.g. `0`, `1`, `2` |
| `min` | `BDouble` | numeric |
| `max` | `BDouble` | numeric |
| `range` / `enumrange` | `BEnumRange` | `A,B,C` or `0:A,1:B,2:C` |

Example — voltage with one decimal, 0…300 V:

```
units=volt;precision=1;min=0;max=300
```

Example — power factor, no unit, two decimals, 0…1:

```
precision=2;min=0;max=1
```

**Clearing a unit:** write `units=null` (or omit `units` entirely — the whole facet
value is replaced, not merged).

---

## Trap 1 — `,` is not a separator (v2.4 → v2.41.2)

Only `;` splits fields. A comma is **not** a separator, so this:

```
units=volt,precision=1,min=0,max=300
```

is parsed as **one** field — key `units`, value `volt,precision=1,min=0,max=300` — and
the entire string is stored as the unit. Every field after the first is lost, and the
unit is junk.

**Always use `;`:**

```
units=volt;precision=1;min=0;max=300
```

---

## Trap 2 — storing a unit as text (v2.4 → v2.41.2)

`units` is typed **`javax.baja.units.BUnit`** — an object — not a string. Through v2.41.2
the facet writer stored non-numeric facet values as `BString`, so `units` went in as
text. The readback looked plausible (`units=V`), but the slot held a `BString`.

The failure only appears when something *formats a number with that unit* — which is
exactly what Workbench does when it renders the point:

```
java.lang.ClassCastException: javax.baja.sys.BString cannot be cast to javax.baja.units.BUnit
    at javax.baja.sys.BDouble.toString(BDouble.java:393)
    at javax.baja.status.BStatusNumeric.valueToString(BStatusNumeric.java:148)
    at com.tridium.wiresheet.PropertyBarGlyph.updateValueString(PropertyBarGlyph.java:60)
```

**From v2.41.3**, `units` is resolved to a real `BUnit` via `BUnit.getUnit(name)`. A name
that does not resolve is rejected with a clear error instead of being stored:

```json
{"OP":"mod","error":"Unknown unit 'bogus'. Use a Niagara unit name, for example: volt, ampere, watt, kilowatt, volt ampere, kilowatt hour, hertz, percent, celsius, day, hour, second."}
```

**How to tell a good unit from a bad one:** read `facets` back. A real unit renders its
**symbol** (`V`, `A`, `W`, `VA`, `kW-hr`, `s`). Text renders whatever you typed
(`volt`).

**Clearing a unit written before v2.41.3:** re-write the facet string with the fields you
want and **no `units`** (or `units=null`). The facet value is replaced wholesale, so the
old text unit is dropped.

```
precision=1;min=0;max=300
```

---

## Common unit names

Names verified against the station's unit database:

| Quantity | Name to write | Renders as |
|:--|:--|:--|
| Voltage | `volt` | `V` |
| Current | `ampere` | `A` |
| Active power | `watt` | `W` |
| Active power (large) | `kilowatt` | `kW` |
| Apparent power | `volt ampere` | `VA` |
| Apparent power (large) | `kilovolt ampere` | `kVA` |
| Energy | `kilowatt hour` | `kW-hr` |
| Frequency | `hertz` | `Hz` |
| Ratio | `percent` | `%` |
| Temperature | `celsius`, `fahrenheit`, `kelvin` | `°C`, `°F`, `K` |
| Duration | `second`, `millisecond`, `minute`, `hour`, `day` | `s`, `ms`, `min`, `hr`, `day` |
| Data | `byte`, `bit` | `byte`, `bit` |

Two-word names are written with a **space**, not a hyphen: `volt ampere`, `kilowatt hour` —
not `volt-ampere` / `kilowatt-hour`. A name that is not in the database is rejected.

---

## Verifying the result

A facet write is only correct if the value *renders* with it. Check all three:

1. **Readback shows a symbol** — `units=V`, not `units=volt`:

   ```json
   {"OP":"read","PATH":".../points/Phase1_Voltage","N":"facets"}
   {"OP":"read","value":"units=V,precision=1.00,min=0.00,max=300.00","status":"ok"}
   ```

2. **The point's value reads without fault** — a bad unit faults on formatting:

   ```json
   {"OP":"read","PATH":".../points/Phase1_Voltage","N":"out"}
   {"OP":"read","value":"225.00 {ok}","status":"ok"}
   ```

3. **It renders in Workbench** — open the point on a wire sheet. A `ClassCastException`
   stack trace in the Workbench console means a text unit is still in the slot.

---

## Worked example — APC AP8858 PDU, 14 points

All written with `;`, all read back as symbols.

| Point | Facet string | Readback |
|:--|:--|:--|
| Phase1_Voltage | `units=volt;precision=1;min=0;max=300` | `units=V,precision=1.00,min=0.00,max=300.00` |
| Phase1_Current | `units=ampere;precision=1;min=0;max=20` | `units=A,…` |
| Phase1_PeakCurrent | `units=ampere;precision=1;min=0;max=20` | `units=A,…` |
| Phase1_Power | `units=watt;precision=0;min=0;max=4000` | `units=W,…` |
| Phase1_ApparentPower | `units=volt ampere;precision=0;min=0;max=4000` | `units=VA,…` |
| Phase1_PowerFactor | `precision=2;min=0;max=1` | `precision=2.00,min=0.00,max=1.00` |
| Phase1_LoadState | `precision=0;min=0;max=4` | `precision=0.00,…` |
| PDU_Power | `units=watt;precision=0;min=0;max=4000` | `units=W,…` |
| PDU_PeakPower | `units=watt;precision=0;min=0;max=4000` | `units=W,…` |
| PDU_Energy | `units=kilowatt hour;precision=1;min=0` | `units=kW-hr,precision=1.00,min=0.00` |
| PDU_ApparentPower | `units=volt ampere;precision=0;min=0;max=4000` | `units=VA,…` |
| PDU_PowerFactor | `precision=2;min=0;max=1` | `precision=2.00,min=0.00,max=1.00` |
| PDU_LoadState | `precision=0;min=0;max=4` | `precision=0.00,…` |
| SysUpTime | `units=second;precision=0;min=0` | `units=s,…` |

Points with real values then read as, for example, `225.00 {ok}` (V), `5.00 {ok}` (A),
`32557.00 {ok}` (kW-hr).

---

## Summary

| Rule | Detail |
|:--|:--|
| Field separator | **`;`** — a comma is not a separator |
| `units` | a Niagara unit name; resolved to `BUnit` from v2.41.3 |
| Two-word units | space, not hyphen (`volt ampere`) |
| Clearing a unit | omit `units`, or `units=null`; the facet value is replaced wholesale |
| Verified by | readback renders a **symbol**, and `out` reads without fault |
| Pre-v2.41.3 | units were stored as text and crashed Workbench on render — upgrade, or leave units unset |

---

Shanghai Gline Net Co. · jason.zhang@gline-net.com
