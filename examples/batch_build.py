#!/usr/bin/env python3
"""Build a small point set on a Niagara station through the REST API, then verify it.

One HTTP request carries the whole build. This is the shape that saves time when you
have hundreds of points to create: describe the work as data, send it once, read it back.

Standard library only. Python 3.8+.

Dry run (no station contacted, prints the JSON bodies):

    python3 batch_build.py --host <HOST> --user <USER> --pass <PASS> --dry-run

Real run against a station, cleaning up afterwards:

    python3 batch_build.py --host <HOST> --user <USER> --pass <PASS> --cleanup

The folder name defaults to `RestApiDemo`. Adjust `--folder` to avoid collisions.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request

NUMERIC = "control:NumericWritable"


def request(host: str, port: int, path: str, body, user: str, password: str, dry: bool):
    url = f"http://{host}:{port}{path}"
    payload = json.dumps(body, indent=2) if body is not None else None

    if dry:
        method = "POST" if payload is not None else "GET"
        print(f"\n$ curl -s -u '<USER>:<PASS>' -X {method} {url}" +
              (f" \\\n    -H 'Content-Type: application/json' \\\n    -d '<PAYLOAD>'"
               if payload is not None else ""))
        if payload is not None:
            print("\n<PAYLOAD>")
            print(payload)
        return None

    data = payload.encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET")
    req.add_header("Content-Type", "application/json")
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        sys.exit(f"HTTP {exc.code} from {path}: {detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"Cannot reach {url}: {exc.reason}")


def build_ops(folder: str):
    """The build, expressed as data: create, write, link, then read back."""
    base = f"/{folder}"
    return [
        {"OP": "add", "PATH": "/", "T": "baja:Folder", "N": folder},
        {"OP": "add", "PATH": base, "T": NUMERIC, "N": "ZoneTemp"},
        {"OP": "add", "PATH": base, "T": NUMERIC, "N": "ZoneSetpoint"},
        {"OP": "add", "PATH": base, "T": NUMERIC, "N": "ValveCommand"},
        {"OP": "mod", "PATH": f"{base}/ZoneTemp", "N": "out", "V": "21.5"},
        {"OP": "mod", "PATH": f"{base}/ZoneSetpoint", "N": "out", "V": "22.0"},
        {"OP": "mod", "PATH": f"{base}/ZoneSetpoint", "N": "facets", "V": "units=celsius;precision=1"},
        # A link, not a copy: ZoneSetpoint.out drives ValveCommand.in16 and converts types.
        {"OP": "link", "PATH": f"{base}/ZoneSetpoint", "N": "out",
         "TARGET": f"{base}/ValveCommand", "TARGET_N": "in16"},
        {"OP": "read", "PATH": f"{base}/ZoneTemp", "N": "out"},
        {"OP": "read", "PATH": f"{base}/ValveCommand", "N": "in16"},
        {"OP": "list", "PATH": base},
    ]


def report(results, folder: str) -> int:
    """Print what came back. Returns a shell exit code."""
    if results is None:
        return 0

    print(f"{'OP':10} {'RESULT':12} DETAIL")
    print("-" * 72)
    failures = 0
    for item in results:
        op = str(item.get("OP", "?"))
        status = str(item.get("status", "?"))
        detail = (item.get("value")
                  or item.get("name")
                  or item.get("path")
                  or (f"{item.get('count')} rows" if "count" in item else "")
                  or item.get("error", ""))
        if status != "ok":
            failures += 1
        print(f"{op:10} {status:12} {detail}")

    # A link is only real if the target reports a value from its source.
    linked = [r for r in results if r.get("OP") == "read" and r.get("N") == "in16"]
    if linked:
        value = str(linked[0].get("value", ""))
        print(f"\nlink check: ValveCommand.in16 = {value}")
        if "{ok}" not in value:
            print("  the link did not resolve — check that both slots share a type "
                  "or that a conversion link was created")
            failures += 1

    print(f"\nfolder /{folder} now holds "
          f"{len(results[-1].get('children', [])) if results else 0} children")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True, help="station address")
    ap.add_argument("--port", type=int, default=8082, help="8082 for v2 (default), 8081 for v1")
    ap.add_argument("--user", default="", help="v2 username")
    ap.add_argument("--pass", dest="password", default="", help="v2 password")
    ap.add_argument("--folder", default="RestApiDemo", help="folder to create")
    ap.add_argument("--dry-run", action="store_true", help="print requests, contact nothing")
    ap.add_argument("--cleanup", action="store_true", help="remove the folder afterwards")
    args = ap.parse_args()

    if args.port == 8082 and not args.dry_run and not (args.user and args.password):
        ap.error("v2 needs --user and --pass")

    if not args.dry_run:
        status = request(args.host, args.port, "/api/status", None,
                         args.user, args.password, False)
        print(f"station: {status.get('name')} {status.get('version')} "
              f"on port {status.get('port')}")

    results = request(args.host, args.port, "/api/batch", build_ops(args.folder),
                      args.user, args.password, args.dry_run)
    code = report(results, args.folder)

    if args.cleanup:
        print(f"\nremoving /{args.folder}")
        request(args.host, args.port, "/api/batch",
                [{"OP": "remove", "PATH": f"/{args.folder}"}],
                args.user, args.password, args.dry_run)

    return code


if __name__ == "__main__":
    sys.exit(main())
