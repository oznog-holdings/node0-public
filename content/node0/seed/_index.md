---
title: "Build a starter Node0"
description: "The smallest expandable version of Node0, for one person or a small business: what to buy, what to run, and the order to do it in."
layout: "n0-landing"
date: 2026-09-20
captured: "20260920"
source: "node0 seed v0.1 (design of 20260920), sections 1 to 3 and the cost totals of section 13"
sanitized: "checklist v0.1, 20260921; hosts by role, reference hardware described not named, no vendor links; voice pass 20260921"
photo: "bench-seed.jpg"
photo_alt: "A workbench with a laptop, two small white computers, a small network switch and a monitor, tools on the wall behind"
photo_caption: "Where it starts: the spare hardware on the bench, unconfigured, before rung 1 goes up. Photographed 20260921."
---

It is called a seed, not a lite version, on purpose. A lite version would be a smaller copy of Node0. A seed is the same pattern at the size it starts, and what it grows into is not Node0 but your own site. It is written for someone who has never run a server, will lean on agents to learn, and wants each purchase to be the last one they need until they choose the next. Point your agent at it with what you have and what you need.

Version 0.1, 20260920. Prices checked 20260920, US. Derived from the internal design, sanitized 20260921 against checklist v0.1. The detail behind everything below is on [the rest of the design](design/).

## Not far from how Node0 began

Node0 started as a laptop, one agent machine and one storage box on a bench. It grew into racks, Ceph, a stratum-1 clock and a two-firewall edge. Almost none of that is needed for the thing that mattered: a place where a person and their agents share infrastructure they own, that keeps working when the laptop is closed, and that can grow one box at a time without a rebuild.

The difference between then and now is everything that was learned on the larger site: which services earn their keep, what monitoring has to exist before the first incident rather than after, what worked and what did not, and a plan to grow rung by rung instead of finding out later what the growth should have been. Everything below was learned at some cost. Where a lesson holds the fuller story, it is named.

## What has actually been run

Each rung says whether it exists only on paper, is in progress on the bench, has been deployed on spare hardware, or is running as someone's site. This table is the seed's own status and is kept current; a document that says which parts have been run is worth more than one that implies all of it has.

| rung | state | hardware | date | what diverged from the design |
|---|---|---|---|---|
| 0 | in progress | the laptop; a bucket | 20260921 | nothing yet; fills in as rung 0 runs |
| 1 | designed | | | |
| 2 | designed | | | |
| 3 | designed | | | |
| 4 | designed | | | |
| 5 | designed | | | |

Four states: designed, in progress, deployed on spare hardware, running as someone's site. Rung 0 is in progress; the spare hardware for rung 1 is on the bench; each row fills in as it happens, and the parts list with prices is published once rungs 0 and 1 have run.

**Build log**, newest first, one entry per session on the bench:

- **20260921.** Rung 0 started on the laptop. The spare hardware for rung 1 laid out on the bench and photographed, unconfigured.
- **20260920.** Design v0.1 finished, after two review rounds.

## Ten principles

Every rung below is built to these. They are numbered because they are referred to by number.

1. **Start with the smallest complete thing that works.** Every rung is a working site, not a stage of one.
2. **Nothing that has to keep running lives on the laptop.** The laptop closes, travels and sleeps.
3. **The operator's hands survive the outage they are needed for.** The agent host is separate from the infrastructure host as soon as it can be, and resolves names without it.
4. **Backups of the core data exist before the second box does.** Offsite, append-only, restore-tested. Not a later rung.
5. **Silence is not success.** Every unattended job is watched for staleness, not for errors. Every alarm is proven once by causing the condition it watches for.
6. **Everything has a name, a reservation and a record.** Even at three boxes.
7. **Own the parts of the network that break you, leave the rest alone.** DNS and time from rung 1; DHCP and wifi stay on the consumer router until a real one arrives.
8. **Expandable means added, not swapped.** Compute is a list of backends behind one gateway.
9. **Configuration in git, secrets in the vault, nothing in between.** The repo can rebuild every box; the password manager holds what the repo must not.
10. **Copy, verify, delete, as three observed steps.** Never a deletion in the same command as the transfer it depends on.

## Four roles

Node0 has many roles. The seed collapses them to four, and the first three can start as one box. The laptop is a client; it is never a role, and that includes development.

