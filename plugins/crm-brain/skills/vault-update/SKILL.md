---
name: vault-update
description: >
  This skill should be used to create or update account and opportunity pages in
  the crm-brain vault from notes, emails, pasted text or approved meeting intake
  proposals. Triggers include "update the account", "add this to [client]",
  "record what we know about [client]", "new client", "the deal moved to
  [stage]", "we submitted the proposal", "we lost the deal", "we won",
  "update the opportunity", "new competitor on [deal]", and "where does this
  belong". Trigger whenever durable knowledge about a client or movement on a
  specific deal should be saved, even without the word "vault".
metadata:
  version: "0.1.0"
---

# vault-update

Writes to `accounts/` and `opportunities/` with the protocol that keeps a shared folder from drifting.

## Route first

- Durable knowledge about the organisation (profile, stack, risks, history) → **account page**.
- Movement on a specific pursuit with a value, a stage or a close date → **opportunity card**.
- A person → `contact-sync`.
- A whole meeting → `meeting-intake`, which sends approved proposals back here.
- A long analysis (a proposal outline, an architecture option, a pricing derivation) → not a page edit. Save it as a dated file in `briefs/` and link it from the card. A card that grows into a 5000 word document stops being updated.

## Before writing

1. Read the vault `CLAUDE.md` (rules), the matching file in `_templates/` (structure) and, for opportunities, `_config/salesforce.md` (stages, closed reasons, value field). Do not rebuild structure from memory; templates change.
2. `Glob` for the page. Watch for name variants: brand versus group, abbreviations, old names.

## Write protocol

The vault may sit on a shared drive that does not merge, or in a repo several people push to. This protocol is not optional.

1. Existing page: `Read` it right before writing and note `last-updated`.
2. Check `owner`. Not the user: write anyway, note it in the log, and tell the user whom to notify.
3. `Edit` the fragment. Do not `Write` the whole file; a full overwrite multiplies the damage of a collision.
4. If `last-updated` changed between the read and the write, stop, show the difference and ask.
5. Set `last-updated` to today.
6. Add a line to `_log/YYYY-MM-[user-slug].md`. Create the file if needed. Never write to someone else's log.
7. New page: add one line to `index.md` and link it from the related page (opportunity from account, account from opportunity).

## Opportunity cards and Salesforce

- **Numbers come from Salesforce.** Stage, value and close date on the card mirror the CRM, using the value field named in the config. If the user states a different number, write the CRM value in the frontmatter and the user's number in the text with a note, and propose a CRM update. Do not invent ranges and do not copy a figure from a proposal into the frontmatter; the offer value and the CRM value often differ.
- **Context comes from the vault**: why we win, why we could lose, how they decide, competition.
- Every stage change gets a dated line in "Stage history" with what caused it. Stages can move backwards; record that too.
- `stage` uses slugs from the config. A stage outside that list is an error, not creativity. Ask.
- Closing: `outcome: won | lost`. When lost, `closed-reason` from the config and a "Why we lost" section are both required. Avoid "other" if any listed reason fits even partly; "other" is where lessons go to die.
- Propose the matching Salesforce change (stage, close date, closed reason, next step Task) and write it only on "yes".

## Account pages

- The page is a profile someone reads in five minutes, not an analysis.
- History **includes losses**. Do not smooth them over.
- An empty Risks section means nobody thought, not that there are no risks. Ask.
- "What the CRM does not show" is the most valuable section: keep each line dated and sourced.

## Content limits

Refuse and explain, then offer the part that can be saved:

- raw material (pasted emails, contract text, transcripts): write the conclusion, cite the source
- secrets of any kind
- personal data outside professional context
- in team mode: pages about colleagues, assessments of people, staffing and pay

## Citations

Every factual line has `(source: ...)`. No source: `[unconfirmed]`. A contradiction with what is already on the page is written into the text with both dates and sources. It is information, not an error to sweep away.

## Finish

Show the real list of changed sections (not a paraphrase), proposed Salesforce changes, and everything marked `[unconfirmed]` as questions to close. Action items found in the material go to `todos/inbox.md` on "yes".
