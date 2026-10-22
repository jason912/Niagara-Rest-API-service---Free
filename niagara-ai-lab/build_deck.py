#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a slide-format PDF (16:9) for the Niagara protocol capability matrix.

No LibreOffice on this host, so the deck is drawn directly with reportlab:
one 960x540 pt page per slide, same layout a PPT would produce.
"""
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "niagara-protocol-capability-matrix.pdf")

LAT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LATB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LATM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
CJK = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"

pdfmetrics.registerFont(TTFont("Lat", LAT))
pdfmetrics.registerFont(TTFont("LatB", LATB))
pdfmetrics.registerFont(TTFont("LatM", LATM))
pdfmetrics.registerFont(TTFont("CJK", CJK))

W, H = 960.0, 540.0
NAVY = (0x11 / 255, 0x24 / 255, 0x39 / 255)
ACCENT = (0xE1 / 255, 0x89 / 255, 0x2E / 255)
INK = (0x1B / 255, 0x25 / 255, 0x32 / 255)
MUTED = (0x6B / 255, 0x78 / 255, 0x85 / 255)
GRID = (0xD5 / 255, 0xDC / 255, 0xE4 / 255)
ALT = (0xF4 / 255, 0xF6 / 255, 0xF9)
HDRBG = (0x2C / 255, 0x4A / 255, 0x66 / 255)
YES = (0x1B / 255, 0x7F / 255, 0x45 / 255)
NO = (0xB0 / 255, 0x30 / 255, 0x28 / 255)
PART = (0xB9 / 255, 0x7C / 255, 0x00 / 255)

LEFT = 48.0
RIGHT = W - 48.0
BODY_TOP = H - 108.0
BODY_BOT = 62.0


def runs(text):
    """Split text into (font, chunk) runs: ASCII/Latin vs CJK glyphs."""
    out, cur, cur_lat = [], "", None
    for ch in text:
        lat = ord(ch) < 0x2000
        if cur_lat is None or lat == cur_lat:
            cur += ch
            cur_lat = lat
        else:
            out.append(("Lat" if cur_lat else "CJK", cur))
            cur, cur_lat = ch, lat
    if cur:
        out.append(("Lat" if cur_lat else "CJK", cur))
    return out


def tw(text, size, bold=False):
    w = 0.0
    for f, chunk in runs(text):
        if f == "Lat" and bold:
            f = "LatB"
        w += pdfmetrics.stringWidth(chunk, f, size)
    return w


def draw_text(c, x, y, text, size, color=INK, bold=False):
    c.setFillColorRGB(*color)
    for f, chunk in runs(text):
        if f == "Lat" and bold:
            f = "LatB"
        c.setFont(f, size)
        c.drawString(x, y, chunk)
        x += pdfmetrics.stringWidth(chunk, f, size)
    return x


def wrap(text, size, maxw, bold=False):
    """Greedy wrap that respects mixed-script widths."""
    words, lines, cur = text.split(" "), [], ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if tw(trial, size, bold) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def header(c, title, kicker=None):
    c.setFillColorRGB(*NAVY)
    c.rect(0, H - 84, W, 84, stroke=0, fill=1)
    c.setFillColorRGB(*ACCENT)
    c.rect(0, H - 87, W, 3, stroke=0, fill=1)
    ty = H - 46 if kicker else H - 54
    draw_text(c, LEFT, ty, title, 21, (1, 1, 1), bold=True)
    if kicker:
        draw_text(c, LEFT, H - 68, kicker, 10.5, (0.72, 0.79, 0.86))


def footer(c, n, total):
    c.setStrokeColorRGB(*GRID)
    c.setLineWidth(0.6)
    c.line(LEFT, 42, RIGHT, 42)
    draw_text(c, LEFT, 28, "box  ·  oBIX  ·  REST API v2      Niagara 4.14.0.162, verified 2026-10-21",
              8.2, MUTED)
    s = "%d / %d" % (n, total)
    draw_text(c, RIGHT - tw(s, 8.4), 28, s, 8.4, MUTED)


def cell_color(v):
    v = v.strip()
    if v.lower().startswith("yes"):
        return YES
    if v.lower().startswith("no"):
        return NO
    if v.lower() == "partial":
        return PART
    return INK


def table(c, x, y, widths, rows, size=10.0, lead=13.0, head_size=10.0,
          pad=7.0, mono_cols=(), status_cols=()):
    """rows[0] is the header. Returns the y of the bottom edge."""
    # vertical extents
    heights = []
    for i, row in enumerate(rows):
        n = 1
        for j, cell in enumerate(row):
            lines = wrap(str(cell), size if i else head_size, widths[j] - 2 * pad,
                         bold=(i == 0))
            n = max(n, len(lines))
        heights.append(n * (lead if i else head_size + 3) + 2 * pad)

    cy = y
    for i, row in enumerate(rows):
        h = heights[i]
        if i == 0:
            c.setFillColorRGB(*HDRBG)
        elif i % 2 == 0:
            c.setFillColorRGB(*ALT)
        else:
            c.setFillColorRGB(1, 1, 1)
        c.rect(x, cy - h, sum(widths), h, stroke=0, fill=1)

        cx = x
        for j, cell in enumerate(row):
            s = str(cell)
            bold = (i == 0)
            fs = head_size if i == 0 else size
            color = (1, 1, 1) if i == 0 else (cell_color(s) if j in status_cols else INK)
            lines = wrap(s, fs, widths[j] - 2 * pad, bold=bold)
            ty = cy - pad - fs
            for ln in lines:
                draw_text(c, cx + pad, ty, ln, fs, color, bold=bold)
                ty -= lead
            cx += widths[j]
        c.setStrokeColorRGB(*GRID)
        c.setLineWidth(0.5)
        c.line(x, cy - h, x + sum(widths), cy - h)
        cy -= h

    # vertical rules
    c.setStrokeColorRGB(*GRID)
    cx = x
    for j, wd in enumerate(widths):
        cx += wd
        if j < len(widths) - 1:
            c.line(cx, y, cx, cy)
    c.setStrokeColorRGB(*HDRBG)
    c.setLineWidth(0.9)
    c.rect(x, cy, sum(widths), y - cy, stroke=1, fill=0)
    return cy


def bullets(c, x, y, items, size=11, lead=17, gap=6, marker="—"):
    for it in items:
        draw_text(c, x, y, marker, size, ACCENT, bold=True)
        lines = wrap(it, size, RIGHT - x - 24)
        ty = y
        for ln in lines:
            draw_text(c, x + 20, ty, ln, size, INK)
            ty -= lead
        y = ty - gap
    return y


def note(c, x, y, w, text, size=9.6, fill=(0xFD / 255, 0xF4 / 255, 0xE6 / 255)):
    lines = wrap(text, size, w - 24)
    h = len(lines) * (size + 4) + 16
    c.setFillColorRGB(*fill)
    c.roundRect(x, y - h, w, h, 4, stroke=0, fill=1)
    c.setFillColorRGB(*ACCENT)
    c.rect(x, y - h, 3, h, stroke=0, fill=1)
    ty = y - 10 - size
    for ln in lines:
        draw_text(c, x + 14, ty, ln, size, INK)
        ty -= size + 4
    return y - h


# ----------------------------------------------------------------- slide 1
def s1(c):
    c.setFillColorRGB(*NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColorRGB(*ACCENT)
    c.rect(LEFT, 372, 64, 4, stroke=0, fill=1)
    draw_text(c, LEFT, 396, "Niagara 4 point deployment", 13, (0.72, 0.79, 0.86))
    draw_text(c, LEFT, 316, "Publishing and Consuming Points", 34, (1, 1, 1), bold=True)
    draw_text(c, LEFT, 272, "Capability matrix across box, oBIX and REST API v2", 17,
              (0.80, 0.86, 0.92))
    c.setStrokeColorRGB(0.28, 0.38, 0.48)
    c.setLineWidth(0.8)
    c.line(LEFT, 232, RIGHT, 232)
    draw_text(c, LEFT, 206, "Verified on Niagara 4.14.0.162  ·  server exports and client collection",
              11, (0.66, 0.74, 0.82))
    draw_text(c, LEFT, 186, "Every result confirmed by an independent client off-station",
              11, (0.66, 0.74, 0.82))
    draw_text(c, LEFT, 84, "Shanghai Gline Net Co., Ltd.", 12, (0.85, 0.89, 0.93), bold=True)
    draw_text(c, LEFT, 66, "@jason912   ·   jason.zhang@gline-net.com", 10.5,
              (0.62, 0.70, 0.78))


# ----------------------------------------------------------------- slide 2
def s2(c):
    header(c, "Three channels, three different jobs",
           "No channel replaces another — each owns a step the others cannot perform")
    cards = [
        ("box", "In-station JavaScript",
         "The station's own web app, driven through require(['baja!']). "
         "Runs as the logged-in session; no separate port.",
         ["clear a priority slot to a true null",
          "BoxFile / file space",
          "BoxTable from BQL"]),
        ("oBIX", "HTTP + Basic Auth",
         "Standard oBIX endpoint at /obix/config. Same server publishes exports "
         "and answers queries.",
         ["bind BOrd slots (pointOrd, point)",
          "write DynamicEnum (escaped name)",
          "history and alarm queries"]),
        ("REST API v2", "HTTP + Basic + CIDR",
         "glineRestApi module. Batch of 11 operations in one POST, "
         "atomic per request.",
         ["create / copy / rename / delete",
          "link, invoke, facets",
          "history and alarm extensions"]),
    ]
    cw = (RIGHT - LEFT - 2 * 14) / 3.0
    x = LEFT
    for name, sub, body, owns in cards:
        c.setFillColorRGB(*ALT)
        c.roundRect(x, 150, cw, 268, 6, stroke=0, fill=1)
        c.setFillColorRGB(*NAVY)
        c.roundRect(x, 380, cw, 38, 6, stroke=0, fill=1)
        c.setFillColorRGB(*NAVY)
        c.rect(x, 380, cw, 8, stroke=0, fill=1)
        draw_text(c, x + 14, 394, name, 15, (1, 1, 1), bold=True)
        y = 356
        for ln in wrap(sub, 9.8, cw - 28):
            draw_text(c, x + 14, y, ln, 9.8, ACCENT, bold=True)
            y -= 13
        y -= 6
        for ln in wrap(body, 10.2, cw - 28):
            draw_text(c, x + 14, y, ln, 10.2, INK)
            y -= 14
        y -= 8
        draw_text(c, x + 14, y, "Uniquely owns", 9.6, MUTED, bold=True)
        y -= 15
        for it in owns:
            draw_text(c, x + 14, y, "·", 10.2, ACCENT, bold=True)
            for k, ln in enumerate(wrap(it, 10.0, cw - 46)):
                draw_text(c, x + 26, y, ln, 10.0, INK)
                if k < 2:
                    y -= 13
            y -= 15
        x += cw + 14
    note(c, LEFT, 132, RIGHT - LEFT,
         "Rule of thumb: if a step touches a component's structure, REST does it. "
         "If it touches a typed slot the REST encoder cannot express, oBIX does it. "
         "If it needs a real null or a file, box does it.")


# ----------------------------------------------------------------- slide 3
def s3(c):
    header(c, "Capability matrix — component structure",
           "Yes / No / Partial, each cell measured against an independent client")
    rows = [
        ["Capability", "box", "oBIX", "REST v2", "Note"],
        ["Read component tree and point values", "Yes", "Yes", "Yes", "all three, different shapes"],
        ["Write a point value", "Yes", "Yes", "Yes", "oBIX must POST to /set/"],
        ["Write an existing slot", "Yes", "Yes", "Yes", "oBIX PUT <value>"],
        ["Create a component", "No", "No", "Yes", "oBIX: BadUriErr, every variant"],
        ["Copy a component", "Yes", "No", "Yes", "box: transfer.copy"],
        ["Rename a component", "No", "No", "Yes", "REST: new name goes in NEW"],
        ["Delete a component", "Yes", "No", "Yes", "box: transfer.delete"],
        ["Link two components", "Yes", "No", "Yes", "box: makeLink"],
        ["Invoke an action", "Yes", "No", "Yes", "action name in N"],
        ["Add history extension", "No", "No", "Yes", "three ext types"],
        ["Add alarm extension", "No", "No", "Yes", "alarm:AlarmSourceExt"],
        ["Edit facets", "No", "No", "Yes", "v2.4 and later"],
        ["BQL query", "Yes", "No", "Yes", "box returns BoxTable"],
    ]
    widths = [280, 82, 82, 90, 330]
    table(c, LEFT, BODY_TOP, widths, rows, size=10.2, lead=13.4, status_cols=(1, 2, 3))


# ----------------------------------------------------------------- slide 4
def s4(c):
    header(c, "Capability matrix — data, edge cases, gaps",
           "The four rows at the bottom are the ones that decide a design")
    rows = [
        ["Capability", "box", "oBIX", "REST v2", "Note"],
        ["Read history records", "Yes", "Yes", "No", "oBIX has the query endpoints"],
        ["Read alarm records", "Yes", "Yes", "No", "oBIX: ~alarmQuery"],
        ["File space (file:^)", "Yes", "No", "Yes", "REST is sandboxed"],
        ["Write proxy in1–in16", "Yes", "No", "Yes", "oBIX set node is inert"],
        ["Write proxy out", "Yes", "No", "Yes", "bypasses the priority chain"],
        ["Write a BOrd slot", "No", "Yes", "No", "only oBIX PUT <uri> — one channel"],
        ["Write DynamicEnum", "No", "Yes", "No", "escaped name from ~range — one channel"],
        ["Clear a slot to true null", "Yes", "No", "No", "only box — one channel"],
        ["Write a NaN instead of null", "—", "—", "Yes", "stored as nan, still {overridden}"],
    ]
    widths = [280, 82, 82, 90, 330]
    table(c, LEFT, BODY_TOP, widths, rows, size=10.2, lead=13.4, status_cols=(1, 2, 3))
    note(c, LEFT, 172, RIGHT - LEFT,
         "Three capabilities have exactly one channel each. A workflow that needs any of them "
         "cannot be built on a single channel — plan for two, and test the boundary between them.",
         size=10.2)


# ----------------------------------------------------------------- slide 5
def s5(c):
    header(c, "Publishing a station point outward — four protocols, three steps",
           "\"Add a point\" is never one operation; the step that fails is usually the second")
    rows = [
        ["Protocol", "1 · Create the object", "2 · Bind source / address", "3 · Public identity", "Channels"],
        ["BACnet export", "REST add  bacnet:*Descriptor", "pointOrd  →  oBIX PUT <uri>", "objectId  →  REST mod", "REST + oBIX"],
        ["oBIX export", "REST add  obixDriver:ObixExport", "point  →  oBIX PUT <uri>", "binding is the identity", "REST + oBIX"],
        ["Modbus TCP slave", "REST cp  (add leaves NullProxyExt)", "dataAddress  →  REST mod", "binding is the identity", "REST only"],
        ["SNMP agent", "REST add  SnmpExportFolder first", "objectIdentifier  →  REST mod", "OID is the identity", "REST only"],
    ]
    widths = [148, 246, 214, 156, 100]
    table(c, LEFT, BODY_TOP, widths, rows, size=9.8, lead=14.6, status_cols=())
    y = 250
    draw_text(c, LEFT, y, "Why step 2 breaks", 13, NAVY, bold=True)
    bullets(c, LEFT, y - 24, [
        "BOrd slots reject REST strings outright — BString cannot be cast to BOrd. box reads them, writes them silently to no effect.",
        "Modbus slave points cannot be created with add: the result carries NullProxyExt and has no dataAddress slot at all.",
        "A BACnet descriptor renames itself the moment objectId is written — analogValue:100, not the name you typed.",
    ], size=10.6, lead=15.5)


# ----------------------------------------------------------------- slide 6
def s6(c):
    header(c, "The two traps that cost the most time",
           "Both present as {stale} with an empty faultCause — no error anywhere")
    # left column
    c.setFillColorRGB(*ALT)
    c.roundRect(LEFT, 268, (RIGHT - LEFT - 16) / 2, 220, 6, stroke=0, fill=1)
    x2 = LEFT + (RIGHT - LEFT - 16) / 2 + 16
    c.setFillColorRGB(*ALT)
    c.roundRect(x2, 268, (RIGHT - LEFT - 16) / 2, 220, 6, stroke=0, fill=1)

    cw = (RIGHT - LEFT - 16) / 2
    draw_text(c, LEFT + 16, 456, "Trap 1 · dataType travels with the copy", 12.4, NAVY, bold=True)
    y = 434
    for ln in wrap("cp copies every slot, including the register interpretation. An integer "
                   "register read through Float Type decodes two registers as one IEEE-754 "
                   "value: the point reads 0.00 with no fault and no hint.", 10.2, cw - 32):
        draw_text(c, LEFT + 16, y, ln, 10.2, INK)
        y -= 14
    y -= 6
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(LEFT + 16, y - 62, cw - 32, 62, 3, stroke=0, fill=1)
    for ln, col in [("out = 0.00 {stale}     faultCause = \"\"", INK),
                    ("readValue = 0.00 {ok}  enabled = true", INK)]:
        draw_text(c, LEFT + 26, y - 22, ln, 9.6, col)
        y -= 16
    y -= 10
    draw_text(c, LEFT + 16, y - 2, "Fix: set proxyExt/dataType = integerType over oBIX.",
              10.0, YES, bold=True)

    draw_text(c, x2 + 16, 456, "Trap 2 · the status facets lie", 12.4, NAVY, bold=True)
    y = 434
    for ln in wrap("Four independent signals report success on a point that never receives "
                   "data. None of them is a measurement of collection.", 10.2, cw - 32):
        draw_text(c, x2 + 16, y, ln, 10.2, INK)
        y -= 14
    y -= 4
    for sig, why in [("device {ok}", "driver accepted the config"),
                     ("health = Ok", "PingMonitor ran, separate path"),
                     ("readValue {ok}", "a value object exists"),
                     ("readStatus okNotActive", "\"not active\" is literal")]:
        draw_text(c, x2 + 16, y, sig, 9.6, NO, bold=True)
        draw_text(c, x2 + 16 + 120, y, why, 9.6, MUTED)
        y -= 14
    draw_text(c, x2 + 16, y - 4, "Fix: read pollScheduler and change the value outside.",
              10.0, YES, bold=True)

    note(c, LEFT, 248, RIGHT - LEFT,
         "An empty faultCause is the normal appearance of a wrongly decoded point and of a point "
         "that is not polled at all. The two are distinguishable only by counters — and by an "
         "external value change.", size=10.2)


# ----------------------------------------------------------------- slide 7
def s7(c):
    header(c, "Is the client collecting? Two counters settle it",
           "Read pollScheduler twice, ten seconds apart, before touching any configuration")
    rows = [
        ["Reading", "Value", "Conclusion"],
        ["pollScheduler.totalPolls", "increasing", "scheduler running — look downstream (decode, mapping)"],
        ["pollScheduler.totalPolls", "frozen", "nothing is being polled at all"],
        ["pollScheduler.normalCount", "current = 1", "a point is in the queue"],
        ["pollScheduler.normalCount", "current = 0", "the queue is empty — not \"polling failed\""],
    ]
    table(c, LEFT, BODY_TOP - 6, [250, 130, 484], rows, size=10.4, lead=14,
          status_cols=())
    y = 300
    draw_text(c, LEFT, y, "Same station, same minute", 12.4, NAVY, bold=True)
    rows2 = [
        ["Network", "Scheduler class", "totalPolls", "normalCount"],
        ["SnmpNetwork1", "NPollScheduler", "122 over 17s", "current = 1"],
        ["ModbusTcpNetwork", "BasicPollScheduler", "0 over 0ms", "current = 0"],
    ]
    bot = table(c, LEFT, y - 16, [200, 220, 180, 190], rows2, size=10.2, lead=14)
    note(c, LEFT, bot - 18, RIGHT - LEFT,
         "normalCount = 0 is not a failure of polling. It means no point was ever registered. "
         "Read both numbers before changing anything: they split the problem into "
         "\"queue empty\" and \"poll runs but the value is wrong\".", size=10.0)


# ----------------------------------------------------------------- slide 8
def s8(c):
    header(c, "The only proof: change the value outside",
           "Status facets, health monitors and copied values can all fake a healthy point")
    c.setFillColorRGB(*NAVY)
    c.roundRect(LEFT, 226, RIGHT - LEFT, 196, 6, stroke=0, fill=1)
    draw_text(c, LEFT + 22, 394, "Modbus slave loop on one station", 12.6, (1, 1, 1), bold=True)
    draw_text(c, LEFT + 22, 374, "external master writes, client point on the same station follows",
              10.2, (0.70, 0.78, 0.86))
    y = 344
    for seq, val in [("FC06 write HR[1] = 5555", "5555.00 {ok}"),
                     ("FC06 write HR[1] = 6666", "6666.00 {ok}"),
                     ("FC06 write HR[1] = 4321", "4321.00 {ok}")]:
        draw_text(c, LEFT + 22, y, seq, 10.6, (0.86, 0.91, 0.95))
        draw_text(c, LEFT + 40, y - 15, "→", 10.6, ACCENT)
        draw_text(c, LEFT + 62, y - 15, "point C1 = " + val, 10.6, (1, 1, 1), bold=True)
        y -= 42
    draw_text(c, LEFT + 380, 344, "totalPolls climbing throughout", 10.2, (0.86, 0.91, 0.95))
    draw_text(c, LEFT + 380, 329, "slave currentConnections = 1", 10.2, (0.86, 0.91, 0.95))
    draw_text(c, LEFT + 380, 314, "three distinct values, each reflected", 10.2, (0.86, 0.91, 0.95))

    y = 196
    draw_text(c, LEFT, y, "What this rules out in one step", 12.4, NAVY, bold=True)
    bullets(c, LEFT, y - 22, [
        "A duplicated device that shows data proves nothing — copied points carry the source's last value, and a clone looks healthy while collecting nothing.",
        "A working neighbour exonerates the network, the driver module and the protocol at once: same second, same network, one device collecting and one not.",
        "Only a value change at the far end separates \"polled and decoded\" from \"looks plausible\".",
    ], size=10.6, lead=15.5)


# ----------------------------------------------------------------- slide 9
def s9(c):
    header(c, "Choosing a channel by task",
           "Ordered so the first channel named is the one to reach for")
    rows = [
        ["Task", "First choice", "Why", "Fallback"],
        ["Create or tear down components", "REST v2", "only channel with add / remove", "—"],
        ["Build points in bulk from a template", "REST v2", "one POST, atomic batch", "box transfer.copy"],
        ["Bind a source point to an export", "oBIX", "only channel that writes BOrd", "—"],
        ["Set a NIC / IP / adapter dropdown", "oBIX", "only channel that writes DynamicEnum", "—"],
        ["Clear a priority slot properly", "box", "only channel that writes a true null", "—"],
        ["Read trend or alarm data", "oBIX", "query endpoints exist", "box BoxTable"],
        ["Ad-hoc table query", "REST v2 BQL or box", "both return real rows", "—"],
        ["Move or copy files", "box / REST", "BoxFile or sandboxed file:^", "—"],
        ["Diagnose collection", "REST v2 (read-only)", "scheduler + poll config, no side effects", "—"],
    ]
    widths = [270, 150, 300, 144]
    table(c, LEFT, BODY_TOP, widths, rows, size=10.0, lead=13.6)


# ----------------------------------------------------------------- slide 10
def s10(c):
    header(c, "Summary", "What holds, and what stays open")
    rows = [
        ["Established", "Single-channel", "Two-channel", "Open"],
        ["Read and write of point values", "BOrd slot binding", "BACnet export", "Three Modbus client devices"],
        ["Component lifecycle over REST", "DynamicEnum writes", "oBIX export", "Non-zero consecutivePointsToPoll"],
        ["Extensions, facets, BQL over REST", "true-null slot clearing", "Modbus slave points", "BACnet client coverage"],
        ["History and alarms over oBIX", "", "", ""],
    ]
    table(c, LEFT, BODY_TOP - 4, [246, 190, 160, 268], rows, size=9.8, lead=13.2)
    y = 250
    draw_text(c, LEFT, y, "Two rules worth carrying into any deployment", 12.4, NAVY, bold=True)
    bullets(c, LEFT, y - 24, [
        "Verify with an independent client, from another host, using a value you changed yourself. Everything inside the station can report success.",
        "When one device collects and an identical one beside it does not, stop testing the protocol — the difference is in the objects, not the driver.",
    ], size=10.6, lead=15.5)
    c.setStrokeColorRGB(*GRID)
    c.line(LEFT, 120, RIGHT, 120)
    draw_text(c, LEFT, 96, "Shanghai Gline Net Co., Ltd.   ·   @jason912   ·   "
              "jason.zhang@gline-net.com", 10.5, MUTED)
    draw_text(c, LEFT, 78, "Companion documents: niagara-bacnet-server-points.md, "
              "niagara-modbus-server-points.md, niagara-obix-server-points.md, "
              "niagara-client-collection.md", 9.6, MUTED)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    c.setTitle("Niagara 4 Point Deployment - Capability Matrix")
    c.setAuthor("Shanghai Gline Net Co., Ltd.")
    c.setSubject("box / oBIX / REST API v2 capability matrix for Niagara 4.14")

    pages = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
    for i, fn in enumerate(pages, 1):
        fn(c)
        if i > 1:
            footer(c, i, len(pages))
        c.showPage()
    c.save()
    print("wrote", OUT, os.path.getsize(OUT), "bytes,", len(pages), "pages")


if __name__ == "__main__":
    main()
