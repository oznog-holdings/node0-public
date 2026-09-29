---
title: "Node0"
description: "A sovereign, self-hosted infrastructure site in two rooms of a home in northern Utah: built by one person and a set of agents, documented in the open, and the pattern anyone can start from."
layout: "n0-landing"
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 1; the public site plan of 20260920"
sanitized: "checklist v0.1, 20260921; voice pass 20260921; the Seed, agent and why-run-your-own paragraphs added 20260928"
photo: "studio-dark.jpg"
photo_alt: "A dark studio: a desk with a glowing workstation, and beside it three server racks lit by their own LEDs and two dashboards"
photo_caption: "The studio, lights off. The racks run whether or not anyone is at the desk."
cascade:
  showDate: false
  showReadingTime: false
---

Node0 is a real place: two rooms, four racks, a fabric of six switches, nine storage servers, a UPS wall, a set of GPU hosts behind one model gateway, and the agents that help run it. Christoph built it over 2025 and 2026, most of the distance in six weeks of the summer of 2026, out of pocket. It runs the work of Oznog today: development, incubation and pre-production of digital intelligence work that stays private by choice.

It is not a datacenter and does not pretend to be one. It runs on one fibre line and a battery, not two providers and a generator. What it has instead is a datacenter's discipline: the inventory is the source of truth, every alert names its runbook, and backups are proven by restoring them. These pages are derived from a dated capture of the whole site.

## Build it with an agent

These pages are written to be read by a person and used by their agents. Point an agent at them, or at [the repository](https://github.com/oznog-holdings/node0-public) that holds them as Markdown and YAML, and tell it what you have on the bench and what you need the site to do. It will find where to start on [the Seed's ladder](/node0/seed/), the decisions that transfer, and the lesson that would otherwise cost you the same time it cost us. Every page names its source and its date, so an agent can tell a rule from an instance. A prompt that works:

> Read the Seed and the Seed design, then the as-it-stands pages for the layers I name. I have [the hardware on my bench], I need the site to [the workloads], and my limits are [budget, power, space]. Ask me what is missing, recommend the rung to start on, and cite the page or lesson behind each choice. Keep separate what Node0 actually ran, what the Seed proposes, and what you infer.

[The Seed's status table](/node0/seed/#what-has-been-run) says which rungs have actually been run; have the agent check it before treating a design as demonstrated practice. Next on the Seed's roadmap is [an agent that helps monitor, manage and maintain the site](/node0/seed/#coming-next-an-agent-that-looks-after-the-site).

These pages get technical quickly. The detail is for your agent, so ask it what anything means, why you would want it, and what happens if you skip it. If you are wondering whether any of this is worth it for you, start with [why run your own, and when not to](/node0/why-run-your-own/).

## Three doors

{{< n0-doors >}}

## Why it is published

We want many others to deploy a Node of their own, so we share as much as we can without compromising the security of this one. Everything on these pages is derived from the private site through a checklist. Humans other than Christoph appear by role and agents by name. There are no addresses, credentials, serials or paths, and the finance system is described by shape only. Every page names its source and the checklist version it passed.

For Node0 itself, what is here on purpose is the architecture, the design decisions with their trade-offs, the lessons and the rules we run by. Those are what we believe transfer, and many of the lessons and rules were distilled from the runbooks in the first place. The pages, the figures they draw on, the drawings' data files and the tools live in one public repository: [github.com/oznog-holdings/node0-public](https://github.com/oznog-holdings/node0-public).

The Seed goes further. Its repository, [github.com/oznog-holdings/node0-seed](https://github.com/oznog-holdings/node0-seed), holds what the bench ran, for a builder's agent to repeat it: the configuration exactly as it ran, the scripts, the monitoring rules with their tests, the measurements, the pitfalls and the recovery-pack runbook, with secrets and serials removed and every address outside the Seed replaced. Step-by-step runbooks for each rung come next. Node0's own runbooks, configuration, monitoring and management scripts, and the agents' skills will follow the same route out as each piece proves itself, sanitised for privacy and security before it leaves.

{{< n0-figure src="room-from-door.jpg" alt="Three server racks in a row in a basement room, two dashboards mounted above them, a cedar wall to the right" caption="The server room from the door: racks 1 to 3, the dashboards above them. Rack 0, the edge, is in the network room next door." >}}

## What it is, in one paragraph each

**The site.** Four racks. Rack 1 holds the power: four UPS at 240 V and their battery packs. Rack 2 is the storage and compute wall: the Ceph cluster, the hypervisors, the storage hub, the Pi clusters. Rack 3 holds the GPU hosts, the agents' machines, the utility hosts and the ClusterHAT rig. The transfer switches sit in racks 2 and 3, beside what they feed. Rack 0, a small enclosure in the network room, is the edge: two firewalls, the time server, the replica server, the offsite dock.

**The people and the agents.** Christoph decides. The agents do most of the typing and, within written permissions, most of the operating. Rigger builds. Bosun watches the site from inside the fabric and acts on what it sees. The commit log says who typed what, and one operation is evidenced on the as-it-stands page.

**The pattern.** Every NixOS host, most of the servers, is one file in one repository, so a dead machine comes back from git; the Macs and the Debian Pis are backed up by script instead. The inventory describes every device, cable and address, and monitoring targets are discovered from it. Notifications leave through a machine that is not the one being watched. A backup destination never holds a backup that came from itself. Those four rules are most of what lets more than one actor operate the site.

{{< n0-figure src="hand-seating-cable.jpg" alt="A hand seating a cable in a patch panel, the switch ports lit green behind it" caption="Both ends of every cable recorded before a box goes in a rack; the colour standard is on the fabric page." >}}

{{< n0-figure src="env-sensor.jpg" alt="A small temperature and humidity display clipped to a rack post" caption="Eleven sensors and one hub watch the two rooms; the summer ceiling and what was done about it are on the power page." >}}

## Status

Online 20260630. Production-ready 20260913, which means built, monitored, backed up and documented, a different thing from switched on; most of the runbooks were written between those two dates. Captured 20260920, with the figures re-measured on 20260921. The capture does not change. The next one is taken when the open list on the as-it-stands page is closed, not by editing this one. [How it grew](/updates/), from the hardware that waited in 2024 to today.
