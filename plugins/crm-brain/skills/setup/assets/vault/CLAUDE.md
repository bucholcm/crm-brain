# CRM Brain vault: the contract

This folder is a deal memory that sits next to your CRM. Salesforce keeps the fields. This vault keeps what was actually said: who really decides, what the client avoided answering, why the last deal was lost, what was promised on a call and never logged.

Claude maintains it. You curate sources, approve changes and ask questions. Every skill in the `crm-brain` plugin reads this file first. If you change a rule here, every skill follows the new rule from the next run. No plugin update needed.

---

## Folders

| Folder | What lives there |
|---|---|
| `accounts/` | One file per client organisation. Profile, stack, people, history including losses, risks. |
| `opportunities/` | One card per deal. Stage, value, next step, competitors, why we win, why we could lose. |
| `contacts/` | People on the client, partner or vendor side. **Only people who came up in a conversation.** |
| `meetings/` | Meeting stubs: link to the transcript, decisions, signals. Never the transcript itself. |
| `briefs/` | Generated work: account briefs, pipeline reviews, lint reports. Dated filenames. |
| `todos/` | Your action items. `inbox.md` is where skills drop new ones. |
| `_config/` | What setup learned about your Salesforce org, plus transcript name fixes. |
| `_templates/` | Page structures. Skills read them; they never hardcode a schema. |
| `_log/` | Change log, one file per person per month: `_log/YYYY-MM-[user-slug].md`. |
| `index.md` | One line per page. Skills add to it when they create a page. |

---

## The ten rules

1. **Do not mirror the CRM.** A contact page is created when a person comes up in a meeting, email or chat. A mention is the trigger, not the size of the contact list in Salesforce.
2. **Numbers belong to the CRM, context belongs to the vault.** On stage, amount and close date, Salesforce is right. On why, who and what next, the vault is right. On "when did we last really talk to them", the vault is usually right: activity fields in CRMs are often empty or stale.
3. **A disagreement is a note, not an overwrite.** When CRM and vault say different things, write both versions with dates and mark the line `[unconfirmed]`. Never pick one silently.
4. **Every claim has a source.** Format: `(source: meetings/2026-10-01-acme-discovery.md)` or `(source: Salesforce, 2026-10-01)`. No source means `[unconfirmed]`. An empty field is better than an invented one.
5. **Transcripts are proposals, not facts.** Speech to text mishears names, drops the word "not" and assigns sentences to the wrong speaker. Nothing from a transcript goes into an account or opportunity page without a human "yes".
6. **One copy of every page.** Never duplicate a page into another folder, repo or drive. Copies drift, and the stale one always gets read.
7. **Read before you write.** Read the file right before editing it, compare `last-updated`, edit the fragment rather than rewrite the file. If the file changed under you, stop and ask.
8. **Check the layout before you blame a person.** A field that is not on the page layout cannot be filled. Read `_config/salesforce.md` before reporting a gap as someone's omission. Write "amount missing", never "Jane did not enter the amount".
9. **No raw material.** No pasted emails, contracts or transcripts. Write the conclusion and link the source.
10. **People pages are professional only.** Test: would this person read their page without surprise? Role, priorities, how they decide: yes. Health, family, private contact details, gossip: never.

---

## Salesforce writes

Skills read Salesforce freely. **They write to Salesforce only after showing the exact change and getting an explicit "yes".** That covers creating Tasks, fixing a title, changing a record owner, everything.

The field mapping skills rely on (which field holds the amount, where the real next step lives, which stages are in use) is in `_config/salesforce.md`. Setup writes it by inspecting your org. Re-run setup when your admin changes layouts.

---

## Page format

Every page starts with frontmatter and a summary:

```markdown
---
owner: [your-slug]
last-updated: YYYY-MM-DD
---

# Title

**Summary**: One or two sentences. Someone reads this five minutes before a meeting.

**Sources**: Where this comes from.

---
```

Then the sections from the matching file in `_templates/`.

- File names: lowercase, hyphens, no accents or spaces. `acme-retail.md`, `jane-doe.md`, `acme-retail-crm-2026.md`.
- Links: bare wiki links `[[acme-retail]]`, never paths.
- **No empty sections and no pointer lines.** Do not write "see meetings folder for more". If there is nothing dated to record, leave the section out. An absent section says "nothing happened", which is information. A pointer says nothing.

After every content change:

1. Update `last-updated`.
2. Add one line to `_log/YYYY-MM-[user-slug].md`.
3. New page: add one line to `index.md`.

---

## Action items

Skills drop action items for you into `todos/inbox.md` in this format:

```markdown
- [ ] Verb first, what to do ^id-YYYYMMDD-abc
  - source: fireflies | salesforce | email | manual
  - priority: P1 | P2 | P3
  - due: YYYY-MM-DD
  - added: YYYY-MM-DD
  - link: URL to the meeting, record or thread
  - context: One sentence on why it matters.
```

The `^id` must be unique across every file in `todos/`. Default priority is P2. Only items the user must do personally go in; things other people promised become "make sure X does Y" only when the user owns the follow up.

`[x]` means done. `vault-lint` offers to move ticked items to `todos/done.md`; you can also ask for it any time.

---

## Team mode

When several people share this vault (a shared drive or a git repo):

- Keep `todos/` private. Each person points skills at their own private folder for action items.
- Logs stay per person. **Never create a shared append-only file**; two people writing the same file is how sync tools create conflict copies.
- Pages about your own colleagues do not belong here. Mention them by name and role ("account owner: Jane Doe"), but no pages, no assessments, no staffing or pay.
- Shared drives do not merge. Rule 7 is the only protection you have.

---

## Settings

Edit these lines to change behaviour. Skills read them.

- `user-name:` [filled by setup]
- `user-slug:` [filled by setup]
- `company-email-domain:` [filled by setup, used to stop your colleagues being filed as client contacts]
- `todos-folder:` todos/
- `mode:` solo
- `stale-opportunity-days:` 21
- `stale-account-days:` 90
- `no-activity-days:` 30
- `stuck-stage-days:` 45
