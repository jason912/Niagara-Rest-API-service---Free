# Signature timestamps — why Workbench says "not timestamped"

**Applies to every Gline Niagara module jar. First shipped timestamped in `glineRestApi` v2.41.1.**

---

## What "not timestamped" means

When you register a signed module jar, Workbench reports whether the signature
carries a **timestamp**:

| Workbench shows | Meaning |
|:--|:--|
| *(nothing)* | The signature has a valid RFC 3161 timestamp |
| **`not timestamped`** | The signature is valid **now**, but has no timestamp |

"Not timestamped" is not a warning that the jar is corrupt — the signature
verifies fine today. It is a statement about **the future**.

---

## Why it matters

A code-signing certificate has an expiry date. Without a timestamp, a signature
is only trusted while that certificate is still valid. The day the certificate
expires, **every jar signed without a timestamp starts failing validation**,
including jars already deployed in the field. You would have to re-sign and
re-deploy every module, on every station.

With a timestamp, a Time Stamping Authority (TSA) cryptographically records
*when* the jar was signed. A verifier can then confirm the signature was made
while the certificate was still current, so the signature **keeps validating
after the certificate expires** — indefinitely.

For modules deployed to customer sites, that difference is the whole ballgame:
one is a future outage across every installation, the other is not.

---

## How to add it

`jarsigner` takes the TSA URL with `-tsa`:

```bash
jarsigner -keystore "$KS" -storepass "$KEYSTORE_PASS" -keypass "$KEYSTORE_PASS" \
  -sigalg SHA256withRSA -digestalg SHA-256 \
  -tsa http://timestamp.digicert.com \
  "$JAR" "$ALIAS"
```

DigiCert's public TSA (`http://timestamp.digicert.com`) is free and needs no
account. On success `jarsigner` prints the timestamp's expiry:

```
时间戳将于 2031-11-10 到期。
```

Roughly five years out — that is the TSA response's own validity window, not a
limit on how long the signature stays good.

---

## How to verify

Two checks. Both must pass.

**1. The timestamp is present:**

```bash
jarsigner -verify -verbose -certs "$JAR" | grep -c -E "TimeStamping|Timestamp Responder"
```

A count greater than zero means a TSA counter-signature is embedded. You will
see entries like:

```
X.509, CN=DigiCert SHA256 RSA4096 Timestamp Responder 2026 1, O="DigiCert, Inc.", C=US
X.509, CN=DigiCert Trusted G4 TimeStamping RSA4096 SHA256 2025 CA1, O="DigiCert, Inc.", C=US
```

**2. The signing certificate is still the Gline one:**

```bash
unzip -p "$JAR" META-INF/GLINE.RSA > /tmp/gl.der
openssl pkcs7 -inform DER -in /tmp/gl.der -print_certs | openssl x509 -noout -subject -fingerprint -sha256
```

Expect `subject=CN=gline, O=gline, C=US` and SHA-256 fingerprint
`02:47:5E:30:B7:9A:81:19:AF:8B:C2:26:79:82:43:94:7C:D1:75:DC:61:3C:D8:B0:36:B1:ED:2F:6D:75:3F:BA`.

---

## Order of operations

**Timestamping is the last step before release, and it changes the jar bytes.**

Adding a timestamp rewrites `META-INF/` inside the jar, so **the MD5 and SHA-256
change**. Anything that already recorded the pre-timestamp hashes — release
notes, deployment records, upload manifests — is now stale.

Sequence:

1. Compile
2. Sign (with `-tsa`)
3. Verify both checks above
4. Record the hashes — **these are the release hashes**
5. Ship

Do not re-sign or touch the jar afterwards.

> This is exactly what happened between `glineRestApi` v2.41.0 and v2.41.1.
> v2.41.0 was signed without `-tsa`; shipping it would have left every
> installation with an expiring signature. v2.41.1 is the same code re-signed
> with the timestamp. Its hashes differ from v2.41.0 **by design** — the
> timestamp is the only functional change.

---

## Checking a deployed jar

The timestamp travels inside the jar, so an installed module's signature can be
verified in place:

```bash
curl -u "<USER>:<PASS>" http://<HOST>:<PORT>/api/status
{"status":"ok","name":"glineRestApi","version":"2.41.1","port":8082}
```

Then verify the jar copied into `<NIAGARA_HOME>/modules/` with the two checks
above. If check 1 returns zero, that installation is running an untimestamped
build.

---

Shanghai Gline Net Co. · jason.zhang@gline-net.com
