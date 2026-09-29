---
title: "Why run your own (and when not to)"
description: "For people who are not technical: what Apple, Google and the AI companies do for you, what it really costs (mostly not money), when only your own will do, and how to choose piece by piece. Connected sovereignty, in practice."
layout: "n0-page"
date: 2026-09-28
source: "the Seed's build and costs of 20260928; hosted prices checked 20260928"
sanitized: "checklist v0.1; new page 20260928"
weight: 3
---

[The Seed](/node0/seed/) is the smallest self-hosted site we describe, and almost everything it does, you can already buy. Apple or Google keeps your photos and files. A password manager keeps your passwords. A backup service copies your computer. ChatGPT or Claude answers your questions and writes with you. They are good at it, and most of the time they just work.

This page is for someone who is not technical and is asking a fair question: why would I take any of that on myself? We do not think everyone should. We think everyone should know what they are trading, so they can choose. You can run one piece yourself and leave the rest where it is, and the Seed is built so you can stop at any rung.

## Connected sovereignty

Running your own does not mean cutting yourself off. Sovereignty, as we mean it, is choice: the option to run independently when you need to, and to connect deeply when it serves you. We call it connected sovereignty. You decide deliberately what is worth holding and trusting yourself, and what to use from others where they make a real difference. The terms of anything you rent keep shifting, in price, in policy and in who is allowed in, so having a capability of your own is not paranoia. It is a negotiating position.

The Seed is built that way. What must stay private lives on boxes in your house. Where a hosted service is better, the Seed uses one: an offsite bucket for backups, a hosted password manager for emergencies, and frontier AI models for work that needs them. One gateway decides which requests may leave the house and which never do. You hold the choice, and you can change it. [Node0](/node0/), the site the Seed is taken from, is connected sovereignty running at scale: four racks of its own for what must stay private, and frontier services used where they make a real difference.

## What the services give you

Convenience, first. Someone else buys the hardware, keeps it running, applies the updates, and gets woken at night when it breaks. Their systems are larger and more reliable than anything in a home, and their apps are polished because millions of people use them. For a lot of people that is the right answer, and nothing here argues otherwise.

## What they cost you

Money is part of it, and rarely the deciding part. What decides it for most people who run their own is everything else.

**What happens to your data.** A hosted service sees what you store and what you do, and its terms decide what that data is used for. For years that meant advertising: profiles built from what you do online, and sold as attention. Now it also means training AI models, on writing, photos, voices and conversations. Opting out, where it is offered, is often partial, and the terms can change after you have handed the data over. This matters more every year, because what AI can do with a person's data keeps growing, for them and against them.

**Whether you are the customer or the product.** A service is built for whoever it ultimately serves. When that is an advertiser or a data buyer, you are what is being sold. We choose to be the customer, the one the service answers to, in as many places as we can.

**Whether you can still reach it.** Stop paying, and the service ends; what happens to your data then depends on their terms, not yours. An account that is locked, hacked or closed can put years of photos and records out of reach until someone else decides otherwise. Years of data are easy to put in and slow to take out, so the price and the terms have to get quite bad before most people move. And when the service is down, or a feature is retired, you wait.

**Money, every month, for as long as you use them.** Checked 20260928, in US dollars:

| service | what it does | price |
|---|---|---|
| iCloud+ or Google One, 2 TB | photos, files, device backups | $9.99 a month |
| Bitwarden Premium | passwords | $19.80 a year |
| Backblaze Personal Backup | backs up one computer | $99 a year |
| ChatGPT Plus or Claude Pro | an AI assistant | $20 a month |

Together that is about $480 a year for one person, and more for a family or a small business. The prices move when the company decides: Bitwarden's premium plan doubled in January 2026.

## When only your own will do

Some things need a privacy that only running your own can give, and AI has made that list longer.

- **The law or a contract says so.** Client files, health records and work under a confidentiality agreement may have to stay under your control, and sending them to someone else's AI can break that.
- **Children.** What children write, say and photograph deserves more care than a service built on profiles will give it, and they cannot yet choose for themselves.
- **Proprietary work.** Business plans, unreleased products, source code and research are worth more before anyone else has read them, and an AI provider is someone else.
- **You simply want the choice.** That is our reason. We want to decide what our data is used for, so that it is used for us and never against us.

For these, a local model is the point, not a hobby: the question is asked and answered inside the house, and nothing is kept anywhere else.

## What running your own costs you

Running your own can be more expensive, slower and more technical than paying someone, and more trouble when something breaks. Agents have changed that a great deal, as the next section says. The costs are still real.

