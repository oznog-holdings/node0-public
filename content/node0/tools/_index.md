---
title: "Tools"
description: "What each tool in the repository is for."
layout: "n0-page"
date: 2026-09-20
sanitized: "checklist v0.1, 20260922"
---

| tool | what it is for | status |
|---|---|---|
| `sanitize-check.py` | the mechanical half of the publication checklist: addresses, credential shapes, credential-store names, image metadata | in use on this repository, locally and in CI |
| `diagrams/gen.py` | draws every diagram on these pages from a data file | in use on this repository |

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

Every tool here is MIT licensed, so it can be copied into your own repository, changed, and shipped, with the notice kept. The pages and data around them are CC BY 4.0.
