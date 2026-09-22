---
aliases: ["/node0/site/operations/"]
title: "Operations"
layout: "n0-layer"
layer: 11
gist: "The habits that let more than one actor change the site without the history, the credentials or the inventory drifting."
figures: ["2,069 commits since 20260810", "140 runbooks", "one branch between written and running"]
photo: "hand-seating-cable.jpg"
photo_alt: "A hand seating a network cable into a patch panel"
photo_caption: "Every change has a physical end somewhere."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.11"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 11
---

## What this layer is for

Operations owns no rack position and runs no service of its own. It is the set
of habits and mechanisms that let Node0 be changed safely by more than one
actor, mostly agents, over weeks. The test it has to pass is that the change
history, the credentials and the inventory never drift from what is actually
running. It answers three questions: how a change reaches a machine, how it is
undone when it is wrong, and how anyone finds out afterwards what happened.

Nearly every part of it was built after a failure rather than before one. The
repository opens on 20260810. By 20260921 it holds 2,069 commits, counted from
`git log` that day: 1,834 by the agent Rigger, 163 by the agent Bosun, 27
under a generic Claude identity, 34 by two unattended jobs, and 11 directly by
Christoph. Christoph sets direction and makes the decisions that matter. The
agents do the typing. Who did what is the commit author field rather than
anyone's memory.

## How it is built

**CI runs on every push.** A Forgejo runner on sandbox1 claims each push and
runs one workflow: unit tests, a secret scanner, a repository validator, a
check that every NixOS host configuration still evaluates, and a check that the
flake lock is complete. The workflow file is checked into the repository with
the code it checks. Its value is that it cannot be skipped. On 20260920 CI
reported rather than gated, so a red run was advisory. That holds while one
careful actor commits, and it becomes load-bearing the moment that stops being
true.

**Deployment is pull, and promotion is one push.** A timer on every NixOS host
builds and switches to a `deploy` branch each hour, so hosts converge rather
than receive. `git push origin main` reaches no hardware.
`git push origin main:deploy` is the single command that turns a written change
into a running one. On 20260920 `main` sat two commits ahead of
`origin/deploy`, which is the design working rather than drift.

**Credentials stay out of the repository by rule.** If rotating a credential
requires editing this repository, the design is wrong. The rule was adopted
20260905, and a gate in CI enforces it on every push. Routine access is by key,
custody is in a password manager, and vendor defaults survive only as a
verified break-glass path behind a key. A secrets vault (OpenBao) has since
been built, three raft members across three platforms, initialised 20260912 and
healthy on 20260920. It is so far lightly used.

**The inventory is the authority.** NetBox holds one record per thing. The
nightly export of 20260920 carried 191 device records, 185 of them active, with
407 cables, 827 interfaces, 22 VLANs and 322 inventory items. NetBox became the
single authority in stages, a foundation on 20260906 and an authority review on
20260909, because the alternative was several hand-maintained documents that
could each be true or stale independently.

**Configuration is captured nightly, and traps are written down.** Since
20260911 every device with an export path sends its configuration to git each
night, so a hand-made change appears the next morning as a diff. The rest stay
manual and are listed as such. On 20260921 the repository also held 140
runbooks, 3 decision records and 2 lesson documents. Its 29 NixOS host
directories evaluate to 37 configurations plus one variant, and share 14 roles.
Every trap that has been hit once is written into a runbook.

| host (owning layer) | role in operations |
|---|---|
| unraid1 (services and storage) | the git forge and the inventory system |
| sandbox1 (agents) | the CI runner that claims every push |
| core1 (bootstrap) | nightly configuration backup and inventory export |
| util2 (compute and bootstrap) | image and rescue builds, package cache, network boot |
| di5 (compute) | the fleet's default build host since 20260910 |
| every NixOS host | hourly convergence to the `deploy` branch |

**Failure domain.** This layer has no rack position and cannot itself go down,
but its mechanisms carry everything else's ability to recover. If the git forge
is unreachable, nothing converges and promotion stops. Hosts that have already
converged keep running as they are, so the layer fails static rather than open.
None of it takes down a service, and all of it can corrupt the record of what
is true without anyone noticing.

## The decisions

### 20260816: CI on every push, and a branch between written and running

**Workload.** A fleet changed many times a day, almost entirely by agents.

**Requirement.** No change reaches hardware unchecked.

**Choice.** A runner validates every push to `main`. Hosts converge hourly to a
separate `deploy` branch, and promotion is one command. Automatic deployment on
merge was declined.

**Accepted trade-off.** Promotion stays manual and depends on one trusted
actor, and a change can wait an hour to land.

