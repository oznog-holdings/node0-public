#!/usr/bin/env python3
"""gen.py: draw the node0 diagrams as SVG from the data files in data/diagrams/.

    python3 tools/diagrams/gen.py            # every diagram
    python3 tools/diagrams/gen.py stack      # one

Each diagram is generated from a data file, never drawn by hand, so it is regenerated at the
next capture. The data files and the generated SVGs go through the publication gate like
every other file; the generator itself does no sanitizing.
The SVG is inlined into the page by the n0-diagram shortcode, so its text is readable by an
agent and indexable; the data file beside it is the version an agent actually wants.

Kinds:
  stack        the eleven layers (one full drawing, plus one per layer with that layer lit)
  flow         columns of boxes with arrows between them (backup, models, alerts, topology,
               power, ladder); edge styles: solid, dashed (a check or a control path), gated
               (an arrow that only passes with permission, drawn red)
  elevations   the four racks from the inventory export, front and rear
"""
import sys, os, yaml, html, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data", "diagrams")
OUT = os.path.join(ROOT, "static", "images", "node0", "diagrams")

C = dict(g0="#0D0D0D", g1="#121212", g2="#181818", g3="#232323", line="#2A2A2A",
         t1="#ECEAE6", t2="#A8A5A0", t3="#918E88", red="#A22F2E", red3="#EA7170",
         wash="rgba(162,47,46,.18)")
FONT = "'Space Grotesk', system-ui, -apple-system, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"


def esc(s):
    return html.escape(str(s), quote=True)


def svg_open(w, h, title, desc, uid):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" '
            f'aria-labelledby="{uid}-t {uid}-d" font-family="{FONT}">\n'
            f'<title id="{uid}-t">{esc(title)}</title><desc id="{uid}-d">{esc(desc)}</desc>\n'
            f'<defs><marker id="{uid}-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,1 L9,5 L0,9 z" fill="{C["t3"]}"/></marker>'
            f'<marker id="{uid}-ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,1 L9,5 L0,9 z" fill="{C["red3"]}"/></marker></defs>\n'
            f'<rect width="{w}" height="{h}" fill="{C["g0"]}"/>\n')


def box(x, y, w, h, lit=False, dim=False, dashed=False, fill=None):
    fill = fill or (C["wash"] if lit else C["g2"])
    stroke = C["red"] if lit else C["line"]
    extra = ' stroke-dasharray="4 4"' if dashed else ''
    op = ' opacity="0.45"' if dim else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1"{extra}{op}/>\n'


def text(x, y, s, size=14, fill=None, weight=400, anchor="start", mono=False, dim=False):
    ff = f' font-family="{MONO}"' if mono else ''
    op = ' opacity="0.45"' if dim else ''
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill or C["t1"]}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{ff}{op}>{esc(s)}</text>\n')


def wrap(s, width):
    return textwrap.wrap(str(s), width) or [""]


# ---------------------------------------------------------------- stack
_clip = [0]


def layer_cell(x, y, w, h, L, lit, dim):
    _clip[0] += 1; cid = f"c{_clip[0]}"
    s = f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w - 6}" height="{h}"/></clipPath>\n'
    s += box(x, y, w, h, lit=lit, dim=dim)
    s += f'<g clip-path="url(#{cid})">\n'
    s += text(x + 12, y + 22, f"{L['n']}", size=12, fill=C["red3"], mono=True, dim=dim)
    s += text(x + 34, y + 23, L["name"], size=15, weight=600, dim=dim)
    # the gist wraps to the cell (about 6.2 px a character at 12 px) and takes at most two lines
    for i, line in enumerate(wrap(L["gist"], max(16, int((w - 20) / 6.2)))[:2]):
        s += text(x + 12, y + 43 + i * 15, line, size=12, fill=C["t3"], dim=dim)
    s += '</g>\n'
    return s


