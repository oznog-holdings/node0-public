---
aliases: ["/node0/site/edge/"]
title: "Edge"
layout: "n0-layer"
layer: 2
gist: "The boundary between Node0 and the internet: one fibre, a firewall pair that survives losing one of itself, and an outside watcher."
figures: ["2 firewalls, active and passive", "9 CARP groups, one master", "1 fibre, no second provider"]
photo: "edge-rack0.jpg"
photo_alt: "A small open rack holding two compact firewalls, a time server and a dock for an offsite drive"
photo_caption: "The edge rack: two firewalls, the time server, the offsite dock."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.2"
sanitized: "checklist v0.1, 20260921"
weight: 2
---

## What this layer is for

The edge is the boundary between Node0 and the internet. It has five jobs. It
carries the single fibre connection in and out. It decides what may pass in
either direction. It presents Node0's public identity in a form that survives
one firewall dying. It gives Christoph a way to reach the site from anywhere
without opening a general hole in the perimeter. And it watches, from a
vantage point Node0 does not control, whether any of that has failed without
announcing it.

Mail rides the same boundary. The four Proxmox hosts send through an external
relay that authenticates Node0 by the source address the site presents to the
internet, so the edge's public identity is also Node0's mailing identity. If
that identity changes without the relay being told, mail stops silently.

## How it is built

The boundary is the one layer where a mistake takes the whole site off the
air rather than one service. That makes it the first place to buy redundancy,
ahead of any storage or compute tier. On Node0 the redundancy is a pair: fw1 and fw2, two Minisforum MS-01
small-form machines running OPNsense, active and passive, sharing their
addresses through CARP. CARP is the Common Address Redundancy Protocol, which
lets two machines share a floating address and a virtual hardware identity, so
one takes over from the other without anything upstream noticing.

The pair was proven in a lab on sandbox1 on 20260817, before it touched
production wiring. That lab is where OPNsense's resistance to being managed
like a NixOS host was worked through: config edits that fail to hot-reload
without reporting it, an API that never syncs a change to the peer, a root
shell that is csh. The lab also measured failover as close to free, at zero
packet loss across a live major-version upgrade.

Two floating addresses sit on top of the pair, and both move to whichever
firewall is master. One carries every public web service, through HAProxy on
the firewalls to an internal reverse proxy. The second carries paging
notifications only.

The pair also serves DHCP for the household network in hot standby using Kea,
and it routes the Node0 VLANs once the fabric hands them over. The retired
household router is still racked and powered as a fallback on its own
long-established provider binding, and it leaves the rack in 2027.

The fibre is terminated by the provider's own optical network terminal,
wall-mounted rather than racked, handing off at 10 gigabit into the fabric's
first switch. It is the provider's device on the provider's terms, and it is not in the
inventory as a Node0 host.

Outside all of it sits outpost1, a small rented cloud VM in another country
that holds no Node0 credential of any kind. It is the only vantage point that
sees Node0's public surface the way the internet does. A core host reaches out
to it on a schedule, scans Node0's public address range from there, and alarms
inside Node0 on anything reachable that should not be. Each scan first proves
it can see a known reference host, so a broken scanner and a clean perimeter
cannot be confused.

| host | role | form | where | OS |
|---|---|---|---|---|
| fw1 | firewall, CARP master on the capture day | small-form desktop | rack0, the edge rack | OPNsense, current release |
| fw2 | firewall, CARP backup | small-form desktop | rack0, the edge rack | OPNsense, current release |
| gw-tplink1 | retired household router, kept as a fallback path | consumer WiFi router | rack0, the edge rack | vendor firmware |
| outpost1 | external vantage point, holds no credential | rented cloud VM | offsite, another country | Debian |

## The decisions

### 20260817: both firewalls in at once, with the old router left untouched

**Workload.** replacing a consumer router that could not be demoted, on a live
household connection. **Requirement.** a pair that fails over, with no window
where the home has no internet. **Choice.** both machines in at once on the
standard configuration, no hardware-address spoofing, and the old router left
powered on its established provider binding. **Accepted trade-off.** a rack
position and a little power on a router nobody uses, against a fallback that
needs no rebuild. **Verified.** in the lab, and again three days later, when
the cutover hit an unpredicted fault and the fallback carried the home.

### 20260820: CARP on the internet-facing side becomes the production design