**Verified.** In daily use since 20260816. It was hardened on 20260918 so that
convergence fails closed, comparing the resolved revision against the branch
head rather than trusting a success message.

### 20260816: credentials by key and custody now, a vault later

**Workload.** Bring-up, with dozens of devices arriving on vendor defaults.

**Requirement.** Routine security work must not wait on anything unbuilt.

**Choice.** Keys for routine access, a password manager for custody, and vendor
defaults kept only as a verified break-glass path behind a key.

**Accepted trade-off.** Custody stays partly manual, and a proper vault arrives
later rather than shaping the design from the start.

**Verified.** The decision followed an internet-facing edge switch that sat on
a shared default for a week, because its hardening had been routed through the
unbuilt vault.

### 20260905: a credential rotation is an operational act, never a commit

**Workload.** Scripts and configurations that authenticate to devices and
services.

**Requirement.** An operator can rotate any credential without a review, a
merge and a deploy.

**Choice.** The one-sentence rule stated above, enforced by a gate in CI.

**Accepted trade-off.** A few named, dated exceptions exist where a device's
own dependency forbids the clean design. Each is written down as an exception
rather than passing unrecorded.

**Verified.** The gate runs on every push as of 20260920.

### 20260904: one numeric identity per account, fleet-wide

**Workload.** A mixed NixOS, Debian, macOS and Unraid fleet sharing files.

**Requirement.** The same two administrative accounts mean the same thing
everywhere.

**Choice.** Ids are declared explicitly in the shared base module rather than
left to creation order. The id change and the file reownership are done as one
operation per host.

**Accepted trade-off.** macOS and Unraid keep their native numbering, two
documented exceptions.

**Verified.** A survey of every host touching shared storage found thirteen,
later fourteen, with the two ids exactly swapped.

### 20260906 and 20260909: the inventory is the authority

**Workload.** Agents answering questions about hardware they cannot see.

**Requirement.** One record per thing, and one place allowed to be right. A
confident wrong answer is worse than no record, because agents act on it.

**Choice.** NetBox was loaded in stages. An authority review then covered
locations, the spares shelf and warranty fields, after which the older
hand-maintained documents were marked superseded for data.

**Accepted trade-off.** A live edit that is not written back into the manifest
seeding the inventory is reverted by the next seed.

**Verified.** The nightly export is the diff that catches that, and this page's
figures come from it.

## What it cost

Replacement costs for this layer are being researched and will be added.
Purchase prices are not published. Operations owns no hardware of its own, and
its mechanisms run on hosts other layers already paid for.

## What broke

- **Lesson 6.3, The default password week.** An internet-facing edge switch sat
  on a shared vendor default for about a week, because its hardening had been
  routed through a platform nobody was building yet.
- **Lesson 6.4, A check you have not seen fail for the right reason is not one
  yet.** In one afternoon a monitor called a healthy host unreachable because it
  ran under a shell that splits words differently, and a CI step called a
  complete lock file stale because the tool it compared with was missing.
- **Lesson 6.5, NixOS creates users alphabetically, and that is a
  security-relevant bug in your fleet.** Two accounts with the same names held
  swapped numeric ids across a mixed fleet, silent until something crossed a
  boundary that carries numbers instead of names.
- **Lesson 6.10, A failed fetch still exits zero, and "already converged" can
  mean "still stale".** A build whose fetch failed fell back to the cached tree
  and exited zero, so convergence logged success while it built the old
  configuration.
- **Lesson 6.11, Two agents, one git index.** Two agents working one checkout
  staged changes at once. The first commit swept up the other's files with no
  error, and the second reported nothing to commit.

## State on the day

Healthy on 20260920: the repository and its history, CI on every push, hourly
convergence on every NixOS host, the promotion gate, the nightly configuration
backups and inventory export, and NetBox as the authority. Each has been
through at least one real incident and come back. The two-commit gap between
`main` and `deploy` that afternoon was a runbook and a rollback note waiting to
be promoted.

Open, from Christoph's list of 20260920: the secrets vault is live and healthy
but the secrets have not moved into it, and a handful of inventory records lag
the site. Closed the same day, and marked as such: Bosun's heartbeat now
refuses to beat unless its session is present and its login valid, and its
memory path was corrected, lessons 6.14 and 6.15.

Closed on the capture day, and marked as such: forty-one alert rules that
carried no instruction for whether to act were labelled, and a missing backup
job was added, both by the agent Bosun the same evening. Two of this capture's
own findings were closed hours after they were raised, by rerunning the
inventory export by hand, so the figures here read against an export that
contains the day's changes.
