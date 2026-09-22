---
title: "Node0, as it stands"
description: "Inside a self-hosted infrastructure site: two rooms, four racks, 71 hosts, a storage cluster, a hypervisor cluster, GPU hosts behind one model gateway, and the agents that help run it. Its architecture, its decisions, what broke, and what it can carry, captured on 20260920 and re-measured on 20260921."
layout: "n0-page"
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, sections 1, 2, 4 and 8"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
---

Four unnoticed failures on one day in September drove the monitoring build. Since then every alert names its runbook, the inventory is the source of truth, and backups are proven by restoring them. That is how the enterprise systems its architect built for Fortune 500 companies are run, at the size of one person.

**The private site keeps changing; this capture does not.** Figures name their source and date, and estimates state their assumptions. The capture was taken on 20260920 and its figures re-measured on 20260921; two things found and fixed on the capture day are marked as such. Sanitized 20260921: no addresses, credentials or serials; hosts keep their names; the finance host is described by shape only.

Published so that many others can deploy a Node of their own: as much as can be shared without compromising this one.

On this page: [the layers](#the-layers) · [in use, and capacity](#in-use-and-capacity) · [how it came to be](#how-it-came-to-be) · [what runs on it](#what-runs-on-it-day-to-day) · [running models locally](#running-models-locally) · [what is shared](#what-is-shared-and-why) · [why we chose it](#why-we-chose-it) · [state at capture](#state-at-capture-running-and-unresolved)

{{< n0-figure src="storage-and-di-racks.jpg" alt="Two rack fronts side by side: the storage servers with their drive bays, and the fan trays of the GPU hosts" caption="Racks 2 and 3: the storage and compute wall, and the DI servers." >}}

## The layers

Eleven pages, in the order the site depends on itself: the container everything runs in, then the boundary, the data plane, what must exist before anything else can be trusted, and up through the services a person touches. Each page has the same six parts: what the layer is for, how it is built, the decisions with their trade-offs, what it cost to replace, what broke, and its state on the day.

{{< n0-diagram name="stack" caption="Read upward: each band rests on the one below. Site is the frame, power feeds everything, operations runs across every layer. Every layer page carries this drawing with its own layer lit." >}}

{{< n0-layers >}}

## In use, and capacity

Measured on 20260921 by read-only queries over the inventory export, the configuration repository and the live systems; nothing is a hand count. Each figure is what is in use today against what the site can carry, because the point of the build is the second number. The whole file of figures, with a source and date on every row, is published beside these pages. Inventory detail (cables, VLANs, interfaces) is on the layer pages.

{{< n0-numbers >}}

### Who typed the history

2,069 commits since 20260810, counted 20260921: 1,834 by Rigger, 163 by Bosun, 27 by Claude, 34 by two unattended jobs, and 11 by Christoph. Christoph decided each thing and the agents did most of the typing. That is not the same as operating it, so here is one operation with evidence.

### One agent operation, evidenced

**20260920, afternoon.** The capture's audit found that the hypervisor cluster had no scheduled guest backups: the backup server's housekeeping ran green every night around an empty datastore.

**What the agent could change.** Bosun, under its written permissions, created the nightly job (all guests except the two test VMs, so a new guest is covered the day it exists), ran it by hand on both nodes, and wrote the monitoring: a rule that pages within an hour if the job ever disappears again.

**What needed approval.** Nothing in that list; promotion to the deploy branch did, and waited for Christoph.

**How it was checked.** A real guest restored from the new archive to a scratch machine, booted isolated to a login prompt with its database up, then destroyed. Recorded in the runbook and the audit row the same evening.

## How it came to be

It began as a laptop doing everything. An agent machine followed, because work that has to keep running cannot live on a machine that closes and travels. An all-flash storage box became the hub, and the only copy of years of documents and photos, which was named as the risk it was. Then, in a little over a month, the site went from a flat consumer network to what this page describes. The longer arc, from the first hardware in March 2024 through the period when Node0 was hardware much like the seed's, is [the build log](/updates/).

| date | what |
|---|---|
| 20240320 | The first hardware purchased: servers, switches, storage. It waited. |
| 20251227 to 20251231 | Five days of building: the storage hub, the first DI servers, the network gets a name. |
| 20260630 | Online: the racks powered and running. |
| 20260810 | The repository that now holds everything opens with Rigger's first commits. |
| 20260818 to 20260820 | A firewall pair on a routed public block, cut over after a two-day diagnosis of the provider's edge. The switch fabric goes live: three pairs, twenty-two VLANs. |
| 20260828 | Every host migrated onto its VLAN in one day. |
| 20260902 to 20260903 | A Ceph cluster of nine used Supermicro servers bootstrapped from bare metal in a day and a half. |
| 20260904 | A new storage hub, with thirty-eight containers moved onto it in one day. |
| 20260906 | A single day in which four separate failures went unnoticed. The monitoring stack is built in phases from that day. |
| 20260910 to 20260913 | Five GPU hosts behind one model gateway; a four-node hypervisor cluster; a secrets vault. |
| 20260913 | Production-ready for development, incubation and pre-production: built, monitored, backed up, documented. Guest-disk backups were found missing and closed on 20260920; the power-outage rehearsal is still pending. |
| 20260917 | Bosun, an agent, moved in-fabric to watch it all. |
| 20260920 | This capture. |
| 20260922 | Shared and made public, so others can benefit and build their own. |

## What runs on it, day to day

The site exists for the work that runs on it. Each flow below gets its own page as it is documented, with the one constraint that shaped it; together they are the data the business agents can reference, which is why each one is worth the setup.

**Running local AI models.** Every agent and process asks one gateway address; behind it, models loaded on demand on the GPU hosts and the two laptops, with hosted vendors in the same list for what local cannot do yet. Detail below. *7 GPUs + 2 laptops · 1 gateway · keys per consumer.*

**Documents.** Every paper that arrives is scanned, OCR'd, tagged and searchable; the agents answer questions against it. *18,791 documents · auto-tagging.*

**Photos and video.** A lifetime of photographs and footage, referenced in place, faces and places indexed, backed up under the same rules as everything else. It is the archive that content creation and the production studio draw from. *105,873 photos · 21,284 videos, on 20260921.*

**Finance, for a holding company and the companies under it.** Every account, card and payment processor feeds one ledger on its own host. The morning question, where do we stand in each company and across them, is answered from a dashboard rather than a login tour. Books per entity, rebuilt from statements, close on their own numbers. The agents answer against the ledger. One rule a business owner will recognise: the site's monitoring may know the books are fresh, never what is in them. *1 host · several entities · fresh daily.*

**Code and deployment.** The forge, the runners, the deploy branch: every NixOS host converges to one branch; the storage hub and the firewalls are configured by hand and backed up by script. *36 repositories · 4 runners.*

**The rooms.** Temperature, humidity, door and leak sensors, smart outlets and the thermostat for the server and network rooms, through one hub that survives the storage box: monitoring for Node0 today, and the basis for its automations later. *11 sensors · 1 hub.*

## Running models locally

One gateway address, and behind it every model the site can serve, with hosted models as further entries in the same list.

**The gateway.** LiteLLM on a guest of the hypervisor cluster, so it fails over with the cluster rather than dying with one box; we design single points of failure out wherever the layer allows. One address for every agent and process, a key per consumer, spend and latency metered, thinking and tool-use options normalised across backends.

**The backends.** llama-swap on each GPU host loads and unloads models on demand from a shared archive; two laptops serve as full-time backends; hosted vendors sit in the same list for what local cannot do yet.

**What it enables.** An agent chooses local or hosted per task by policy, not habit. A key can be limited to local backends, so a workflow that must not leave the site is held by the gateway rather than by good intentions. The bill is one number a day. A new model is a registry entry, not a project.

The [compute page](/node0/site/compute/) carries the client profiles, the placement rules, the model archive, and the traps (a gateway that is up and a backend that is not look identical from outside).

## What is shared, and why

The reason is simple. We want many others to deploy a Node of their own, so we share as much as we can without compromising the security of this one. Selected documentation and reusable tools are published from the private site through a boundary. The public repository holds everything on these pages, the figures they are drawn from, the drawings' data files, and the tools that made them. The private repository holds the site itself.

**Public.** The seed, this capture, the lessons, and the reusable tools with generic names, at [github.com/oznog-holdings/node0-public](https://github.com/oznog-holdings/node0-public) (a mirror of the site's own forge). Each tool page says input, output, and what it needs. The publication gate refuses addresses outside documentation ranges, credential shapes, credential-store names, and images that still carry metadata. Writing, diagrams, photographs and the figures file are CC BY 4.0; the tools are MIT. Both ask only for attribution.

**Private, on the site.** The configuration that rebuilds every box, the runbooks, the inventory, the credentials' locations. Everything public is derived from it through a checklist, never edited in place, and every page names the checklist version it passed. Never mirrored.

## Why we chose it

The technologies, named and linked, and the reason each one is here. We chose open source wherever it could carry the job, because software we can read, run and rebuild is the only kind that fits a sovereign site; the two exceptions, Unraid and the Arista switches, are named below with their reasons. Someone replicating this can take the same choices or their commercial equivalents, on their own values, capabilities and needs. We are grateful to every one of these projects and the people behind them; this site is built on their work. Please support them if you are able to. Then the decision ledger: what was decided, when, and the layer page that carries the long form with its trade-offs.

**[NetBox](https://netboxlabs.com/docs/netbox/).** The inventory as source of truth: every device, cable, address and VLAN, and the monitoring targets are discovered from it. At 71 hosts and 185 devices a spreadsheet stops being honest, and it stopped well before that.

**[NixOS](https://nixos.org/).** Every NixOS host, 29 of the 71, is one file in one repository; a dead one comes back from git, and a new one is the same file with a different role. The Macs, the Debian Pis and the storage hub are managed by hand and backed up by script. The agents are fluent in NixOS.

**[Forgejo](https://forgejo.org/).** The site's own git forge and CI runners, because the repository that rebuilds every box should not live on a service that can change its terms.

**[OpenBao](https://openbao.org/).** A three-node secrets vault, so a machine can fetch what it needs without a human ever having pasted it.

**[OPNsense](https://opnsense.org/).** Two firewalls with failover over the WAN, on a routed public block; rules that can be read, backed up and monitored.

**[Arista](https://www.arista.com/).** Used data-centre switches in three pairs, because a host should survive a switch, and because the fabric is where a provider diagnosis, a VLAN and a bond can all be read from one console. The other exception: proprietary hardware, chosen used because EOS is documented in depth and the agents know it well, so a switch is something they can read, diagnose and change with the same fluency as a Linux host.

**[OpenWrt](https://openwrt.org/).** The one access point inside the site, an OpenWrt One run as a dumb AP: no DHCP, no DNS and no routing of its own, each SSID mapped to a segment on a trunk, so a wireless client lands where its trust puts it and the fabric and firewalls decide the rest. Chosen because its configuration is a file we can read, version and restore, and because lesson 4.6 records what a default access point does to a network until it is told otherwise.

**[Headscale](https://headscale.net/) and [Tailscale](https://tailscale.com/).** Remote access as a WireGuard mesh, with the coordination server run on the site itself, so that who may reach what is decided here and not by a hosted control plane; the site's subnets are routed by both firewalls independently, after the outage in lesson 4.13.

**[Technitium](https://technitium.com/dns/).** Authoritative DNS as a three-member cluster with zone transfers, after the simple resolver stopped being enough. The deployed primary is still a container on the storage hub, with the two small always-on boxes as secondaries; moving the primary to the box that never reboots is the design the bootstrap page argues for and the seed follows.

**[Caddy](https://caddyserver.com/).** Both reverse proxies, public and internal, and so every name the site answers to: one configuration in git, certificates renewed by DNS challenge without a hand touching them, and a configuration a person can read in one sitting. Every service depends on it, which is why it is on this list and not the services page.

**[ZFS](https://openzfs.org/).** Checksums, snapshots and send-and-receive, which is the whole replication and consistent-backup story.

**[Unraid](https://unraid.net/).** The storage hub: ZFS pools with a UI, containers and VMs on one box, and a control surface a person can run before there is a repo. The classic mixed-drive array is not why it is here; ZFS is. It is licensed software, one of the two exceptions, kept because the hub predates the repo and a person can operate it without one.

**[Ceph](https://ceph.io/en/).** Storage that survives a whole host, grows by adding a host, and gives the hypervisors and the model archive one place to live. Proven in a lab first.

**[restic](https://restic.net/), [Backrest](https://github.com/garethgeorge/backrest), [Proxmox Backup Server](https://www.proxmox.com/en/products/proxmox-backup-server/overview).** File-level backups to an append-only bucket and a rest-server, and disk-level guest backups, with the rule that a destination never holds a backup that came from itself.

**[Proxmox](https://www.proxmox.com/en/products/proxmox-virtual-environment/overview).** The hypervisor cluster, using Ceph as an external client rather than hyperconverged, so storage and compute fail separately.

**[LiteLLM](https://github.com/BerriAI/litellm) and [llama-swap](https://github.com/mostlygeek/llama-swap).** One gateway address for every model, local or hosted, metered per key; models loaded on demand on each GPU host from a shared archive.

**[Prometheus](https://prometheus.io/), [Grafana](https://grafana.com/oss/grafana/), [Loki](https://grafana.com/oss/loki/), [ntfy](https://ntfy.sh/).** Metrics, dashboards as generated code, logs, and notifications that leave through a box other than the one being watched.

**[herdr](https://herdr.dev/).** The fleet session manager the agents live in: one sidebar across every agent and development host, with each remote session mirrored in and controllable from the operator's own machine, and the session state carried on the host so a session survives the laptop that opened it closing. It is the piece that makes a fleet of agent machines feel like one desk, and it is pinned to one version fleet-wide because the agents depend on it staying still.

**[Matrix](https://matrix.org/) on [tuwunel](https://github.com/matrix-construct/tuwunel).** The site's own chat: people and agents in the same rooms, on a server we run, over an open federated protocol, so the running record of how the site is operated belongs to the site and can reach other sites without a hosted intermediary. tuwunel because it is one Rust binary a small site can run and back up as one more database, and it is the maintained successor to the homeserver it replaced.

Two services outside the building carry the parts of the design that must not be inside it, both chosen for their reputation, their reliability and their values, which line up with ours, and both named here with thanks. **[Backblaze B2](https://www.backblaze.com/cloud-storage)** holds the offsite bucket: the small irreplaceable tier, written nightly under a rule that hides rather than deletes, so a stolen writer key cannot take the history with it. **[Hetzner](https://www.hetzner.com/)** rents the one machine off the property, the outside-in vantage point that scans the site's public surface with no credential to it, in a datacentre in Germany.

The choices that belong to one service rather than to the site, the document, photo, media, finance, automation and home stacks, are listed the same way, with links and reasons, on the [services page](/node0/site/services/#why-we-chose-it).

### The decision ledger

| date | decision | long form |
|---|---|---|
| 20260815 | The first NixOS host, to prove an agent can operate NixOS without imperative drift. Every new x86 box after it is NixOS. | [operations](/node0/site/operations/) |
| 20260816 | Ceph proven in a lab (failure domains, disk replacement, total power loss, upgrade) before any production disk. | [storage](/node0/site/storage/) |
| 20260816 | CI/CD: a runner validates every push, hosts converge to a deploy branch, promotion is one push. | [operations](/node0/site/operations/) |
| 20260817 | Fabric: management on its own VLAN; switch pairs in-rack, not across racks; every host bonds to a pair. | [fabric](/node0/site/fabric/) |
| 20260817 | DNS moves from a simple resolver to an authoritative server with three members, the second on a small always-on box the same day. | [bootstrap](/node0/site/bootstrap/) |
| 20260820 | The provider rebuilds the circuit as a transparent LAN service; firewall failover over the WAN becomes the production design. | [edge](/node0/site/edge/) |
| 20260821 | Everything moves off the first hub to a new one; the first takes a lighter second role and leaves the site in 2027. | [storage](/node0/site/storage/) |
| 20260824 | PDU and ATS management stays on an isolated VLAN with per-card rules; the boundary is the VLAN, not the transport. | [power](/node0/site/power/) |
| 20260901 | The hypervisor cluster uses Ceph as an external client, not hyperconverged. | [compute](/node0/site/compute/) |
| 20260903 | Label everything, front and back, both ends of every cable, before a box goes in a rack. | [site](/node0/site/site/) |
| 20260904 | UPS low-battery raised to fifteen minutes and made the sole shutdown trigger; storage and hypervisors shut down and return as one unit. | [power](/node0/site/power/) |
| 20260905 | If rotating a credential requires editing the repository, the design is wrong. Enforced in CI. | [operations](/node0/site/operations/) |
| 20260905 | A destination never holds a backup that originated from itself. Enforced in code. | [storage](/node0/site/storage/) |
| 20260906 | Notifications leave through a box that is not the one being watched, on their own public address, with per-host write-only tokens. | [observability](/node0/site/observability/) |
| 20260906 | The inventory system goes live as the fleet's single source of truth: every device, cable, address and VLAN, with monitoring targets discovered from it. At this scale it stopped being optional. | [site](/node0/site/site/) |
| 20260909 | Rack 2 accepted at 103% of one UPS on failover, by decision, with the arithmetic recorded. | [power](/node0/site/power/) |

## State at capture: running, and unresolved

Running is what the pages above describe. Unresolved is the list Christoph set on 20260920 as the remaining distance; the next capture is taken when the last box is ticked, not by editing this one. Closed on the capture day itself, and marked so above: the hypervisor guest backups. Closed since, on 20260922: Bosun on the in-fabric agent host, watching every notification and managing the site; its move to internal models waits on the last item below.

- The OpenBao secrets vault: full deployment, the security sweep and clean-up.
- Firewall rules tightened to actual need without becoming restrictive.
- Fuller deployment and use of the internal AI models.
- Power-outage configuration: power-on return, the walk-in and the return order, tested by causing the condition.
- Spare hardware and parts inventory.
- Current RMAs processed and received.
- A second wallboard, and the display on top of rack 1; racks 2 and 3 have theirs.
- The hypervisors moved to on-board SATA; the RAID cards removed.
- Additional smart outlets: the network room's air conditioner, two server room fans.
- Monitoring refinements over the next few weeks.

Beyond the list, the four things that would change what the site is rather than finish it, none of them scheduled: more GPU compute, staged in as the work demands it, into rack space and power already waiting; a whole-site generator, so an outage becomes a fuel question rather than a battery one; a second provider with BGP over the site's own address space, so one line and one provider stop being the single points of failure the landing page admits to; and the 34,000 BTU mini-split the power page prices, dedicated cooling for the server room, which the GPU growth would bring forward.

Still to come on these pages: the bill of materials by layer with replacement costs, researched before publication.
