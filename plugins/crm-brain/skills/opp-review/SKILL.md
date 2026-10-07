---
name: opp-review
description: >
  This skill should be used to review opportunities straight from Salesforce and
  show what is missing: no next step, overdue close dates, no activity, stuck
  stages, empty value, zombie stages, plus commitments made in meetings that never
  reached the CRM. Works on one deal, the user's own pipeline, their team's, or any
  scope set in the vault config. Triggers include "review my pipeline",
  "pipeline health check", "what's missing on this opp", "which deals have no next
  step", "deals without activity", "audit our opportunities", "prep for pipeline
  review", and "summarise the [client] opportunity". Trigger whenever deal state or
  CRM data quality is being judged, even without saying "Salesforce".
metadata:
  version: "0.1.0"
---

# opp-review

A summary of opportunities from Salesforce and an honest list of what is missing. Two modes: **one deal** (deep) and **a set of deals** (patterns). Output goes to the chat. Read only.

## Before starting

1. Read the vault `CLAUDE.md` and `_config/salesforce.md`. The config says which field holds the value, where the real next step lives, which stages exist and what the default scope is. Without it, offer to run `setup`. If the user declines, use standard fields and state that the results may accuse people of gaps that are not theirs.
2. Mode: a client, deal name or Id means one deal. "Pipeline", "all", "my team", "which deals" means a set. Ambiguous: do the set, then offer to go deep on the worst.
3. Scope: use the default from the config unless the user names another. Always state the scope in the first line of the result, and for team scope list the people it covered, so nobody compares numbers from two different sets.

## The honesty rule

Read this before reporting anything as someone's gap.

A data gap is not the owner's fault until it is clear that the field is on their layout and the data does not live somewhere else. A review that reads the standard Amount field in an org where the value lives in a custom field will accuse every owner of missing amounts. The amounts were there.

- Judge only fields that are on the layout of that record type (the Layouts table in the config). If the config has no Layouts table yet, say so and judge only the standard fields every layout has.
- Next step: look in the configured place (NextStep field, open Tasks with a date, future Events) **and** in the vault card's `next-step`. Missing in all of them means missing.
- Write "next step missing", not "Jane did not enter a next step". The owner's name is a column, not an accusation.

## Getting the data

Use SOQL through the Salesforce connector. Queries and paging notes are in `references/review-rules.md`. Fetch in batches if the connector has a response size limit. Fetch long text fields separately and only check whether they are empty and how long they are.

If the vault is available, match opportunity cards in `opportunities/` by `salesforce-id`, then by account. If a recorder connector is available and the mode is one deal, search the last 60 days of meetings for the account.

## Rules

Apply the rules in `references/review-rules.md`. Three levels:

- 🔴 **Critical**: the deal has no direction (no next step, overdue next step, close date in the past, no activity, no value, zombie stage).
- 🟡 **Important**: the deal has no substance (empty description, stage stuck, close date pushed twice or more, probability far from the stage default, required-in-UI fields empty).
- ⚪ **Cosmetic**: single deal mode only.

Plus one rule only crm-brain can run:

- 🟡 **Said but not logged**: a commitment or next step in a recent meeting stub or transcript with no matching open Task, future Event or vault `next-step`. Quote the source line, not the transcript.

## One deal

```
**[Name]** · [Client] · [Owner] · [record type]
[Stage] ([P]%) · [value] · close [date] · in stage for [N] days

**What the deal is**: two or three sentences from Description and qualification fields. Empty: "Salesforce does not say what this deal is about." That is a finding too.
**Momentum**: last activity (what, when), stage and close date changes from history.
**People**: who on the client side appears in activities and meetings.
**Next step**: what, who, when. Or 🔴 none.

**Gaps**
🔴 …
🟡 …
⚪ …

**CRM versus vault**: stage, value, close date, next step where they differ. Salesforce is right on numbers.

**Questions for the owner**: three to five that close the biggest gaps. "Who signs on their side?", not "fill in field X".
```

## A set of deals

1. **Header**: scope, number of open deals, total value and probability weighted value, split by record type when there is more than one.
2. **Table of deals with gaps**, sorted by number of 🔴, then by value descending:

   | Deal | Client | Owner | Stage | Value | Close | 🔴 | 🟡 | Worst gap |

   Deals without 🔴 or 🟡: one count under the table, no rows.
3. **Patterns**: how many deals hit each rule ("No next step: 18 of 40"). This tells whether the problem is process (most deals) or individual (a few).
4. **By owner**: deals and 🔴 per person. Facts, no commentary.
5. **To clean up**: zombie stages, placeholder values, likely duplicates (same account, same value, same stage).

Fetch field history only for the top 10 rows and say so under the table.

## Finish

One sentence: **the single most important thing to fix**. In set mode it is usually a pattern; in single mode it is the first question for the owner.

Then offer in one line each, only on explicit request: save the report to `briefs/YYYY-MM-DD-pipeline-review.md`, add action items to `todos/inbox.md`, or fix fields in Salesforce. Fixing fields is a write: show every change and wait for "yes".
