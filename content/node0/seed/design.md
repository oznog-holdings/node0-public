---
title: "The rest of the seed design"
description: "The detail behind the ladder: network, names, backups, time, development, operating the site, monitoring, services, and the traps carried over from Node0."
layout: "n0-page"
date: 2026-09-20
source: "node0 seed v0.1, sections 4 to 12"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 2
---

This page carries the detail the ladder on the seed page points at, in the
design's order, so a person and their agents can do each part without having
done it before. The roles it names are the seed's four: the infra box, the
agent box, the core box, compute.

## Network

**One switch for the whole ladder, bought once**, chosen by where it will
sit. Out of earshot, buy an eight-port 10GBASE-T switch with two SFP+. Every
RJ45 port negotiates 10G down to 1G, so the infra box runs at 10G and the
2.5G boxes are unaffected. Its cost is a fan, 39 to 41 dBA against a 34 dBA
floor, measured by ServeTheHome. In a living space, buy a fanless eight-port
2.5G switch, since nothing in rungs 1 through 4 saturates 2.5G. Its catch is
that SFP+ takes a DAC, so 10G on copper then needs a hot-running module per
device. A five-port switch is the wrong buy either way, because the gap to
the next model up is less than the cost of the swap.

**Check the negotiated speed after plugging anything in.** Our 2.5G USB
adapters report "USB 10/100 LAN" while linking at 1G, and anything without
NBASE-T, the 2.5G and 5G copper standard, links at 1G.

Wire the infra, agent, core and compute boxes, and leave the laptop on wifi.
Run one flat network, with no VLANs before rung 5. DHCP stays on the consumer
router, with a reservation per box. Never run a second DHCP server to work
around a router that cannot be told to stop, because two responders is the
failure to avoid.

**Tailscale from rung 1.** The infra box is the subnet router and laptops
accept routes. Hosts inside the site never accept routes, or they prefer the
tunnel to the LAN beside them. No port forwards, ever. A full-tunnel VPN
client on the laptop captures the routes to the site, so every host goes dark
while the internet stays up.

**The site owns a domain from rung 1**, its names in one subdomain, from a
registrar with an API because rung 1's certificates want DNS-01 challenges.
Never use a made-up TLD or `.local`. One collides with the internet, the
other with mDNS. Only the subdomain is answered locally, and names outlive
boxes.

## DNS: AdGuard Home until rung 5, then Technitium

Seed runs **AdGuard Home** for one reason. The site's records belong in the
config repo, and AdGuard on NixOS is fully declarative.

    services.adguardhome = {
      mutableSettings = false;
      settings.filtering.rewrites = [
        { domain = "infra.site.example.com"; answer = "<the infra box>"; }
      ];
    };

Adding a name is then a one-line diff and a deploy, and a dead core box
comes back from the repo with its names intact. The rung 3 move is one list
rendered twice. The core box's configuration and the container's yaml are
generated from the same rewrites, so there is no second copy, no zone
transfer and nothing to drift. Two limits are worth knowing. Rewrites produce
no PTR records, which nothing in rungs 1 through 4 needs, and ad filtering is
on by default.

**Switch to Technitium at rung 5** on a trigger rather than on taste. The
triggers are a real router whose DHCP should update DNS, a second site that
should be a true secondary, or reverse zones per segment once VLANs are
taken. Technitium brings zones, AXFR, PTRs, delegation, DNSSEC and an API,
and the migration is an afternoon, since the rewrites list becomes one zone
file. Records then live in the server, so "records in the repo" becomes a
push script. One trap waits for that day. Its API sets the PTR flag as a
replace, so deleting a record destroys the reverse entry of whatever else is
at that address.

## Backups

Backups are the first job on the first box, and the last thing allowed to
break silently. Two flows run, and they stay apart.

- **The site's own data.** Backrest on the infra box runs restic to Backblaze
  B2 daily, with an application key that has no delete rights, into the
  bucket whose 30-day hidden-version window was set at rung 0. The set is
  documents, finance, photos, appdata, the Forgejo data and the flash backup,
  the irreplaceable and the small. Bulk media waits for rung 5's second site.
