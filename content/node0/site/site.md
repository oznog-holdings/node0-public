---
title: "Site"
layout: "n0-layer"
layer: 1
gist: "The container every other layer runs inside: two rooms, four racks, the cable plant, and the conventions that find one thing among many."
figures: ["185 active devices", "4 racks in 2 rooms", "407 cables, 270 carrying a colour"]
photo: "studio.jpg"
photo_alt: "A desk and chair in the foreground, server racks standing along the wall behind them"
photo_caption: "The working end of the room, with the racks alongside."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.1"
sanitized: "checklist v0.1, 20260921"
weight: 1
---

## What this layer is for

Every other layer in this capture describes something that runs. This one
describes the container they run inside. Two rooms of a home hold four racks, the cable
plant, and the naming and labelling conventions that let a person or an agent
find one thing among 185 active devices without walking the room twice. The
layer has no hosts of its own. It is where the hosts are.

The inventory export of 20260920 counts 185 active devices of 191 recorded,
the other six being four hardware spares and two ledger entries. It counts 7
virtual machines, 407 cables, 31 IP prefixes and 22 VLANs, 19 of them active
and 3 reserved.

71 of those devices are hosts, by the rule adopted on 20260921: every active
device that runs an operating system we operate, counting the Pi and cluster
nodes and the small utility hosts, and leaving out personal laptops, the consumer router, the rack displays, the console server, the
offsite dock and anything offline. 69 of the 71 stand in these two rooms; one
is a canary at a second home nearby, and one is a rented instance in another
country. Across the 71 the fleet has
1,235 threads / 735 cores and about 8.4 TiB of memory, read on 20260921 over ssh (cores on 20260922) with
`nproc` and `MemTotal` on the Linux hosts and `hw.ncpu` and `hw.memsize` on the
Macs, with the four Windows and firewall hosts taken from Christoph's record of
the same day. The seven hypervisor guests sit inside the hypervisor figures and
are not counted again.

The scale continuum Node0 is built against names four stages. Seed is one machine, Hearth is a computer plus a NAS, Site
adds redundant power and networking with clustered storage and compute, and
Constellation is several sovereign sites, none subordinate to another. Node0
walked that ladder to Site in one basement, reaching these four racks in the
first days of September 2026. The ladder runs both ways. nexus stopped being the central server when
unraid1 took that role, decided 20260821, and is planned to leave the site in
2027. Hardware graduates in, does the central job, and graduates back out.

## How it is built

The network room is a closet off the server room with its own air
conditioning, and it holds rack0 (12U), the spares shelf and 23 devices. The
server room holds racks 1, 2 and 3, 42U each, and 142 devices. The home side
of the building connects one way. It can reach into Node0, and Node0 cannot
reach back.

44 of the inventory records are this layer's own, and not one of them is a
host: shelves, cable management, fans, displays, a transformer, a crash cart,
four receptacle circuits and two parts ledgers. Carrying a circuit or a ledger as a device
makes what plugs into which circuit, and where a part went,
records rather than memories.

{{< n0-diagram name="elevations" caption="The four racks from the inventory: every positioned device by rack unit, front face left and rear face right, with the shelf-mounted machines listed under each rack." >}}

| rack | U | role | grounding |
|---|---|---|---|
| rack0 | 12U | network closet: internet ingress, fw1/fw2, sw-wan1, home-side gear | not bonded (deliberate) |
| rack1 | 42U | UPS and battery: ups1 to ups4, two packs each, the step-down transformer | bonded 20260912 |
| rack2 | 42U | infrastructure and storage: ceph1 to ceph9, prox1 to prox4, unraid1, core1/core2, the Pi clusters, dev1 to dev4 | bonded 20260912 |
| rack3 | 42U | compute, inference, dev: di1 to di5, the agents, util1/util2, the sandboxes | bonded 20260912 |

Rack fill by occupied U, from the same export: rack1 93%, rack2 100%, rack3
98%. Rack 2 is full in the plain sense. Rack 3's figure is the inventory's,
not the room's: its shelves count as occupied units, but they were placed to
hold the compute that is still to come, behind the GPU hosts and on the shelf
at U31, which is why transfer-switch ports there sit free. By Christoph's
estimate rack 3 is about two-thirds full in the sense that matters. An
inventory models a shelf as a device, not as room. Rack0 has no fill figure,
because its devices sit on one labelled shelf with no individual rack positions
in the record.

The racks were filled with pulled enterprise gear, ex-datacenter and bought
used. The first batch was thirteen Supermicro chassis: three one-unit, nine
two-unit, and one four-unit 36-bay machine, which is unraid1. A fourth
one-unit hypervisor, prox4, was ordered on 20260903 and joined afterwards.
Bring-up ran 20260901 to 20260903 and is the source of most of the site's
physical discipline. All thirteen boards of that first batch are ex-hosting-provider pulls carrying a signed OEM BIOS
locked at 3.2a that the vendor's own updater refuses to flash, proven on ceph7
on 20260903. One replacement board arrived unlocked, so Node0 re-applies its
own settings file to whichever BIOS a board carries rather than chasing version
parity.

### The cable plant

Eight colours cover the data cables. Orange is firewall and internet, yellow is
management, red is the Ceph back end, blue is the storage front end, green is
Proxmox and virtual machines, purple is support and the Pi rigs, and white is
inference, GPU and agent links. Black means either a switch-to-switch
interconnect or the right colour not being available at that length. Power
cords are left uncoloured.

