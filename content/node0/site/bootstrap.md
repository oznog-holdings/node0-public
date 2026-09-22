---
title: "Bootstrap"
layout: "n0-layer"
layer: 4
gist: "The services that must exist before anything else comes up: names, time, power signals, secrets, and a way to rebuild a host."
figures: ["3 resolvers, 3 platforms", "3 NTP sources, 1 GPS", "3-member vault"]
photo: "core-and-cluster.jpg"
photo_alt: "A rack bay holding a pair of transfer switches, two small core hosts, several single-board probes, and a cluster of Raspberry Pis on a shelf."
photo_caption: "The core hosts and the small cluster share a shelf with the transfer switch pair."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.4"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 4
---

## What this layer is for

Bootstrap is what has to work before any other part of Node0 can come up on its
own. A name resolves, a clock agrees with every other clock, a host learns its
power has gone away, a machine fetches a secret nobody typed in for it, and a
machine that lost its disk gets rebuilt without anyone remembering how.

Every other layer leans on this one, and this one leans on almost nothing above
it. Christoph settled the boundary while placing the long-running monitoring
agent, with one question. Is this thing part of the bootstrap layer, or a
consumer of it?

Two kinds of thing answer yes: whatever must exist before anything else works,
and whatever must survive the failure of the layer it sits on. On Node0 that is
the firewalls, the secondary nameservers, core1 and the console attachment.
Everything else is a workload and can virtualize. This layer, mostly, cannot.
It did not arrive as a plan. It accreted, each time Node0 found the same
failure twice.

## How it is built

What must exist before anything else can be trusted gets its own small
hardware, and the small box that never reboots is the primary. On Node0 those
boxes are core1, a Raspberry Pi 4B, and core2, a small x86 laptop. Between them
they carry a secondary nameserver each, one of the three time sources, both
power-event daemons and one vault member, and no workload at all. One service
breaks the rule. The editable DNS primary is a container on the storage hub,
and the failure domain below says what that costs.

**Names.** Three Technitium DNS servers run on three platforms, clustered so
that blocklists and policy replicate between them automatically. Zone data
moves on its own path, by signed transfer from the one editable primary. That
primary is ns1, a container on the storage hub. The secondaries are ns2 on
core1 and ns3 on core2.

**Time.** Three sources serve the site. ntp1 is a GPS-disciplined appliance and
the site's one independent hardware clock. ntp2 is a chrony container on the
storage hub. ntp3 runs on core1, with public servers as the fallback. Every host
carries all three resolvers. Every host also carries its NTP servers by address
rather than by name, so a cold boot needs neither DNS nor the internet to find
the time. ntp1 was an anchor on paper for most of a year, because its clients
were right to refuse a source that reported multi-second uncertainty about
itself. An external GPS antenna fixed reception on 20260910.

**Power signals.** Two NUT servers run on core1 and core2, polling the same
four UPS cards. NUT is Network UPS Tools, the daemon that reads a UPS and tells
hosts when to shut down. core1 holds the shutdown authority. core2 adds
notification and a second observer, and is deliberately not a failover.

**Secrets.** A three-member OpenBao vault spans three failure domains, with no
member on the clustered storage tier. The members are joined by raft, a
consensus protocol that keeps one agreed copy of the data across them. The
vault unseals itself. A full-site power loss therefore reforms the cluster with
nobody present, and a machine fetches what it needs unaided.

**Rebuilding a machine.** One build host, di5, rebuilds any NixOS machine from
the flake, including one with no disk yet. util2 is the fallback builder, and
also holds the nix cache and the network-boot server. Hosts converge to a
`deploy` git ref on their own schedule rather than being pushed to, so a host
that was off during a change window catches up unattended. Machines with no
out-of-band management reach a console through kvm1, a PiKVM riding the
sixteen-port switch console1. A printed bring-up card covers the case where
even the agent is away.

### Out-of-band management

Every server's management controller (the BMC, the small computer inside a
server that stays up on standby power), every switch's management port, the
UPS, strip and transfer-switch cards and the PiKVM sit on the management
segment, on the management switch, each on its own access port and never on
the host's bond. So nothing done to an operating system, a bond or a switch
pair can take remote power or a console away, and that was confirmed rather
than assumed. Two GPU hosts are the exception: their controller shares a
network port with the host and answers reliably only while the host is down.
Three more have no controller at all and use the PiKVM.

