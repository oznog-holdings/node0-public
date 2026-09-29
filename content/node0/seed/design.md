---
title: "How the Seed fits together"
description: "The detail behind the ladder: network, names, backups, time, development, operating the site, monitoring, compute, services, and the traps carried over from Node0."
layout: "n0-page"
date: 2026-09-20
source: "node0 seed v0.1, sections 4 to 12"
sanitized: "checklist v0.1, 20260921; voice pass and reconciliation with the build 20260928; trimmed and linked 20260928"
weight: 2
---

This page gives the detail behind the ladder on the Seed page and its rung pages, in the
design's order. The roles it names are the Seed's four: the infra box, the
agent box, the core box and compute.

## Network

**One switch for the whole ladder, bought once**, chosen by where it will
sit. Out of earshot, buy an eight-port 10GBASE-T switch with two SFP+. Every
RJ45 port negotiates 10G down to 1G, so the infra box runs at 10G and the
2.5G boxes are unaffected. Its cost is a fan, 39 to 41 dBA against a 34 dBA
floor, measured by ServeTheHome. In a living space, buy a fanless eight-port
2.5G switch, since nothing in rungs 1 through 4 saturates 2.5G. Its catch is
that SFP+ takes a DAC, so 10G on copper then needs a hot-running module per
device. A five-port switch is the wrong buy either way, because the gap to
the next model up is less than the cost of the swap. The bench ran an
unmanaged eight-port 10GBASE-T switch, which has no configuration to back up.

**Check the negotiated speed after plugging anything in.** Our 2.5G USB
adapters report "USB 10/100 LAN" while linking at 1G, and anything without
NBASE-T, the 2.5G and 5G copper standard, links at 1G. A 10GBASE-T link can
also flap after a cold start and never settle. On 20260928 the infra box's
link went up and down 125 times in 17 minutes, and a second power cycle cured
it. A box that draws its running power but never answers gets one power cycle
before anyone chases cables. The monitoring alerts on four link changes in 10
minutes. On a Mac, a new USB network adapter shows no network interface until
its approval prompt is accepted.

