---
name: contact-sync
description: >
  This skill should be used when a person on the client, partner or vendor side
  comes up and their page should be created or updated, with a two way check
  against Salesforce. Triggers include "add a contact", "new stakeholder", "I met
  [name]", "who is [name]", "update [name]'s page", "[name] changed jobs",
  "who is the champion at [client]", "sync contacts for [client]", and "is
  [name] in Salesforce". Also trigger when a meeting or email introduces a named
  person on the client side. Do not use for the user's own colleagues.
metadata:
  version: "0.1.0"
---

# contact-sync

Contact pages for people who matter, synced with Salesforce in both directions. The vault does not mirror the CRM: a CRM can hold hundreds of contacts on key accounts while the vault holds a few dozen pages. That is correct. A page exists because someone came up in a conversation.

## First question, always: which side are they on?

- An address on `company-email-domain` (from the vault settings), or a role on the user's own team: **a colleague. No page here.** Say so. Colleagues can be named on account pages by role, nothing more.
- Client, partner or vendor: continue.
- Unsure: ask. Never guess. A wrong guess puts private notes about a colleague into a folder others read.

Check the same thing in Salesforce: a Contact record with the user's own company domain filed on a client account is a defect worth reporting. A colleague recorded as the client's champion distorts every account review that reads it.

## Before writing

1. Read the vault `CLAUDE.md`, `_templates/contact.md`, `_config/salesforce.md`.
2. `Glob` `contacts/` for the person by surname and by first name separately; the same person can be filed under a variant.
3. Search Salesforce:

```sql
SELECT Id, Name, Title, Email, Account.Name, Owner.Name, Owner.IsActive,
  LastActivityDate, CreatedDate
FROM Contact WHERE Name LIKE '%[Surname]%' OR Email = '[email]'
```

Watch for: two records with one email (duplicates), several people with the surname on different accounts, no record at all.

## Salesforce to vault

Take from Salesforce: title, account, email, record owner, last activity, Salesforce Id.

- **Title**: the CRM title usually wins over a guess from a transcript. If the person clearly does something else in meetings, write both: "CRM title: X. In practice: Y (source)".
- **Last contact**: the CRM is often wrong here. Activity fields are empty, lag behind, or contain impossible dates. Use the latest dated meeting or email in the vault or recorder for `last-contact`, and note the CRM date only if it differs.
- **Duplicates**: when two records exist with different titles, the newer one usually carries the current title. Note which record should survive a merge and which values must be kept: a merge keeps the master record's values, not the best ones.

## Vault to Salesforce

Propose fixes for what the CRM lacks and the vault knows. Show each exact change and write only on "yes":

- empty `Title`
- record owned by an inactive user (propose the active relationship owner)
- person who speaks in meetings but has no Contact record
- colleague filed as a client contact

A missing title or an inactive owner is a defect to fix in the CRM, not something to work around in the vault.

Sometimes an anonymous record, no title, no activity, owned by someone who left, belongs to the most senior person on the account. When a name from a meeting matches a record like that, say so plainly.

## Writing the page

1. Existing page: `Read` right before writing, keep `last-updated` in mind, `Edit` the fragment.
2. Fill the frontmatter that matters: `position` (champion, neutral, against, unknown) and `influence` (decision-maker, influencer, operational, gatekeeper). "unknown" is honest and a prompt for work; do not default to "neutral" to fill the field.
3. **"What they care about" is the reason the page exists.** If nothing is known, ask the user for one sentence from observation, not from LinkedIn. If they have none, write the page anyway but list the gap.
4. Role changes are added with a date under "Contact history". Never delete the old role.
5. Disagreements go under "CRM notes", marked `[unconfirmed]`.
6. Update `last-updated`, add a `_log/` line, add new pages to `index.md` **and** link them from the account page's People table. A contact not linked from its account is an orphan.

## Hard limits

Do not record personal data outside professional context: private phone, home address, family, health, politics, gossip. Work email and phone are fine. Do not record opinions the user would not say to the person's face. If the user dictates something on this list, write the rest and say plainly which part was left out and why.

## Finish

Say what was written in the vault, what was proposed for Salesforce, and list separately everything still `[unconfirmed]`, especially `position` and `influence` if they came out "unknown". Those are questions for the next meeting.
