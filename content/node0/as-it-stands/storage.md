---
aliases: ["/node0/site/storage/"]
title: "Storage"
layout: "n0-layer"
layer: 5
gist: "Four tiers that each cover a different way to lose data, and the nightly habit that proves they work."
figures: ["916 TiB Ceph raw", "493 TiB hub pool", "171 OSDs on nine hosts"]
photo: "storage-wall-dark.jpg"
photo_alt: "A rack of storage servers in a darkened room, drive activity showing as blue points down the full height of the rack"
photo_caption: "Rack 2 at night: nine storage hosts and the hub, drive activity in blue."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.5"
sanitized: "checklist v0.1, 20260921"
weight: 5
---

## What this layer is for

Storage is where Node0 keeps everything that must survive a reboot, a drive
failure, a whole-home event, or Christoph's own mistakes. Those are four ways
to lose data, and no one box covers all four. So the layer has four tiers.

- **A hub.** unraid1 is the local disk shelf: five ZFS pools, 493 TiB (542 TB)
  raw on the bulk pool, and the place the fleet's own backups land.
- **A replica.** nexus holds a second on-site copy of 58.2 TiB (64 TB), and
  will eventually leave the property.
- **A cluster.** ceph1 to ceph9 hold 916 TiB (1,007 TB) raw across 171 OSDs,
  and serve block, object and file storage to the rest of the site.
- **Two escape hatches.** An offsite bucket on Backblaze B2, and two rotating offsite USB
  drives of about 23.5 TB each.

A fifth part of the layer is a habit rather than a place. Every night the site
takes snapshot-consistent backups and checks that every restic repository is
still receiving them, and every week it rehearses a restore, because a backup
nobody has restored is a belief.

Until the summer of 2026 all of this was one box, nexus, which also held the
docker fleet, the DNS resolver and the only copy of years of photos. On
20260821 Christoph ruled that everything moves to a new hub, unraid1.

## How it is built

unraid1 runs five ZFS pools. `tank` is 493 TiB raw across three 10-wide raidz3
groups, with a mirrored NVMe metadata device and an Optane write log. `fast` is
a mirrored NVMe pair for container state. `ssd` is six SATA SSDs in raidz2 for
photos and studio work. `local` and `flash` sit on the boot SSDs. A live read
on 20260921 found 53.8 TiB allocated on `tank`, and all five pools ONLINE with
no errors.

{{< n0-diagram name="backup" caption="Every arrow is a copy; the dashed ones are checks. Nothing points back into the box it came from." >}}

nexus is unraid1's pull replica. Every hour it receives a one-way encrypted ZFS
stream of a chosen 31-dataset subset. It is not a mirror, because unraid1 holds
far more than nexus can carry. On 20260921 it was ONLINE with 26.4 TiB used,
and its last scrub, on 20260915, found nothing.

Ceph is nine hosts and 171 OSDs, where an OSD is one daemon that owns one disk.
It holds 916 TiB raw: 794 TiB of HDD, 65 TiB of SSD, 57 TiB of NVMe. On
20260921 the cluster reported HEALTH_OK with 43.2 TiB used, 17 pools, and every
placement group active and clean. It serves S3, CephFS with Samba and NFS
gateways, iSCSI, NVMe-over-TCP, and the Proxmox cluster's shared VM pool. Ceph
and unraid1 are separate on purpose. Neither is built on the other.

Raw capacity is not usable capacity. Divide each tier by its own protection
scheme before planning against it, because the schemes differ inside one
cluster. Here 5+2 erasure coding returns five sevenths of the HDD tier, the
flash pools are three-way replicated and return a third, and the two together
come to about 608 TiB usable. That is arithmetic from the pool layouts on
20260921, not a tested fill. Across the three tiers together the usable figure
on 20260922 was 987 TiB (1,085 TB): the 608 on Ceph, 338 on unraid1's five pools
and 41 on nexus, the last two read as used plus available from ZFS. Every disk in
every one of the 71 hosts, the boot drives and the Pis' cards included, adds up
to 1,606 TiB (1,766 TB) across 356 disks; the storage tier is 95% of it.