def draw_stack(d, current=None):
    layers = {L["slug"]: L for L in d["layers"]}
    W, H = 760, 440
    pad = 18
    frame_slug, under_slug, beside_slug = d["frame"], d["under"], d["beside"]
    lit = lambda slug: current == slug
    dim = lambda slug: current is not None and current != slug
    s = svg_open(W, H, d["title"], "The eleven layers of Node0 drawn as a stack: site as the frame, power under everything, operations beside everything, and the layers that rest on each other in bands from the edge and fabric up to services, agents and observability.", uid=f"stack-{current or 'all'}")
    fx, fy, fw, fh = pad, pad, W - 2 * pad, H - 2 * pad - 62
    s += box(fx, fy, fw, fh, lit=lit(frame_slug), dim=dim(frame_slug), dashed=True)
    Ls = layers[frame_slug]
    s += text(fx + 12, fy + 20, f"{Ls['n']}", size=12, fill=C["red3"], mono=True, dim=dim(frame_slug))
    s += text(fx + 34, fy + 21, f"{Ls['name']}: {Ls['gist']}", size=13, weight=600, dim=dim(frame_slug))
    bw = 150
    bx, by, bh = fx + fw - bw - 12, fy + 34, fh - 46
    Lb = layers[beside_slug]
    s += box(bx, by, bw, bh, lit=lit(beside_slug), dim=dim(beside_slug))
    s += text(bx + 12, by + 22, f"{Lb['n']}", size=12, fill=C["red3"], mono=True, dim=dim(beside_slug))
    s += text(bx + 34, by + 23, Lb["name"], size=15, weight=600, dim=dim(beside_slug))
    for i, line in enumerate(("deploy branch, CI,", "the inventory", "as authority")):
        s += text(bx + 12, by + 46 + i * 16, line, size=12, fill=C["t3"], dim=dim(beside_slug))
    ax, aw = fx + 12, fw - bw - 36
    n_bands = len(d["bands"]); gap = 10
    band_h = (bh - gap * (n_bands - 1)) // n_bands
    y = by
    for band in d["bands"]:
        n = len(band); cw = (aw - gap * (n - 1)) // n; x = ax
        for slug in band:
            s += layer_cell(x, y, cw, band_h, layers[slug], lit(slug), dim(slug)); x += cw + gap
        y += band_h + gap
    for i in range(n_bands - 1):
        yy = by + (i + 1) * (band_h + gap) - gap // 2
        s += f'<line x1="{ax + aw // 2}" y1="{yy - 3}" x2="{ax + aw // 2}" y2="{yy + 3}" stroke="{C["t3"]}" stroke-width="1" opacity="0.6"/>\n'
    ux, uy, uw, uh = pad, H - pad - 52, W - 2 * pad, 52
    Lu = layers[under_slug]
    s += box(ux, uy, uw, uh, lit=lit(under_slug), dim=dim(under_slug))
    s += text(ux + 12, uy + 22, f"{Lu['n']}", size=12, fill=C["red3"], mono=True, dim=dim(under_slug))
    s += text(ux + 34, uy + 23, Lu["name"], size=15, weight=600, dim=dim(under_slug))
    s += text(ux + 12, uy + 42, Lu["gist"] + ". Everything above is fed by it; the shutdown design is its own layer's.", size=12, fill=C["t3"], dim=dim(under_slug))
    s += text(W - pad, H - 4, "rests on: read upward. Generated from data/diagrams/stack.yaml.", size=10, fill=C["t3"], anchor="end", mono=True)
    return s + "</svg>\n"


