---
aliases: ["/node0/site/fabric/"]
title: "Fabric"
layout: "n0-layer"
layer: 3
gist: "The switches, VLANs and bonds that decide what can reach what inside Node0."
figures: ["6 Arista switches", "19 active VLANs", "135 hosts migrated in a day"]
photo: "fabric-front.jpg"
photo_alt: "Five rows of switches seen from the front, patch cables running out of them in the colours of the cabling standard"
photo_caption: "The front of the fabric: three MLAG pairs, and the colour standard that says what each run is for."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.3"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 3
---

## What this layer is for

The fabric is Node0's data plane: the switches that move packets between
racks, the VLANs (virtual LANs, separate broadcast domains carried over the
same wires) that keep one purpose's traffic away from another's, and the
bonding conventions that let a host survive losing a switch. It sits between
the edge, the boundary to the internet, and every host that plugs into a rack.
Storage, compute, services and the agents all sit on top of whatever the
fabric decides is reachable.

Before 20260818 there was no fabric. Node0 ran flat, one broadcast domain
behind a consumer router. Ceph's public and cluster networks, the management
plane, the DMZ (the segment for internet-exposed services) and the internal
service tier all wanted separate wires. A flat network had none to give.

## How it is built

Six Arista DCS-7050TX-64-R switches carry the data plane as three MLAG pairs.
MLAG (multi-chassis link aggregation) lets two physical switches present
themselves to a host as one, so a host's two uplinks become a single bonded
link across two boxes. The drawing shows the three pairs and which of them
routes.

{{< n0-diagram name="topology" caption="Every host bonds to one MLAG pair inside its own rack; Pair A is the only pair that routes. No addresses or VLAN numbers are drawn." >}}

All routing lives on Pair A. Eleven VLANs take their gateway from VARP
(virtual ARP, Arista's active-active scheme in which both switches answer for
the same gateway with the same virtual MAC, so east-west traffic never crosses
the peer link). The rest are trunked to the firewalls. Pair B does not route.
It serves the compute and dev racks and reaches everything else over a 160
Gbps back-to-back port-channel to Pair A. The third pair is a Ceph backend
island with jumbo frames and no gateway at all, so cluster replication never
leaves it.

Every regular host attaches by a single LACP bond (link aggregation control
protocol, which negotiates two ports into one logical link), both members on
one MLAG pair, never split across pairs. The management switch is the one
deliberate exception. It is dual-homed to both pairs with spanning tree
blocking one path, so a bad push to one pair cannot strand out-of-band access
to the switches you need out-of-band access to fix.

| host | role | form | rack | OS |
|---|---|---|---|---|
| `sw-fa1`, `sw-fa2` | frontend Pair A, the only switches that route | Arista DCS-7050TX-64-R | rack 2 | EOS |
| `sw-fb1`, `sw-fb2` | frontend Pair B, layer 2 only | Arista DCS-7050TX-64-R | rack 3 | EOS |
| `sw-cb1`, `sw-cb2` | Ceph backend pair, jumbo frames, no gateway | Arista DCS-7050TX-64-R | rack 2 | EOS |
| `sw-mgmt1` | management and out-of-band switch, dual-homed to both pairs | Netgear S3300-52X-PoE+ | rack 2 | vendor firmware |
| `sw-wan1` | transparent layer-2 bridge between the provider's handoff and the firewalls | MikroTik CRS305-1G-4S+IN | rack 0 | RouterOS |
| `sw-rpi1`, `sw-rpi2` | power over Ethernet for the Pi cluster | STEAMEMO GPS208 v3 | rack 2, shelf | web-only firmware |
| `ap1` | the only access point inside Node0's own network | OpenWrt One | rack 3 | OpenWrt |
| `sw-lan1`, `sw-studio1`, `sw-lab1` | unmanaged edge switches, no address, no management plane | YuanLey and Sodola 2.5GbE | rack 0 and unracked | none |

Two Arista spares and one Netgear spare sit unracked and unpowered. The
inventory export of 20260920 counts 407 cables, 270 of them carrying a colour
from the standard. The same export lists 22 VLANs, 19 of them active and three
reserved as layer 2 while they wait for a gateway. Management has its own VLAN
and its own switch. The VLAN-to-subnet table stays internal, so this page gives the shape
and not the map.

### The VLAN shape, without the map

