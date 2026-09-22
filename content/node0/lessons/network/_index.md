---
title: "Network and edge"
layout: "n0-theme"
theme: "network"
gist: "Twenty lessons in which the network was healthy on every check and wrong on the wire."
date: 2026-09-20
source: "node0 lessons v0.1, section 4"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 4
---

The network lessons share one shape. A check said fine, and the wire said
otherwise. A firewall pair reported both members healthy while both claimed
the same gateway address; a DNS server answered every direct query while half
the fleet could not reach it; a cluster reported itself connected and in sync
while the thing it exists to replicate had stopped moving. In almost every
case the instrument was honest and was measuring the wrong thing.

The order is roughly the order the edge was built. Through late August 2026
the firewall pair came up on the bench and then went live: a CARP split brain
that turned out to be two bad cables (4.1), a two-day diagnosis with the
provider over a virtual MAC address their equipment would not relearn (4.2),
a renumber that left a rule pointing at nothing and put an admin login page on
the internet for ten minutes (4.3), and five separate silent defects before
failover DHCP actually failed over (4.4). Used and consumer hardware arrived
with its own history: a management switch still enforcing a previous owner's
access list (4.5), an access point still resolving DNS after its DHCP server
was turned off (4.6), and a network chip that eats its own DHCP replies below
the driver (4.7).

Then the fabric. A renumber done on paper only, deliberately (4.8), preceded
the one-day cut of 135 hosts from a flat network to eighteen VLANs, and the
two and a half hour DNS outage that came out of it (4.9). Two design
corrections sit alongside: why cross-rack switch pairing was wrong here
(4.10), and a whole switch generation with a silent speed ceiling (4.11).

September belonged to DNS and to remote access: transfers authorised by a
shared key rather than an address (4.12), a redesign of remote access that a
lab test corrected before production did (4.13), a misspelled API field that
redirected every public service for six minutes (4.14), a cluster that lied by
omission (4.15), and a helper tool whose convenience rewrote the wrong reverse
record twice (4.16). The last four are about the machine you troubleshoot
from: a VPN client that captured the routes (4.17), an SSH default that pages
like an outage (4.18), a directory mode that looks like a broken account
(4.19), and six laptops' worth of divergent SSH trust (4.20).

## Declined

- A fail-closed credential-rotation design for the edge switch is a careful
  piece of engineering, but it is a decision made in advance, not a lesson. It
  has still not been executed months later and nothing has gone wrong to write
  up.
- A deliberate two-DHCP-responder arrangement exists on one of the networks
  the firewall pair serves. It is worked around because a consumer router
  cannot have its DHCP server disabled, and it is a design accommodation
  rather than a dated incident with a cost.
- An OPNsense API client failing with an obscure TLS error on one laptop and
  not another, while a command-line fetch worked on both, cost minutes and
  changed one flag in one script.
- A network card that dropped both its ports three times on 20260909 and was
  replaced is a genuine hardware fault, but it belongs to the hardware theme.
  It is noted here only because it sits on the same card as 4.1.
- Small documentation drift found in the as-built audit, a missing row in one
  table, an unclosed parenthesis in a role name, unfilled rack-position
  fields, was closed the same day as record keeping. No incident, no cost.
- The relay for the remote-access mesh briefly lost its home region during the
  DNS cutover of 20260828 and recovered on the next restart once DNS was back.
  The relay had minutes of degraded, not broken, performance, and one update
  interval was tuned down as a precaution.