| host | role | rack | OS |
|---|---|---|---|
| ceph1 to ceph9 | Supermicro 2U, 19 OSDs each; monitors, metadata servers, gateways | 2 | Debian 13, Ceph 20.2.4 |
| unraid1 | the hub: containers, five pools, fleet backup server | 2 | Unraid 7.3.2 |
| nexus | encrypted pull replica; subnet router | rack 0 | Unraid 7.3.2 |
| nexus-spare | spare chassis, unpopulated | shelf | not deployed |
| ceph-backup1 | backs CephFS up to the hub | 2 | NixOS guest |

### The backup flow

The drawing above is the shape. What follows is the schedule.

Laptops and agent hosts back themselves up every two hours to an append-only
restic server on unraid1. unraid1 backs itself up from a frozen view. At 02:50
an orchestrator takes one atomic ZFS snapshot per pool and bind-mounts it
read-only before Backrest reads a byte. If that snapshot is missing, stale or
partly built, the orchestrator refuses to run.

Two runs read from that view. One writes the small irreplaceable tier to the
offsite bucket at 03:00. One writes nearly all of unraid1 into a bucket on the
site's own object storage at 04:00, which is a second local copy in a different
failure domain. A third flow does not need that view at all: at 02:00 syncoid sends
ZFS snapshots to whichever offsite USB drive is attached, mirroring the
source's own snapshot set, and a ZFS snapshot is consistent by construction. Two flows run on their own clocks: unraid1 sends hourly encrypted
snapshots to nexus, and a guest backs CephFS up into the restic server, so the
12 TiB archive of model weights has a copy outside Ceph.

One script is the sole writer of the two managed plans. Every night it checks
the live configuration against its own specification, and it refuses to run if
the two differ.

### The invariant

One rule covers every flow above. **A destination never holds a backup that
originated from itself.** A copy that lands inside its own source dies in the
same event it exists for. The plan that backs unraid1 up into Ceph excludes
Ceph's landing zone on unraid1, in code. The Ceph identity bundle goes to the
offsite bucket and the USB drives, never back into Ceph. The archive of model
weights goes from CephFS to unraid1, never the other way. The generator that
writes the plans enforces the rule, so nobody has to remember it.

### The three checks

One check cannot cover a backup, because arriving, coming back and still being
sent are three different failures. Three checks answer three questions here,
and none of them trusts the others.

Does a repository still receive snapshots? A daily verify sweep answers that,
moved from core2 to util2 on 20260830. Does the data come back? A restore test
restores and byte-compares three repositories a week. Is the ZFS replica still
receiving sends? A third check on util2, added 20260914, answers that.

### What is covered, and what is not

unraid1 is the single point of failure for everything that is not also on Ceph,
nexus or offsite. It has redundancy inside itself, since raidz3 tolerates three
drive losses per group, but none against the loss of the box, the room or the
home. On 20260915 the inside redundancy did its job. A `tank` drive died hard
in the middle of a scrub, the pool stayed ONLINE on two parity disks, and the
replica stayed current through the swap.

Ceph tolerates the loss of a full host by design. One tier of raw, regenerable
datasets on it has no backup, by policy. Losing nexus costs nothing
irreplaceable. Losing either escape hatch costs the only off-property copy of a
few things, most importantly the archive, for the reason in the third decision
below.

## The decisions

### 20260903: 5+2 erasure coding, host as the failure domain

**Workload.** Bulk object and file storage for the site, plus block storage for
the Proxmox cluster's virtual machines.

**Requirement.** Real capacity out of 72 spinning disks, while keeping the
ability to lose a whole host.