What can be shared is the set of segments and the rules that decided them;
the tags and prefixes are the one thing on this page a reader has no use for
and an attacker does. The segments are one per purpose and trust level:
management, with its own switch; the Ceph back-end, an island with jumbo
frames and no gateway; the storage front-end; the hypervisors and their
guests; the agents and development hosts, on jumbo frames; a trusted wireless
segment and a separate one for IoT devices; the probes; a bootstrap segment
for network installs; a DMZ for internet-exposed services; a legacy segment
that only shrinks; and the studio.

- **Route where the policy lives.** The fabric routes the segments whose
  problem is throughput, storage and compute, with VARP so east-west traffic
  never crosses the peer link. The firewalls route the segments whose problem
  is trust: the wireless networks, the probes, the DMZ. The general rule is
  that the higher-security segments route through the firewalls, where every
  packet between segments meets a rule, and the lower-security, high-volume
  segments route on the switches, so the firewalls never become the
  bottleneck for storage and compute traffic they have no reason to inspect.
- **Give management its own switch, not only its own VLAN.** A tag keeps
  traffic apart; a separate switch keeps the console reachable when the fabric
  itself is what is broken.
- **A back-end that never needs a gateway should never get one.** The Ceph
  replication segment has no route out, so a misconfiguration elsewhere cannot
  pull replication traffic across the firewalls or expose it.
- **Declare a segment before it is used.** Three segments exist on the
  switches as layer 2 with no gateway yet, waiting on a firewall interface.
  Reserving the tag and the name early costs nothing and stops the number
  being taken by something else.
- **A bootstrap segment, with installs armed per machine.** Network installs
  land on their own segment, and the install server answers only for a MAC
  address that has been armed for it, so a box that boots from the network by
  accident gets nothing.
- **Renumber on paper first, then move hosts one at a time.** Lesson 4.8 is
  the rule: documentation may run ahead of the live state, never the reverse,
  and a live address changes only at the moment its host moves. Lesson 4.9 is
  the day 135 hosts moved and the outage a stale switch entry caused.
- **A vacated tag stays vacant.** A number retired by a renumber is not reused
  while anything might still reference it, so a stale reference fails visibly
  instead of landing in the wrong segment.
- **Wireless is a dumb access point on a trunk.** The access point runs no
  DHCP, no DNS and no routing of its own; each SSID maps to a segment, and the
  fabric and the firewalls make every decision. Lesson 4.6 is what a default
  access point does otherwise.

### The cable colours

The legend is public, because a colour reveals nothing a label does not, and
because it is the single cheapest piece of discipline on this page. One colour
per purpose, chosen by Christoph on 20260913 and back-filled across every
existing data cable the next day; new work only would have left the racks
lying about their history for years.

| colour | what it carries |
|---|---|
| orange | firewall and internet |
| yellow | out-of-band management |
| red | Ceph back-end |
| blue | storage front-end |
| green | hypervisors and guests |
| purple | support: the access point, the Pi rigs |
| white | GPU compute and the agents |
| black | switch-to-switch interconnect, or any run the right colour was not available for at that length |

Black is the trap, and the reason the standard is descriptive rather than
load-bearing. It carries two meanings, so a black cable is not evidence of its
purpose, and tooling that reads colour to infer a role treats black as
unknown. The colour is also recorded on each cable in the inventory, which is
what lets a script check the racks against the standard; on 20260920 that was
270 of 407 cables carrying a colour from it, with the rest black, power, or
not yet coded.

**Failure domain.** Losing Pair A takes the whole routing plane, because Pair
A alone holds the transit link and every VARP gateway. Rack 2 also holds Ceph,
Proxmox, the management switch and the DNS and NTP secondaries that were once
split out for exactly this kind of redundancy, and Bosun's guest runs on a
hypervisor there. Losing rack 2 is close to a total service loss. Losing rack 3
costs the GPU hosts, the agents' own machines and the utility hosts; the site
keeps running without them.

## The decisions

### 20260817: MLAG pairs in-rack, and one bonding rule for every host

**Requirement.** Survive one switch failing without a host losing its network,
under one rule rather than a rule per host class.

**Choice.** Pair the two switches of a pair inside the same rack, not across
racks. Give management its own VLAN and its own switch. Bond every front-end
host port to Pair A whatever the host is.

**Accepted trade-off.** A rack-level loss takes both members of a pair, and
load and risk concentrate on Pair A. Cross-rack pairing would have needed long
40 Gbps runs the existing cabling could not reach, for a benefit that does not
help a host dying with its own rack anyway.

**Verified.** The assumption was re-examined against where the equipment
physically sat and reversed the same evening. The failure domain that results
is written down rather than discovered later.

### 20260818: the fabric built and live in one session

