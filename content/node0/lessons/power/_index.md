---
title: "Power and environment"
layout: "n0-theme"
theme: "power"
gist: "Twenty lessons on UPS behaviour, transfer switches, shutdown and restart, and keeping a server room cool."
date: 2026-09-20
source: "node0 lessons v0.1, section 5"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 5
---

Power is the layer where Node0 found the most instruments that lie. Not fail,
lie: a transfer switch reporting a healthy source as faulty because the two
supplies disagreed about nominal voltage (5.1), a management card returning an
empty string rather than a busy signal when two of the fleet's own jobs asked
it a question at once (5.4), a server's modern management API returning a
confident 18 watts and zero fan speed for a machine running at 9,400 RPM (5.7),
a label field that recorded what somebody believed on the day the rack was
wired rather than what the copper does (5.2). In every case the output looked
like a measurement. The habit that worked, over and over, was to get the same
fact from a second, independent instrument: follow the cable, meter the
voltage, read the device's own screen, ask the older CLI.

The order matters, because the theme builds. August was bring-up: voltage,
labels, battery vocabulary (5.3), fuses (5.19), and the deliberate decision to
keep telnet on management hardware too old for usable SSH (5.8). Early
September was measurement and its traps: the credential that crossed from a
protected transport onto a cleartext one, a secret rotation that changed
nothing while reporting success (5.9), a rack whose two supplies cannot carry
each other and a nameplate rating that had been wrong for months (5.10).

Mid-September covered the harder half of the shutdown design: getting the fleet
to come back. The shutdown design had been declared finished once on the
strength of shutdowns alone. Asking the other half of the question found a two-
minute deadline hidden in a factory default (5.5), a BIOS setting that
guarantees a fleet stays dark after a textbook shutdown and means the opposite
thing on two boards from the same vendor (5.11), commands that only work while
the UPS is genuinely on battery (5.13), and a control path that ran through the
firewalls the power event would also take down (5.14). Cooling ran alongside
it: a real heat problem solved with existing capacity and kept explicitly
provisional (5.16).

## Declined

- **A lab-bench UPS and surge strip, deliberately unmonitored.** A design choice, excluded from metrics and dashboards on purpose; nothing changed as the result of a problem.
- **A USB Ethernet adapter that enumerated as a mass-storage device.** A real, dated hardware lesson, but it belongs to the hardware and bring-up theme, and is declined here to avoid telling it twice.
- **SNMPv1 left enabled on the four UPS network cards by design, decided 20260920.** An accepted trade-off, since the PDUs can only read a UPS's status over SNMPv1 or v2c and disabling it fleet-wide would break that stock feature. It is context for the credential-class lesson, not a lesson of its own.
- **One transfer switch's dead application link, fixed by a firmware reflash on 20260911.** Real and dated, but a straightforward firmware fix with no design change and no reusable check beyond reflash and verify, and it is folded into the richer transfer-switch fault story from the same week.
- **Thermostat wiring carried over from the previous unit, using a spare conductor for common.** A one-time installation detail with no cost, no monitoring change and no reusable check beyond labelling your wires.
- **Wireless environment sensors offline for an hour after a password change on the sensor network.** Diagnosed quickly from the access point's own log; it changed no design and no standing check.
- **A contact sensor re-adhered on 20260915 after false alerts.** A one-line physical maintenance fix with no design change, too small to carry a standalone lesson.
