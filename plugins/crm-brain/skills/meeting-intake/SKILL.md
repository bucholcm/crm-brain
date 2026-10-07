---
name: meeting-intake
description: >
  This skill should be used after a client meeting to turn a Fireflies transcript,
  another recorder's transcript or plain meeting notes into vault knowledge,
  Salesforce follow ups and personal action items. Triggers include "process this
  meeting", "meeting intake", "ingest the transcript", "here is the Fireflies link",
  "what came out of the call with [client]", "file my last meeting", and "turn this
  call into next steps". Trigger whenever meeting output is supplied and the user
  expects it to land somewhere and produce follow ups.
metadata:
  version: "0.1.0"
---

# meeting-intake

One meeting feeds three places at once: the shared record of the account, the CRM, and the user's own to-do list. Split the transcript into four streams.

| Stream | Goes to | Mode |
|---|---|---|
| 1. Meeting stub | `meetings/YYYY-MM-DD-[slug].md` | shown first, written on one quick "yes" |
| 2. Facts and signals | `accounts/`, `opportunities/`, `contacts/` | **proposal, waits for "yes"** |
| 3. CRM follow ups | Salesforce Tasks, next step, stage | **proposal, waits for "yes"** |
| 4. Action items | `todos/inbox.md` (or the private `todos-folder`) | written straight away |

Streams 1 to 3 wait for the user on purpose; only stream 4, the user's own private list, is written straight away. Speech to text mishears names, drops negations and assigns sentences to the wrong speaker. Nothing enters the account record or the CRM without a human "yes".

## Step 0: before starting

1. Find the vault (folder with `CLAUDE.md`, `_config/`, `meetings/`). Read its `CLAUDE.md` and `_config/normalizations.md`.
2. Get the transcript:
   - If a Fireflies (or other recorder) connector is available, search by date, title or attendee and fetch the transcript and its summary.
   - Otherwise use what the user pasted or attached.
   - A bare link with no content and no connector: ask for the text or the file. Never invent what was said.
3. Identify the account and, if any, the opportunity. Check `accounts/` and `opportunities/` with `Glob`. If Salesforce is connected, look up the Account and its open Opportunities by name.

## Step 1: read critically, do not summarise

Before writing anything, establish:

- **Who spoke.** If attribution is uncertain, do not quote a statement as a named person's position.
- **What was agreed versus what was discussed.** The stub keeps agreements.
- **Negations.** Check every key agreement in context. A sentence that reads like a yes may be a no.
- **What the client avoided.** A question asked twice and dodged twice is a signal. Silence is data.
- **Commitments said out loud.** "We will send the architecture by Friday" is a next step, whether or not anyone logs it.

Apply `_config/normalizations.md` to names. Use spellings from `contacts/` and Salesforce, not from the transcript.

## Step 2: meeting stub

Draft `meetings/YYYY-MM-DD-[slug].md` from `_templates/meeting.md`, show it, and write it once the user confirms the decisions and signals are right. A stub, not a transcript: link to the recording, attendees, three to five decisions, signals, next steps, wiki links to the account and opportunity. No verbatim quotes and no pasted transcript.

Then: `last-updated`, a line in `_log/`, a line in `index.md`.

## Step 3: proposals for the vault

List concrete, ready to approve changes, not "consider updating the account":

```
accounts/acme-retail.md
  → Stack: add "order management is in-house, no integration with the web shop"
  → Risks: add "budget unconfirmed, decision after Q4 planning"
opportunities/acme-retail-oms-2026.md
  → next-step: "send AS-IS architecture for review" · next-step-date: 2026-10-10
  → competitors: add vendor-x
contacts/jane-doe.md  (new)
  → Head of E-commerce, raised integration risk twice, position: unknown
```

New people: propose a contact page only for people who spoke or were discussed with substance. Check affiliation first: an address on `company-email-domain` is a colleague, not a client contact.

When the meeting contradicts the vault, show both versions with dates and ask. When the meeting overturns the direction of a deal (approach rejected, key assumption gone), say so in one line at the top. That is bigger than a page edit.

After approval, apply changes with the write protocol from the vault `CLAUDE.md` (read right before writing, edit fragments, update `last-updated`, log). The `vault-update` and `contact-sync` skills implement that protocol; use them for anything beyond a few lines.

## Step 4: proposals for Salesforce

This is the stream that closes the gap between what was said and what the CRM knows. Read `_config/salesforce.md` first: it says where the next step lives in this org.

Propose, do not write:

- **Next step as an open Task** on the opportunity (subject, due date, owner) for every commitment made by our side, if the org uses Tasks for next steps.
- **Log the meeting** as a completed Event or Task if it is not already logged.
- **Stage or close date change** only when the meeting clearly moved the deal. Show old and new value and the sentence that justifies it.
- **Contact fixes**: missing title, a person who spoke but has no Contact record.

Show each change exactly as it will be written. Write only the ones the user approves. Never change Amount from a transcript; numbers come from the deal owner.

## Step 5: action items

Extract **only tasks for the user**. Not tasks for the client, not tasks for the world. Write them to `todos/inbox.md` (or the `todos-folder` from settings) using the schema in the vault `CLAUDE.md`, with `source: fireflies` (or the recorder used) and the transcript link. Check that each `^id` is unique across all files in the todos folder.

Commitments by colleagues become "make sure [name] does [thing]" only if the user owns the follow up.

## Step 6: report

In this order:

1. Where the stub landed.
2. Vault proposals, waiting for "yes".
3. Salesforce proposals, waiting for "yes".
4. How many action items went to the inbox.
5. **What was ambiguous in the transcript** and needs the user's memory, not Claude's interpretation. Say plainly if parts were unreadable instead of smoothing them over.
