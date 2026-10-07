---
name: vault-lint
description: >
  This skill should be used to audit the crm-brain vault for drift: conflict
  copies, duplicates, contradictions between pages, drift between opportunity
  cards and Salesforce, stale deals, missing sources, orphans, dead links and
  content that should not be there. Triggers include "lint the vault", "audit
  the vault", "vault health check", "what is stale", "find duplicates", "check
  for conflicts", "orphan pages", and "is the vault in sync with Salesforce".
  Use for the weekly hygiene pass or whenever the user suspects drift.
metadata:
  version: "0.1.0"
---

# vault-lint

A weekly audit. Drift in a shared knowledge base is a matter of time, not risk. The job is to catch it while it is cheap to fix.

Report first. Fix nothing without approval, except an obvious typo in a frontmatter key, which can be fixed while saying so.

## How to work

Start with `Glob **/*.md` for the full file list. Use `Read` and `Grep` for content. If the vault lives on a streamed cloud drive, shell tools may only see files already downloaded; prefer the file tools.

Read the vault `CLAUDE.md` for thresholds and `_config/salesforce.md` for stages and the value field.

## Checks, in order of severity

### 1. Conflict copies and duplicates (data loss)

- Files named like `page (1).md`, `page (conflict).md`, `page-copy.md`, `page 2.md`.
- Two pages about the same entity under different names.
- The same page living in two places (another folder, another repo). One copy is always stale, and it is always the one somebody reads.

Read both versions, show the difference, ask which to keep. Never delete on your own. Report the count of conflict copies on its own line: it is the metric that tells whether the sync method works.

### 2. Content that should not be here

- Secrets: `token`, `password`, `api_key`, `secret`, strings that look like keys.
- Personal data outside professional context in `contacts/`.
- Raw material: long quoted blocks, pasted emails, contract passages.
- Colleagues filed as client contacts (addresses on `company-email-domain`).
- In team mode: pages about colleagues, assessments, staffing or pay.

Quote the hit with its path and propose where it should go instead.

### 3. Contradictions

- Opportunity stage on the card versus the account page's Open deals line.
- A person's role in `contacts/` versus the account's People table.
- Deal value in two places.

Show both versions with their `last-updated`. The newer one is not automatically right. Ask.

### 4. Drift against Salesforce (if connected)

For each opportunity card with a `salesforce-id`, compare stage, value field, close date and closed status. List differences in a table. Salesforce is right on numbers; propose card updates via `vault-update`. Cards whose Salesforce record is closed or deleted while the card is open are 🔴.

Also: open deals in the user's scope with recent meetings in `meetings/` but no card. Those are deals with context nobody wrote down.

### 5. Pipeline hygiene on cards

- `last-updated` older than `stale-opportunity-days` [21].
- `next-step-date` in the past, or `next-step` that is filler ("follow up", "waiting", "monitoring").
- `close-date` in the past on an open stage.
- `stage` outside the config list.
- Closed without `outcome`; lost without `closed-reason` or without "Why we lost"; `outcome` set on an open stage.

### 6. Orphans and gaps

- Pages with no inbound `[[link]]`.
- Contacts and opportunities not linked from their account.
- Names that recur across several pages without a page of their own. This is the most common source of knowledge gaps.
- `[[links]]` that point nowhere.
- Pages missing from `index.md`.

### 7. Age and format

- Accounts with `last-updated` older than `stale-account-days` [90]: either the account died or nobody owns it.
- Missing `owner` or `last-updated`.
- Claims without a source and not marked `[unconfirmed]`.
- Empty template sections and pointer lines ("see the meetings folder"). Remove them; absence carries more information.
- File names with capitals, spaces, accents or underscores.
- Any shared append-only file written by more than one person. That is a design error, not a cosmetic one.

### 8. Action items

- Ticked `[x]` items still in `todos/inbox.md` or `todos/active.md`: offer to move them to `todos/done.md` (create it if missing).
- Open items with a `due` date in the past: list them, do not change them.

## Report

One summary sentence with counts per severity. A clean vault gets one sentence and nothing more.

Then a numbered list sorted by severity, not by category:

```
N. [CRITICAL | IMPORTANT | COSMETIC] path: what is wrong
   → proposed fix
```

End with the conflict copy count on its own line.

## After the report

Ask what to fix. Apply fixes through `vault-update` and `contact-sync`, which carry the read before write protocol. Add a line to `_log/` with the date and number of findings.

If this is the first lint, or it was run by hand, offer to schedule it weekly (Friday morning works well). Hygiene that depends on someone remembering is not hygiene.