What the pulled boards taught, in the form a builder can use. They are AMI
controllers on Supermicro X10 boards; other vendors differ in detail and
rarely in kind.

- **Read a boot override back before you trust it.** Set while the
  controller is still settling after a power change, it returns an error and
  is not applied, and the host boots whatever its firmware remembers. The
  override flipping back after the boot is the proof it was honoured.
- **A graceful shutdown does nothing on a machine with no operating system.**
  It is an ACPI request, and something has to be listening. Use a hard off
  while a box is bare or sitting in an installer, and retest the graceful path
  once there is an OS to answer.
- **Redfish power and thermal are stubs on unlicensed boards.** They reported
  18 W and every fan at 0 RPM while the machine was running at over 9,000 RPM,
  which reads exactly like a failed power-on. The power state is correct; the
  sensors are not. Read sensors over IPMI (`ipmitool sdr`), and never wire an
  alert to Redfish thermal on these boards.
- **Set the controller's hostname before its static address**, or the address
  silently reverts, and finish with a controller cold reset.
- **A power-off resets the fan mode to full.** Any custom fan floor has to be
  re-asserted by a boot-time unit on the host, with a read-back, and zone
  writes issued back-to-back are dropped, so pace them a few seconds apart.
- **No virtual media without the vendor licence.** Network boot is the only
  remote install path, so the network-boot server comes before the first box.
- **Power restore policy: power on, and check the enum per board family.** "Previous" sounds
  right and is a trap: a clean shutdown leaves a server in soft-off, and "previous" then restores
  off, so the fleet came back dark after its own orderly shutdown (lesson 5.11). Every server
  is set to power on when mains returns, and the return order is the shutdown design's job.
  On these boards the BIOS value that means "power on" differs by board family, and the
  setting reads back as the old value until the next boot, so a real reboot is the only
  proof, and that proof is still pending on part of the fleet.
- **Outlet control on the strip is the fallback for a wedged controller, and
  only that.** Cutting the outlet also cuts the controller's standby power, so
  a machine whose outlet is off cannot be woken remotely until the outlet is
  back.
- **A controller password never goes on a command line**, where it lands in
  shell history and every process listing. Node0 learned that one the hard
  way, and it is one of the four lessons kept back.

Open on the capture day: two controllers refuse Redfish with credentials that
IPMI accepts, uncosted, on hosts outside the paging path.

| host | role | form | rack | OS or firmware |
|---|---|---|---|---|
| core1 | secondary DNS, NTP, NUT with shutdown authority | Raspberry Pi 4B | rack 2 | Debian 13 |
| core2 | secondary DNS, NUT observer, vault member | small x86 laptop | rack 2 | NixOS 26.05 |
| ntp1 | stratum-1 GPS time source | NTP appliance | rack 0 | appliance firmware |
| util2 | nix cache, network boot, fallback builder | small desktop | rack 3 | NixOS 26.05 |
| kvm1 | remote head onto console1 | PiKVM | rack 2 | Arch Linux ARM |
| console1 | sixteen-port HDMI and USB console switch | 1U KVM | rack 2 | appliance |
| openbao3 | third vault member | NixOS guest on a hypervisor | rack 2 (its host) | NixOS 26.05 |

**Failure domain.** Losing the hub takes the only zone-editable primary with
it. Both secondaries keep answering every query, and go stale only if the hub
stays down past a settings change. Losing one DNS or NTP box changes nothing
observable. Losing two of the three vault members stops reads and writes,
though consumers keep the secret they already rendered. Losing both builders
stops the fleet rebuilding itself, and what already runs keeps running.

## The decisions

### 20260817 to 20260819: three resolvers, three platforms

**Workload.** Every name in the site, served by one AdGuard instance until
20260817.

**Requirement.** DNS survives a reboot of any single machine, including the hub
that used to own it.

**Choice.** A Technitium cluster with one editable primary and two secondaries.
ns2 runs on core1, a Raspberry Pi that boots from a card, so its recovery story
is "reinstall, point it at the primary, walk away". ns3 runs on core2, which is
x86 where core1 is ARM, so one bad image cannot take both secondaries.

**Accepted trade-off.** Three upgrade paths to keep in step, and zone edits
possible in only one place.

