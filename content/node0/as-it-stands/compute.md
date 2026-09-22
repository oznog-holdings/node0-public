---
aliases: ["/node0/site/compute/"]
title: "Compute"
layout: "n0-layer"
layer: 6
gist: "The hypervisor cluster, the GPU hosts and the model gateway: the layer that turns rack space into work."
figures: ["4 hypervisors, 224 threads / 112 cores", "9 accelerators on 7 hosts", "1 gateway address"]
photo: "di-servers-rack3-wide.jpg"
photo_alt: "Rack 3 seen wide from the front, the fan trays of the GPU servers stacked down it, with the edge of rack 2 in frame"
photo_caption: "Rack 3: the GPU hosts, with rack 2 at the edge of the frame."
date: 2026-09-20
captured: "20260920"
source: "node0 as-built v0.1, section 3.6"
sanitized: "checklist v0.1, 20260921; voice pass 20260921"
weight: 6
---

## What this layer is for

Compute is four things a site of this size needs, and one it does not.

A hypervisor cluster holds the utility guests, so a service is a virtual machine that can move between nodes, not a box. GPU hosts run inference and training, each with a different card and therefore a different job. One gateway gives every process on the site a single address to ask a model a question, and decides which model answers. Two laptops serve models as their full-time job.

The thing it does not need is a cluster of identical machines. Every host here has a shape, and the work is matched to the shape. Every other layer either runs on this one or reaches through it for a model's answer.

## How it is built

The hypervisor cluster is four Supermicro nodes running Proxmox VE. It formed on 20260901 with three nodes and reached four the week of 20260908. On 20260921 each node had 512 GB of RAM (503.75 GiB usable) and 56 logical CPUs, so the cluster has 224 threads and 2 TB. Christoph settled on 512 GB per node on 20260913, against an original plan of 768 GB, and put the memory meant for the higher figure into prox1 to prox3 instead. Storage is not hyperconverged. The cluster is an external client of the Ceph tier that the storage layer owns.

{{< n0-diagram name="models" caption="One address, one key per consumer; the red arrow passes only for a key that carries the external tag." >}}

Seven guests run on it. This layer owns one of them, the model gateway `llm-gw1`. Four are hosted here and owned elsewhere: `ceph-backup1` by storage, `openbao3` by secrets, `fin1` by services, `agent6` by agents. Two, `debtest1` and `nixtest1`, exist to be destroyed while testing failover.

The GPU tier is five standalone NixOS hosts on their own VLAN, with no failover between them. The rule for a small fleet of mixed cards is to give each card the job its shape suits, and it looks like this on Node0.

- di1 has two RTX 4090 cards with no peer-to-peer path between them, and 503 GB of host RAM behind them. Its job is holding mixture-of-experts models in host memory. A mixture-of-experts model activates only part of itself per token, so it can live mostly in RAM and still answer quickly. Splitting one model across two cards that cannot talk to each other would be the wrong shape.
- di2 has two RTX 3090 cards joined by a real NVLink bridge, and 440 GB of host RAM behind them, so it can hold a mixture-of-experts model in host memory the same way di1 does. It is also the only host where training and tensor-parallel serving (one model split across both cards at once) are the right shape.
- di3 has a single RTX 4090 and is the best serving box per watt.
- di4 has an RTX 4060 Ti and does small models, embeddings and reranking.
- di5 has an RTX 2080 Super, old enough to run llama.cpp only. It has been the fleet's Nix build host since 20260910.

All seven cards were confirmed live on 20260921. The serving fleet is those seven discrete cards on the five DI hosts and two laptops that serve from unified memory, nine accelerators in all. The DI cards hold 136 GiB of VRAM, and the memory a model can be loaded into across the serving fleet is 357 GiB, the 136 discrete plus 128 GiB of unified memory on the MacBook Pro and 93 GiB on the Framework, both shared with the operating system, so somewhat less is usable. One more card sits on site outside the serving fleet, an RTX 4070 Ti in a workstation, which is on the record and not behind the gateway, and is the tenth GPU the front door counts.

