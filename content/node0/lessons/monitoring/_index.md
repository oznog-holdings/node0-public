---
title: "Monitoring and alerting"
layout: "n0-theme"
theme: "monitoring"
gist: "Twenty-two lessons from building an alerting system after the day four failures went unnoticed."
date: 2026-09-20
source: "node0 lessons v0.1, section 2"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 2
---

This theme starts on 20260906, the day Node0 found two hosts hung for ten hours, four switches minutes from an automatic thermal shutdown, a disk dead for a day and a half, and a rack that had rebooted itself, all at once and all by accident. Nothing paged anyone. The whole monitoring stack was built in the weeks after that, and these lessons are what was learned while building it, mostly by getting it wrong first.

They fall into three groups, and they arrived roughly in that order. The first group is about signals that exist but are not being read: the hidden device-statistics log on the fleet's most common drive model, the firmware event log on every server, the flow-control counters on the switch ports. Nearly every failure of 20260906 had already announced itself somewhere; the founding brief was written by listing those announcements rather than designing from a blank page.

The second group is about monitors that are themselves broken, which turned out to be the larger problem. Four monitors written in one week all had defects, and the silent ones were the dangerous ones. A monitor that polls over a login session faulted the very thing it was watching. An alert keyed to a device path paged seven times for drives that had not changed. An alert built on a wrong mental model reported a healthy standby as a fault, continuously. In every case, reading the check for correctness was not enough; only causing the condition proved anything.

The third group is about the alerting path as a system in its own right, with its own failure modes: a folder permission that silenced everything for 98 minutes, a quorum threshold that a fourth cluster member made silently wrong, rules shipped before the thing they watch existed, a maintenance silence that muted almost nothing, and the discovery that no monitor inside a network can tell a closed port from an exposed one at that network's own edge.

The two later additions, from July and August, predate the build and were folded in because the rest of the theme kept arriving at their conclusions independently.

## Declined

- The habit of reading fire-and-resolve notification pairs together as a single incident (20260912): a change in how someone reads a channel, not a change to a system, tool or runbook. Folded into the dead-man's-switch lesson as context.
- A dashboard-embedding quirk in the storage cluster's Grafana folder (20260911): a one-time documentation note about an exception to a convention, with no incident and no cost attached.
- Two permanently unreachable scrape targets removed from monitoring (20260910): a clean, uneventful correction with no cost and no near-miss.
- Windows event logs not yet flowing into the log aggregation system (open as of 20260920): a known gap, not yet a dated event with a cost and a fix.
- The Ceph maintenance-mode procedure lapsing a second time, on a different host, after having been fixed once: an adherence lapse rather than a defect in the monitoring system. The check that catches it is procedural discipline, not a new alert.