**Verified.** During the primary's outage of 20260920 both secondaries answered
every query, with no fleet-wide impact.

### 20260911: re-initialize the vault, three members, unattended unseal

**Workload.** Machine-fetched secrets for the fleet.

**Requirement.** A full-site power loss must not leave the site waiting for a
person to type something in, and the vault must not depend on the storage tier
it helps bring up.

**Choice.** Retire the earlier instance rather than migrate it, since it held
no production secret. Stand up three members on three platforms, none on the
clustered storage tier, unsealing unattended rather than on key shares
presented by a human. Boot-critical and outage-critical secrets, the ones
needed to bring the site back when the vault is not there, stay outside it in
the encrypted secrets file.

**Accepted trade-off.** A vault that unseals itself is one an attacker holding
the hardware can unseal too, so the protection moves to physical access.

**Verified.** Brought up and sealed the same evening, initialized the next day,
and healthy at the capture.

### 20260829 and 20260910: one build host, one sanctioned rescue path

**Workload.** Building configurations for 29 NixOS hosts, and recovering one
that will not boot.

**Requirement.** Any machine rebuilds from the repository, and remote recovery
has one method known to work.

**Choice.** util2 became the build host on 20260829, and the faster di5 took
over on 20260910 with util2 kept as cache, network boot and fallback. Never
boot a rescue image by loading a kernel from the running one, because the load
can hang the machine with nothing left to read. Use a one-shot boot-manager
entry with automatic fallback instead.

**Accepted trade-off.** Two machines to keep current, and a rescue method that
needs the machine to actually reboot.

**Verified.** The rescue rule was formalized after the older method hung a
laptop twice with zero diagnostics (20260829). Since 20260918 pull-deploy has
compared the resolved commit against the branch head, failing closed.

### 20260920: pin the image, never a floating tag

**Workload.** The clustered resolver, and any clustered service run as a
container.

**Requirement.** No unattended process moves one member's version out from
under the rest.

**Choice.** Pin the image by exact tag rather than `latest`. Coordinate parity
inside one maintenance window, with members restarted one at a time.

**Accepted trade-off.** Upgrades become a scheduled act, and one member stays
behind until the distribution ships the matching version.

**Verified.** Decided the same day the skew was found and fixed (20260920). The
gap on the third member was still open at the capture.

## What it cost

Replacement costs for this layer are being researched and will be added.
Purchase prices are not published. The bill of materials of 20260920 carries
"to be researched" against every part of this layer.

## What broke

- **Lesson 4.15, A resolver that lied by omission: healthy on every check while
  replication silently stopped.** An unattended image pull recreated the DNS
  primary with a dormant permission setting. The newer primary that came back
  could no longer replicate configuration to the older secondaries, and every
  signal being watched said "healthy".
- **Lesson 4.12, Zone transfers need a shared key, not just a source-address
  rule.** A secondary sometimes asked for a zone from a different one of its own
  addresses than the primary's allow-list expected. Transfers failed until
  authorization moved to a key on 20260818.
- **Lesson 6.10, A failed fetch still exits zero, and "already converged" can
  mean "still stale".** The build tool fell back to its local cache when it
  could not reach the repository. It warned quietly and exited zero, and the
  layers above read that as a real convergence.
- **Lesson 1.15, Half a KVM stopped taking keystrokes, and the fix is a new
  KVM.** One bank of the console switch stopped forwarding keyboard input while
  video kept working. That left eight hosts with a console you can watch but
  not type into.

## State on the day

Healthy on 20260920: DNS, NTP and the two NUT servers, all four on the
as-built's stable list. Both core hosts had selected ntp1 as their stratum-1
reference, checked live during the capture. The vault cluster was live.
pull-deploy was converging and failing closed.

Open at the capture of 20260920: the vault's full deployment, security sweep
and clean-up, with the cluster running and the secrets not yet moved into it.
The version gap on the third resolver is held back until the distribution ships
the matching version. The console switch's dead bank has been open since
20260918, its hosts moved to the surviving bank with one port kept as a manual
bypass, and Christoph's verdict is that this model will be replaced when funds
allow.

Closed on the capture day itself: the resolver outage and the replication
failure behind it. One secondary was brought up to the primary's version, and
replication restarted. A stale "last synced" timestamp updated the moment the
versions matched, which is the proof.