- **The laptops and the agent box.** Backrest on each machine backs up every
  two hours to a restic **rest-server on the infra box started with
  `--append-only`**, one repository per machine. Forget and prune run nightly
  on the server, since the clients cannot delete, and that job is the **one
  writer**. That directory reaches the offsite store as an **rclone mirror to
  a separate bucket**, never as a restic backup of restic repositories, and
  **from a ZFS snapshot taken after the maintenance window**. The 30-day
  window stops the mirror mirroring a deletion.

We learned every rule below by breaking it.

- **Never a backup of a backup.** A destination never holds data that
  originated from itself, because those chains compound and loop.
- **One writer per repository** for backup, forget and prune.
- **Pin the host name in every plan** (`--host <machine>`), or reverse-DNS
  drift forks the lineage into orphans under an address-derived name.
- **403 on every retry means orphan packs**, because a pack landed
  server-side after the client gave up and every retry is refused as an
  overwrite. With no restic process running, run `unlock`, then
  `repair index --read-all-packs`. Ordinary interruptions resume by
  themselves.
- **Backrest does not reload a hand-edited config.** Verify through its local
  API, never the file.
- **Re-read the exclude list on every change.** An exclude for a path that
  later becomes real drops it with no error.
- **Run a weekly verify sweep**: snapshot freshness per repository, then
  `restic check --read-data-subset=N/26` with N stepping from 1 to 26 across
  the weeks, kept in a state file and advanced only after a green run, so every
  pack is read back over half a year. A fixed `1/26` reads the same twenty-sixth
  every week. Plain `restic check` reads the index, not the data.
- **Run a weekly restore test.** A few small files per repository in
  rotation, compared by hash, with **skipped** raised as its own alarm. Only
  `restore` proves a file comes back.
- **Run a quarterly application restore** from the offsite store rather than
  the local copy. Load a database dump into a scratch container and count the
  rows against production.
- **Fail closed at the source.** An unmounted dataset presents as an empty
  directory and backs up successfully, protecting nothing. Snapshot, check the
  mount, back up.
- **Database consistency** comes from the application's own nightly dump or a
  snapshot, never from copying a live data directory.
- **Check the bucket lifecycle yearly** against the billing report, not the
  size shown on the bucket.

## Time

Run internal NTP from rung 1, for agreement rather than accuracy. Alert
timestamps, commits, snapshots and log lines then line up during an incident,
and the LAN stays consistent through an internet outage. Run chrony on the
infra box, then on the core box. Clients name the internal server with
`prefer` and the public pool without it, since chrony chooses by quality and
not by order. The core box carries `local stratum 10` so it keeps
serving through a long WAN outage, and `makestep 1 3` lets a box that booted
without a real-time clock jump to the right time. Nothing in these rungs
punishes clock skew hard enough to want GPS.

## Development on the agent box

Development lives on the agent box rather than on the compute box or the
laptop. Anything scheduled on a laptop stops when the lid closes, and the
failure looks like the remote end. The filesystem is the other reason. APFS
is 5 to 10x slower than ext4 or XFS at package installs, worktree creation
and deleting `node_modules`, and worse again in parallel, as Theo (t3.gg)
measured across five filesystems in "MacOS Is Making Your Mac Slow"
(20260820). The Mac is the right inference backend and the wrong place to run
worktrees.

**The dev volume is not the OS.** The OS is disposable and comes back from
the repo. `/work` is a separate XFS volume on a second NVMe or partition, so
it survives every rebuild and never needs restoring.

- One directory per user under `/work`, one for the person and one for an
  unprivileged agent account. Numeric user ids travel with rsync and NFS, so
  fix them before the first shared mount and never renumber them.
- The package store sits on the same volume as the worktrees, since hard
  links and reflinks only work within one filesystem. Turn on hard-link
  installs, which on XFS takes deletion and recreation from 7 s to under 3.
- **Source trees are backed up; stores and build output are not.** Forgejo
  holds the repos of record, but not unpushed commits, untracked files or a
  half-finished branch. Backrest backs up each user's tree every two hours,
  excluding `node_modules`, the store, `target` and `dist`. At the rung 2
  move, retire the old volume only once the new one is verified.