**Workload.** carrying Node0's public identity across a firewall failover.
**Requirement.** an address that moves between chassis without anything
upstream having to relearn it. **Choice.** CARP on the internet-facing side,
after the provider rebuilt the circuit as a plain layer 2 handoff with its
address-to-hardware binding removed. **Accepted trade-off.** the design depends
on the provider keeping that handoff plain. An alternative that avoids CARP on
that side is written up and kept unused as the fallback. **Verified.** on the
wire on 20260820, by moving a floating address between chassis and watching
outbound traffic survive it. An abrupt uplink loss failed over in 4.1 seconds
with every packet replied to, and a full chassis reboot did the same.

### 20260906: the paging path gets its own public address

**Workload.** alerting a human when something inside Node0 has failed.
**Requirement.** the alert path must not share a failure with the thing most
likely to be failing. **Choice.** a second floating address for notifications
only, and the reverse proxy added to the pair's synchronised configuration
list. **Accepted trade-off.** one more public address to hold and watch,
against an alert path that survives the loss of the web path. **Verified.** the
notification path has since run through service-layer incidents without going
dark with them.

### 20260911: remote access moves onto the firewalls

**Workload.** reaching the site from anywhere, for Christoph and for the
agents. **Requirement.** remote access must not depend on a storage host. A
maintenance window on one storage host took internal name resolution down
fleet-wide on 20260905. **Choice.** terminate the self-hosted mesh on both
firewalls independently, with no shared state and no dependency on which is
master. **Accepted trade-off.** two terminations to keep in step rather than
one, against a remote path that inherits nothing else's failover behaviour.
**Verified.** in the lab first, where the design found one of its own
assumptions wrong and corrected it before it shipped. The cutover completed on
20260911.

### Not yet: a second way out

Three answers to the single-fibre problem are designed and none are built: a
second provider with its own routing, an independently announced address
range, and a satellite tier for the day the whole valley loses its one egress.
The blocker is money. Until then the fibre and its terminal are single points
of failure the pair does nothing about. CARP protects against a firewall
dying, not against the circuit dying.

## What it cost

Purchase prices are not published, and replacement costs are still being
researched. The bill of materials of 20260920 carries the two firewalls, the
fibre terminal and the fallback router as cost to be researched. The external
vantage point is a rental, not a capital item.

## What broke

- **Lesson 4.1, CARP split-brain that was two bad cables, not bad config**
  (20260817): both firewalls claimed master on two of three groups, and the
  authentication counters pointed at a key mismatch. The fault was a failing
  cable and an unmanaged lab switch mishandling CARP's multicast.
- **Lesson 4.2, the two-day diagnosis of a CARP virtual-hardware-address fault
  on the provider's circuit** (20260818 to 20260820): the provider's edge
  equipment bound each public address to the first hardware address that spoke
  from it and never relearned a virtual one. Failover worked everywhere except
  where it counted.
- **Lesson 4.3, Ten minutes with the admin login page open to the internet**
  (20260820): an address renumber left filter rules written for a service that
  had moved. The firewall's own login page became reachable from anywhere, and
  luck found it, not monitoring.
- **Lesson 4.4, Kea DHCP high availability: five defects before it actually
  failed over** (20260817 lab, 20260827 production): five defects in a row,
  each leaving a pair that called itself enabled and would not have failed
  over.
- **Lesson 4.7, The Intel chip that eats its own DHCP replies** (20260828): one
  of two otherwise identical onboard ports drops every outbound DHCP reply
  below the driver, invisible to the packet filter and to a capture on the
  machine itself.
- **Lesson 2.21, You cannot see your own front door from inside your own
  home** (20260820 to 20260907): from inside the perimeter, a correctly
  silenced public address and a wide open one look identical. That is the
  structural reason the external vantage point exists.

## State on the day

The layer was healthy on 20260920, verified live rather than read from
documentation. Firewall fw1 held all nine CARP groups as master and fw2 held
none, which is the intended split. Both firewalls ran the same
release, rolled in production on 20260917 at a cost of one lost ping in
eighteen minutes. The external vantage point answered with 30 days of uptime
and zero failed system units, and the metric that depends on it was green.

One item is open on the day, from Christoph's own list. He wants the firewall
rules tightened to actual need without becoming restrictive, an acknowledgement
that the ruleset still carries history from the cutover and the renumber. Open
by budget rather than design: the second provider, its routing, the satellite
tier.

One fault is known and accepted rather than open. A change applied through the
API to one firewall does not sync to its peer, and a gated five-minute job is
the only thing closing that gap. Narrowing a binding to fix an exposure broke
that sync once already, on 20260821, with nothing reporting it. The current
state has one piece of hardware history behind it. An add-in network card in
fw2 was replaced on 20260910 after repeated port drops. Nothing in this layer
opened or closed on the capture day itself.
