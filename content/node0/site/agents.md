---
title: "Agents and dev"
layout: "n0-layer"
layer: 8
gist: "The machines the agents and the developers run on, the sandboxes the agents are allowed to break, and the rules that say what an agent may change without asking."
figures: ["six agent machines", "2,069 commits, 11 by a human", "one shared account, one key per agent"]
photo: "agents-shelf.jpg"
photo_alt: "Laptops and small-form computers on a rack shelf, lids open, cables gathered to one side"
photo_caption: "The agents' machines on their shelf."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.8"
sanitized: "checklist v0.1, 20260921"
weight: 8
---

## What this layer is for

Node0 is operated by agents, not only for them. Its founding principle is
agent-forward, human-sovereign operation. Digital intelligences (DIs, this
site's term for its AI agents) do the deployment, monitoring, diagnosis,
repair and documentation. Christoph keeps sovereignty through readable
interfaces, exact approval of the operations that matter, and the ability to
run the foundation himself if the agents go away. This layer is the machines
the sessions run on, and the rules that keep one shared, root-equivalent
credential from being a single point of failure.

The claim is checkable in one place. The Node0 repository opened on 20260810
and held 2,069 commits on 20260921 (git log, 20260921): 1,834 by the agent
Rigger, 163 by Bosun under two spellings of its name, 27 by a generic Claude
identity, 34 by two unattended jobs, and 11 by Christoph. He decides, the
agents do essentially all of the typing, and the commit author field is the
record of who did what.

## How it is built

| host | role | form | rack | OS |
|---|---|---|---|---|
| agent1 | agent host | MacBook Pro M1 Max, 64 GB | rack 3 shelf | macOS |
| agent2 | agent host | MacBook Pro M1 Max, 64 GB | rack 3 shelf | macOS |
| agent3 | agent host | Mac mini M4 | rack 3 shelf | macOS |
| agent4 | agent host | Mac mini M4 | rack 3 shelf | macOS |
| agent5 | agent host | Mac Pro 2013, 12-core | rack 3 shelf | NixOS |
| agent6 | agent host | virtual machine, 4 vCPU / 16 GB | Proxmox cluster | NixOS |
| dev1 | dev host | MacBook Pro M1 Max, 64 GB | rack 2 | macOS |
| dev2 | dev host | MacBook Pro M1 Max, 64 GB | rack 2 | macOS |
| dev3 | dev host | Dell OptiPlex 5050 | rack 2 | NixOS |
| dev4 | dev host | HP EliteDesk 800 G3 | rack 2 | NixOS |
| sandbox1 | sandbox | MacBook Pro 2018 (T2) | rack 3 | NixOS |
| sandbox2 | sandbox | HP ProBook 6570b | rack 3 | NixOS |

The roster started as laptops: M1 Max MacBook Pros, chosen for their
processing capacity and because 64 GB of memory came at a reasonable cost
against the alternatives, and four of them are agent1, agent2, dev1 and dev2.
agent3 and agent4 arrived as Mac minis on 20260818. agent5, a salvaged 2013 Mac Pro converted to NixOS on 20260830, is left unused
on purpose, since a machine does not earn its power draw by being available.
agent6 is the only virtual one, and it runs Bosun, the agent that operates the
site day to day. The dev hosts carry development sessions and, on the NixOS
pair, continuous integration. Forgejo Actions runners went onto dev3, dev4 and
sandbox1 by benchmark on 20260831, and onto dev2 by hand, because a macOS
build needs a macOS runner. sandbox1 was the site's first NixOS host, wiped
and rebuilt from committed configuration alone on 20260816. The rebuild was
checked against a closure hash (the identity of the exact package and
configuration set a NixOS system resolves to) taken before the disk was
touched, and every later NixOS host here inherited that.

The four dev hosts are where applications get built, as distinct from where
the site gets operated. They carry the development of the projects that run
on Node0 and are incubated by Oznog, [Relational Core](https://standpointlabs.com)
first, with the [incubator](/apply-for-incubator/) opening in Q4. A project
gets its development sessions on a dev host, the site's local models through
the gateway, the storage tiers, and the CI runners on the same shelf, so it is
built on the infrastructure it will run on rather than ported to it later.
The two Macs cover the work that needs macOS; the two small NixOS boxes cover
the rest and run the runners.

The two sandboxes are on this shelf because they are the agents' rehearsal
machines, and an agent fleet needs them more than a human team does. An agent
operating something for the first time builds it on a sandbox first, breaks it
on purpose, writes down what it found, and only then goes near live hardware;
the storage cluster, the firewall pair and the remote-access design were each
proven and corrected there before they touched anything real. Two old laptops
that nothing depends on are the cheapest insurance on the site, and old is
fine: sandbox2 is a 2012-era business laptop, and it had the capacity to
model the whole hypervisor and storage cluster deployment as a set of virtual
machines before any real hardware was tested, with room to spare. Lesson 6.18
carries the instances and the rule.

[herdr](https://herdr.dev/), a fleet session manager, carries session state and is pinned to one
version across the NixOS hosts. A mirror plugin on Christoph's own machines
gives him one sidebar onto every session. Claude Code and Codex are the
runtimes, both pinned to upstream releases rather than to the distribution's
packaging, which had drifted 53 patch versions behind when this was noticed.

## The decisions

### 20260811, one shared account with one key per agent

**Workload.** every DI that touches a fleet host, over ssh and over service
APIs. **Requirement.** attribution and revocation per agent, without spending
bring-up on privilege boundaries for a fleet whose shape was not yet known.
**Choice.** one shared, root-equivalent operating-system account for every DI,
with a distinct credential per agent landing in it. Bosun is named as an
independent operator under Christoph's direct authority, distinct from Rigger,
the commissioning lead. **Accepted trade-off.** a leaked credential from any
host here reaches everything that account reaches, taken for deployment
throughput. The fuller deployment of the secrets vault is where that
trade-off gets scoped down further, credential by credential, and it is on
the open list. **Verified.** the commit log separates the two agents from the
first week onward, and every later credential decision here follows from this
one.

### 20260917, the operating agent moves in-fabric

**Workload.** Bosun's monitoring and remediation session, run from Christoph's
laptop since the beginning. **Requirement.** hands that survive a closed lid
and an absent person. **Choice.** a NixOS guest, agent6, on the Proxmox
cluster, under twelve decisions accepted the same evening. The substantive
ones are an ssh key generated on the guest rather than copied to it, the
shared account kept rather than a new one made, per-service credentials of its
own wherever it touches a service, no out-of-band device passwords on the
guest, an independent clone of the repository, and a heartbeat to a dead-man
on another host. **Accepted trade-off.** a cluster outage takes agent6 and
with it Bosun, accepted because Bosun's job in a cluster-wide outage is to
have already paged, not to fix it. **Verified.** deployed 20260917 into
20260918; on 20260920 the guest reported about two days seventeen hours of
uptime, with its session process and timers checked live.

### 20260920, the standing authority boundary

An agent's standing authority is two written lists: what it may change
unaided, and what needs the person.

**Workload.** everything Bosun does between messages from Christoph.
**Requirement.** an agent useful enough to close real problems alone, without
one that can take the site down alone. **Choice.** those two lists, each
row justified by the incident that set it, drafted from the first three days
on agent6 and revised by Christoph; three of those incidents are lessons
below, and the cost is latency where latency is cheapest.

Without asking, Bosun may run read-only queries anywhere; edit inventory
records, which are reversible by object identifier and seeded from the
repository; change alert rules, thresholds and labels with tests, and change
dashboards through the generator, because a bad rule is noise rather than an
outage; commit and push runbooks and tools after rebasing; set a silence with
a stated reason and an expiry of at most seven days; restart and re-time its
own monitors on its own host; make edits that stay dormant until a container
is recreated, when it reports the landing time; and apply a fix found on one
host to the rest of that class, after a read-only check confirms it.

Bosun asks first before rebooting or power-cycling any host, however harmless
it looks; deleting anything it did not itself create in the same task,
including files, records, containers and snapshots, so cleaning up its own
working files and test objects is inside its authority and nothing else is; promoting the deploy branch, which converges every host at once;
changing the version of a resolver, a firewall, or anything on the paging
path; creating, rotating or deleting credentials on a shared service; anything
physical; restarting a firewall or moving the edge; touching another host's
secrets; silences longer than seven days, or any silence on a scarred drive;
anything inside another agent's domain; and building something because a gap
seems to exist, without first searching for what may already close it.

## What it cost

Replacement costs are being researched and will be added. The bill of
materials of 20260920 carries these hosts with both cost columns open, and
purchase prices are not published.

## What broke

- **Lesson 6.2, Imperative drift on NixOS evaporates silently.** An
out-of-band change succeeds and then vanishes at the next rebuild, which is
worse than a refusal because it looks like success.
- **Lesson 6.11, Two agents, one git index.** One agent's commit swept up
seventeen files another had staged, with no error on either side; the real fix
is a worktree per agent.
- **Lesson 6.14, The heartbeat that was not watching what mattered.** It
proved the guest was up, not that the session inside it was alive and logged
in; writing the operating runbook found that, not an outage.
- **Lesson 6.15, A second AI, forked from the first one's memory, that could
not find it.** A 178-file agent memory was migrated to the new host while the
session read a different, empty path, so the agent worked without its own
history and nothing errored.

## State on the day

Healthy on 20260920: twelve hosts active, none retired; four CI runners
registered; Bosun three days into running on agent6, checked live by host
name, uptime, its session process and its timers.

Open: sandbox1 has a pattern of spontaneous power-offs at five-day intervals,
most likely tied to running Linux on a machine with Apple's T2 controller and
everything that brings with it; under diagnosis and mitigation, with the
lessons to be recorded as it closes (1.16).

Closed on the capture day, marked as such: the memory-path mismatch was fixed,
and the heartbeat given gates that make it refuse to beat unless the session
process is present and its login still valid. The as-built capture, written
earlier that day, still lists that gap as open; the next capture settles it.

That evening also produced the operation that best shows what the arrangement
is for. An audit asked of the hypervisor's backup server how old the
newest archive was, per source, rather than whether the jobs were green. There
were no jobs. The datastore held one archive from a restore test of 20260904,
and five production guests had never had a disk-level backup. Nothing said so, because
every existing check looked at the backup server's own housekeeping, and a
prune job with nothing to prune succeeds. Bosun closed it the same evening.
One cluster-wide job runs at 04:45 nightly in snapshot mode, covering every
guest but the two test ones, so a new guest is covered the day it exists, with
retention held on the backup server. Bosun ran the job by hand rather than
waiting for it, and wrote six alert rules that page if it disappears or if a
guest's newest archive passes thirty hours. One production guest's archive was
restored to a scratch virtual machine, booted in isolation to a login prompt
with its database up, then destroyed. The question that would have caught this
a fortnight earlier is now in the backup runbook.

An agent found the gap, built the job, ran it, wrote the alarm, proved the
restore and cleaned up, in one evening, inside a boundary that would have made
it ask before deleting anything it had not made.