**XFS with reflink, and no compression layer underneath** (decided 20260920)
until a NixOS module for one exists, since a hand-built device-mapper volume
would make the volume that survives rebuilds depend on a systemd unit. ZFS
and btrfs were slower at parallel worktree creation, and reflink already
shares unchanged files between worktrees. The rule behind the choice is to
benchmark before the first instance of a class, record the result, and make
the winner the standard.

**Agents and humans share one repository**, and each rule here came from an
incident. Each agent works in **its own worktree**, and nobody shares a
checkout. **In a shared checkout the git index is shared process state**, so
stage and commit in one command naming explicit paths, and never
`git add -A`, because another agent's commit takes whatever is staged with no
error. **Never run a bare `git reset --hard`**, since a tree dirty with other
people's changes is normal; undo your own change by path. **Every
long-running job records its state to a file in the repo**, newest first, and
commits at green states.

At rung 1 the same layout applies inside the agent VM, recreated at rung 2
rather than copied.

## Operating the site

### Secrets and access

**A password manager before the first server**, and a separate authenticator
app, so the vault and the second factor are not one app with one failure. One
item per device, titled the device's name.

Secrets have three states. **At rest** they are encrypted in the repo's
secrets files, the password manager and the flash backup. **At runtime** a
secret is a plaintext file at mode `0600`, neither synced nor in git. **In
transit** it never passes through a synced folder, since a sync client
replicates a stray key everywhere within minutes. The Unraid flash holds host
keys, so its backup is encrypted and off-box.

- **Keys for routine access, passwords as break-glass.** One key per human
  and per agent, and every host gets every laptop's key, or the laptop in the
  shop is the one that locks you out.
- **Machine secrets are encrypted to three recipients**: the laptop's key,
  the host's key, and an offline master key held only in the password manager,
  which is what makes a reinstall survivable. Unraid, lacking the tooling,
  keeps its few in a mode `0600` directory on the pool.
- **On NixOS the host's ssh key is its decryption identity**, so keep a copy
  off the host. Never render a secret with `writeText`, because it lands
  world-readable in `/nix/store`, and rotating does not re-render it.
- **A vault service waits until rung 5.** A single member seals on every
  reboot with nobody to unseal it, and even with ours the boot-critical
  secrets stay in the encrypted files. Add one when rotating a secret means
  editing more than a handful of files, or when a second agent host needs
  attributed reads.
- **The recovery pack** exists from rung 1, in two places, neither of which
  is the site. It holds a bare mirror of the config repo, the restic
  passwords, the object store keys, the master key, the flash backup and its
  passphrase, the host identity tarballs, and a one-page order of operations.
  Rehearse it once on spare hardware with the infra box off.
- **No user directory until rung 5, and possibly not then** (decided
  20260920): single sign-on for remote access, per-box ssh keys for hosts, the
  password manager for the rest. A directory must be up before anyone can log
  in. The trigger is a third human.
- **Three boundaries from rung 1, and no VLANs** (decided 20260920): IoT on
  the router's guest network, the NixOS firewall denying inbound by default,
  the agent user unprivileged with sudo for named commands only.
- Three ssh facts read as something else. A timeout can be OpenSSH 9.8 and
  later penalising the source after failed logins. A correct key can be
  denied because `/etc/ssh` is not mode `0755`. `ssh-keygen -R` removes the
  whole `known_hosts` line.

### Deploying from the repo

- Track a **`deploy` ref rather than `main`.** Promotion is one push after
  the change is read, and a bad deploy is reverted by moving the ref.
- **Pull-deploy fails closed.** A failed fetch must refuse rather than build
  the cached tree and exit 0. Ours did not, and every "successful" deploy was
  old.
- **Rebuild one machine on purpose**, and make it the agent box, because a
  restore procedure is trusted only once it has run.
- **Build every host's closure nightly from `deploy`**, so a failed build is
  an alert before it is a broken deploy.
- **A bad deploy of the OS is a reboot, not a rebuild**, since NixOS keeps
  every generation in the boot menu. Keep a monitor and keyboard within reach,
  and give every box a rescue boot entry with automatic fallback. A generation
  cannot roll back application state, which is what the sandbox is for.