**Hardware, once, and some of it again later.** On the Seed's prices, one box that runs the site is $1,580 to $2,580 (rung 1), and the whole site without local AI is $2,060 to $3,780 (rungs 0 to 3). The [Seed page](/node0/seed/#what-each-rung-costs-and-what-the-site-costs-to-run) has every rung. Drives and batteries wear out and get replaced.

**Some hosted services, still.** The Seed keeps an offsite bucket for backups, a domain, a hosted password manager for emergencies, and hosted AI for the work a home computer does slowly. At list prices a `.com` domain and its DNS come to about $22 a year, and storage under 10 GB is free; a DNS plan whose key can be limited to your one domain can cost more (DNSimple's is $29 a month, checked 20260928), and hosted AI is billed by use. Running your own is not all or nothing, and it is not always cheaper.

**Power, space and some noise.** On the Seed's bench, the site itself drew about 49 W at rest (the router and switch, on the wall, were not counted): roughly 430 kWh a year, about $69 at $0.16 per kWh.

**Your time.** On the bench, an agent built rungs 0 to 4b in six days, with a person doing the hands: plugging in, pressing buttons, deciding. After that there are updates, the occasional alert, and a failed drive to replace now and then. We have not measured the hours yet, and we will publish them when we have; until then, treat anyone's claim that it takes "no time" with suspicion, including ours.

**The responsibility.** When a hosted backup fails, it is their problem to find. When yours fails, it is yours. That is why the Seed proves its backups by restoring them from the start, and from rung 1 alerts you when something stops; at rung 0 you check the backup yourself.

## What agents change

An AI agent can do most of the typing: it reads these pages, runs the commands, explains what it did, and fixes routine problems. That makes a site like this possible for people who would never have attempted it. It does not remove the hardware, the bills or the responsibility, and it is still you who decides what it may touch. Agents also need somewhere to run while your laptop is closed, which is one of the reasons the Seed exists.

## Piece by piece

For each piece, the hosted way, the Seed's way, and when to keep the hosted one. Choose each on its own.

**Backups.** The hosted way is a backup service or your phone's cloud backup: install it and forget it. The Seed's way copies your files to a storage bucket with a key that can add files but never delete them: ransomware or a mistake can hide files, and the bucket keeps what was hidden for 30 days, so you can put it back, and from rung 1 the site proves its backups by restoring from them every week. *Keep the hosted one if* you have one computer and want to set it up once. That is a good choice; a backup that runs is worth more than a better one that does not.

**Passwords.** The hosted way is Bitwarden or the keychain built into your phone and browser. The Seed runs its own password server, Vaultwarden, which works with Bitwarden's apps, so each of your agents can be given only the passwords it needs, and every read is recorded against the agent that made it. *Keep the hosted one if* you do not want to be the person who restores your passwords after a failure. The Seed keeps a hosted password manager anyway, for emergencies.

**Blocking ads and trackers.** The hosted way is an extension in your browser, which covers that browser. The Seed filters for the whole house at the network, so phones, televisions and guests' devices are covered too, and your own services get names instead of numbers. *Keep the extension if* only your own computer needs it.

**Photos and files.** The hosted way is iCloud, Google Photos or Dropbox, with sharing that just works. Running your own (the Seed lists these as optional) keeps the originals in your house and ends the monthly storage bill, at the price of setting up sharing yourself. *Keep the hosted one if* sharing with family is the main thing you use it for.

**AI models.** The hosted way is ChatGPT, Claude or Gemini, which are faster and more capable than anything that runs at home: on the Seed's bench, a long request took 84 seconds on the home computer and under 4 seconds hosted. Running your own means private material never leaves the house and never ends up in anyone's training data, there is no bill per use, and it works when the internet does not. The Seed uses both, through one gateway that decides which requests may leave. *Keep hosted alone if* you do not handle private material you would worry about. Some private AI needs no server at all: [FluidVoice](https://altic.dev/fluid) turns your speech into text on a Mac without it leaving the machine, and it is free.

**An assistant that works while you are away.** Hosted agent services exist and are getting better. Your own box gives the agent your files, your services and your rules, and it keeps working when a provider changes its plans. *Keep hosted if* the agent's work lives mostly in other companies' services anyway.

## When not to

Running your own is the wrong choice if nobody will look at an alert. It is the wrong choice if the only copy of something irreplaceable would end up on hardware nobody checks. And it is the wrong choice if what you want is to stop thinking about technology altogether. In each of those cases, a good hosted service is the better answer, and [rung 0](/node0/seed/rung-0/), a laptop with backups that cannot be wiped, may be all you need.

If you are not sure, ask your agent. Tell it what you use today, what you worry about losing, and how much time you want to spend, and ask it which of these pieces, if any, are worth it for you.
