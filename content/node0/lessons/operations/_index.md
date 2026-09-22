---
title: "Operations and agents"
layout: "n0-theme"
theme: "operations"
gist: "How a fleet run mostly by AI agents keeps its work attributable, its changes real, its checks honest, and its first attempts in a sandbox."
date: 2026-09-20
source: "node0 lessons v0.1, section 6"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 6
---

Node0 is operated by agents more than by hands, and this theme is what
that turned out to require. The lessons here are about tooling, identity
and process rather than about hardware, and they share one shape. A thing
reported success, and the success was not real.

The order matters. The first decisions came in August 2026, before the
fleet had settled. One shared operating-system account served every
agent, with attribution and revocation carried by a distinct key per
agent rather than by separate accounts. A first NixOS host was used
deliberately to find out what a declarative system does with an
undeclared change. It accepts the change, then forgets it silently.
And a week on a vendor default password came not from oversight but from
a routine security task that had been made to wait on a platform nobody
was building yet. That week produced the standard the fleet still runs
on.

From there the pattern repeats in different tools. A CI gate and a
background monitor each failed at the level of the check itself, and each
reported a confident, specific, false diagnosis. That is where the
standing rule came from. A check you have not watched fail for the right
reason is not a check yet. A build that could not reach its source of
truth built from cache and exited zero. An inventory filter that did not
support its own operator returned every device instead of an error. A
re-seed reverted a live correction without a word. Two agents sharing one
working tree absorbed each other's staged files, silently.

September brought the agent-specific versions of the same thing. A
heartbeat proved a guest was up while saying nothing about the session
inside it. A migrated agent memory existed on disk at a path the running
session never read. Two lessons are about looking before
building, and about the audit tooling making exactly the mistakes the
infrastructure makes. The last one, added on 20260922 at Christoph's
request, is the one most of the others lean on: a sandbox the agents are
allowed to break, where the storage cluster, the firewall pair and the
remote-access design were each proven and corrected before they touched
live hardware (6.18). And one rule that was never broken, written down because the seed inherits it: nothing the site depends on runs on a laptop that travels, and no secret stays on one outside a vault (6.19).

## Declined

- The commit-author breakdown for an agent-run fleet: a genuine data point, but a steady state rather than a dated event with a cost and a fix.
- The arc from a laptop drawer to a rack-hosted agent: a narrative frame, not an incident; its two real incidents are written up on their own.
- Proving a NixOS host can die and come back: a successful controlled exercise with no cost, and the negative finding it produced is published separately.
- A laptop that powers itself off every five days: unresolved as of 20260920, with no fix or changed check yet, and it belongs to hardware.
- The full table of what an agent may and may not do without asking: a compiled artefact assembled from incidents already written up, not a dated event of its own.
- A brief window of unfiltered DNS from a version-change gate being crossed: a real near-miss, but its subject belongs to network and edge.
- The decision to start the secrets platform clean rather than migrate a placeholder: an architectural choice with no incident behind it, folded into the credential-stance lesson instead.
- A stale runner count in the CI practices document: already self-corrected in that document's own header note, with nothing new to add.
- Rollback artefact retention and the weekly hygiene sweep's other housekeeping: routine maintenance discipline, not a dated incident.

## Not published

- A standard written after credentials were found passed on a command line, told here only as the rule it produced.
- A credential exposed twice, the second time by a redaction that kept part of the value, told here only as the rule it produced.
- A credential artefact that reached a deployment branch without passing the gate, told nowhere.
- An automated credential operation that deleted the wrong keys and took a telemetry feed down, told nowhere.