Wire the infra, agent, core and compute boxes, and leave the laptop on wifi.
Run one flat network until devices you do not trust would otherwise share a
wire with the boxes. Laptops and phones stay on the consumer router's DHCP;
the servers get static addresses, set where each is installed, outside the
router's DHCP pool.
DHCP hands clients the site's DNS server, and the router must also stop
advertising itself as a DNS server in its IPv6 router advertisements (on
[OpenWrt](https://openwrt.org), `dhcp.lan.dns_service=0`), or IPv6 clients
keep asking the router. Never run a second DHCP server to work around a
router that cannot be told to stop, because two responders is the failure to
avoid.

**[Tailscale](https://tailscale.com) from rung 1.** The infra box is the
subnet router at rung 1, and from rung 2 the agent box advertises the same
range, so the site is reachable when either is up. On the bench the agent box
carried the route and infra's stayed a standby we never exercised. Laptops
accept routes. Hosts inside the site never accept routes, or they prefer the
tunnel to the LAN beside them. No port forwards, ever. A full-tunnel VPN
client on the laptop captures the routes to the site, so every host goes dark
while the internet stays up. Turn on the VPN client's LAN exclusion, or remove
the client, and have the laptop's own check fail if the site's range leaves
the wired port.

**The site owns a domain from rung 1**, its names in one subdomain, with a DNS
provider whose API token can be limited to that one domain, because rung 1's
certificates want DNS-01 challenges and the certificate job holds that token.
The Seed uses [DNSimple](https://dnsimple.com). Set a short TTL on the
challenge record, 60 seconds. Resolvers cache the old token for the record's
TTL, so a staging run blocks the real certificate that long; on the bench it
was an hour. Never use a made-up TLD or `.local`. One collides with the
internet, the other with mDNS. Local DNS answers only the subdomain.

## DNS: AdGuard Home until rung 5, then Technitium

The Seed runs [AdGuard Home](https://github.com/AdguardTeam/AdGuardHome)
because the site's records belong in the config repo, and AdGuard's
configuration can be generated from it. The names live in one list,
`dns/rewrites.yaml`, and a small script renders AdGuard's settings from it
over the pinned version's defaults. The rendered file is mounted read-only
and copied over AdGuard's own at every start, so a change made in AdGuard's
web page lasts only until the next restart. A check script reports any
difference between the repo and what each server serves before then. On the
bench AdGuard ran as a container on the infra box and, from rung 3, as a
system service on the core box.

    - { domain: infra.site.example.com, answer: <the infra box> }

Adding a name is then a one-line diff and a deploy, and a dead core box
comes back from the repo with its names intact. At rung 3 the same list is
rendered for the core box and for the infra container, so there is no zone
transfer and nothing to drift. Rewrites produce no PTR records, which nothing
in rungs 1 through 4 needs. Leave ad filtering on for every client, because
in AdGuard the rewrites are part of the filtering engine, and a client
exempted from filtering loses the site's names too.

**Switch to [Technitium](https://technitium.com/dns/) at rung 5** when one of
these appears: a dedicated router whose DHCP should update DNS, a second site
that should be a secondary, or reverse zones per segment once VLANs are
taken. Technitium brings zones, AXFR, PTRs, delegation, DNSSEC and an API,
and the migration is small, since the rewrites list becomes one zone file.
Migrate as a copy, verify every name from a third machine, and only then cut
over.
Records then live in the server, so "records in the repo" becomes a push
script. Technitium's API treats the PTR flag as a replace. Deleting one
record also deletes the reverse entry of every other record at that address.

## Backups

Two backup flows run from rung 1, and they stay apart.

- **The site's own data.** [Backrest](https://github.com/garethgeorge/backrest)
  on the infra box runs [restic](https://restic.net) nightly to
  [Backblaze B2](https://www.backblaze.com/cloud-storage) through its S3
  endpoint, with an application key that has no delete rights (made with
  `b2 key create`, as on [rung 0](../rung-0/)), into the bucket with rung
  0's 30-day rule. The set is each application's own dump, made just before, the app data without the live databases and
  repositories the dumps cover, the flash, the host identity tarballs, and
  documents, finance and photos. A start hook refuses to run if the dumps are
  more than 26 hours old or any source is empty. Bulk media waits for rung 5's
  second site, where we decide whether that site receives it.
- **The laptops and the agent box.** Each machine runs plain restic on a timer
  every two hours, with its host name pinned, to a restic
  **[rest-server](https://github.com/restic/rest-server) on the infra box
  started with `--append-only`**, one repository per machine. Forget and prune
  run nightly on the server, since the clients cannot delete, and that job is
  the one writer. The server keeps 48 hourly, 14 daily, 8 weekly, 12 monthly
  and 10 yearly snapshots per host and path. The rest-server's directory
  reaches the offsite store as an **[rclone](https://rclone.org) mirror to a
  separate bucket**, never as a restic backup of restic repositories, and from
  a ZFS snapshot taken after the maintenance window. The second bucket gets the
  same 30-day rule and its own no-delete key, and rclone runs without hard
  delete, so a deletion the mirror copies can still be recovered.

{{< n0-diagram name="seed-backup" caption="Two flows that stay apart, and the checks that prove them. The rest-server leaves the site as a mirror, never as a backup of backups." >}}

Each rule below came from a failure on Node0.

- **Never a backup of a backup.** A destination never holds data that
  originated from itself, because those chains compound and loop.
- **One writer per repository** for forget and prune, because two writers
  pruning one repository remove each other's data.
- **Judge a forget by the snapshots left, never by the exit code.** Against an
  append-only server a client's `restic forget` is refused, prints the
  refusal, and exits 0 with nothing deleted.
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
- **Run a weekly restore test.** Up to three small files per repository in
  rotation, compared by hash. A skipped test raises its own alarm, like a
  failed one. Only `restore` proves a file comes back. From rung 3 the core
  box also restores from the bucket every week, into memory with `--verify`,
  using a key that can only list and read. A read-only key cannot write a
  lock, so those restores run with `--no-lock`.
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

The quarterly restore and the yearly lifecycle check need a person, so the
core box sends each as a reminder on its date.

## Time

Run internal NTP from rung 1, so alert timestamps, commits, snapshots and log
lines line up during an incident, and the LAN stays consistent through an
internet outage. Clients of [chrony](https://chrony-project.org) name the core box with `prefer`, then the infra
box, then the public pool without it, since chrony chooses by quality and not
by order. Make it a hierarchy, not a pair. Core takes the pool, marked
`prefer`, and infra; infra takes only the pool. Without `prefer` on the core
box, chrony can pick infra, and the primary then takes its time from the
second server. Two servers that list each other time each other in a loop
through an internet outage and never fall back to their own clocks.

The core box carries `local stratum 10`, so it keeps serving through a long
WAN outage. A Pi has no clock, so it also carries `orphan activate 0.1` and
serves only after one real sync. `makestep 1 3` lets a box that booted without
a clock jump to the right time. On the bench a Pi that started 9 hours behind
corrected itself in one step 22 seconds after boot and never served the wrong
time as good. On 20260924 we blocked the internet's time servers for three
hours, and every box stayed within a few milliseconds of the others. Nothing
in these rungs punishes clock skew hard enough to want GPS.

On the infra box chrony runs as a container on the host network with the
right to set the clock, and [Unraid](https://unraid.net)'s own NTP is off.
Applying that setting moved the clock back by a few seconds, and chrony's
first step corrected it. chrony refuses a comment on the same line as a
directive and will not start, and no check of the
[NixOS](https://nixos.org) configuration runs chrony's own parser. We check
rendered files with `chronyd -p` and keep comments on their own lines.

## Development on the agent box

Development lives on the agent box rather than on the compute box or the
laptop. Anything scheduled on a laptop stops when the lid closes, and the
failure looks like the remote end. The filesystem is the other reason. APFS
is 5 to 10× slower than ext4 or XFS at package installs, worktree creation
and deleting `node_modules`, and worse again in parallel, as Theo (t3.gg)
measured across five filesystems in "MacOS Is Making Your Mac Slow"
(20260820). The Mac is the right inference backend and the wrong place to run
worktrees.

**The dev volume is not the OS.** `/work` is a separate XFS volume on a second
NVMe or partition, so it survives every rebuild and never needs restoring. On
20260927 we rebuilt the agent box from the site's
[Forgejo](https://forgejo.org) forge, and `/work` came through untouched. A
reinstall must never format it. Declare `/work` in the disk layout as a
partition with no filesystem, make the filesystem once by hand, and pin its
UUID. The mounts for the agent's state and its backup then refuse any `/work`
that is not the pinned one. Our first layout listed `/work` for formatting,
and we caught it by reading the layout before the first rebuild.

- One directory per user under `/work`, one for the person and one for an
  unprivileged agent account. Numeric user ids travel with rsync and NFS, so
  fix them before the first shared mount and never renumber them.
- The package store sits on the same volume as the worktrees, since hard
  links and reflinks only work within one filesystem. Turn on hard-link
  installs, which on XFS takes deletion and recreation from 7 s to under 3.
  pnpm 11 reads `pnpm_config_*` and ignores `npm_config_*`; with the old names
  our installs came out as reflinks with a link count of 1, so check the link
  count after the first install.
- **Source trees are backed up; stores and build output are not.** Forgejo
  holds the repos of record, but not unpushed commits, untracked files or a
  half-finished branch. restic backs up `/work` every two hours, excluding
  `node_modules`, the store, `.cache`, `target` and `dist`, and refuses to run
  if `/work` is not mounted or the agent's tree is empty. When `/work`
  moves from the rung 1 VM to the rung 2 box, retire the VM's volume only
  after comparing file counts and hashes.

**XFS with reflink, and no compression layer underneath** (decided 20260920).
A hand-built device-mapper layer would make the volume that survives rebuilds
depend on a systemd unit; revisit when NixOS has a module for one. ZFS and
btrfs were slower at parallel worktree creation in our benchmark of 20260920,
and reflink already shares unchanged files between worktrees. The rule behind
the choice is to benchmark before the first instance of a class, record the
result, and make the winner the standard.

**Agents and humans share one repository**, and each rule here came from an
incident. Each agent works in **its own worktree**. Where a checkout is
shared anyway, its git index is shared process state, so stage and commit in
one command naming explicit paths, and never `git add -A`, because another
agent's commit takes whatever is staged with no error. **Never run a bare
`git reset --hard`**, since a tree dirty with other people's changes is
normal; undo your own change by path. Every long-running job records its state
to a file in the repo, newest first, and commits at green states.

At rung 1 the same layout applies inside the agent VM, recreated at rung 2
rather than copied.

## Operating the site

### Secrets and access

**A hosted password manager before the first server** (the Seed uses
[Bitwarden](https://bitwarden.com)), and a separate authenticator app, so the
vault and the second factor are not one app with one failure. One item per
device, titled the device's name.

**At rest** secrets are encrypted in the repo's secrets files, the password
manager and the flash backup. **At runtime** a secret is a plaintext file at
mode `0600`, neither synced nor in git. **In transit** it never passes through
a synced folder, since a sync client such as
[Syncthing](https://syncthing.net) replicates a stray key everywhere within
minutes. The Unraid flash holds host keys, so its backup is encrypted and
off-box.

- **Keys for routine access, passwords as break-glass**, kept for emergencies only. One key per human
  and per agent, and every host gets every laptop's key, or the laptop in the
  shop is the one that locks you out.
- **Machine secrets are encrypted to three recipients**: the laptop's key,
  the host's key, and an offline master key held only in the password manager,
  so a reinstalled host's secrets can still be decrypted
  ([sops](https://github.com/getsops/sops) with
  [age](https://age-encryption.org) keys on the bench). Unraid, lacking the
  tooling, gets its few from the site's password manager at deploy time, as
  `0600` files in a `0700` dataset on the pool. A Debian core box keeps one
  age file encrypted to the same three kinds of key.
- **On NixOS the host's ssh key is its decryption identity**, so keep a copy
  off the host. Never render a secret with `writeText`, because it lands
  world-readable in `/nix/store`, and rotating does not re-render it.
- **A vault service waits for a trigger, whatever the rung.** A single member
  seals on every reboot with nobody to unseal it. Node0 runs a vault, and even
  there the boot-critical secrets stay in the encrypted files. Add one when
  rotating a secret means editing more than a handful of files, or when a
  second agent host needs attributed reads.
- **A self-hosted password manager at rung 1**
  ([Vaultwarden](https://github.com/dani-garcia/vaultwarden), one collection
  per identity) gives agents attributed reads early without the unseal
  problem. Vaultwarden is a password manager, not a vault service, and nothing
  the site needs to boot or restore may live only in it. Move routine secrets
  across as a copy, prove the backup and a restore, and only then trim
  Bitwarden to the break-glass set: the pack's passphrase, the site password
  manager's own unlock and admin token, root on infra and the router, the
  master key, every backup password and key, the DNS token, and the key that
  pauses the external dead-man (a hosted check that alarms when expected
  pings stop). If the proxy's own password lives in the
  site's password manager, a restore needs a bootstrap: start the proxy
  ([Caddy](https://caddyserver.com)) with a throwaway hash, restore the
  password manager, then set the real hash.
- **The recovery pack** is one encrypted file on each of two sticks, one fully
  off site and one on site in a separate place. It holds the config repo as a
  git bundle, every restic password and rest-server login, the bucket keys
  including one that can only read, the master key, the agent's login to the
  password manager, the flash backup, the host identity tarballs, a one-page
  order of operations, and the sha256 of every file. Its passphrase lives in
  the hosted password manager and on paper, never in the pack. A script builds
  it. It finds each stick by serial, because the Unraid boot flash is a USB
  stick too, and it reads the new pack back and decrypts it before deleting
  the previous one. Fetch every branch before bundling, and pack only the key
  line of the master key: our first rehearsal found a stale deploy branch and
  a master key that age refused.

  Rehearse it on spare hardware with the infra box off. On 20260927 we
  restored the pack from the stick alone in about 4.5 minutes. On 20260928 we rebuilt the infra box on a spare mini PC from it, in
  1 hour 48 minutes, 70 of them on traps. Set the firmware clock to UTC first,
  restore only the configuration that moves to new hardware, restore the data
  with `--exclude /boot` so the old flash does not overwrite the new stick, and
  turn container autostart back on, since a restore does not carry it. Decide
  how a new Unraid stick will be licensed before you need it: a paid licence
  moved to a new stick retires the old one, and a trial is refused on a stick
  holding a restored installation. A
  fireproof safe is rated for paper, and flash fails at lower temperatures, so
  the off-site copy is the one that covers a fire.
- **No user directory at any rung until a third human arrives** (decided
  20260920): single sign-on for remote access, per-box ssh keys for hosts, the
  password manager for the rest. A directory must be up before anyone can log
  in.
- **Three boundaries, and no VLANs** (decided 20260920): guest and IoT
  devices on their own wifi networks, each a routed segment that reaches only
  the internet, with the LAN allowed to open connections into IoT and IoT
  allowed none back; every host's firewall denying inbound by default; the
  agent user unprivileged with sudo for named commands only. The last two hold
  from rung 1. The wifi segments need a router you control, so they come at
  rung 5, or at any rung if you already run one; until then wifi stays on the
  consumer router.
- Some ssh failures look like something else. A timeout can be OpenSSH 9.8 and
  later penalising the source after failed logins. A correct key can be
  denied because `/etc/ssh` is not mode `0755`. `ssh-keygen -R` removes the
  whole `known_hosts` line, including any other names on it.
- **Account connectors come with an agent's login.** Logging an agent tool in
  with a person's account also connects that account's mail, documents and
  calendars, so switch the connectors off for every agent and check the tool's
  list. On a Mac nobody logs into at the screen, an agent cannot save its
  login to the keychain; use the tool's long-lived token in a file only that
  account can read.

### Deploying from the repo

- Track a **`deploy` ref rather than `main`.** Promotion is a pull request
  from `main`, merged fast-forward only when the build check has built every
  host from that exact commit, and a revert takes the same path. The ref takes
  no direct pushes, from admins either.
- **Pull-deploy fails closed.** Compare the fetched commit with the remote
  ref, and stop if the fetch failed or they differ. Ours built the cached tree
  and exited 0, and every "successful" deploy was old. Each box pulls every 15
  minutes with a read-only deploy key and the forge's pinned host key. End
  every deploy by asking the running service what it serves and restarting on
  any difference, and check each rendered file with the program's own parser.
  One of our deploys copied new files and failed before the restart, and the
  next run saw no change.
- **Rebuild one machine on purpose**, and make it the agent box, because a
  restore procedure is trusted only once it has run. We rebuilt the agent box
  on 20260927 with no one at the box, from a keyed installer on its own USB
  stick and a one-time boot entry, in about 4 minutes from restart to
  answering. Check the firmware's boot entries after an install, since ours
  still pointed at the wiped boot partition.
- **Build every host's closure for each pull request into `deploy`, and again
  nightly**, so a failed build is an alert before it is a broken deploy.
- **A bad deploy heals itself.** Give every NixOS box boot counting and a
  rescue entry that runs from memory. A new generation gets three tries and is
  marked good only when a check after boot proves the network, ssh, the forge
  and `/work`; otherwise the box boots the last good generation by itself.
  Write the loader's `preferred` entry for the new generation, because it does
  not count tries against `default`, and point `default` at the last
  generation that was marked good. The hardware watchdog, with a panic on boot
  failure, turns a hung boot into a counted try. On 20260928 a deploy with no
  network rolled back in 22.5 minutes, three tries of about 7 minutes each,
  with nobody at the box, and the rescue entry reaches ssh in 27 seconds. A
  generation cannot roll back application state; test those changes in the
  sandbox.
- **The identity store** holds every host's ssh host key, and the agent box's
  Tailscale state and forge deploy key, as tarballs on the infra box, in the
  backup set from the day it is built. Without them a rebuilt box rejoins the
  tailnet (your Tailscale network) as a new machine and needs its route approved again. Before any wipe,
  check that the host's tarball is in the store, opens, and is owned by root.
- **Disable, do not delete.** A declaration out of service stays, disabled,
  with the evidence and the condition that would bring it back.

### A sandbox, so agents can break things that do not matter

- **A sandbox VM on the infra box, from the same repo**, with its own name
  and nothing of production in it, where a change to a role is deployed first.
  It is marked a sandbox in the inventory, **not monitored** by design, and
  not brought back after a reboot. It follows `main`, so every change reaches
  it as soon as it is pushed, and production follows `deploy`.
- **A throwaway VM of any host, on the agent box.** `nixos-rebuild build-vm
  --flake .#core` boots that host's configuration under QEMU with nothing
  shared.
- **Scratch containers on the infra box** for trying a service. Each gets a
  separate docker network, plus a name and address no real service will have,
  and goes away when the trial ends.

**No production secrets.** The sandbox has its own, with throwaway values.
**No route to production data.** It sits on an isolated network with NAT out
and nothing in, enforced on the infra box and never inside the sandbox, and it
reaches only the forge's git port and the internet. **What it teaches leaves
as a commit or a runbook line.**

### Discipline for agents (and people) operating the site

A command can appear to do one thing and do another, or report success while
doing nothing, and the output still looks like evidence. The defence is to
**assert the state you want, from a source that cannot be the thing you are
testing.** A failed command is not a finding, so verify DOWN from a second
angle. A correlated event is not evidence, so ask what a person touched. When
a command accepts a setting with a warning, read the setting back. Kill any
wait loop you started before the session ends.

### The agent kit

**A long-running agent process** handles the work that happens while nobody
is at a keyboard, and ours is
[Hermes Agent](https://github.com/NousResearch/hermes-agent). **[ntfy](https://ntfy.sh)
carries alerts and a phone messenger carries conversations**, because an alert
in a chat stream scrolls away; the Seed's messenger is
[Telegram](https://telegram.org) first. **A session manager for coding
agents**, [herdr](https://herdr.dev/), gives one sidebar across every
machine's sessions. The kit is not yet part of any rung: it is coming, and
gets its own guide once it has been built and tested on the bench. The coding agents are pinned in the agent box's configuration
with their self-updaters off, because they release faster than the operating
system's channels. **LLM subscriptions** are not in the cost table, since
they depend on use and the gateway ([LiteLLM](https://github.com/BerriAI/litellm))
meters them. A subscription plan can sit behind the gateway with its own
limits on one key, as the bench's coding plan does; read the plan's terms
first.

### Inventory

A `hosts.md` in the repo with name, role, address, MAC, location and arrival
date is the inventory's record. Update it in the same commit as the DNS
record. The bench also ran [NetBox](https://github.com/netbox-community/netbox)
from rung 1, filled from `hosts.md` by a small sync that reports any
difference; a small site can keep the file alone. Pull every management
device's config to the repo on a schedule, from the day the device arrives.
On the bench a daily job pulls the router's export over ssh with a key allowed
only that command, with secrets redacted on the router, adds the UPS
settings, and commits both to a repository of their own.

## Monitoring

**The stack** (decided 20260920) is [Prometheus](https://prometheus.io),
Alertmanager, node_exporter and the blackbox exporter as containers on the
infra box, with alerts to ntfy. Every rule here is an age or a growth
expression. Our simple uptime checker could not say "backup older than 36
hours", so we removed it. The Seed repo ships the
floor's rules with a unit test for each, run before every deploy, and the
bench's containers as Unraid templates to copy. Prometheus and Alertmanager
listen on localhost only, behind the proxy with a password.

- **Alert on staleness, never on errors alone.** Silence is not success. A
  stopped writer leaves its last file in place and raises no error, so every
  job publishes a completion timestamp and the alert fires on the age of that
  timestamp.
- **Deploy the alert with the producer, not before**, or it pages about
  unfinished work and keeps paging until someone removes it.
- **Verify every alarm once by causing the condition**: cut the UPS input,
  stop the backup timer, unplug the core box. On 20260927 cutting the UPS
  input sent no "on battery" alert, because the one read inside the shutdown
  saw "SHUTTING DOWN" and counted it as mains. Treat every status other than
  mains as a power event. Put the switch and the router on the UPS too, or
  during a real cut no alert can leave the site. On the bench they stayed on
  mains, so the 20260927 test did not prove that path. To shorten the test, raise
  the runtime threshold; a high charge threshold trips at once, because the
  charge reading fell from 100% to 79% in 40 seconds. After a UPS shutdown the
  infra box stays off when the mains returns until someone cycles its power.
- **A dead-man alert that always fires**, to the phone at a slow cadence, so
  silence from the monitoring itself is noticed. The same alert pings a hosted
  check ([Healthchecks.io](https://healthchecks.io)) every minute, which emails
  when the pings stop. With the infra box fully down its email arrived in
  about 6 minutes, and on 20260924 it was the only alarm in a 12-minute
  outage. Pause it before a planned shutdown.
- **Use growth rather than absolutes for drive health.** Alert when a drive's
  error counters grow over 24 hours (on NVMe, media errors and error-log
  entries), and on any critical-warning bit, never on a count, because a fixed
  threshold stays silent on the next disk. The counts belong on a dashboard,
  with the serial.
- **Read the scrub result.** Repaired bytes or checksum errors on a pool that
  stays ONLINE are the alert Unraid does not send. An overdue scrub is its own
  alert.
- **The notifier logs its own failures**, since a paging service that is down
  eats the alarm about itself. From rung 3, alerts about the core box and
  about failed delivery go to a hosted topic, since core's notifier cannot
  carry news of its own absence.
- **The capacity alarm compares the delta, not the total**, or it fires on
  every run in steady state.
- **Financial and personal data never enter the monitoring stack**: ages,
  counts and completion times only.

{{< n0-diagram name="seed-alerts" caption="An alert about a box never travels through that box. The dead-man proves the path by going quiet." >}}

The floor for rung 1 goes to a phone by ntfy and covers backup age per
repository, restore-test result, scrub result and scrub age, SMART growth,
UPS state, disk free, and one dead-man.
[Grafana](https://grafana.com/oss/grafana/) waits, because rung 1 needs
alerts on a phone before it needs dashboards. The UPS needs its own reader
every 10 to 15 seconds, faster than the 5-minute producer. From rung 4 a
probe sends one completion through the gateway every 5 minutes, and an alert
fires when none has succeeded for 20 minutes.

## Compute

Only the gateway holds a compute box's key, so spend and use stay metered in
one place. On the
bench the compute box runs [llama.cpp](https://github.com/ggml-org/llama.cpp)'s
`llama-server`, because it allocates its memory at start and a ceiling then
holds by construction. Measure what the operating system needs with the model
out, and set the ceiling below the GPU's own working-set limit. A small
supervisor stops the server when memory pressure leaves normal. Set its
free-memory threshold below what the ceiling leaves free; our first threshold
stopped the server before the ceiling was reached.

At rung 4b one router process serves chat, embeddings, a reranker and
speech-to-text in under 44 GiB. Each kind either falls back to a hosted model or
fails closed. Embeddings fail closed, because vectors from another model would
quietly corrupt the index, and private audio never leaves the house. We chose
each model by a rule written before measuring. We turn off llama-server's
prompt cache for every model we do not chat with, since it grew the small
models by about 0.5 GB per request and cut reranking accuracy from 95% to
40%. A benchmark that repeats one prompt measures the cache, so first-token
time comes from a cold prompt.

## Services

The first list is what every Seed site runs. The second is decided by need,
and fits on the infra box.

### Core services: present at every site

| service | rung | where |
|---|---|---|
| DNS | 1 | infra, then core with infra second |
| NTP | 1 | infra, then core with infra second |
| UPS monitoring | 1 | infra drives the UPS and serves its state; core reads it and reports; only infra shuts itself down |
| Backrest and the rest-server, Forgejo, Caddy, Vaultwarden, NetBox, the LLM gateway | 1 | infra |
| Restore rehearsal | 1, moves at 3 | infra, then core |
| Mesh VPN | 1 | infra as subnet router, agent box second at rung 2 |
| [Postgres](https://www.postgresql.org) and [Valkey](https://valkey.io) | 1 | infra, shared by the gateway and NetBox |
| Notifications | 1, moves at 3 | a hosted topic at rungs 1 and 2; own ntfy on core at 3, the hosted topic kept for alerts about core |
| External dead-man | 1 | a hosted check pinged by the monitoring |
| Monitoring | 1 | infra, probes from the agent box at rung 2 |
| Syncthing | 1 | infra, with staggered versioning |
| Device config backup | 1 | infra, on a schedule |

A box cannot observe its own absence, so the monitoring probes the infra box
from the agent box. The agent box's watcher is one scheduled script that sends
straight to ntfy. It also asks Unraid's own web page, which answers with the
array stopped, so its message says whether the services or the whole box are
down.

These wait until a Seed site becomes a fleet: a self-hosted mesh control
plane, an exposure scanner, the vault, and central log aggregation. journald
with a size cap is fine at three hosts, and we needed aggregation only at
forty. A Seed needs no separate build host; builds run on the agent box.

### By need: any of these, all of them, or none

None of these ran on the bench; each gets its own guide once it has.

| service | for | the thing to know |
|---|---|---|
| [Home Assistant](https://www.home-assistant.io/) | the home, if it is part of the site | A container on infra, then on core at rung 3 so it outlives infra. |
| [Paperless-ngx](https://docs.paperless-ngx.com/) | documents | It ignores an API filter it does not recognise, with no error, and returns everything. Verify ingest by checksum before deleting the source, and give the container a writable scratch mount at `/tmp`, since its OCR writes to `/tmp` whatever the setting says. |
| [Stirling PDF](https://www.stirlingpdf.com/) | splitting and merging before ingest | Stateless, but its office-document path defeats some spreadsheets, so keep the original. |
| [Immich](https://immich.app/) | photos | Uploads are copied into its storage, so a source may be retired once every file is verified by hash and both the storage and the database are in the backup set. External libraries are referenced in place, so deleting the tree deletes the photos. |
| Finance: [Sure](https://github.com/we-promise/sure) for accounts, fed by [SimpleFIN](https://www.simplefin.org/), with [Metabase](https://www.metabase.com/) for reports; the books in [Beancount](https://beancount.github.io/), read through [fava](https://beancount.github.io/fava/); statements from [Ledgersync](https://ledgersync.com/) | accounts and books | Buy the bank feed and the statements, never scrape a bank's portal, so no bank login lives on the site. Keep the books as plain text in a private repository, one ledger per entity, which an agent can rebuild, diff and check. Metrics export operational values only, the dump is nightly and in the backup set, and a wall display pulls a rendered frame, never a balance. |
| Environmental monitoring | temperature, humidity, power | Sensors report to Home Assistant on the core box, and the values reach the monitoring as metrics. |
| Media: [Jellyfin](https://jellyfin.org/), [Navidrome](https://www.navidrome.org/), [Audiobookshelf](https://www.audiobookshelf.org/), [Kavita](https://www.kavitareader.com/) | films, music, audiobooks, books | Config on the pool, media read-only, the GPU passed through for transcoding, every item in its own folder. |

Whatever else is added, automation and chat included, takes the same shape:
config on the pool, data in a named share, a completion timestamp the
monitoring can read, and a line in `hosts.md`.

## Traps carried over from Node0

The sections above carry most of them in place. These are the rest.

| trap | what happens |
|---|---|
| macOS headless | upgrades drop permission grants, a pending prompt hangs a job with no output, Spotlight and the media daemons eat a server (Spotlight indexed our 45 GB of model files, so turn it off), CLI auth is per machine, and APFS is case-insensitive, so verify copies by count; an agent with no login session cannot use the keychain |
| Unraid RAM root | `/home`, `/tmp` and the crontab vanish at reboot, with nothing to signal it |
| Unraid docker networking | a custom `--network` makes Unraid drop its own, addresses collide after edits, and a host on ipvlan cannot reach its containers |
| `docker.img` | it fills from writable layers and one container takes the rest down; use a docker directory |
| Unraid defaults | besides auto start and the cache ceiling on [rung 1](../rung-1/), any stick labelled `UNRAID` can be booted as the system; Docker started from an ssh session breaks `docker exec` when that session ends |
| object store lifecycle | keeping all versions bills pruned packs forever; keeping only the last version makes a bad prune unrecoverable by morning; set 30 days from hiding to deleting |
| Pi boot | SD wear kills always-on Pis, so boot from an SSD with the SD card kept as the way back; many portable SSDs drop off a Pi 4 until `usb-storage.quirks=<vendor>:<product>:u` is on the kernel command line |
| manageability filters | one NIC variant's filter ate outbound DHCP below the driver; treat that variant as suspect |
| consumer routers | some cannot be told to stop serving DHCP |
| copy then delete | a transfer that failed with no error, plus an `rm` in the same command, destroyed three irreplaceable recordings; copy, verify, delete, as three observed steps |
