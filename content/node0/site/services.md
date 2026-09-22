---
title: "Services"
layout: "n0-layer"
layer: 7
gist: "The layer a person actually touches: the names, the proxy in front of them, and the applications behind them."
figures: ["53 containers on one host", "18,791 documents", "105,873 photos and 21,284 videos"]
photo: "room-from-door.jpg"
photo_alt: "Three racks seen straight on from the doorway, with dashboards on the wall above them"
photo_caption: "The three racks and the dashboards, straight on."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.7"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 7
---

## What this layer is for

Every layer below this one exists so somebody can type a name into a browser
and get their paperwork back. Services is the set of those names. Two
reverse-proxy instances turn a container's private port into a stable,
TLS-protected hostname, and the applications sit behind those names. If a
part of Node0 has a name a family member could say out loud, it lives here.

## How it is built

Two Caddy instances on unraid1 carry every name. One faces the public
internet with four names: the chat server, the photo library, the mesh
coordinator (the remote-access mesh), and a split-horizon notification name
that terminates TLS here and proxies onward to the notification server on
core2. The other carries the internal names, now well over two dozen.
Certificates come from DNS-01 against the domain's DNS provider. HTTP-01
cannot survive the load-balancer path in front of the site, and TLS-ALPN-01
breaks for any name whose SNI is routed elsewhere, so DNS-01 is the only
challenge left.

Tier the services by how much it would hurt to lose them, because that
ordering decides which probe you write first. On Node0 the top tier is the
one where a quiet failure blocks recovery of everything else, and it holds
Forgejo with its runner pool on dev3, dev4, sandbox1 and the macOS runner
dev2, together with the mesh coordinator. The daily tier holds Immich,
Paperless-ngx, NetBox, the media servers (Jellyfin, Navidrome,
Audiobookshelf, Kavita, Pinchflat), Matrix (tuwunel), n8n, and the Grafana
and Prometheus web interfaces themselves. The convenience tier holds
Stirling PDF, Dozzle, Krusader and the rest, worth a probe but not a page.

The finance stack is deliberately not one more container on that shared
fleet. It is fin1, its own Proxmox guest, built 20260915 to 20260918 on
NixOS. It runs Sure as the ledger engine, Metabase as the dashboard, and
fava over the reconstructed Beancount ledgers. Loaders on systemd timers
pull from a statement-feed aggregator and two payment processors into
Postgres. Mail is the smallest service here. Only the four Proxmox nodes run
a mail transfer agent at all, and they relay outbound through a large
provider's SMTP relay authenticated by address, with no credential stored on
the fleet.

### Hosts

| name | role | form | rack | OS |
|---|---|---|---|---|
| unraid1 | the hub: both proxy instances and 53 containers | 4U Supermicro chassis | rack 2 | Unraid OS 7.3.2 (no systemd) |
| nexus | retired as a service host, now an hourly encrypted pull replica of unraid1 | small SSD NAS | rack 0, network room | Unraid OS |
| fin1 | the finance guest | virtual machine on a Proxmox node, 4 vCPU, 8 GB, 40 GB ext4 | rack 2 | NixOS |
| wallboard1 | drives two rack-top displays | Raspberry Pi 4B | rack 2 | Grafana kiosk (OS not stated in the source) |
| slate1 | the e-ink finance frame | Raspberry Pi Zero W | in the home, not in the racks | Raspbian 13 |

### The applications a person chooses to add

This is what someone running the pattern adds, grouped by the need it
answers. None of it is required. The seed runs with none of these and gains
each one on a need.

| need | what Node0 runs | the thing to know |
|---|---|---|
| every document in one place | Paperless-ngx with Postgres, Redis, Tika and Gotenberg; Stirling PDF for splitting and decrypting before ingest; a desktop scanner pipeline | 18,791 documents on 20260921. Ingest is verified by checksum before any source is deleted |
| photos, out of the cloud | Immich with its own Postgres, hardware transcoding, and machine learning on a GPU host | 105,873 photos and 21,284 videos on 20260921, in 506.8 GB on the 20260920 capture. External library trees are referenced in place and must never be deleted |
| media | Jellyfin, Navidrome, Audiobookshelf, Kavita, Pinchflat | config on the NVMe pool, media read-only; every item in its own folder; transcoding passed through |
| finances | Sure with Metabase; Beancount ledgers with fava, in a private repository; loaders for the statement feed and two payment processors; slate1 as the e-ink add-on | the D7 rule: no financial value ever enters the fleet monitoring stack, only ages and counts |
| bringing data home | cloud exports (photos, mail archives, file storage) land on the hub and are ingested | one pattern for every source: transfer, verify by checksum or count, then delete, as three observed steps |
| git and CI | Forgejo with four Actions runners (three on NixOS, one for macOS) | 36 repositories and 18 users, carried from the 20260920 capture; the deploy ref and pull-deploy are what make the public site a site |
| chat and automation | Matrix (tuwunel) with a public name; n8n | each is one more database in the backup set; a seed site uses a chat bot and skips Matrix |
| the home | Home Assistant with Zigbee, Thread and Matter radios on env1, its own Pi on its own VLAN | Prometheus is the one timeline, Home Assistant the sensor and actuator hub |
| a wall that shows the state of things | wallboard1 driving two displays; slate1 for one figure at a time on e-ink | a Grafana kiosk on a Pi; the e-ink panel refreshes only when the figures change |