- **The identity store** holds every host's ssh host key as a tarball on the
  infra box, in the backup set from the day it is built, checked before any
  wipe.
- **Disable, do not delete.** A declaration out of service stays, disabled,
  with the evidence and the condition that would bring it back.

### A sandbox, so agents can break things that do not matter

- **A sandbox VM on the infra box, from the same repo**, with its own name
  and nothing of production in it, where a change to a role is deployed first.
  It is marked a sandbox in the inventory, **not monitored** by design, and
  not brought back after a reboot.
- **A throwaway VM of any host, on the agent box.** `nixos-rebuild build-vm
  --flake .#core` boots that host's configuration under QEMU with nothing
  shared.
- **Scratch containers on the infra box** for trying a service. Each gets a
  separate docker network, plus a name and address no real service will have,
  and goes away when the trial ends.

Three rules keep it from becoming a second production. **No production
secrets.** It gets its own, with throwaway values. **No route to production
data.** It sits on an isolated network with NAT out and nothing in, and the
only production data it sees is a read-only mount of a copy. **What it
teaches leaves as a commit or a runbook line.**

### Discipline for agents (and people) operating the site

A command can appear to do one thing and do another, or report success while
doing nothing, and the output still looks like evidence. The defence is to
**assert the state you want, from a source that cannot be the thing you are
testing.** Four cases matter most. A failed command is not a finding, so
verify DOWN from a second angle. A correlated event is not evidence, so ask
what a person touched. Accepted with a warning is not applied. A stray wait
outlives the session that started it. Our operating-traps runbook holds the
rest.

### The agent kit

**A long-running agent process** handles the work that happens while nobody
is at a keyboard, and ours is Hermes. **ntfy carries alerts and a phone
messenger carries conversations**, because an alert in a chat stream scrolls
away. **A session manager for coding agents** gives one sidebar across every
machine's sessions. **LLM subscriptions** are not in the cost table, since
they depend on use and the gateway meters them.

### Inventory

A `hosts.md` in the repo with name, role, address, MAC, location and arrival
date is the whole inventory a small site needs. Update it in the same commit
as the DHCP reservation and the DNS record. Pull every management device's
config to the repo on a schedule, from the day the device arrives.

## Monitoring

Keep monitoring small, and build it on the rules rather than the tools. **The
stack** (decided 20260920) is Prometheus, Alertmanager, node_exporter and the
blackbox exporter as containers on the infra box, with alerts to ntfy. Every
rule here is an age or a growth expression, which a simple uptime checker
cannot express. Ours could not say "backup older than 36 hours", so we
removed it. The seed repo, when it is built, will ship the compose file and the
rules together, so the person edits a target list rather than PromQL.

- **Alert on staleness, never on errors alone.** Silence is not success. A
  stopped writer leaves its last file in place and raises no error, so every
  job publishes a completion timestamp and the alert fires on the age of that
  timestamp.
- **Deploy the alert with the producer, not before**, or it pages about
  unfinished work, and deployed rules do not un-deploy themselves.
- **Verify every alarm once by causing the condition**: pull the UPS plug,
  stop the backup timer, unplug the core box.
- **A dead-man alert that always fires**, to the phone at a slow cadence, so
  silence from the monitoring itself is noticed.
- **Use growth rather than absolutes for drive health.** Alert on reallocated
  sectors increasing over 24 hours, never on the count, because a threshold
  becomes a silence that rots past the disk it was written for. The counts
  belong on a dashboard, with the serial.
- **Read the scrub result.** Repaired bytes or checksum errors on a pool that
  stays ONLINE is the alert Unraid does not send. An overdue scrub is its own
  alert.
- **The notifier logs its own failures**, since a paging service that is down
  eats the alarm about itself.
- **The capacity alarm compares the delta, not the total**, or it fires on
  every run in steady state, and an alarm that always cries is worse than
  none.
- **Financial and personal data never enter the monitoring stack**: ages,
  counts and completion times only.

The floor for rung 1 goes to a phone by ntfy and covers backup age per
repository, restore-test result, scrub result and scrub age, SMART growth,
UPS state, disk free, and one dead-man. Grafana waits, because the product at
rung 1 is a phone that buzzes and not a wall of graphs.