**Requirement.** Three MLAG pairs, VARP gateways, the full VLAN set and
cross-rack routing, without a multi-week staged cutover.

**Choice.** Build it in one multi-agent session on temporary addresses, then
verify end to end before anything moved onto it.

**Accepted trade-off.** A long day with a large blast radius, against weeks of
a half-migrated network running two sets of rules at once.

**Verified.** The VLAN set of that day, eighteen of them, was verified
cross-rack before the session ended. Management addressing moved into a
dedicated VRF (virtual routing and forwarding instance) after EOS refused an
overlapping prefix, the kind of thing one session surfaces immediately.

### 20260827 and 20260828: renumber on paper, then migrate 135 hosts in one day

**Requirement.** Move every online host onto segmented VLANs without a long
outage and without breaking live services ahead of the move.

**Choice.** Renumber five VLAN identifiers and add two new ones on paper
first, freezing every live address until its host's own migration. Then
migrate in a fixed order: a disposable test host first, the dependency hub
next, then management, then everything else, and the DNS secondaries last so a
resolver stayed up throughout. Almost every host kept its address and changed
only mask, gateway and VLAN tag. Ten actually renumbered.

**Accepted trade-off.** That continuity left the numbering less tidy than a
clean sheet would have been.

**Verified.** Executed against a written progress log on 20260828, the
management devices following in the same migration.

### 20260913 and 20260914: a cable colour standard, back-filled across the fleet

**Requirement.** Tell what a run is for by looking at it, without reading a
label.

**Choice.** Christoph set a colour per purpose, back-filled across the
existing data cables the next day rather than applied only to new work.

**Accepted trade-off.** One colour carries two meanings, so it cannot by
itself distinguish an interconnect from a substitution.

**Verified.** The back-fill completed on 20260914 and went into the inventory,
and the export of 20260920 shows the distribution.

## What it cost

Replacement costs for this layer are being researched and will be added.
Purchase prices are not published. The bill of materials of 20260920 gives the
quantities (eight Arista DCS-7050TX-64-R, two Netgear S3300-52X, one MikroTik
CRS305, two PoE switches, three unmanaged edge switches, one OpenWrt One) with
both cost columns still marked "to be researched".

## What broke

- **Lesson 4.5, The management switch that arrived from a previous life,
  locked.** It came with an access control list still active from its previous
  owner. It was unreachable by every normal recovery path and had to be
  factory-reset before it could join Node0.
- **Lesson 4.6, A default OpenWrt access point is a rogue DHCP and DNS
  server.** It was staged on an isolated host so its out-of-the-box services
  could never reach the live network. Turning off a service's most obvious
  function turned out not to turn the service off.
- **Lesson 4.9, Cutting a flat 135-host network to eighteen VLANs in one day,
  and the DNS outage that came out of it.** A host's MAC address changes when
  it moves onto the fabric, and a secondary service address that only replies
  and never sources traffic is never re-learned by the switch. The result was
  two and a half hours of DNS that looked healthy from the host and was
  invisible above the link layer.
- **Lesson 4.10, Why cross-rack switch pairing sounded right and was wrong.**
  The argument for pairing across racks did not survive contact with where the
  equipment actually sat.
- **Lesson 4.11, One switch generation, one silent 2.5 gigabit ceiling.** This
  Arista generation is not NBASE-T (the standard that added 2.5G and 5G to
  copper Ethernet), so it negotiates only 100M, 1G and 10G. Any 2.5GbE port
  plugged into one runs at 1G for good, and eighteen interfaces across eleven
  devices carry that exception.

## State on the day

Healthy on 20260920: the fabric and the migration onto it are both in the
stable column of the capture. The three MLAG pairs, the VARP gateways, the
back-to-back port-channel, the dual-homed management switch and the access
point's bonded uplink are in service and have been through real incidents.

Open on 20260920:

- Three VLANs exist as layer 2 on the Aristas with no gateway yet, by design,
  waiting on a firewall interface.
- The switch runbook contradicts itself about how the management switch is
  dual-homed. The settled design says two bonds, an earlier passage two
  non-bonded links. The settled design is what is deployed.
- The WAN-side bridge's credential rotation is prepared and still not
  executed. It fails closed rather than making a live change, because a
  mistake there touches the provider-facing identity of the whole site.
- Eleven cable records carry a colour on a power port, a reconciliation owned
  by the site layer's audit row.

Nothing in this layer closed on the capture day. The last fabric work before
it was the second wireless network of 20260912, which turned the port-channel
to the access point into a trunk, and the colour back-fill of 20260914.