Above that tier sits the gateway. `llm-gw1` is a small NixOS guest running LiteLLM, pinned by container digest and backed by Postgres. Behind it, every serving host runs llama-swap, which loads and unloads models on demand so a host need not hold all of them at once. There is one address for the whole fleet and one key per consumer. Consumers ask for a role alias, not a host: `chat`, `code`, `chat-best`, `embed`, `probe` and others. Each key carries a tag that decides whether it may reach local backends only, or an external subscription-backed deployment as well. A key without the tag cannot reach an external deployment at all. The gateway fails over between local deployments, and between local and external where the key allows it. The defaults for scanned documents were set on 20260913: GLM-OCR for print, Chandra for handwriting.

Two laptops are full members of that fleet, not occasional helpers, and both are available to every consumer through the gateway. A MacBook Pro with 128 GB of unified memory holds the 120-billion-parameter gpt-oss-120b whole and serves it nearly four times faster than di1 can by pushing experts into host RAM, so it carries `chat-best`. A Framework laptop with 93 GiB serves alongside it. The lesson for a builder is that unified memory on a docked laptop is the cheapest way to serve one very large model at usable speed, and the seed's compute rung says the same.

The lab clusters are compute in the literal sense and nothing else. Eight Raspberry Pi 5 boards with 8 GB each sit on a shelf in rack 2 as the general-purpose cluster, on NixOS like the rest of the fleet. Seven Raspberry Pi CM3 modules on a Turing Pi V1 board with a Pi 4B head, built 20260901 to 20260914, exist to prove that a physical box never needs a bench trip again: a failed module is swapped, and the identity follows the storage. A ClusterHAT rig, built 20260914, exists to be killed mid-job so a cluster-computing curriculum has something real to observe.

| host | role | form | rack | OS |
|---|---|---|---|---|
| prox1 to prox4 | Hypervisor | Supermicro 1U, dual Xeon E5-2690 v4 | 2 | Proxmox VE 9.2.18 |
| di1, di2 | GPU compute | ASUS Pro WS workstation build | 3 | NixOS |
| di3, di4 | GPU compute | MSI X570 workstation build | 3 | NixOS |
| di5 | GPU compute | MSI B760 open frame | 3 | NixOS |
| serving laptop (MacBook Pro) | Serving laptop | MacBook Pro, 128 GB unified | 3 | macOS 26.6 |
| serving laptop (Framework) | Serving laptop | Framework Laptop 13, 93 GiB | 3 | Arch / Omarchy |
| cm1 to cm7, cmctl1 | Lab cluster | Pi CM3 on a Turing Pi V1 board, Pi 4B head | 2 | Debian 13 |
| rpi1 to rpi8 | Lab cluster | Raspberry Pi 5, 8 GB, on a shelf | 2 | NixOS |
| clusterhat1, chp1 to chp4 | Teaching cluster | Pi 3B+ controller, 4x Pi Zero W | 3 | Raspberry Pi OS |

**Failure domain.** Losing the Ceph tier takes down every Ceph-backed guest regardless of its failover state, which is every guest but `openbao3`, whose disk sits on a node's local ZFS for exactly that reason. Losing the cluster's single membership ring below three of four nodes loses quorum, which is the majority a cluster needs before it will keep running. Losing a GPU host loses only what it serves; the gateway routes around it. Losing `llm-gw1` stops everything that talks to a model, since it is the one address; that is mitigated by the guest being under the cluster's high-availability management, so it restarts on another node when its host dies, and it stays a single address while it does. The lab clusters have no monitoring or backup by design, so their failure is invisible until somebody looks.

## The decisions

### 20260901: storage as an external Ceph client, not hyperconverged

**Workload.** Utility guests for the whole site, on hardware already separate from the storage nodes.

**Requirement.** One pool for guest disks, without storage daemons on the hypervisors.

**Choice.** The cluster is an external Ceph client. The Ceph cluster belongs to the storage layer.

**Accepted trade-off.** A Ceph outage takes every guest but the vault member down wherever it is running, against the simplicity of one pool and one owner.

**Verified.** prox1 to prox3 were quorate the same evening, 20260901. prox4 joined the week of 20260908. Live queries on 20260920 showed four equal nodes.

### 20260911 and 20260913: one guest deliberately off Ceph and off failover

