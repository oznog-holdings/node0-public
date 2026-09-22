# node0, public

The public face of node0: a sovereign, self-hosted infrastructure site built
by one person and a set of agents, and the smallest version of it (the seed)
that anyone can start from.

- **Site:** https://oznog.com/node0 (this repository's `content/` is mounted
  into the oznog.com Hugo build)
- **Source of truth:** the private node0 repository. This one is a derived,
  sanitized copy: nothing here is edited in place, every page names its
  source and the checklist version it was produced against.
- **Mirror:** Forgejo is the origin; GitHub (`oznog-holdings/node0-public`) is a
  push mirror. Node0 is built by Oznog Labs; the repository is held by Oznog
  Holdings LLC, which owns the work.

## Layout

    content/node0/     Hugo content: landing, seed, site, lessons, guides, tools
    static/images/     processed photographs and diagrams (no metadata, no labels)
    tools/             reusable tools with generic names; sanitize-check.py is the gate
    tests/             tests for the tools
    .forgejo/workflows/sanitize.yml   every push runs the gate

## The gate

`tools/sanitize-check.py` is run locally before every push, with the two private
files that never enter this repository, and that run is the gate:

    python3 -B tools/sanitize-check.py --names ../private/sanitize-names.txt --rules ../private/sanitize-rules.txt

It refuses IP literals outside the documentation ranges, MAC addresses, email
addresses, credential shapes and assignments, the names and paths of
credential stores, the private names and patterns from the two files, and any
image that carries anything beyond pixels. It scans what git would publish,
including every file name, and reports a hit as a rule, a file, a line and a
length, never the match. Exit 0 is clean, 1 is a hit, 2 is a configuration
error. Accepted exceptions go in `.sanitize-allow`, scoped to a rule, with a
reason; there are none for images.

The CI job runs the pattern half again at the pushed commit as a second check.
It cannot see the private files and it does not scan history: a secret that was
ever committed needs a history rewrite, not a later commit that removes it. A
green run is necessary, never sufficient.

## Licences

Two, by directory, both attribution licences; `LICENSE` at the root maps them.
Writing, diagrams, photographs and data (`content/`, `static/`, `data/`): CC BY 4.0
(`LICENSE-content`). Tools and their tests (`tools/`, `tests/`): MIT
(`LICENSE-tools`). Copyright Oznog Holdings LLC, 2026.

## Status

Published 20260922, as the first drop. What is here first, on purpose, is the
architecture, the design decisions with their trade-offs, the lessons and the
rules the fleet runs by, because those are what we believe transfer, and because
many of the lessons and rules were distilled from the runbooks in the first place.
As the site matures and each piece proves itself, the other artefacts a builder
would want follow the same route out: runbooks, configuration, the monitoring and
management scripts, the agents' skills, each sanitised for privacy and security
before it leaves.
