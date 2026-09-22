---
title: "Hardware failures and RMAs"
layout: "n0-theme"
theme: "hardware"
gist: "Seventeen faults in a fleet built from used enterprise gear, and the check each one left behind."
date: 2026-09-20
source: "node0 lessons v0.1, section 1"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 1
---

Node0's hardware story starts with a purchase decision: thirteen ex-datacenter
Supermicro chassis bought as cheap pulls, plus drives sold as refurbished and
never run. Everything in this theme follows from that. Buying used buys you
capacity at a price that makes a home datacenter possible, and it buys you a
defect rate no one would accept from new hardware, firmware you cannot change,
and parts whose history you do not know.

The order is roughly the order of a build. Two days before the racks were
touched, a NixOS install on a small host taught the first lesson of the set
(1.6), and it is the theme's shape in miniature: a symptom that appeared only
under load, read as dying hardware, that turned out to be a configuration
artefact. Then the three days of bring-up, 20260901 to 20260903 (1.1), with
their bill of dead parts, the board that needed two replacements before it was
right (1.2), and a vendor tool that under-reported and nearly cost real money
(1.3). From 20260906 the fleet was carrying data, and the faults changed
character: hosts that hung with nothing left to say (1.4), network cards that
failed in several unrelated ways in the same week (1.7, 1.8), drives and bays
and controllers that each lied in their own dialect (1.9, 1.10, 1.11), a
transfer switch that answered everything except the question that mattered
(1.12). The middle of the month brought a hypervisor fenced by a five-day-old
warning nobody was reading (1.13), a drive that died at 297 hours into a pool
that did not care (1.14), half a KVM that stopped accepting keystrokes (1.15),
and a laptop that still switches itself off every five days (1.16). Two of
these are still open.

What they have in common is not the hardware. It is that in almost every case
something was reporting healthy while being broken: a link up at a hundredth
of its speed, a SMART table with no column for the failure, a management card
answering every command but the one that matters, a log line watched on one
host that was true of four. The counter-habit runs through the whole theme:
identify parts by serial rather than by slot or letter, substitute a
known-good part rather than reason about a suspect one, and end a job with a
check's output rather than a person's confidence (1.5, 1.17). The last
lesson, added on 20260922 at Christoph's request, is the count the others
add up to: storage failed early and more than anything else, and new storage
earns trust by time under load, not by a health check at rest (1.18).

One more thing runs through the theme without a lesson of its own. Almost
every incident here was diagnosed by an agent, and an agent iterates on
configuration in seconds but pays for every step that needs hands with a
person's time and a host outage around it. The diagnoses that took a week
(1.2, 1.7) took a week for that reason. The practice that came out of it,
rule 24, is to exhaust what software can rule out first and then batch the
hands-on work into one ordered visit.

## Declined

- A macOS quirk that writes hidden companion files onto FAT32 media and breaks
  firmware updates. The triggering incident was a desktop 3D printer, out of
  scope here, and the mechanism has not yet recurred on Node0's own USB media
  prep.
- A macOS installer that crashes when built across too large a version gap:
  documented on Christoph's personal laptops, with no Node0 device tied to it.
- A Ceph hard drive condemned in one bay and then cleared twice on retest, in
  two bays on two hosts, 20260904 to 20260907. It is inconclusive, held as an
  unresolved marginal case, and it changed nothing that lesson 1.17's testing
  discipline does not already cover.
- A slot-7 NVMe capacity expansion on unraid1, 20260910 to 20260911: a routine
  addition in a maintenance window, with no fault, no new check and no rule.
- A hypervisor's original RAID card, dead on arrival during initial bring-up:
  one of the three cards already counted in lesson 1.1's dead-on-arrival
  figures, not a separate story.
- Two servers' management controllers returning 401 to Redfish despite correct
  IPMI credentials. This is open and uncosted, and those hosts sit outside
  this theme's device list.
- PDU fuses that give no visible sign of having blown, and the topology and
  terminology of UPS battery packs, are real hardware lessons. They belong to
  power and environment.
- A bare-metal reinstall reproduced a byte-identical system closure. It is a
  strong result, but it demonstrates software determinism rather than a
  hardware failure, so it sits with operations. The power-off mystery from the
  same host is lesson 1.16.
