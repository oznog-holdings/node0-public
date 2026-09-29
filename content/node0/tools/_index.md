---
title: "Tools"
description: "What each tool in the repository is for."
layout: "n0-page"
date: 2026-09-28
sanitized: "checklist v0.1, 20260928"
---

The tools live in [github.com/oznog-holdings/node0-public](https://github.com/oznog-holdings/node0-public) under `tools/`, and every command below runs from the repository root. `sanitize-check.py` also needs two private files that each site writes for itself and never commits. The names list holds the literals that must never appear, one per line: host, people, place and account names. The rules file holds the site's own patterns, one `name: regex` per line, such as its address ranges and identifier shapes.

| tool | what it is for | status |
|---|---|---|
| `sanitize-check.py` | the mechanical half of the publication checklist: addresses, credential shapes, credential-store names, image metadata | in use on this repository, locally and in CI |
| `diagrams/gen.py` | draws every diagram on these pages from a data file | in use on this repository |
| `seed-rungs.py` | generates the Seed's rung pages from the rung READMEs in the node0-seed repository | in use on this repository |
| `site-check.py` | reads a built copy of the site and reports broken links and anchors, pages nothing links to, repeated links, images without alt text and stray dashes | in use before each publication |

## sanitize-check.py

Needs Python 3.11 or later and nothing else. Scans what git would publish
(every tracked and untracked-not-ignored file, or the paths given), file names
included, and prints one line per hit with the rule, the file, the line and
the length of the match, never the match itself. Exit 0 is clean, 1 is at
least one hit, 2 is a configuration error: a missing path, an unreadable
private file, a bad regex, a malformed exception. Text is scanned as text;
JPEG, PNG and WebP files are walked segment by segment to the end and every
segment must be one that carries pixels; anything else that cannot be decoded,
a symlink or a special file is a hit. Exceptions live in `.sanitize-allow` at
the repository root, each scoped to one rule and carrying a reason, and there
are none for images.

The tool carries only generic patterns. What is specific to a site, its names
and its regexes, goes in two files that never enter the repository, passed as
`--names` and `--rules`; without them the summary line says the pattern half
ran alone. Run it before every push:

```
python3 -B tools/sanitize-check.py --names ../private/sanitize-names.txt --rules ../private/sanitize-rules.txt
```

A green run is necessary, never sufficient. It cannot read a label in a
photograph, decode a secret someone encoded, or know that an unlisted word is
a name, and it scans a tree, not a history.

## diagrams/gen.py

Needs Python 3.11 or later and PyYAML. Reads `data/diagrams/*.yaml` and writes
one SVG per drawing into `static/images/node0/diagrams/`, plus one strip per
layer for the stack. Text comes from the data files, sizes from the drawing
code; the output is deterministic, so a regenerated tree that differs is a
change to look at. Run it from the repository root after editing a data file:

```
python3 tools/diagrams/gen.py
```

The site pages inline the SVGs, so a regenerated drawing is live on the next
build. The generator does no sanitizing; its inputs and outputs go through the
gate like every other file.

## seed-rungs.py

Needs Python 3 and git, and a checkout of
[node0-seed](https://github.com/oznog-holdings/node0-seed) beside this
repository, or its path given with `--src`. It reads each
`rungs/<n>-<name>/README.md` there, writes `content/node0/seed/rung-<n>.md`, and
copies the photos the rungs use into `static/images/node0/seed/`. The README's
H1 becomes the page title, and its "In plain terms" paragraph becomes the
description and is removed from the body. Links into the repository become
links to it on GitHub, and links between rungs become links between the rung
pages. It stops with an error on a link or a photo that is not in the
repository.

```
python3 tools/seed-rungs.py
python3 tools/seed-rungs.py --check
```

`--check` writes nothing and exits 1 if any page or photo would change, so the
gate can refuse a stale page. Edit the README in node0-seed, never the
generated page, because the next run overwrites it.

Every tool here is MIT licensed, so it can be copied into your own repository, changed, and shipped, with the notice kept. The pages and data around them are CC BY 4.0.

## site-check.py

Needs Python 3 and a built copy of the site. Build it with `hugo -d <dir>`, then run
`python3 tools/site-check.py <dir> --base <the baseURL it was built with>`. It reads every
`index.html` and reports, per page: broken internal links and anchors; pages that no content
links to (the section nav and the breadcrumb do not count); pages more than three clicks from
the home page; the same internal target linked more than once in one page, and the same
external link repeated; images without alt text; en or em dashes in page text; and headings
under /node0 that look Title Case. It exits 1 on a broken link, a missing alt text or a dash.
The rest is for reading: a page that links the same evidence twice to prove two different
claims is fine.
