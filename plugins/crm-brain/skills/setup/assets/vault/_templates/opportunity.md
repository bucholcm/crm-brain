---
account: [account-slug]
owner: [your-slug]
salesforce-id: [Opportunity Id]
stage: [slug from _config/salesforce.md]
outcome: [ONLY when the stage is closed: won | lost]
closed-reason: [ONLY when outcome is lost: slug from _config/salesforce.md]
value: [number from the amount field named in _config/salesforce.md]
currency: [ISO code]
close-date: YYYY-MM-DD
next-step: [a concrete action, never "follow up"]
next-step-date: YYYY-MM-DD
competitors: [slug, slug]
last-updated: YYYY-MM-DD
---

# [Client] · [What we are selling]

**Summary**: What we sell, to whom, why now. Two sentences.

**Sources**: Where we know this from.

---

## Why we win

Concrete advantages in this deal: references, relationships, stack fit, price, timing. Not slogans from the deck.

## Why we could lose

The most honest section in the file. Empty means nobody thought about it, not that there are no risks.

## How they really decide

Not what the RFP says. Who has a veto. What is a hard requirement and what is a wish list.

## People

| Person | Role | Position | Note |
|---|---|---|---|
| [[first-last]] | | champion / neutral / against / unknown | |

## Competition

Who else is in, what their pitch is, where they are weak.

## Stage history

- YYYY-MM-DD · `discovery` → `proposal` · what moved it

## Why we lost

*(Only when `outcome: lost`. Required then. The real cause, not "price". If it was "no decision", describe where qualification failed.)*

## Related

- [[account-slug]]