# ---------------------------------------------------------------- flow
def draw_flow(d, name):
    cols = d["columns"]; ncol = len(cols)
    W, pad = 980, 18
    col_gap = 64 if any(e.get("label") for e in d.get("edges", [])) else 34
    col_w = (W - 2 * pad - col_gap * (ncol - 1)) // ncol
    chars = max(18, int(col_w / 6.4))
    head_h = 30
    layout, col_heights = {}, []
    for ci, col in enumerate(cols):
        y = pad + head_h + 8
        for nd in col["nodes"]:
            lines = wrap(nd.get("sub", ""), chars)
            tl = wrap(nd["label"], max(14, int(col_w / 7.6)))
            h = 12 + 17 * len(tl) + 15 * len(lines) + (6 if lines and lines[0] else 0)
            layout[nd["id"]] = dict(ci=ci, x=pad + ci * (col_w + col_gap), y=y, w=col_w, h=h, lines=lines, tl=tl, nd=nd)
            y += h + 26
        col_heights.append(y)
    body_h = max(col_heights)
    note_lines = []
    for n in d.get("notes", []):
        note_lines += wrap(n, int((W - 2 * pad) / 6.2)); note_lines.append("")
    H = body_h + 10 + 15 * len(note_lines) + 22
    uid = f"flow-{name}"
    s = svg_open(W, H, d["title"], d.get("desc", ""), uid)
    for ci, col in enumerate(cols):
        x = pad + ci * (col_w + col_gap)
        s += text(x, pad + 16, col["name"], size=11, fill=C["red3"], mono=True)
        s += f'<line x1="{x}" y1="{pad + 22}" x2="{x + col_w}" y2="{pad + 22}" stroke="{C["line"]}"/>\n'
    labels = []
    for e in d.get("edges", []):
        a, b = layout[e["from"]], layout[e["to"]]
        style = e.get("style", "solid")
        stroke = C["red3"] if style == "gated" else C["t3"]
        dash = ' stroke-dasharray="5 4"' if style in ("dashed", "gated") else ''
        marker = f'url(#{uid}-ar)' if style == "gated" else f'url(#{uid}-a)'
        if a["ci"] < b["ci"]:
            x1, y1, x2, y2 = a["x"] + a["w"], a["y"] + a["h"] / 2, b["x"], b["y"] + b["h"] / 2
            mx = (x1 + x2) / 2; path = f'M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}'
            if b["ci"] - a["ci"] > 1:   # spans a column: route under the columns in between, never through their boxes
                lane = max(L["y"] + L["h"] for L in layout.values() if a["ci"] < L["ci"] < b["ci"]) + 16
                xa, xb = a["x"] + a["w"] + col_gap / 2, b["x"] - col_gap / 2
                path = f'M{x1},{y1} C{xa},{y1} {xa},{lane} {xa + 12},{lane} L{xb - 12},{lane} C{xb},{lane} {xb},{y2} {x2},{y2}'
        elif a["ci"] > b["ci"]:
            x1, y1, x2, y2 = a["x"], a["y"] + a["h"] / 2, b["x"] + b["w"], b["y"] + b["h"] / 2
            mx = (x1 + x2) / 2; path = f'M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}'
        else:
            x1 = x2 = a["x"] + a["w"] / 2
            y1, y2 = (a["y"] + a["h"], b["y"]) if a["y"] < b["y"] else (a["y"], b["y"] + b["h"])
            path = f'M{x1},{y1} L{x2},{y2}'
        s += f'<path d="{path}" fill="none" stroke="{stroke}" stroke-width="1.2"{dash} marker-end="{marker}" opacity="0.9"/>\n'
        if e.get("label"):
            lw = len(e["label"]) * 6.2 + 8
            if a["ci"] != b["ci"] and lw <= col_gap - 6:
                labels.append(((x1 + x2) / 2, (y1 + y2) / 2 - 5, e["label"], style))
            else:   # too wide for the gap, or a vertical edge: sit under the source box
                labels.append((a["x"] + 6 + lw / 2, a["y"] + a["h"] + 13, e["label"], style))
    for nid, L in layout.items():
        nd = L["nd"]
        s += box(L["x"], L["y"], L["w"], L["h"], lit=nd.get("lit", False))
        for i, line in enumerate(L["tl"]):
            s += text(L["x"] + 10, L["y"] + 19 + i * 17, line, size=13, weight=600)
        ty = L["y"] + 19 + (len(L["tl"]) - 1) * 17
        for i, line in enumerate(L["lines"]):
            s += text(L["x"] + 10, ty + 17 + i * 15, line, size=11, fill=C["t3"])
    for lx, ly, label, style in labels:      # edge labels on top of everything, on a ground-coloured backing
        lw = len(label) * 6.2 + 8
        s += f'<rect x="{lx - lw / 2}" y="{ly - 10}" width="{lw}" height="14" fill="{C["g0"]}" opacity="0.92"/>\n'
        s += text(lx, ly + 1, label, size=10, fill=C["red3"] if style == "gated" else C["t2"], anchor="middle", mono=True)
    y = body_h + 8
    s += f'<line x1="{pad}" y1="{y}" x2="{W - pad}" y2="{y}" stroke="{C["line"]}"/>\n'
    y += 18
    for line in note_lines:
        if line: s += text(pad, y, line, size=11, fill=C["t2"])
        y += 15
    s += text(W - pad, H - 6, f"Generated from data/diagrams/{name}.yaml.", size=10, fill=C["t3"], anchor="end", mono=True)
    return s + "</svg>\n"


