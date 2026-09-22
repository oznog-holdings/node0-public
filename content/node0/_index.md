---
title: "Node0"
description: "A sovereign, self-hosted infrastructure site in two rooms of a home in northern Utah: built by one person and a set of agents, documented in the open, and the pattern anyone can start from."
layout: "n0-landing"
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 1; the public site plan of 20260920"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
photo: "studio-dark.jpg"
photo_alt: "A dark studio: a desk with a glowing workstation, and beside it three server racks lit by their own LEDs and two dashboards"
photo_caption: "The studio, lights off. The racks run whether or not anyone is at the desk."
cascade:
  showDate: false
  showReadingTime: false
---

Node0 is a real place: two rooms, four racks, a fabric of six switches, nine storage servers, a UPS wall, a set of GPU hosts behind one model gateway, and the agents that help run it. Christoph built it over 2025 and 2026, most of the distance in six weeks of the summer of 2026, out of pocket. It runs the work of Oznog today: development, incubation and pre-production of digital intelligence work that has to stay private.

These pages are written to be read by a person and used by their agents. Point an agent at them and tell it what you have on the bench and what you need the site to do. It will find the rung to start on, the decisions that transfer, and the lesson that would otherwise cost you the same time it cost us. Every page names its source and its date, so an agent can tell a rule from an instance.

It is not a datacenter and does not pretend to be one. It runs on one fibre line and battery, not two providers and a generator. What it has instead is the discipline of one. The inventory is the source of truth. Every alert names its runbook. Backups are proven by restoring them. A dated capture of the whole site is what these pages are derived from.

## Three doors

{{< n0-doors >}}

## Why it is published

We want many others to deploy a Node of their own, so we share as much as we can without compromising the security of this one. Everything on these pages is derived from the private site through a checklist. Humans other than Christoph appear by role and agents by name. There are no addresses, credentials, serials or paths, and the finance system is described by shape only. Every page names its source and the checklist version it passed. This is the first drop. What is here first, on purpose, is the architecture, the design decisions with their trade-offs, the lessons and the rules we run by, because those are what we believe transfer, and because many of the lessons and rules were distilled from the runbooks in the first place. As the site matures and each piece proves itself, the other artefacts a builder would want will follow the same route out: runbooks, configuration, the monitoring and management scripts, the agents' skills, each sanitised for privacy and security before it leaves. The pages, the figures they draw on, the drawings' data files and the tools live in one public repository: [github.com/oznog-holdings/node0-public](https://github.com/oznog-holdings/node0-public).

{{< n0-figure src="room-from-door.jpg" alt="Three server racks in a row in a basement room, two dashboards mounted above them, a cedar wall to the right" caption="The server room from the door: racks 1 to 3, the dashboards above them. Rack 0, the edge, is in the network room next door." >}}

## What it is, in one paragraph each

**The site.** Four racks. Rack 1 holds the power: four UPS at 240 V and their battery packs. Rack 2 is the storage and compute wall: the Ceph cluster, the hypervisors, the storage hub, the Pi clusters. Rack 3 holds the GPU hosts, the agents' machines, the utility hosts and the ClusterHAT rig. The transfer switches sit in racks 2 and 3, beside what they feed. Rack 0, a small enclosure in the network room, is the edge: two firewalls, the time server, the offsite dock.

**The people and the agents.** Christoph decides. The agents do most of the typing and, within written permissions, most of the operating. Rigger builds. Bosun watches the site from inside the fabric and acts on what it sees. The commit log says who typed what, and one operation is evidenced on the as-it-stands page.

**The pattern.** Every NixOS host, most of the servers, is one file in one repository, so a dead machine comes back from git; the Macs and the Debian Pis are backed up by script instead. The inventory describes every device, cable and address, and monitoring targets are discovered from it. Notifications leave through a machine that is not the one being watched. A backup destination never holds a backup that came from itself. Those four rules are most of what lets more than one actor operate the site.

{{< n0-figure src="hand-seating-cable.jpg" alt="A hand seating a cable in a patch panel, the switch ports lit green behind it" caption="Both ends of every cable recorded before a box goes in a rack; the colour standard is on the fabric page." >}}

{{< n0-figure src="env-sensor.jpg" alt="A small temperature and humidity display clipped to a rack post" caption="Eleven sensors and one hub watch the two rooms; the summer ceiling and what was done about it are on the power page." >}}

## Status

Online 20260630. Production-ready 20260913, which means built, monitored, backed up and documented, a different thing from switched on; most of the runbooks were written between those two dates. Captured 20260920, with the figures re-measured on 20260921. The capture does not change. The next one is taken when the open list on the as-it-stands page is closed, not by editing this one. [How it grew](/updates/), from the hardware that waited in 2024 to today.