| role | what it is | first hardware |
|---|---|---|
| infra | storage, services in containers, VMs, backups, the model gateway | an all-flash Unraid box; the reference is a palm-sized eight-slot NVMe unit with one 10 GbE port |
| agent | the always-on host the agents run on, and the development box for people who write code | a VM on infra, then a small x86 box: an N100-class mini PC for agents alone, a Ryzen mini PC if it is also the dev box |
| core | DNS primary and NTP primary, plus the small things that must outlive infra: notifications, the restore rehearsal, the home hub | starts on infra, then a second N100 mini PC, or a Raspberry Pi on SSD |
| compute | local model inference | none, then a Mac, a DGX Spark, a GPU box, or several |

The test for whether something gets its own hardware is not dedicated versus virtual. It is: is this part of the bootstrap layer, or a consumer of it? Physical is right for what must exist before anything else works, or must survive the failure of its host layer. Everything else virtualises. That is why core and the agent earn boxes and the gateway does not.

## The ladder

Each rung is a complete site. Move when the previous rung's failure mode has actually bitten, or when the money is there and the next failure is obvious. Rungs 0 to 3 order by failure mode; 4 and 5 are branches, ordered by what you want.

{{< n0-diagram name="ladder" caption="Each rung is a complete site. The arrows say what failure moves you up; after rung 3 the ladder branches." >}}

### Rung 0: the laptop, with backups already running

**Buy:** nothing. A cloud bucket and a domain.

**Do:**

- The core data (documents, finance, photos, the config repo once it exists) goes offsite from day one. A backup tool on the laptop is fine here; it is the only job the laptop is allowed to carry, and only until rung 1.
- Two keys and one lifecycle rule make the bucket safe. The writer key can upload and hide but never permanently delete; an admin key, kept in the password manager, is the only thing that can; a 30-day rule before hidden versions are removed is the protection. "Keep only the last version" is no protection at all.
- Restore something before trusting it. A backup nobody has restored is a belief.

**Cost:** 0, plus 10 to 25 a month.

**What still fails:** everything lives on the laptop, so everything stops when it closes.

### Rung 1: the infrastructure box

**Buy:** an all-flash Unraid box (the reference: eight M.2 slots, a 10 GbE port, 16 GB stock), the licence tier that covers the drive count, a 2.5G or 10G switch, two or three NVMe drives, one 1500 VA UPS on USB, cables.

**Do:**

- ZFS pools, no parity array: two drives a mirror, three or four raidz1, five or more raidz2. Choose for the drive count you will end at, because a raidz group can take one more drive at a time but never changes its parity level, and a mirror does not become raidz without rebuilding the pool from backup. A second mirror or a second group can always be added beside the first.
- Run the stock 16 GB through rungs 1 and 2. Buy memory when a workload asks for it, and on that day buy 32 GB unless 48 GB is under 1.5 times its price (on 20260921 it was not).
- DNS and time move here from the consumer router, as containers. The model gateway exists from this rung, because it meters hosted spend and every later compute box is one more entry behind it.
- The UPS shuts the box down cleanly; the shutdown is tested by pulling the plug, once.
- Backups move off the laptop and onto this box, with the same two keys.

**Cost:** 1,580 lean, 2,580 full, 3,430 with 48 GB.

**What still fails:** everything is on one box, including the names and the clock. The operator's agent still lives on the laptop.

### Rung 2: the agent gets its own box

**Buy:** a small always-on x86 box. Agents only: an N100-class mini PC with 16 GB and a 2.5G port. Agents and development: eight cores, 32 to 64 GB, two NVMe slots, still small and quiet.

**Do:**

- NixOS from the start, deployed from the site's own git forge. The learning curve is real and the agents are there to flatten it; the payoff is that this box is disposable and comes back from the repo.
- The agent host resolves names without the infra box, by carrying the site's few addresses in its own hosts file from the repo. It never depends on the thing it is watching.
- It carries as little as possible beyond the agent: a remote-access node that also advertises the site's range, and a watcher the size of a cron job that pings DNS, backups and the web front door and sends one line when any of them fails.
- If this is also the dev box, the second NVMe is the work volume, mounted before the first repo is cloned.

**Cost:** 150 lean, 1,290 full.

**What still fails:** DNS and time still live on infra. The operator survives an infra outage; the rest of the home does not.

### Rung 3: the core box

**Buy:** a second N100-class mini PC, 150 to 220. A Raspberry Pi used to be this box; in 2026 a kitted Pi costs the same or more, and the N100 is the same architecture as the agent box, so it is the same build with a different role list.

**Do:**

