---
title: "Learn from what broke"
description: "A hundred and sixteen lessons from building Node0 between July and September 2026: a hundred and thirteen published from a collection of a hundred and seventeen, and three added on 20260922. Each one: what happened, what it cost, what changed, and the check that catches it now."
layout: "n0-page"
date: 2026-09-20
captured: "20260920"
source: "node0 lessons v0.1 (the collection of 20260920)"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
---

Collection v0.1, 20260920, from the runbooks, the inventory's journal, the agents' memories and the incident records. A hundred and thirteen of the hundred and seventeen are published, and three more, on the sandbox, on burning storage in, and on laptops that travel, were added on 20260922; the four that concern credentials are listed by shape only on their theme page. Sanitized 20260921: humans other than Christoph by role, agents by name, no addresses or serials.

**The one sentence, before the hundred and sixteen.** Almost every lesson below is the same lesson wearing different hardware. A check was skipped, or the check could not tell the outcomes apart, and the output looked like evidence. The counter-habit that worked, when it was used, is to state what result would falsify the claim, then go and get that result before writing the claim down.

## Six themes

In the order things happened inside each. Things that happened and changed nothing are listed as declined at the end of every theme, so you can see what was left out and why.

{{< n0-themes >}}

## Start with these

Ten that have a turn in them, chosen for a reader who has never seen this site.

{{< n0-openers lessons="2.1 1.10 3.21 1.11 5.2 2.5 3.1 5.12 5.10 6.11" >}}

## One lesson, in full

Every lesson has the same shape: five facts, then the story for someone who was not there.

{{< n0-lesson-full lesson="3.1" >}}

## Rules we now run by

Twenty-seven fleet rules came out of the collection and were written into the operating rules the agents work under. Six rules to start with, five from that list and one straight from a lesson, each with the failure it prevents:

1. **After any hard hang, power off and on.** A warm reset does not clear a CPU IERR or a wedged NVMe controller; a real power cycle does. And a clean health reading afterwards proves nothing, so write the event down.
2. **Identify a drive, board or card by its own serial, never by slot, bay or letter.** Letters shuffle on a reboot; slots get reseated; the serial is the thing.
3. **Clean the bay before condemning the drive.** One contaminated connector wears two disguises; a soak test on a known-good spare tells them apart.
4. **Build and confirm the producer before the rule.** An alert written ahead of the thing it watches pages a human about your own unfinished work, and creating an inventory record for a host starts paging about it before it is built.
5. **Bound every wait loop, or make it die with its own session.** An abandoned loop locked the only dashboard account out for a day by re-arming its own lockout.
6. **Never delete in the same command as the copy it depends on.** Copy, verify, delete, as three observed steps. No exemption for small.

[All twenty-seven](/node0/lessons/rules/), with the lesson each one came from.

## How this was produced, and what is next

**How a lesson earns its place here.** A lesson derived from a document Christoph has reviewed inherits that review, and its source line names the document. A lesson written from a ruling or a conversation names that instead, and Christoph reads it before it is published. The source line is the difference, and it is on every lesson.

Six agents read the runbooks, the inventory's journal entries and hardware records, the agents' own memories and the incident records, one theme each, in parallel, with one shared brief. A seventh did the assembly, the tables and the placements. A fresh-eyes read and an independent review followed, and every lesson that lived only in an agent's memory, or nowhere, was placed in the runbook or on the device it belongs to. Six more agents derived the public pages from that collection, one theme each, through the sanitization checklist, and Christoph read them. The collection is dated. It grows by capture, not by edit.
