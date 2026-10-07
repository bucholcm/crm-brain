---
name: setup
description: >
  This skill should be used when the user wants to start using crm-brain, set up a
  deal memory or CRM wiki next to Salesforce, or re-learn their Salesforce org after
  layout changes. Triggers include "set up crm-brain", "install crm-brain",
  "create my vault", "connect my Salesforce to a wiki", "learn my org",
  "re-run setup", "our Salesforce layout changed", and "how do I start".
  It creates the vault folder, checks the Salesforce and Fireflies connectors,
  inspects the org to find which fields really hold the amount and the next step,
  writes that to the vault config, and finishes with one useful result.
metadata:
  version: "0.1.0"
---

# setup

Five steps. The user should get something useful out of step 5, not just an empty folder. Keep user-facing language plain: say "your vault" and "your Salesforce", not paths and API names, unless asked.

## Step 1: the folder

1. Ask where the vault should live. Offer: a new folder inside a connected working folder (default name `crm-brain-vault`), or an existing folder the user names. If no folder is connected, ask the user to connect one and stop until they do.
2. Ask: solo or team? Team means the folder is shared (a shared drive or a git repo) and each person keeps their own private folder for action items. Default: solo.
3. If the target folder already contains a `CLAUDE.md` whose first heading is "CRM Brain vault" and a `_config/salesforce.md`, this is a re-run. Go to "Re-runs" at the bottom.
4. If the target folder contains any other `CLAUDE.md` (a code repo, another wiki), **stop and ask**. Propose a `crm-brain-vault/` subfolder instead. Never merge into or edit someone else's `CLAUDE.md`.
5. Copy the starter kit from `${CLAUDE_SKILL_DIR}/assets/vault/` (the `assets/vault/` folder next to this SKILL.md) into the folder: `CLAUDE.md`, `index.md`, `_templates/`, `_config/`, `todos/`. Create empty folders `accounts/`, `opportunities/`, `contacts/`, `meetings/`, `briefs/`, `_log/`. Never overwrite an existing file.
6. Ask for the user's name and their company email domain. Fill the Settings block at the bottom of the vault `CLAUDE.md` you just copied (`user-name`, `user-slug`, `company-email-domain`, `mode`). In team mode, set `todos-folder` to the user's private folder.

## Step 2: connectors

Check which tools exist in this session. Do not guess from names alone; look for actual capabilities.

- **Salesforce**: a connector that can run SOQL (often a `query` path such as `/services/data/vXX.X/query`, sometimes behind a discover / describe / dispatch pattern). Run one harmless query to prove it works: `SELECT Id, Name FROM User WHERE IsActive = true LIMIT 1`.
- **Fireflies** (or another meeting recorder): a connector that can list or search transcripts. Optional. Without it, `meeting-intake` works from pasted notes or exported files.

If Salesforce is missing, say that crm-brain still works as a meeting and account memory, and that steps 3 and 5 need the connector. Offer to continue without it.

## Step 3: learn the org

Follow `references/salesforce-discovery.md`. It is a fixed sequence of read-only queries. The goal is an honest fingerprint of the org, written to `_config/salesforce.md`:

- who the user is and who reports to them (User.ManagerId, one level)
- which field the pipeline really uses for value (standard `Amount` or a custom field)
- whether `NextStep` is used at all, or the real next step is an open Task
- which stages and closed reasons are in use
- which record types carry open deals
- whether email and calls are logged automatically
- a contact hygiene snapshot on accounts with open deals

Ask the user to confirm the two judgement calls: **which number their pipeline report shows** and **what their default review scope is**. Do not decide those from fill rates alone.

Read only. Setup never writes to Salesforce.

## Step 4: show the fingerprint

Summarise in five to eight short lines what was learned, in plain language. Lead with the findings that change behaviour, for example:

- "Your deal value lives in a custom field. The standard Amount is empty on 96% of open deals, so any report reading it would say your team never enters amounts."
- "Next Step is filled on 3% of open deals. I will treat an open Task with a date as the next step."
- "On accounts with open deals, 41 contacts have no title and 9 are owned by people who have left. Those are worth a look: unknown records sometimes hide the most senior person on the account."

Then write `_config/salesforce.md` and add a line to `_log/`.

## Step 5: first result

Offer one of these, in this order of preference:

1. **A brief for the next real meeting.** Ask which client they meet next, then run `account-brief`.
2. **A pipeline health check** of their scope with `opp-review`.
3. **Intake of the last recorded client meeting** with `meeting-intake`.

Finish with one line on what to do next week: run `vault-lint` on Fridays, and offer to schedule it.

## Re-runs

When layouts change, run steps 2 to 4 only. Then:

1. Compare the new findings with the existing `_config/salesforce.md` and show the differences (field moved, new stage, fill rate jumped, new layout requirement).
2. Treat anything in the file that discovery did not produce (notes, "fields that lie", manual corrections) as the user's and keep it.
3. Write only after an explicit "yes", using `Edit` on the changed lines rather than rewriting the file.
4. Add a dated line to the "Changes" section at the bottom of the file and a line to `_log/`.