- Move the DNS primary and the NTP primary here; infra's containers become the second server of both. The small box that never reboots is the primary, because resolvers try servers in order and a primary that is rebooting hangs every client.
- Three more things move here, all small and needed most when infra is down: notifications, so an alert about infra never passes through infra; the restore rehearsal, so backups are read from somewhere other than the box that wrote them; and the home hub, if the home is part of the site.
- Nothing else. Core is boring on purpose, and it is the box that handles power events, so a power event must not be able to kill it.

**Cost:** 150 lean, 220 full. Through rung 3: 1,880 lean, 4,090 full.

**What still fails:** none that takes the operator down. What remains single: the switch, the consumer router, the UPS, and every application on infra, which is what the second site and the backups exist for.

From here the ladder stops ordering by failure mode. Rungs 4 and 5 are independent branches: a site can take the edge before compute, the second site before either, or neither for a long time.

### Rung 4: compute

**Buy one or several, as funds allow:**

- A used M1 Max MacBook Pro with 64 GB (about 1,800): 64 GB of unified memory for the least money in 2026, silent, 30B-class models comfortably. Docked, lid closed, never a daily driver.
- A new Mac mini or Mac Studio at 64 GB or more (2,900 and up), the same silicon family new.
- A DGX Spark (4,999 and up): 128 GB unified, small, quiet, Linux.
- A box with GPUs: the most capacity per dollar and the only loud, hot thing in this design.

**Do:**

- Every compute box is one more backend behind the gateway from rung 1. Which model lives where is written in the repo, not clicked in a UI.
- Hosted models are cheaper and better for most small businesses; local inference is the step toward privacy, sovereignty and learning. This rung is discretionary in cost and central in purpose.

**Cost:** 1,830 lean, 5,000 full, or a GPU box's own budget.

### Rung 5: the edge and the second site

**Buy:** a real router (an N100 box running a firewall OS, 200; or a purpose-built appliance, 890), an access point if the consumer router cannot be demoted, and for the second site a rescued box with its own drives (300) or a second infra box (2,540).

**Do:**

- The router buys DHCP the site owns, with reservations in the repo and leases written into DNS; firewall rules that can be read, backed up and monitored; no double NAT, so remote access connects directly and IPv6 works.
- VLANs are not part of this rung by default. A three-box site has one credible reason to segment: devices it does not trust on the same wire as the boxes. Take it when that is true, not before.
- DNS moves from the simple resolver to a full authoritative server here, on a stated trigger, with the migration done as a copy, a verification from a third machine, and only then a cut-over.
- The second site receives an hourly, one-way, encrypted replica of the datasets that matter. It is the answer to "what if the home burns down" that the cloud bucket only half gives.

**Cost:** 600 lean, 3,580 full. Through rung 5: 4,310 lean, 12,670 full.

{{< n0-figure src="edge-rack0.jpg" alt="A small enclosed rack holding two compact firewalls, a time server, a backup dock and a consumer gateway" caption="What rung 5 could look like for you. (Node0: the edge in its own small rack.)" >}}

## What each rung costs, and what the site costs to run

Three columns. Lean is the cheapest honest version of the rung. Full is what this document recommends for someone who will develop on the site. Max is full plus the one thing full defers, the 48 GB memory, bought now rather than waited out. US prices checked 20260920; tax, shipping and spares on top; rounded to the nearest 10.

| rung | lean | full | max | what the money is |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | plus 10 to 25 a month recurring |
| 1 | 1,580 | 2,580 | 3,430 | the box; licence; switch; two or three drives; UPS; cables; max adds 48 GB |
| 2 | 150 | 1,290 | 1,290 | an N100 box; or a Ryzen mini PC plus a second NVMe |
| 3 | 150 | 220 | 220 | an N100 box; a kitted used Pi is 160 to 300 |
| **through 3** | **1,880** | **4,090** | **4,940** | the complete site without local compute |
| 4 | 1,830 | 5,000 | 5,000 | a used M1 Max plus an adapter; or a Spark; a GPU box is its own budget |
| 5 | 600 | 3,580 | 3,580 | router, access point, the replica box; the VLAN step (250 to 400) not included |
| **through 5** | **4,310** | **12,670** | **13,520** | a small Node0 |

**Recurring.** The bucket at about 7 a month per TB retained; the domain; the password manager; remote access per user if the site is a business. Electricity: lean draws about 75 W continuous, about 9 dollars a month at 16 cents; full about 100 W. A compute box changes that: a Mac adds 10 to 60 W, a Spark up to 240 W under load, a GPU box 300 to 600 W. Hosted model spend is the one line that depends entirely on use; the gateway meters it, which is one of the reasons it exists at rung 1.