# ---------------------------------------------------------------- elevations
def draw_elevations(d, name):
    racks = d["racks"]
    U, rack_w, gap, pad, top = 11, 200, 26, 18, 40
    maxu = max(r["height"] for r in racks)
    shelf_lines = max(len(wrap(", ".join(r["shelf_mounted"]) or "none", 30)) for r in racks)
    W = pad * 2 + len(racks) * rack_w + (len(racks) - 1) * gap
    H = int(top + maxu * U + 40 + 14 + 13 * shelf_lines + 30)
    s = svg_open(W, H, "Rack elevations", "The four racks drawn from the inventory: every positioned device by rack unit, front and rear faces, with the shelf-mounted machines listed under each rack. Rack 0 is shelf-mounted throughout.", "elev")
    for ri, r in enumerate(racks):
        x = pad + ri * (rack_w + gap)
        ytop = top + (maxu - r["height"]) * U
        s += text(x, top - 12, f"{r['name']}  ({r['height']}U)", size=13, weight=600)
        s += box(x, ytop, rack_w, r["height"] * U, dashed=True)
        if not r["positioned"]:
            s += text(x + rack_w / 2, ytop + r["height"] * U / 2, "no rack positions recorded", size=9, fill=C["t3"], anchor="middle", mono=True)
        for u in range(1, r["height"] + 1, 6):
            yy = ytop + (r["height"] - u + 1) * U
            s += text(x - 4, yy + 3, str(u), size=8, fill=C["t3"], anchor="end", mono=True)
        for it in r["positioned"]:
            yy = ytop + (r["height"] - it["u"] - it["h"] + 1) * U
            hh = it["h"] * U
            rear = it.get("face") == "rear"
            overlap = any(o is not it and o.get("face") != it.get("face") and o["u"] < it["u"] + it["h"] and o["u"] + o["h"] > it["u"] for o in r["positioned"])
            if rear:
                fx, fw = x + rack_w // 2 + 2, rack_w // 2 - 4
            else:
                fx, fw = x + 2, (rack_w // 2 - 4 if overlap else rack_w - 4)
            s += box(fx, yy + 1, fw, max(hh - 2, 6), fill=C["g3"] if rear else C["g2"])
            s += text(fx + 5, yy + hh / 2 + 3.5, it["name"], size=8.5 if hh < 14 else 10, weight=600)
        s += text(x + rack_w, ytop + r["height"] * U + 12, "left: front  right: rear", size=8, fill=C["t3"], anchor="end", mono=True)
        y = top + maxu * U + 30
        s += text(x, y, "shelf-mounted:", size=10, fill=C["red3"], mono=True)
        for i, line in enumerate(wrap(", ".join(r["shelf_mounted"]) or "none", 30)):
            s += text(x, y + 14 + i * 13, line, size=10, fill=C["t2"])
    s += text(W - pad, H - 6, f"Generated from data/diagrams/elevations.yaml ({d['source']}).", size=10, fill=C["t3"], anchor="end", mono=True)
    return s + "</svg>\n"


def main(names):
    os.makedirs(OUT, exist_ok=True)
    for name in names:
        d = yaml.safe_load(open(os.path.join(DATA, name + ".yaml")))
        written = []
        if name == "stack":
            open(os.path.join(OUT, "stack.svg"), "w").write(draw_stack(d)); written.append("stack.svg")
            for L in d["layers"]:
                open(os.path.join(OUT, f"stack-{L['slug']}.svg"), "w").write(draw_stack(d, current=L["slug"])); written.append(f"stack-{L['slug']}.svg")
        elif name == "elevations":
            open(os.path.join(OUT, "elevations.svg"), "w").write(draw_elevations(d, name)); written.append("elevations.svg")
        else:
            open(os.path.join(OUT, f"{name}.svg"), "w").write(draw_flow(d, name)); written.append(f"{name}.svg")
        print(f"{name}: {len(written)} file(s)")


if __name__ == "__main__":
    names = sys.argv[1:] or [f[:-5] for f in sorted(os.listdir(DATA)) if f.endswith(".yaml")]
    main(names)
