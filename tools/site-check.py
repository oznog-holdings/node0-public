#!/usr/bin/env python3
"""site-check: mechanical checks over a built Hugo site, before a person or a reviewer reads it.

    hugo -d /tmp/site && python3 tools/site-check.py /tmp/site [--base http://localhost:1313]

Reports, per built page: broken internal links and anchors; pages that no content links to
(nav and crumbs do not count); pages more than three clicks from the home page; the same
internal target linked more than once in one page's content (evidence links that prove
different claims may repeat, so read the list, do not chase it to zero); the same external
link repeated in one page; images without alt text; en or em dashes in page text; and /node0
headings that look Title Case. Exit 1 if any link is broken, any image lacks alt text, or any
dash is found; the rest is for reading. Written 20260928 for the full-site review.
"""
import os, re, sys, collections
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, unquote

import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("root", help="the built site (hugo -d)")
_ap.add_argument("--base", default="http://localhost:1313", help="the baseURL the site was built with")
_a = _ap.parse_args()
ROOT = _a.root
SITE = _a.base.rstrip("/")

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.links = []; s.imgs = []; s.ids = set(); s.depth_main = 0; s.in_main = False
        s.text = []; s.in_script = False; s.tagstack = []; s.headings = []; s.cur_h = None
    def handle_starttag(s, t, a):
        a = dict(a)
        if "id" in a: s.ids.add(a["id"])
        cls = a.get("class", "") or ""
        if t in ("script", "style"): s.in_script = True
        if t in ("h2", "h3"): s.cur_h = [t, ""]
        # content area: node0 article, updates article, prose sections
        if t == "div" and ("oz2-article" in cls): s.in_main = True
        if t == "a" and a.get("href"): s.links.append((a["href"], s.in_main))
        if t == "img": s.imgs.append(a)
    def handle_endtag(s, t):
        if t in ("script", "style"): s.in_script = False
        if t in ("h2", "h3") and s.cur_h: s.headings.append(tuple(s.cur_h)); s.cur_h = None
    def handle_data(s, d):
        if not s.in_script: s.text.append(d)
        if s.cur_h is not None: s.cur_h[1] += d

pages = {}
for dp, _, fs in os.walk(ROOT):
    for f in fs:
        if f == "index.html":
            rel = "/" + os.path.relpath(dp, ROOT).replace(os.sep, "/") + "/"
            rel = "/" if rel == "/./" else rel
            html = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
            if 'http-equiv="refresh"' in html[:600]:  # alias redirect
                continue
            p = P(); p.feed(html); pages[rel] = p

def norm(base, href):
    u = urljoin(SITE + base, href)
    pu = urlparse(u)
    if not u.startswith(SITE): return None, None
    path = unquote(pu.path)
    if not path.endswith("/") and "." not in os.path.basename(path): path += "/"
    return path, pu.fragment

broken, repeats, inbound, graph = [], [], collections.defaultdict(set), collections.defaultdict(set)
for base, p in pages.items():
    seen = collections.Counter()
    for href, in_main in p.links:
        if href.startswith(("mailto:", "tel:", "javascript:")): continue
        path, frag = norm(base, href)
        if path is None: continue
        target_file = os.path.join(ROOT, path.lstrip("/"))
        if path.endswith("/"):
            ok = path in pages or os.path.exists(os.path.join(target_file, "index.html"))
        else:
            ok = os.path.exists(target_file)
        if not ok: broken.append((base, href))
        elif frag and path in pages and frag not in pages[path].ids: broken.append((base, href + "  (no such anchor)"))
        if path in pages:
            graph[base].add(path)
            if in_main and path != base:
                inbound[path].add(base); seen[path] += 1
    for t, n in seen.items():
        if n > 1: repeats.append((base, t, n))

# external links repeated within one page's content
ext_repeats = []
for base, p in pages.items():
    c = collections.Counter(h.split("#")[0].rstrip("/") for h, m in p.links if m and h.startswith("http") and not h.startswith(SITE))
    for h, n in c.items():
        if n > 1: ext_repeats.append((base, h, n))

# depth from /node0/ and from /
def bfs(start):
    d = {start: 0}; q = [start]
    while q:
        x = q.pop(0)
        for y in graph[x]:
            if y not in d: d[y] = d[x] + 1; q.append(y)
    return d
d0 = bfs("/")
orphans = [p for p in pages if p not in inbound and p not in ("/",) and "/page/" not in p]
deep = [(p, d0.get(p)) for p in pages if d0.get(p) is None or d0.get(p) > 3]

noalt = [(b, i.get("src")) for b, p in pages.items() for i in p.imgs if not (i.get("alt") or "").strip()]
dash = []
for b, p in pages.items():
    t = "".join(p.text)
    for m in re.finditer("[\\u2013\\u2014]", t):
        dash.append((b, t[max(0, m.start()-40):m.end()+20].replace("\n", " ")))
titlecase = [(b, h) for b, p in pages.items() for lvl, h in p.headings
             if b.startswith("/node0/") and len(h.split()) > 2 and sum(w[:1].isupper() for w in h.split()[1:] if w.isalpha() and len(w) > 3) >= 2]

def show(name, rows, n=60):
    print(f"\n== {name}: {len(rows)}")
    for r in rows[:n]: print("  ", *r) if isinstance(r, tuple) else print("  ", r)
print(f"pages: {len(pages)}")
show("broken internal links", broken)
show("pages no content links point to (orphans; nav and crumbs excluded)", sorted(orphans))
show("more than 3 clicks from / or unreachable", sorted(deep, key=lambda x: str(x)))
show("same internal target linked more than once in one page's content", repeats)
show("same external link more than once in one page's content", ext_repeats)
show("images without alt text", noalt)
show("en or em dashes in page text", dash)
show("node0 headings that look Title Case", titlecase)
sys.exit(1 if broken or noalt or dash else 0)