**Where the 2026 prices bite.** At rung 1, drives and memory are about 40% of the full column and were about 20% of it in 2025. The design absorbs that three ways: the stock 16 GB is enough until the agent has its own box, eight slots do not need eight drives, and the smallest licence is not lost money. None of the recommendations change; what changes is the order of purchase. The parts list with links is published once rungs 0 and 1 have run.

## Why these choices

Every technology below was chosen on Node0 for a reason that still holds at seed size, and each entry says what would change the choice. [Node0 as it stands](/node0/as-it-stands/) carries the long form of each decision and what it cost.

**Unraid, for the infra box.** ZFS pools with a UI, containers and VMs on one box, and a control surface a non-operator can work at two in the morning. The classic mixed-drive array is not the reason; ZFS is. It is the one box in the seed that a person runs rather than the repo, and that is the point: it is where the site starts before there is a repo. *What would change it:* you already run TrueNAS or Proxmox well, or every drive is the same size and you want ZFS without a licence. The seed's layout (ZFS pools, no parity array) transfers.

**NixOS, for every box after the first.** A box described in one file, rebuilt from the repo, so the agent and core boxes are disposable: a dead one comes back from git in an afternoon, and the same configuration runs on the next box you buy. One language across the fleet, and the agents are good at it. The learning curve is real; the agents are there to flatten it. *What would change it:* you will never have more than one box after infra and do not want a second way of managing things. Debian with the same layout is fine, at the cost of rebuilding by hand.

**ZFS pools, no parity array.** Checksums, snapshots, and send-and-receive to the second site, which is the whole replication story at rung 5. On an all-flash box it is faster than the classic array, and it grows by adding a drive to a raidz group or a second mirror beside the first. *What would change it:* the infra box is a rescued desktop with spinning disks; then the classic parity array for bulk and a small SSD pool for services.

**A simple resolver first, a real one later.** At three boxes a rewrite list in the repo is all the DNS the site needs, and it renders into both the core box and infra's container from one file. A full authoritative server with zone transfers is rung 5, when there is a router that hands out leases to write into it. *What would change it:* you already run a real DNS server; then start there, and skip the migration.

**An append-only bucket, and a tool that restores.** Offsite from day one, with a writer key that can hide but never delete, and a restore rehearsal that reads the backups from a different box than the one that wrote them. The rule underneath: a destination never holds a backup that originated from itself. *What would change it:* never. The provider can change; the two-key shape and the rehearsal do not.

**A mesh VPN for remote access.** No port forwarding, no double-NAT fight, and the agent box as a second subnet router so remote access survives the infra box. Split DNS is how a laptop that is not at home resolves the site's names. *What would change it:* the site is a business with many users; the per-user pricing may push you to self-hosting the control plane, which Node0 does.

**Your own git forge, on infra.** The repo that rebuilds every box should not live on a service that can change its terms, and deploys pull from it. It also gives the agents a place to open branches without a vendor account each. *What would change it:* you are one person with one box; a hosted forge is fine until rung 2, when the first NixOS box needs somewhere to pull from.

**A model gateway from rung 1.** One address for every model, hosted or local, with spend metered per key. Every later compute box is one more backend behind it, which is what "expandable means added, not swapped" means in practice. *What would change it:* never; it is a container, and it is the reason rung 4 is cheap to take.

**Metrics, a notifier, and a dead-man's switch.** Unattended jobs are watched for staleness, not errors, because a job that has stopped raises none. Notifications leave through a box other than the one being watched, and the dead-man pages when the watcher itself goes quiet. *What would change it:* never. Silence is not success.

## The rest of the design

The ladder is the spine. [The rest of the design](design/) carries the detail, in the same order as the internal document, each part written so that a person and their agents can do it without having done it before: the network, DNS, backups, time, development on the agent box, operating the site (secrets and access, deploying from the repo, a sandbox, the discipline for agents and people, the agent kit, the inventory), monitoring, services, and the traps carried over from Node0. The parts list with prices follows once rungs 0 and 1 have run.

**What is next is the build.** The seed will be built on spare hardware as its own project and published alongside these pages: a public repository that is buildable, not a document that is readable. The first build by someone who is not Christoph is where this document's assumptions about a beginner get tested, and the revision that follows that build is v0.2.
