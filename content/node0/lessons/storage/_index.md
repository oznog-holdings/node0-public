---
title: "Storage and backups"
layout: "n0-theme"
theme: "storage"
gist: "Twenty-one storage and backup lessons, mostly about the gap between a backup that runs and a backup that is proven."
date: 2026-09-20
source: "node0 lessons v0.1, section 3"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 3
---

Almost every lesson in this theme is a version of the same sentence. Something
reported success, and the success was not the thing anyone actually needed.
An `scp` that failed silently and a delete in the same command that ran
anyway. A photo library that held pointers rather than copies. A capacity
guard that logged the failure it had predicted and then carried on into it. A
backup datastore that had never had a job pointed at it and therefore never
failed. A lifecycle setting whose plain-English name described the opposite
of the protection it gave. In each case the signal an operator would naturally
look at, an exit code, a green job status, a quiet dashboard, a configuration
file on disk, was a claim rather than a proof.

The order matters, because the lessons built on each other. The first, on
20260723, cost real data and produced the rule that every later
deletion in the project was gated on: transfer, verify, delete, as three
separate observed steps. The lessons that followed were mostly about
discovering where data actually lived: in RAM on an appliance NAS, inside a
fixed-size container image, referenced in place by a media tool rather than
copied, or on an offsite drive whose free space was being consumed by the
best-protected data instead of the least. From 20260821 the work shifted
from finding gaps to proving the absence of them, with a weekly restore
rehearsal that restores real files and reports "skipped" as its own outcome.
The autumn lessons (20260905 onward) came out of rebuilding the whole backup
topology around a new central server, and are about invariants enforced in
code rather than remembered: a destination never holds a backup of itself, a
generated configuration is never hand-edited, a new host is not finished until
the fleet-wide check can see it.

## Declined

- A resolver role moved with a server migration. It was a real fact corrected in the as-built capture, but a documentation placement error rather than an event with a cost, so no practice changed.
- The ceph8 bay-9 "dirty connector, two failure signatures" incident and the wider work on hidden drive health counters are genuine lessons. They are hardware and RMA content, though, and belong to theme 1, not here.
- Bootstrapping a nine-host Ceph cluster in a day and a half, and the hardware provisioning story around it, is compute and hardware-provisioning content. It is assigned to theme 1.
- A fleet backup repository count differed across documents over time (seventeen, then twenty, then sixty-nine). That is ordinary staleness in prose as the fleet grew. The verification sweep's own live number is the authoritative one on any given day, and nothing changed beyond a note.
- A prune list on the old NAS had drifted (ten hosts with no retention policy, one entry with no repository behind it). It was a real incident, but a direct instance of an existing fleet-wide rule that hardcoded lists go stale silently, so it was declined as a duplicate.
- Four different hostname variants fragmented one machine's backup history and were unified on 20260809. It was a data-hygiene rename with no cost incurred and no process change.
- A backup client's host identity was pinned against reverse-DNS drift, fixed on 20260722. It was folded straight into the standard configuration baseline rather than surfacing as a dated incident with a measurable cost.
