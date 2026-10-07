---
name: account-brief
description: >
  This skill should be used when the user is about to meet a client or wants to know
  where an account really stands. It combines Salesforce, past meeting transcripts
  and the vault into a five minute brief, including what the CRM does not show.
  Triggers include "brief me on [client]", "prep me for the meeting with [client]",
  "what do we know about [client]", "where do we stand with [client]",
  "who decides at [client]", "account brief", and "I meet [name] tomorrow".
  Trigger whenever the user is preparing for a client conversation, even without
  saying "brief".
metadata:
  version: "0.1.0"
---

# account-brief

A brief someone reads five minutes before a meeting. Its value is the part no single system holds: the CRM has fields, the recorder has transcripts, the vault has context. The brief puts them side by side and says where they disagree.

Read only. Salesforce writes and vault edits are offered at the end, never done silently.

## Step 0: inputs

1. Find the vault and read `CLAUDE.md` and `_config/salesforce.md`. Without the config, ask whether to run `setup` first; proceed with standard fields if the user declines, and say the amount and next step may be read from the wrong place.
2. Identify the account. Resolve name variants (brand versus legal entity, abbreviations) in both `accounts/` and Salesforce. More than one Account record for the same client is itself a finding.
3. Ask what the meeting is about only if it changes the brief (a renewal versus a new deal). Otherwise draft first.

## Step 1: gather

**Salesforce** (use the field mapping from the config):

- Account: owner, owner active, type, created, last activity.
- Open opportunities: name, stage, value field, close date, owner, last stage change, open Tasks with dates, future Events.
- Closed opportunities in the last 24 months: won and lost, with lost reasons.
- Contacts: name, title, email domain, owner and `Owner.IsActive`, last activity, created date.
- Activities in the last 90 days on the account and its opportunities: subject, type, date, who.

**Recorder** (if connected): meetings in the last 90 days whose title, attendees or content mention the account. Read summaries first, transcripts only where a summary is thin.

**Vault**: the account page, linked opportunity cards, contact pages, meeting stubs, previous briefs.

## Step 2: compare, do not just collect

Look for these. They are the reason the brief exists.

- **People the CRM gets wrong.** A title in Salesforce that differs from what the person does in meetings. Two Contact records for one email with different titles. A colleague from `company-email-domain` filed as the client's champion.
- **Hidden seniority.** Contacts with no title, no activity, created long ago or owned by an inactive user. Look them up by name in transcripts and the vault. Unknown records sometimes hide the most senior person on the account.
- **People who matter but are not in the CRM.** Spoke in recent meetings, no Contact record.
- **Promises not logged.** Commitments in transcripts ("we send the proposal Friday") with no matching open Task or Event.
- **Stale CRM state.** Stage unchanged for longer than `stuck-stage-days` while transcripts show movement, or the reverse: an advancing stage with no conversation behind it.
- **Last real contact.** The latest meeting in the recorder or vault versus `LastActivityDate`. Say which is newer.
- **Loss history.** Lost deals and their reasons. If the vault says one thing and the CRM reason says another, show both.

## Step 3: write the brief

```
# [Client] · brief for [date / meeting]

**Where we stand**: three sentences. Relationship, live deals, the one thing to know.

## Live deals
| Deal | Stage | Value | Close | Next step (source) | Concern |

## People
| Person | CRM title | What they actually do | Position | Last real contact | Note |
Then: hidden seniority, missing records, misfiled colleagues.

## What the CRM does not show
Dated, sourced lines from transcripts and the vault: real decision path, budget hints, objections, competitors named, commitments made.

## History that matters
Wins and losses with reasons. Repeated objections.

## Gaps and conflicts
CRM versus vault versus transcripts, each with both versions and dates.

## For this meeting
Three to five questions that close the biggest gaps. Questions to ask the client, not fields to fill.
One thing not to promise, if the history suggests one.
```

Keep it to what fits five minutes of reading. Cut anything that does not change what the user says or asks in the meeting.

Cite every line: `(source: Salesforce, Opportunity [name], 2026-10-01)`, `(source: meetings/2026-09-12-acme-qbr.md)`, `(source: Fireflies, 2026-09-28)`. Nothing without a source; mark guesses `[unconfirmed]`.

## Step 4: offer, do not do

End with one line each, only where relevant:

- Save the brief to `briefs/YYYY-MM-DD-[account]-brief.md`.
- Vault updates found on the way (a missing contact page, a stale account summary): list them, apply with `vault-update` or `contact-sync` on "yes".
- Salesforce fixes (missing title, inactive owner, unlogged next step): show each exact change, write only on "yes".
- Action items for the user: to `todos/inbox.md` on "yes".
