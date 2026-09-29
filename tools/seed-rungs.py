#!/usr/bin/env python3
"""seed-rungs: generate the Seed's rung pages from the product repository.

    python3 tools/seed-rungs.py [--src ../node0-seed] [--check]

The rung READMEs in node0-seed (rungs/<n>-<name>/README.md) are the single source; this
writes content/node0/seed/rung-<n>.md for each, and copies the photos they use into
static/images/node0/seed/. Edit a rung in node0-seed, never the generated page.

  - The README's H1 becomes the page title; its "In plain terms" paragraph becomes the
    description (the page's lede) and leaves the body.
  - Links into the repository become links to it on GitHub; links between rungs become
    links between the rung pages.
  - A markdown image on a line of its own becomes the n0-figure shortcode.
  - Every page ends with links to the rung before and after it.

--check writes nothing and exits 1 if any generated page or photo would change, so the
publishing gate can refuse a stale page.
"""
import argparse, os, re, shutil, subprocess, sys

REPO_URL = "https://github.com/oznog-holdings/node0-seed"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "content", "node0", "seed")
IMG_OUT = os.path.join(ROOT, "static", "images", "node0", "seed")
WEIGHT0 = 10  # after the summary page and the design page


def rung_id(dirname):
    return dirname.split("-", 1)[0]          # "4b-models" -> "4b"


def order_key(rid):
    m = re.match(r"(\d+)([a-z]*)", rid)
    return (int(m.group(1)), m.group(2))


def param(s):
    """A shortcode parameter: a raw string unless it holds a backtick."""
    if "`" not in s:
        return "`" + s + "`"
    return '"' + s.replace('"', "&quot;") + '"'


def yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def plain(md):
    """Markdown to one line of plain text, for the description."""
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    s = re.sub(r"[*_`]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def convert(text, rdir, ids, images, src):
    lines = text.split("\n")
    title = None
    body = []
    for l in lines:
        if title is None and l.startswith("# "):
            title = l[2:].strip()
            continue
        body.append(l)
    if title is None:
        sys.exit(f"seed-rungs: {rdir}: no H1 title")
    md = "\n".join(body).strip("\n")

    # the description: the plain-terms paragraph, else the first paragraph
    m = re.search(r"\*\*In plain terms\.\*\*\s*(.+?)(?:\n\s*\n|$)", md, re.S)
    first = next((p for p in md.split("\n\n") if p.strip() and not p.lstrip().startswith(("#", "!", "{{"))), "")
    desc = plain(m.group(1)) if m else plain(first)
    if m:
        md = (md[:m.start()] + md[m.end():]).lstrip("\n")   # the lede says it; the body does not repeat it

    # photos on a line of their own
    def fig(mm):
        alt, path, cap = mm.group(1), mm.group(2), mm.group(3) or ""
        name = os.path.basename(path)
        images.add(name)
        out = f"{{{{< n0-figure src={param('seed/' + name)} alt={param(alt)}"
        if cap:
            out += f" caption={param(cap)}"
        return out + " >}}"
    md = re.sub(r'^!\[([^\]]*)\]\((\.\./\.\./images/[^ )]+)(?: "([^"]*)")?\)[ \t]*$', fig, md, flags=re.M)
    if re.search(r"!\[[^\]]*\]\(", md):
        sys.exit(f"seed-rungs: {rdir}: an image that is not on a line of its own, or not under images/")

    # links
    def link(mm):
        label, target = mm.group(1), mm.group(2)
        if re.match(r"[a-z]+:|#|/", target):
            return mm.group(0)
        frag = ""
        if "#" in target:
            target, frag = target.split("#", 1)
            frag = "#" + frag
        rel = os.path.normpath(os.path.join("rungs", rdir, target))
        parts = rel.split(os.sep)
        if parts[0] == "rungs" and len(parts) >= 2 and parts[1] in ids and (len(parts) == 2 or parts[2] == "README.md"):
            return f"[{label}](../rung-{ids[parts[1]]}/{frag})"
        if rel.startswith(".."):
            sys.exit(f"seed-rungs: {rdir}: a link outside the repository: {target}")
        full = os.path.join(src, rel)
        if not os.path.exists(full):
            sys.exit(f"seed-rungs: {rdir}: a link to {target}, which is not in the repository")
        kind = "tree" if os.path.isdir(full) else "blob"
        return f"[{label}]({REPO_URL}/{kind}/main/{rel}{'/' if kind == 'tree' and not rel.endswith('/') else ''}{frag})"
    md = re.sub(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)", link, md)
    return title, desc, md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "..", "node0-seed"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    src = os.path.abspath(a.src)
    rungs_dir = os.path.join(src, "rungs")
    dirs = sorted((d for d in os.listdir(rungs_dir) if os.path.isfile(os.path.join(rungs_dir, d, "README.md"))),
                  key=lambda d: order_key(rung_id(d)))
    ids = {d: rung_id(d) for d in dirs}
    try:
        rev = subprocess.run(["git", "-C", src, "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", src, "status", "--porcelain", "rungs", "images"], capture_output=True, text=True).stdout.strip()
        if dirty:
            rev += ", with uncommitted changes"
    except (subprocess.CalledProcessError, FileNotFoundError):
        rev = "unknown"

    pages, images = [], set()
    for d in dirs:
        text = open(os.path.join(rungs_dir, d, "README.md"), encoding="utf-8").read()
        pages.append((d,) + convert(text, d, ids, images, src))

    stale = []
    def emit(path, content):
        old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old != content:
            stale.append(os.path.relpath(path, ROOT))
            if not a.check:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

    for i, (d, title, desc, md) in enumerate(pages):
        rid = ids[d]
        nav = []
        if i > 0:
            nav.append(f"Before it: [{pages[i-1][1]}](../rung-{ids[pages[i-1][0]]}/).")
        if i + 1 < len(pages):
            nav.append(f"After it: [{pages[i+1][1]}](../rung-{ids[pages[i+1][0]]}/).")
        nav.append("The whole ladder: [the Seed](../).")
        fm = "\n".join([
            "---",
            f"title: {yaml_str(title)}",
            f"description: {yaml_str(desc)}",
            'layout: "n0-page"',
            f"weight: {WEIGHT0 + i}",
            f"source: {yaml_str(f'node0-seed rungs/{d}/README.md at {rev}, generated by tools/seed-rungs.py; edit the README, not this page')}",
            "---",
        ])
        emit(os.path.join(OUT, f"rung-{rid}.md"), f"{fm}\n\n{md}\n\n{' '.join(nav)}\n")

    # rung pages that no longer have a README
    keep = {f"rung-{ids[d]}.md" for d in dirs}
    for f in os.listdir(OUT):
        if f.startswith("rung-") and f.endswith(".md") and f not in keep:
            stale.append(os.path.relpath(os.path.join(OUT, f), ROOT))
            if not a.check:
                os.remove(os.path.join(OUT, f))

    os.makedirs(IMG_OUT, exist_ok=True)
    for name in sorted(images):
        s, t = os.path.join(src, "images", name), os.path.join(IMG_OUT, name)
        if not os.path.exists(s):
            sys.exit(f"seed-rungs: a rung uses images/{name}, which is not in the repository")
        if not os.path.exists(t) or open(s, "rb").read() != open(t, "rb").read():
            stale.append(os.path.relpath(t, ROOT))
            if not a.check:
                shutil.copyfile(s, t)

    if a.check:
        if stale:
            print("seed-rungs: stale, regenerate:", *stale, sep="\n  ")
            sys.exit(1)
        print(f"seed-rungs: {len(pages)} rung pages current (node0-seed {rev})")
    else:
        print(f"seed-rungs: {len(pages)} rung pages from node0-seed {rev}; {len(stale)} file(s) written")


if __name__ == "__main__":
    main()