The export of 20260920 counts 407 cables, 270 of them carrying a colour, and a
live pull on 20260921 matched it in every object count. The back-fill snapshot of
20260914 counted 279 coloured of 403, an earlier and smaller plant, so this
page uses the export.

### What takes the site down

Two things take the whole site down: loss of the building, and the electrical
panel and the circuits feeding the racks. Water is watched but is not on that
list: the portable air conditioner's drain has a sensor on it for early
notice, and there is far more floor than water, so a leak there is a cleanup,
not an outage.

A rack that holds almost no compute can still be the fleet's single point of
failure, because orderly shutdown depends on power.
Rack1 is that rack here. Losing it removes the power buffer racks 2 and 3 draw
on during an outage. Rack0 is a second single point of failure, as the only
rack holding the firewall pair, the WAN switch and nexus, and the only rack not
bonded to ground. If the site goes, everything goes, apart from three
deliberate exceptions where a recovery would start: the rented
instance elsewhere, the offsite bucket, and the rotated drives.

## The decisions

### 20260903: label everything, before the box goes in the rack

**Workload.** Thirteen pulled chassis into four racks in three days.
**Requirement.** Any cable or device identifiable by whoever did not remove it,
an agent working from a description included. **Choice.** Label everything,
front and back, at every U, and both ends of every cable. **Accepted
trade-off.** Slower bring-up, and every move means
relabelling. **Verified.** By the faults it did not prevent. About half the
human-caused faults of bring-up traced back to an unlabelled cable put back
wrong, and a label taken on faith was wrong three times over three weeks
(lesson 5.2).

### 20260912: bond racks 1 to 3 to building ground, and leave rack0 out

**Workload.** Three racks of powered equipment and a UPS wall in a basement.
**Requirement.** Rack frames bonded to the building's electrical ground.
**Choice.** Racks 1, 2 and 3 bonded, rack0 excluded, the network closet judged
low-risk by comparison. **Accepted trade-off.** One rack in four is unbonded,
and it is the one holding the firewall pair. **Verified.** The reasoning went
into the rack records the same day, so it reads as a scope decision and not an
oversight. No electrical test result is recorded.

### 20260913: a colour standard that admits its own ambiguity

**Workload.** Several hundred cables across four racks, read by people and
agents during incidents. **Requirement.** A cable's purpose legible from the
cable. **Choice.** Eight colours, one per function, power cords uncoloured.
**Accepted trade-off.** Black carries two unrelated meanings, and the standard
says so rather than pretending the legend is complete. **Verified.** The
back-fill completed 20260914 across every data cable then recorded, and found
the internet edge had never been entered at all.

### 20260916: three axes for a part, not one

**Workload.** Spares and retired parts moving between shelf, chassis and return
shipment. **Requirement.** Knowing whether a part is actually available.
**Choice.** Parent device, status and disposition on every part, instead of one
status field. **Accepted trade-off.** Three fields to keep right, and the
spares shelf stays a partial record by decision. **Verified.** Adopted after
five already-claimed drives read as available stock.

### 20260920: model the studio before the wall exists

**Workload.** The music and content-creation gear at one end of the server
room, intended to become a separate room once a wall goes in. **Requirement.**
The record describes intent, so the eventual partition is a wall being built
rather than a database migration. **Choice.** Model Node0 Studio as a location
now, ahead of the wall. **Accepted trade-off.** Record and room disagree until
the wall exists, which is a documented disagreement rather than drift.
**Verified.** Partly; see the state below.

## What it cost

Replacement costs for this layer are being researched and will be added.
Purchase prices are not published.

## What broke

- **Lesson 1.1, "What thirteen pulled servers actually cost."** Three working
  days on site, plus 3 of about 80 refurbished, never run 12 TB drives dead on
  arrival, 1 of 3 RAID cards, 5 of 13 CMOS cells and a damaged riser slot.
- **Lesson 1.2, "Board damage an elimination tree cannot see."** One host
  needed three motherboards in nine days, and the first fault was visible only
  with the board out of the chassis under bench light.
- **Lesson 1.5, "Identity lives on the drive or the card, never the board."**
  On two families of single-board computer a board swap cost nothing, because
  hostname and configuration follow the storage. Nobody could say afterwards
  which board went where.
- **Lesson 5.2, "Two labels, corrected three times, before anyone traced a
  cable."** Which supply fed which rack power distribution unit was wrong or
  uncertain for three weeks, and was settled on 20260909 only by walking the
  cables one at a time.

## State on the day

**Healthy on 20260920.** Four racks standing, racks 2 and 3 full, racks 1 to 3
bonded, the colour standard set and back-filled, the bring-up traps written
into runbooks rather than left in an agent's memory, and the inventory holding
185 active devices and 407 cables as that morning's export recorded them.

**Open.** The spare hardware and parts inventory is a partial record by
decision, and closing it is on Christoph's list of what remains before he calls
Node0 stable. Current returns and replacements are still to be processed. A
second wallboard host and the display for the top of rack 1 are not deployed,
so one host drives the two displays above racks 2 and 3.
Several records lag the room: the studio location, the thermostat, and the
home-side edge gear the cable back-fill found missing.

**Closed on the capture day, and marked as such.** One cable recorded as cat6
was found to be cat6a and corrected on 20260920. The studio location's loaders
were written the same day, after the export this page reads, so the location
exists as a decision and as code but not yet in the data quoted here.