**Choice.** 5+2 erasure coding on disk, with the host as the CRUSH failure
domain. CRUSH is Ceph's placement algorithm, and the failure domain is the unit
it will not place two shards inside. The database and write-ahead log sit on
dedicated NVMe. Block pools stay three-way replicated on NVMe for latency.

**Accepted trade-off.** 71% efficiency and slower small writes, against
three-way replication's 33%.

**Verified.** Total power loss and a disk replacement in a lab on 20260816,
before any production disk. All three lab nodes were killed at once, and quorum
reformed unaided in about 90 seconds. The cluster itself was bootstrapped at
19:10 on 20260903 and complete at 21:20.

### 20260905: the recursion rule, and a frozen view

**Requirement.** Backups that cannot become copies of themselves, and cannot
catch a live database mid-write.

**Choice.** The invariant above, enforced by the plan generator, plus Backrest
reading only a frozen snapshot and failing closed.

**Accepted trade-off.** The configuration is generated and never edited, so a
hand edit stops the backup instead of changing it.

**Verified.** Two Codex review rounds closed fifteen findings the same night,
most of them of the shape "a failure here would look like success". The drift
refusal fired for real on 20260909.

### 20260818: what goes offsite, and what does not

**Requirement.** An off-property copy of everything irreplaceable, inside a
monthly budget.

**Choice.** The irreplaceable-and-small tier goes to the offsite bucket
nightly. The largest and oldest material rides the two rotating USB drives
instead: the archive, the fleet's backup repositories and the Ceph identity
bundle.

**Accepted trade-off.** The archive has exactly one off-property copy, and it
is a drive somebody swaps by hand. Putting it in the offsite bucket was costed
at roughly $70 a month and deferred.

**Verified.** The capacity review of 20260818 produced the number and the
decision together.

## What it cost

Replacement costs for this layer are being researched and will be added.
Purchase prices are not published. The bill of materials of 20260920 lists the
hardware: nine Supermicro 2U storage nodes, one 4U chassis and two 8-bay
desktop units, with both cost columns still marked as to be researched.

## What broke

- **Lesson 3.17, Editing the config by hand took out both nightly backups at
  once.** A hand edit on 20260909 disabled both plans. That is why the
  generator now refuses to run on drift.
- **Lesson 3.16, The bucket that was declared purged and wasn't.** A bucket
  noted as purging in the background had no rule to make that happen. 9.97 TiB
  across 614,000 objects sat there for at least six days.
- **Lesson 3.21, The second storage tier nobody was writing to.** The VM backup
  datastore held one archive and the cluster had no backup job, while every
  server-side check ran green.
- **Lesson 3.18, The PG autoscaler that silently did nothing, because two rules
  quietly overlapped.** Ceph will not act on a pool while CRUSH roots overlap,
  and says nothing when that happens. The fix moved roughly 27 TiB in seven
  hours.

## State on the day

Healthy on 20260920. Ceph reported HEALTH_OK across nine hosts and 171 OSDs,
with all 2,497 placement groups active and clean. All five of unraid1's pools
were ONLINE with no errors. The replica was 45% full and had scrubbed clean on
20260915. The nightly plans were on a confirmed live schedule, and the three
checks were in place on util2.

Closed on the capture day, and marked as such. The VM backup datastore was
given the nightly guest job it had never had. The job covers every guest except
two test ones, so a new guest is covered the day it exists, and rules now page
if the job disappears or an archive passes 30 hours. A restore was proven the
same night. Also that day, the offsite bucket moved to a 30-day hidden-version
retention rule, and the NVMe controller watch on ceph8 closed after 243 hours
clean.

Open on 20260920. A second NVMe controller wedge on ceph2, seen 20260917, is
under a watch with a date to recheck. The spare parts inventory is a partial
record, by decision. RMAs are waiting to be processed. Monitoring will be
refined as the hardware burns in. The question that would have caught the empty
datastore a fortnight earlier is now in the backup runbook, and it is "how old
is the newest thing in it, per source", not "are the jobs green".