## Services

Two lists follow. The first is what every seed site runs whatever it is for.
The second is decided by need, and fits on the infra box.

### Core services: present at every site

| service | rung | where |
|---|---|---|
| DNS | 1 | infra, then core with infra second |
| NTP | 1 | infra, then core with infra second |
| UPS monitoring | 1 | infra as server, every box a client |
| Backrest and the rest-server | 1 | infra |
| Restore rehearsal | 1, moves at 3 | infra, then core |
| Mesh VPN | 1 | infra as subnet router, agent box second at rung 2 |
| Forgejo | 1 | infra |
| Caddy | 1 | infra |
| LLM gateway | 1 | infra |
| Notifications | 1, moves at 3 | ntfy on infra or hosted, own ntfy on core at 3 |
| External dead-man | 1 | a hosted check pinged by the monitoring |
| Monitoring | 1 | infra, probes from the agent box at rung 2 |
| Syncthing | 1 | infra, with staggered versioning |
| Device config backup | 1 | infra, on a schedule |
| Home Assistant | 1, moves at 3 | infra as a container, then core, so it outlives infra |

Two rows carry a reason. An alert about the infra box should not pass through
it, so notifications move to the core box at rung 3, and the external
dead-man covers the gap until then. A box cannot observe its own absence, so
the monitoring probes the infra box from the agent box.

Five things wait until a seed site becomes a fleet: a self-hosted mesh
control plane, a full inventory system, an exposure scanner, the vault, and
central log aggregation. journald with a size cap is fine at three hosts, and
we needed aggregation only at forty. The rest of a build host's work belongs
on the agent box or the core box.

### By need: any of these, all of them, or none

| service | for | the thing to know |
|---|---|---|
| Paperless-ngx | documents | It ignores an API filter it does not recognise, with no error, and returns everything. Verify ingest by checksum before deleting the source, and give the container a real scratch mount, since its OCR writes to `/tmp` whatever the setting says. |
| Stirling PDF | splitting and merging before ingest | Stateless, but its office-document path defeats some spreadsheets, so keep the original. |
| Immich | photos | Uploads are copied into its storage, so a source may be retired once every file is verified by hash and both the storage and the database are in the backup set. External libraries are referenced in place, so deleting the tree deletes the photos. |
| A finance stack | accounts and books | Metrics export operational values only, the dump is nightly and in the backup set, and a wall display pulls a rendered frame, never a balance. |
| Environmental monitoring | temperature, humidity, power | Sensors report to Home Assistant on the core box, and the values reach the monitoring as metrics. |
| Media servers | films, music, audiobooks, books | Config on the pool, media read-only, transcoding passed through, every item in its own folder. |

Whatever else is added, automation and chat included, takes the same shape:
config on the pool, data in a named share, a completion timestamp the
monitoring can read, and a line in `hosts.md`.

## Traps carried over from Node0

The sections above carry most of them in place. These are the rest, each
written up in one of our runbooks or in the lesson collection.

| trap | what happens |
|---|---|
| macOS headless | upgrades drop permission grants, a pending prompt hangs a job with no output, Spotlight and the media daemons eat a server, CLI auth is per machine, and APFS is case-insensitive, so verify copies by count |
| Unraid RAM root | `/home`, `/tmp` and the crontab vanish at reboot, with nothing to signal it |
| Unraid docker networking | a custom `--network` makes Unraid drop its own, addresses collide after edits, and a host on ipvlan cannot reach its containers |
| `docker.img` | it fills from writable layers and one container takes the rest down; use a docker directory |
| object store lifecycle | all versions bills pruned packs forever, last version only makes a bad prune unrecoverable by morning; 30 days from hiding to deleting |
| Pi boot | SD wear kills always-on Pis, and a Pi 4 boots with no idea of the time |
| manageability filters | one NIC variant's filter ate outbound DHCP below the driver; treat that variant as suspect |
| consumer routers | some cannot be told to stop serving DHCP, and some devices ignore the link they are plugged into |
| copy then delete | a transfer that failed with no error, plus an `rm` in the same command, destroyed three irreplaceable recordings; copy, verify, delete, as three observed steps |