### The failure domain

Nearly the whole layer sits on one Unraid box. unraid1 hosts 53 containers
on 20260921, both proxy instances among them, so unraid1 down means every
internal name is unreachable at once. That includes Grafana's and
Prometheus's own web interfaces, and the monitoring stack on the same box
stops with it. A layer cannot notice its own absence, so the notice has to
come from a box outside it. On Node0 that box is core2, which carries the
dead-man alert. fin1 fails independently and has its own restic repository,
but every route to it passes through the internal proxy, so unraid1 down
takes fin1's reachability with it while fin1 itself stays healthy. Reload
does not work in this deployment. The reload path inside the container does
not carry the credential the proxy's admin endpoint wants, so every config
change costs a restart and a few seconds of 502s on every name it fronts.
Paperless and the smaller stateful services share one Postgres, and Immich
runs its own. Neither instance fails over; both live on the hub, so the hub is
their common failure domain.

## Why we chose it

The same form as the site-wide list on the [as-it-stands page](/node0/site/#why-we-chose-it): each project named and linked, and the reason it is here. Open source wherever it could carry the job, for the same reason as everywhere else on the site, and the two paid services below are the exceptions, named with why. We are grateful to every one of these projects and services; please support them if you are able to.

**[Paperless-ngx](https://docs.paperless-ngx.com/)**, with **[Stirling PDF](https://www.stirlingpdf.com/)** in front of it. Every paper that arrives, scanned, text-extracted, tagged and searchable, and the agents answer questions against it. Stirling splits and decrypts before ingest, so nothing is handed to the archive that it cannot read.

**[Immich](https://immich.app/).** The photo library, out of the cloud: faces and places indexed on the site's own GPU, external library trees referenced in place rather than copied, backed up under the same rules as everything else.

**[Jellyfin](https://jellyfin.org/), [Navidrome](https://www.navidrome.org/), [Audiobookshelf](https://www.audiobookshelf.org/), [Kavita](https://www.kavitareader.com/), [Pinchflat](https://github.com/kieraneglin/pinchflat).** Video, music, audiobooks, books and archived channels, each by the tool built for exactly that shape of library, with the media read-only and every item in its own folder.

**[Sure](https://github.com/we-promise/sure) with [Metabase](https://www.metabase.com/).** The ledger engine and the dashboard over it, on the finance host that is deliberately its own guest. Sure because it is the maintained community continuation of an open ledger with bank sync, rules and transfer matching built in; Metabase because the morning question is a dashboard, not a report.

**[Beancount](https://beancount.github.io/) with [fava](https://beancount.github.io/fava/).** The books themselves as plain text in a private repository, one ledger per entity, checked by a program and read through fava. Text under version control is the only form of a ledger an agent can rebuild, diff and prove.

**[SimpleFIN](https://www.simplefin.org/) and [Ledgersync](https://ledgersync.com/).** The two paid services in this list, and the reason the finance stack has no scrapers of its own. SimpleFIN is the read-only bank feed, one token per institution, for a few dollars a year. Ledgersync fetches the statements themselves, the PDFs the books are reconciled against, for the accounts it covers. Buy the feed, never scrape the portal: that rule is what keeps credentials for the banks off the fleet entirely.

**[n8n](https://n8n.io/).** Automation with a visual editor, for the workflows a person wants to see and change without reading code; one more database in the backup set.

**[Home Assistant](https://www.home-assistant.io/).** The sensor and actuator hub for the home, on its own Pi on its own segment, with the site's metrics stack as the one timeline it feeds.

Caddy, Matrix on tuwunel, Forgejo, herdr, Grafana and the notification server are on the site-wide list, because the site depends on them rather than one service.

## The decisions

### 20260809: the backends move behind the proxy

**Workload.** A dozen containers reachable by raw port on one box.

**Requirement.** A service's address should survive a move to different hardware.

**Choice.** Put every backend on an isolated tier reachable only through
Caddy, split into an external instance for the handful of public names and
an internal one for everything else.

**Accepted trade-off.** One more hop, and a proxy config that is a single
point of failure for every name.

**Verified.** Addresses stayed constant through every later move, including
the whole-host migration of 20260904, where no DNS record, proxy route or
downstream reference needed an edit.

### 20260904: migrate by same-IP stop-then-start

**Workload.** 38 containers to move from nexus to unraid1 in one day, with a
23 TB replication still running.

**Requirement.** No edits to DNS, proxy routes or hard-coded references downstream.

**Choice.** Build the new host with the same seven Docker networks, the same
names, and every container's address statically pinned to match. A service
moves by being stopped on one host and started on the other at an unchanged
address, and the same container never runs on both hosts at once.

**Accepted trade-off.** The pinning work up front, and a move that cannot be
done half-way as a canary.

**Verified.** The day ran in waves by blast radius, stateless utilities
first and the network and identity tier last, because that tier is what you
would use to diagnose a mistake in anything moved before it. The database
stacks were signed off by an actual OCR run, not a loaded page. Immich went
last of all, on 20260905 from 05:15 to 05:35, held back until the 11.9 TB
external library tree it depends on had finished replicating. Its asset
counts matched exactly before and after.

### 20260907: the internal proxy's config goes into git

**Workload.** The routing table for what was then 26 internal names.

**Requirement.** The config should not exist only as a running state edited live.

**Choice.** Check the file into the repository, with the deploy command and
its traps in the header.

**Accepted trade-off.** There is still no automatic deploy. The file says so
on purpose, so nobody mistakes a repository edit for a live one.

**Verified.** The same pass found three legacy tools superseded. They were
removed rather than left running as a false signal of coverage (20260909).

### 20260915: D7, the finance and monitoring boundary

**Workload.** A ledger engine, a dashboard, and the loaders that feed them.

**Requirement.** The fleet monitoring stack may know that the books are
fresh, and must never know what is in them.

**Choice.** fin1 is its own guest, monitored by the shared stack exactly
like any other host, for host metrics, sync freshness and backlog age. No
transaction or balance value is ever allowed into that stack, and the
finance dashboard is Metabase, never the fleet Grafana.

**Accepted trade-off.** Two dashboard tools on purpose, and a second place
to look during an incident.

**Verified.** The live exports are shape only. On 20260920 the monitoring stack could say that every required account was reporting and that none needed re-authentication, and it carried the reconciliation queues as counts with no value attached; the counts themselves stay inside.

### 20260918: two-mode search, and no AI feature

**Workload.** Search over the whole Paperless corpus.

**Requirement.** Answer real reconciliation questions well enough to stop looking.

**Choice.** Tune the fuzzy-search threshold and keep two-mode search. Do not
build an embedding-backed search integration.

**Accepted trade-off.** No semantic search, and the tuning is revisited as
the corpus grows.

**Verified.** Measured against 22 real questions on 20260918, two-mode
search cleared 88% top-5 recall, which was enough.

## What it cost

Replacement costs for this layer are being researched and will be added.
Purchase prices are not published. The bill of materials of 20260920 lists
the hardware that carries this layer with both cost columns still marked "to
be researched".

## What broke

- **Lesson 2.7, Fifty-three containers, four probes, and a monitoring tool
  with zero monitors configured.** A week of monitoring watched hosts, disks
  and switches and almost nothing watched the services they exist to provide.
  The uptime tool that looked like coverage had no monitors in it at all.
- **Lesson 3.13, Everything moves off nexus: the migration and its USB boot
  saga.** unraid1 could not reliably boot its own operating system from USB,
  a failure the firmware boot menu could not see. The fix was to stop using
  USB boot at all.
- **Lesson 3.2, The library that isn't a copy: Immich's external-library
  rule.** A photo tool that references trees in place holds pointers rather
  than copies, and nothing in its interface tells you which thumbnails are
  the only copy.
- **Lesson 3.4, The Paperless scratch directory and the docker.img ceiling.**
  The document manager's own scratch setting was correct, and the OCR tool it
  shells out to ignored it and filled the container platform's fixed-size
  image twice.

## State on the day

**Healthy on 20260921.** unraid1 carries 53 containers and both proxy
instances. Immich holds 105,873 photos and 21,284 videos. Paperless holds
18,791 documents. Forgejo has 36 repositories, 18 users and its four
runners, carried from the 20260920 capture because the forge API was not
reachable on the night. fin1 is built and reporting its shape-only counts.
nexus runs as an hourly encrypted pull replica of unraid1.

**Open.** slate1 fetches its frame but has never driven its panel. The
ribbon cable broke before the panel ever lit, and a replacement is expected
20260922. wallboard2 is not deployed; wallboard1 drives the displays on
racks 2 and 3, and rack 1's is not up. The internal proxy's config still has no
automatic deploy, by decision. nexus keeps its lighter second role and
leaves the site in 2027.

**Closed on the capture day.** Nothing in this layer.