**Workload.** One member of the OpenBao secrets cluster, which needs a majority of its members in agreement to stay available.

**Requirement.** It must survive an outage of the thing whose administration credentials it holds.

**Choice.** `openbao3` sits on prox4's local ZFS with a virtual TPM, off Ceph and off high availability.

**Accepted trade-off.** It does not move when its host dies and must be recovered by hand. That is the price of being up when Ceph is not.

**Verified.** Not yet by a real Ceph outage. The reverse case was exercised on 20260915, when prox1 fenced itself and its Ceph-backed guests moved automatically.

### 20260910: sending a request to an external model is a conscious act

**Workload.** Every agent, script and service that asks for a model.

**Requirement.** No request leaves the site by accident, and no fallback quietly turns a local call into an external one.

**Choice.** One key per consumer. The key's tag decides whether it may reach an external deployment at all; an untagged or local-only key cannot. A secrets tripwire inspects external-bound traffic.

**Accepted trade-off.** A consumer that would benefit from an external model must be granted it explicitly, and a local outage is an outage rather than a silent hand-off.

**Verified.** The gate closed on 20260913. It is proven daily by attempting the forbidden call and confirming that the gateway refuses it.

### 20260913: the serving laptops stay on Node0 permanently

**Workload.** The `chat-best` alias, the largest model the site serves.

**Requirement.** Serve a 120-billion-parameter model at usable speed.

**Choice.** The two laptops are racked and run as serving hosts, both in full use, not as dev machines that occasionally help.

**Accepted trade-off.** Two personal laptops are now fleet infrastructure and cannot leave.

**Verified.** The primary serves the model nearly four times faster than di1 does, which is what made it primary rather than a curiosity.

## What it cost

Replacement costs for this layer are being researched and will be added. Purchase prices are not published. The bill of materials of 20260920 lists every part of this layer with both cost columns still marked "to be researched".

## What broke

- **Lesson 1.13, A five-day-old battery warning fenced a hypervisor.** A dead cache supercapacitor on prox1's storage controller logged the same line once a day for five days, with nothing watching. Then it faulted hard enough that the cluster's watchdog fenced and reset the node. Every other node had the identical failed part and had never said so anywhere a rule was reading.
- **Lesson 2.12, A written-down cluster quorum threshold became wrong, in the dangerous direction, the day a fourth member joined.** A hardcoded "fewer than two members" alert was right for three nodes and would have sat silent through a frozen two-of-four cluster. The threshold is now derived from the live membership count.
- **Lesson 1.5, Identity lives on the drive or the card, never the board.** Board swaps on the Pi families, including the ClusterHAT controller on 20260915 and two Pi Zeros on 20260919, cost nothing but the swap, because identity follows the storage.

## State on the day

Healthy on 20260920: the four-node cluster and its seven guests, all five GPU hosts confirmed live against both the runbook and the plan, the gateway and its aliases, both serving laptops, both lab clusters. The local model platform went from nothing deployed on 20260909 to a coordinated serving fleet in about two weeks. Multi-step tool calls were proved through the gateway on 20260910, the per-host serving tier and the laptops closed between 20260910 and 20260913, and the privacy gate closed on 20260913.

Open, from Christoph's list of 20260920: fuller deployment and use of the internal models; moving the hypervisors to on-board SATA and removing the storage controllers, for which the 20260915 fence is the argument; and hardware burn-in still being watched past the startup failures. Rack 3's pair drew 1,467 W on 20260921. At full nameplate, the vendor TDP of every card and CPU, the five GPU hosts alone come to roughly 3,400 W and the rack as a whole to about 4,000 W, against the 4,800 W one unit is rated for at 240 V; that is arithmetic, not a measurement. So the rack sits about 800 W under that line at worst case, and one more large GPU host would cross it: growth is limited by UPS capacity before it is limited by rack space.

One capacity figure, because it is the question people ask. With one node held in reserve, the other three hold about 1,511 GiB of usable memory, which is about 190 guests at 8 GB each. That is arithmetic over the live 20260921 figures, not a tested limit. It assumes 2 vCPU per guest, which at that count oversubscribes the remaining 168 threads by roughly 2.3 to 1, nothing reserved for the hypervisors, and no allowance for the seven guests already running.
