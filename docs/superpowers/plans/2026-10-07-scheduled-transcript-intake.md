# Scheduled Transcript Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure an MCP-backed transcript source during setup and process new transcripts twice daily, automatically updating the vault while leaving every Salesforce write pending for explicit approval.

**Architecture:** The packaged vault gains source configuration and append-only processing state files. Setup discovers connector capabilities, validates the user-selected location, writes configuration, and offers a confirmed Cowork schedule; `meeting-intake` consumes that configuration in interactive or scheduled mode and uses stable source IDs for retry-safe processing. Contract tests treat the Markdown skills and templates as executable product behavior, while the existing build script validates and packages the plugin.

**Tech Stack:** Claude plugin skills in Markdown/YAML frontmatter, Markdown vault templates, Python 3 `unittest`, Bash packaging, ZIP plugin artifact.

**Spec:** `docs/superpowers/specs/2026-10-07-scheduled-transcript-intake-design.md`

## Global Constraints

- Fireflies is not a connector requirement, plugin keyword, example source label, or setup instruction.
- The primary transcript source is one Google Drive folder accessed through a user-installed and authorized MCP connector.
- Configuration describes connector capabilities and source location; it never hard-codes MCP tool names.
- Scheduled intake defaults to 08:30 and 16:30 in the user's local timezone and processes at most 20 transcripts per run.
- Meeting stubs, vault knowledge, contacts, opportunity context, and the user's own action items are written automatically.
- Raw transcripts are never copied into the vault; questionable derived claims are marked `[unconfirmed]` and retain source evidence.
- Salesforce may be read during intake but is never written by a scheduled run; every proposed write requires later explicit approval and a fresh read.
- A transcript is marked processed only after all intended automatic vault writes succeed.
- Existing user-authored content and unrelated working-tree changes, including the current `.gitignore` edit, must remain untouched.

## Review Focus

- A transcript that partially wrote files before failure must retry without duplicating meeting sections, facts, contacts, or action items; Task 3 adds a contract test for source-ID reconciliation.
- A scan timestamp must not hide a previously failed transcript; Task 3 tests that failed IDs are fetched before discovering newer items.
- A missing or unauthorized connector must leave both source configuration and processing state unchanged; Task 2 tests the stop-before-write instruction.
- An unknown account or uncertain speaker must not be confidently attached to a record; Task 3 tests `[unconfirmed]` behavior and prohibited guessing.
- A stale Salesforce proposal must never overwrite a newer CRM value; Task 3 tests the fresh-read and changed-value stop condition.

---

### Task 1: Add transcript configuration and state assets

**Files:**
- Create: `tests/test_plugin_contract.py`
- Create: `plugins/crm-brain/skills/setup/assets/vault/_config/transcripts.md`
- Create: `plugins/crm-brain/skills/setup/assets/vault/_config/transcript-state.md`

**Interfaces:**
- Consumes: The setup skill's existing behavior of copying the complete `assets/vault/` tree into a new vault.
- Produces: `_config/transcripts.md` with `source-type`, `source-name`, `source-location`, `source-location-id`, `schedule`, and `last-successful-scan`; `_config/transcript-state.md` with an append-only state table consumed by Tasks 2 and 3.

- [ ] **Step 1: Write the failing asset contract tests**

Create `tests/test_plugin_contract.py`:

```python
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
VAULT = ROOT / "plugins/crm-brain/skills/setup/assets/vault"


class TranscriptConfigAssetsTest(unittest.TestCase):
    def test_transcript_config_has_stable_interface(self):
        text = (VAULT / "_config/transcripts.md").read_text()
        for key in (
            "source-type:",
            "source-name:",
            "source-location:",
            "source-location-id:",
            "schedule:",
            "last-successful-scan:",
        ):
            self.assertIn(key, text)
        self.assertIn("08:30", text)
        self.assertIn("16:30", text)
        self.assertIn("user's local timezone", text)

    def test_transcript_state_is_append_only_and_source_id_keyed(self):
        text = (VAULT / "_config/transcript-state.md").read_text()
        self.assertIn("append-only", text)
        self.assertIn("source-id", text)
        self.assertIn("source-link", text)
        self.assertIn("meeting-date", text)
        self.assertIn("processed-at", text)
        self.assertIn("meeting-stub", text)
        self.assertIn("status", text)
        self.assertIn("processed \\| failed", text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the asset tests and verify the files are missing**

Run: `python3 -m unittest tests.test_plugin_contract.TranscriptConfigAssetsTest -v`

Expected: `ERROR` with `FileNotFoundError` for `_config/transcripts.md` and `_config/transcript-state.md`.

- [ ] **Step 3: Create the configuration asset**

Create `plugins/crm-brain/skills/setup/assets/vault/_config/transcripts.md`:

```markdown
# Transcript source

Setup fills this file after it validates the source through an installed MCP connector. Describe the source here; never store credentials or hard-code MCP tool names.

- source-type: [google-drive | recorder-mcp | unconfigured]
- source-name: [connector or recorder name]
- source-location: [folder URL or recorder scope]
- source-location-id: [stable folder or collection ID]
- schedule: 08:30 and 16:30 in the user's local timezone
- last-successful-scan: never

## Notes

[Manual source notes are preserved when setup runs again.]
```

- [ ] **Step 4: Create the append-only processing state asset**

Create `plugins/crm-brain/skills/setup/assets/vault/_config/transcript-state.md`:

```markdown
# Transcript processing state

Append-only. Never remove a failed row: scheduled intake uses its source ID for retry. Add a later row for a new attempt or final result.

| source-id | source-link | meeting-date | processed-at | meeting-stub | status | note |
|---|---|---|---|---|---|---|
|  |  |  |  |  | processed \| failed |  |
```

- [ ] **Step 5: Run the asset contract tests**

Run: `python3 -m unittest tests.test_plugin_contract.TranscriptConfigAssetsTest -v`

Expected: both tests pass.

- [ ] **Step 6: Commit the configuration assets and tests**

```bash
git add tests/test_plugin_contract.py plugins/crm-brain/skills/setup/assets/vault/_config/transcripts.md plugins/crm-brain/skills/setup/assets/vault/_config/transcript-state.md
git commit -m "feat: add transcript source configuration"
```

### Task 2: Configure the MCP source and schedule during setup

**Files:**
- Modify: `tests/test_plugin_contract.py`
- Modify: `plugins/crm-brain/skills/setup/SKILL.md:3-81`

**Interfaces:**
- Consumes: The configuration keys and state table from Task 1.
- Produces: A setup contract that selects a connector by capabilities, verifies one source file read-only, writes `_config/transcripts.md`, and offers a user-confirmed twice-daily scheduled task.

- [ ] **Step 1: Add failing setup-skill contract tests**

Add below `TranscriptConfigAssetsTest` in `tests/test_plugin_contract.py`:

```python
class SetupSkillTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (
            ROOT / "plugins/crm-brain/skills/setup/SKILL.md"
        ).read_text()

    def test_setup_discovers_capabilities_and_validates_source(self):
        for phrase in (
            "list or search items",
            "read transcript content and metadata",
            "stable source ID",
            "single Google Drive folder",
            "one representative file",
            "read-only",
        ):
            self.assertIn(phrase, self.text)

    def test_missing_connector_stops_before_writing_configuration(self):
        self.assertIn(
            "stop without writing `_config/transcripts.md`",
            self.text,
        )
        self.assertIn("install and authorize", self.text)

    def test_schedule_requires_confirmation_and_local_warning(self):
        for phrase in (
            "08:30",
            "16:30",
            "local timezone",
            "Create it only after explicit confirmation",
            "must run locally",
            "Never perform a Salesforce write",
        ):
            self.assertIn(phrase, self.text)

    def test_setup_has_no_fireflies_dependency(self):
        self.assertNotIn("Fireflies", self.text)
        self.assertNotIn("fireflies", self.text)
```

- [ ] **Step 2: Run the setup tests and verify the old instructions fail**

Run: `python3 -m unittest tests.test_plugin_contract.SetupSkillTest -v`

Expected: failures for missing capability checks, scheduling instructions, and remaining Fireflies text.

- [ ] **Step 3: Replace setup frontmatter and step overview**

Change the description to say that setup creates the vault, validates Salesforce and a user-selected transcript MCP source, stores the transcript location, and offers scheduled intake. Change the body overview from five to six steps. The resulting description must remain under the build script's 1024-character limit and contain no angle-bracket placeholders.

Use this exact connector section:

```markdown
## Step 2: connectors and transcript source

Check which tools exist in this session. Do not guess from connector names; inspect actual capabilities.

- **Salesforce**: require a connector that can run SOQL. Prove it with `SELECT Id, Name FROM User WHERE IsActive = true LIMIT 1`.
- **Transcript source**: require an installed and authorized MCP connector that can list or search items within a user-selected location, read transcript content and metadata, and return a stable source ID or canonical link.

If no compatible transcript connector exists, explain that the user must install and authorize one in Claude. Stop without writing `_config/transcripts.md`; pasted or attached transcripts still work in interactive `meeting-intake`.

When one or more compatible connectors exist:

1. Show their user-facing names and ask which contains the transcripts.
2. For Google Drive, ask the user to provide or select the single Google Drive folder that contains meeting transcripts.
3. List or search that location and read one representative file. This check is read-only.
4. Confirm the chosen source name and location with the user.
5. Fill `_config/transcripts.md`. Store source details, never credentials or MCP tool names.
```

- [ ] **Step 4: Add the scheduled-intake setup step**

Insert this section after the first-result step and renumber the overview accordingly:

```markdown
## Step 6: scheduled intake

Offer a scheduled `meeting-intake` run at 08:30 and 16:30 in the user's local timezone. Let the user choose different times.

Before scheduling, show:

- task name: `CRM Brain meeting intake`
- both run times and timezone
- the configured transcript source and location
- the vault working folder
- approval mode
- the full task instruction

The task instruction must tell Claude to open the vault, invoke `meeting-intake` in scheduled mode, process no more than 20 transcripts, write vault changes and the user's action items automatically, create a dated intake report, and never perform a Salesforce write.

Create it only after explicit confirmation in Claude. If one task cannot express both daily times, propose two daily tasks with identical instructions. If the task needs a local vault folder, warn that it must run locally even though its MCP source may be available remotely.
```

- [ ] **Step 5: Extend re-run behavior for source and schedule changes**

Add these exact rules under `## Re-runs`:

```markdown
When the transcript source or schedule changes, re-run Step 2 or Step 6 as requested. Preserve the Notes section in `_config/transcripts.md`, show the old and new source values, verify the new source before writing, and do not clear `_config/transcript-state.md`. A source change starts discovery in the new location; existing stable source IDs remain the duplicate guard.
```

- [ ] **Step 6: Run setup tests**

Run: `python3 -m unittest tests.test_plugin_contract.SetupSkillTest -v`

Expected: all setup tests pass.

- [ ] **Step 7: Commit the setup flow**

```bash
git add tests/test_plugin_contract.py plugins/crm-brain/skills/setup/SKILL.md
git commit -m "feat: configure scheduled transcript intake"
```

### Task 3: Make meeting intake scheduled, automatic, and retry-safe

**Files:**
- Modify: `tests/test_plugin_contract.py`
- Modify: `plugins/crm-brain/skills/meeting-intake/SKILL.md:3-103`

**Interfaces:**
- Consumes: `_config/transcripts.md`, `_config/transcript-state.md`, the vault write protocol, and connector capabilities validated by setup.
- Produces: Interactive and scheduled intake modes; a 20-item batch limit; source-ID deduplication; automatic vault and todo writes; `briefs/YYYY-MM-DD-HHMM-meeting-intake.md`; pending Salesforce proposals with fresh-read protection.

- [ ] **Step 1: Add failing meeting-intake contract tests**

Add below `SetupSkillTest` in `tests/test_plugin_contract.py`:

```python
class MeetingIntakeSkillTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (
            ROOT / "plugins/crm-brain/skills/meeting-intake/SKILL.md"
        ).read_text()

    def test_modes_and_batch_limit_are_explicit(self):
        for phrase in (
            "## Interactive mode",
            "## Scheduled mode",
            "up to 20",
            "_config/transcripts.md",
            "_config/transcript-state.md",
        ):
            self.assertIn(phrase, self.text)

    def test_failed_items_retry_before_new_discovery(self):
        failed = self.text.index("Retry every latest `failed` source ID")
        discovery = self.text.index("Discover new transcripts")
        self.assertLess(failed, discovery)
        self.assertIn("Do not advance state for an unreadable transcript", self.text)

    def test_stable_id_reconciliation_prevents_duplicate_writes(self):
        for phrase in (
            "stable source ID",
            "canonical source URL",
            "source name, meeting date and title",
            "reconcile every destination",
            "update or skip it; never append a duplicate",
        ):
            self.assertIn(phrase, self.text)

    def test_vault_writes_are_automatic_and_uncertainty_is_preserved(self):
        for phrase in (
            "written automatically",
            "Mark it `[unconfirmed]`",
            "Never guess the account",
            "Never copy the raw transcript",
            "only tasks for the user",
        ):
            self.assertIn(phrase, self.text)

    def test_salesforce_stays_proposal_only(self):
        for phrase in (
            "Never write to Salesforce during scheduled intake",
            "re-read the Salesforce record",
            "current value changed",
            "stop and show the conflict",
            "Never propose Amount",
        ):
            self.assertIn(phrase, self.text)

    def test_meeting_intake_has_no_fireflies_coupling(self):
        self.assertNotIn("Fireflies", self.text)
        self.assertNotIn("fireflies", self.text)
```

- [ ] **Step 2: Run the meeting-intake tests and verify the old approval flow fails**

Run: `python3 -m unittest tests.test_plugin_contract.MeetingIntakeSkillTest -v`

Expected: failures because scheduled mode, state handling, automatic writes, and the new Salesforce boundary are absent.

- [ ] **Step 3: Replace the skill description and stream contract**

Use a description that triggers for supplied transcripts, requests to process recent meetings, and scheduled transcript intake. Replace the stream table and following paragraph with:

```markdown
| Stream | Goes to | Mode |
|---|---|---|
| 1. Meeting stub | `meetings/YYYY-MM-DD-[slug].md` | written automatically |
| 2. Facts and signals | `accounts/`, `opportunities/`, `contacts/` | written automatically |
| 3. CRM follow ups | dated intake report, then Salesforce after approval | proposal only |
| 4. Action items | `todos/inbox.md` or `todos-folder` | written automatically |

Streams 1, 2 and 4 are written automatically. Never write to Salesforce during scheduled intake; interactive intake may apply only the exact changes the user explicitly approves. Speech to text can mishear names, drop negations, and assign the wrong speaker, so preserve source evidence and mark questionable claims `[unconfirmed]`.
```

- [ ] **Step 4: Add explicit interactive and scheduled modes**

Add these sections before transcript analysis:

```markdown
## Interactive mode

Process the transcript named or supplied by the user. Prefer the configured source, but accept an attached file or pasted notes. A bare link requires a connector that can read it; otherwise ask for the file or text.

## Scheduled mode

Read `_config/transcripts.md` and `_config/transcript-state.md`. Stop without changing either file when the connector or configured location is unavailable.

1. Retry every latest `failed` source ID by fetching it directly.
2. Discover new transcripts in the configured location, using `last-successful-scan` only as a search optimization.
3. Process failed items first, then the oldest newly discovered items, up to 20 total.
4. Process each transcript independently. Do not advance state for an unreadable transcript.
5. When discovery succeeds, update `last-successful-scan` even if an individual transcript failed; its recorded source ID keeps it in the retry set.
6. If nothing is eligible, report success briefly and do not create an empty intake report.
```

- [ ] **Step 5: Define identity, reconciliation, and state transition rules**

Add this section before the write streams:

```markdown
## Source identity and retries

Use the connector's stable source ID as the durable identity. If none exists, use the canonical source URL. Only when neither exists, fingerprint the source name, meeting date and title.

Before any write, search meeting stubs and `_config/transcript-state.md` for that identity. On a retry, reconcile every destination by the same identity: if a meeting section, fact, contact update, or action item already came from this source, update or skip it; never append a duplicate.

Append `processed` to `_config/transcript-state.md` only after the meeting stub, vault pages, todo inbox, index, timestamps, and log all succeed. On failure, append `failed` with the short error and the files already changed.
```

- [ ] **Step 6: Replace proposal-gated vault writes with safe automatic writes**

Rewrite the meeting-stub, vault, and action-item sections to require:

```markdown
- Read each destination immediately before editing it and preserve user-authored content.
- Create the meeting stub automatically from `_templates/meeting.md`; include `source-type`, `source-id`, the source link, meeting date, attendees, decisions, signals, next steps, and related wiki links.
- Never copy the raw transcript or use verbatim quotes.
- Automatically update account, opportunity, and professional contact context with dated source citations.
- Mark it `[unconfirmed]` when speaker attribution, name normalization, affiliation, negation, account, or opportunity linkage is uncertain. Never guess the account.
- Record contradictions as dated alternatives; do not silently choose one version.
- Extract only tasks for the user and write them automatically with `source` set to the configured `source-name`, the source link, and a unique deterministic ID that can be recognized on retry.
```

- [ ] **Step 7: Make Salesforce proposals persistent and stale-safe**

Replace the Salesforce section and run report with:

```markdown
## Salesforce proposals

Salesforce reads are allowed for matching and duplicate checks. Never write to Salesforce during scheduled intake. In a later interactive session, write only the exact changes the user explicitly approves.

Propose Tasks, meeting logging, stage or close-date changes, and contact fixes only when transcript evidence supports them. Never propose Amount from a transcript.

Write exact changes, old values, evidence, and source links to `briefs/YYYY-MM-DD-HHMM-meeting-intake.md`. Include processed, skipped and failed transcripts; vault files changed; action items created; ambiguities; and every pending Salesforce proposal.

When the user later approves a proposal, re-read the Salesforce record. If its current value changed since the report, stop and show the conflict instead of applying the stale proposal. Apply only the individually approved changes.
```

- [ ] **Step 8: Run meeting-intake tests and the full contract suite**

Run: `python3 -m unittest tests.test_plugin_contract.MeetingIntakeSkillTest -v`

Expected: all meeting-intake tests pass.

Run: `python3 -m unittest discover -s tests -v`

Expected: all contract tests pass.

- [ ] **Step 9: Commit scheduled and automatic intake behavior**

```bash
git add tests/test_plugin_contract.py plugins/crm-brain/skills/meeting-intake/SKILL.md
git commit -m "feat: automate scheduled meeting intake"
```

### Task 4: Align briefs and the vault contract with configured transcript sources

**Files:**
- Modify: `tests/test_plugin_contract.py`
- Modify: `plugins/crm-brain/skills/account-brief/SKILL.md:18-93`
- Modify: `plugins/crm-brain/skills/setup/assets/vault/CLAUDE.md:9-125`
- Modify: `plugins/crm-brain/skills/setup/assets/vault/_templates/meeting.md:1-14`

**Interfaces:**
- Consumes: Configured transcript source and stable source identity from Tasks 1-3.
- Produces: Account briefs constrained to the configured source; meeting stubs with source metadata; a vault contract that permits automatic transcript-derived writes while enforcing evidence and uncertainty markers.

- [ ] **Step 1: Add failing vault-alignment tests**

Add below `MeetingIntakeSkillTest` in `tests/test_plugin_contract.py`:

```python
class VaultAndBriefContractTest(unittest.TestCase):
    def test_account_brief_uses_configured_source(self):
        text = (
            ROOT / "plugins/crm-brain/skills/account-brief/SKILL.md"
        ).read_text()
        self.assertIn("_config/transcripts.md", text)
        self.assertIn("configured transcript location", text)
        self.assertIn("configured source name", text)
        self.assertNotIn("Fireflies", text)

    def test_meeting_template_carries_source_identity(self):
        text = (VAULT / "_templates/meeting.md").read_text()
        self.assertIn("source-type:", text)
        self.assertIn("source-id:", text)
        self.assertIn("transcript: [canonical source URL]", text)

    def test_vault_contract_allows_automatic_derived_writes_safely(self):
        text = (VAULT / "CLAUDE.md").read_text()
        self.assertIn("Transcript-derived vault updates are automatic", text)
        self.assertIn("mark it `[unconfirmed]`", text)
        self.assertIn("Salesforce writes still require", text)
        self.assertIn("configured transcript source and processing state", text)
        self.assertIn("source: [configured source-name]", text)
        self.assertNotIn("source: fireflies", text)
```

- [ ] **Step 2: Run the alignment tests and verify existing contracts fail**

Run: `python3 -m unittest tests.test_plugin_contract.VaultAndBriefContractTest -v`

Expected: failures for missing source config, source identity fields, and the old human-approval rule.

- [ ] **Step 3: Update account-brief gathering and citations**

Require `account-brief` to read `_config/transcripts.md`, search only the configured transcript location for the last 90 days, and stop source lookup with a clear limitation when the connector is unavailable. Replace the fixed recorder citation with:

```markdown
Cite every line with its actual source: `(source: Salesforce, Opportunity [name], 2026-10-01)`, `(source: meetings/2026-09-12-acme-qbr.md)`, or `(source: [configured source name], 2026-09-28, [source link])`. Nothing without a source; mark guesses `[unconfirmed]`.
```

- [ ] **Step 4: Add source identity to the meeting template**

Change the template frontmatter to:

```markdown
---
date: YYYY-MM-DD
account: [account-slug or unconfirmed]
opportunity: [opportunity-slug or empty]
owner: [slug of the person who ran it]
source-type: [google-drive or configured source type]
source-id: [stable source ID or fallback fingerprint]
transcript: [canonical source URL]
last-updated: YYYY-MM-DD
---
```

- [ ] **Step 5: Update the vault contract**

Change `_config/` in the folder table to mention the Salesforce fingerprint, configured transcript source and processing state. Replace rule 5 with:

```markdown
5. **Transcript-derived vault updates are automatic, not unquestionable.** Preserve the source date and link. When attribution, names, affiliation, negation, account linkage or meaning is uncertain, mark it `[unconfirmed]` instead of guessing. Salesforce writes still require the exact proposed change and an explicit human "yes".
```

Change the action-item source line to:

```markdown
  - source: [configured source-name] | salesforce | email | manual
```

- [ ] **Step 6: Run alignment tests and full contract suite**

Run: `python3 -m unittest tests.test_plugin_contract.VaultAndBriefContractTest -v`

Expected: all alignment tests pass.

Run: `python3 -m unittest discover -s tests -v`

Expected: all contract tests pass.

- [ ] **Step 7: Commit the aligned vault contract**

```bash
git add tests/test_plugin_contract.py plugins/crm-brain/skills/account-brief/SKILL.md plugins/crm-brain/skills/setup/assets/vault/CLAUDE.md plugins/crm-brain/skills/setup/assets/vault/_templates/meeting.md
git commit -m "feat: align vault with transcript sources"
```

### Task 5: Remove Fireflies product coupling from docs and metadata

**Files:**
- Modify: `tests/test_plugin_contract.py`
- Modify: `README.md:1-60`
- Modify: `plugins/crm-brain/README.md:1-28`
- Modify: `plugins/crm-brain/.claude-plugin/plugin.json:1-18`
- Modify: `.claude-plugin/marketplace.json:1-13`
- Modify: `JOURNEY.md:15-20,98-107`

**Interfaces:**
- Consumes: The implemented setup and intake behavior from Tasks 2-4.
- Produces: Installation and product documentation that tells users to configure a compatible MCP connector, select a transcript location, and optionally schedule twice-daily intake.

- [ ] **Step 1: Add failing product-copy and metadata tests**

Add imports and the test class below the existing tests in `tests/test_plugin_contract.py`:

```python
import json


class ProductCopyTest(unittest.TestCase):
    PRODUCT_FILES = (
        "README.md",
        "JOURNEY.md",
        "plugins/crm-brain/README.md",
        "plugins/crm-brain/.claude-plugin/plugin.json",
        ".claude-plugin/marketplace.json",
    )

    def test_product_copy_has_no_fireflies_coupling(self):
        for relative in self.PRODUCT_FILES:
            text = (ROOT / relative).read_text()
            self.assertNotIn("Fireflies", text, relative)
            self.assertNotIn("fireflies", text, relative)

    def test_readmes_explain_drive_connector_folder_and_schedule(self):
        for relative in ("README.md", "plugins/crm-brain/README.md"):
            text = (ROOT / relative).read_text()
            self.assertIn("Google Drive", text, relative)
            self.assertIn("MCP connector", text, relative)
            self.assertIn("transcript folder", text, relative)
            self.assertIn("twice daily", text, relative)

    def test_manifest_keywords_describe_current_integration(self):
        manifest = json.loads(
            (ROOT / "plugins/crm-brain/.claude-plugin/plugin.json").read_text()
        )
        self.assertNotIn("fireflies", manifest["keywords"])
        self.assertIn("google-drive", manifest["keywords"])
        self.assertIn("automation", manifest["keywords"])
```

- [ ] **Step 2: Run product-copy tests and verify Fireflies references fail**

Run: `python3 -m unittest tests.test_plugin_contract.ProductCopyTest -v`

Expected: failures in both READMEs, metadata, and the historical journey wording.

- [ ] **Step 3: Rewrite installation and requirements copy**

In both READMEs, describe the requirement and setup path with this meaning:

```markdown
You need Claude with a folder connected, an optional Salesforce connector, and an MCP connector that can search and read your meeting transcripts. The documented setup uses Google Drive: install and authorize its MCP connector, keep exported transcripts in one Drive folder, then point CRM Brain to that transcript folder during setup.

Setup can also offer a twice daily scheduled intake. It writes meeting knowledge and personal action items to the vault automatically, while Salesforce changes remain proposals until you approve them.
```

Update Cowork and Claude Code steps so they instruct the user to configure the Google Drive MCP connector, connect the vault folder, run setup, and choose the transcript folder. Do not claim CRM Brain installs or authorizes the connector.

- [ ] **Step 4: Update metadata**

Remove `fireflies` from `plugins/crm-brain/.claude-plugin/plugin.json`. Add `google-drive` and `automation`. Rewrite the marketplace description so it says CRM Brain is for Salesforce and MCP-accessible meeting transcripts, without naming a recorder vendor.

- [ ] **Step 5: Align the journey's implementation claims**

Change the May scheduled-run sentence to say it reads new transcripts from a configured source. Change the final lesson about proposals so it states that vault updates preserve evidence and mark uncertainty, while CRM writes remain proposals. Keep the personal narrative and quantitative history intact.

- [ ] **Step 6: Run product-copy and full contract tests**

Run: `python3 -m unittest tests.test_plugin_contract.ProductCopyTest -v`

Expected: all product-copy tests pass.

Run: `python3 -m unittest discover -s tests -v`

Expected: all contract tests pass.

- [ ] **Step 7: Commit documentation and metadata**

```bash
git add tests/test_plugin_contract.py README.md JOURNEY.md plugins/crm-brain/README.md plugins/crm-brain/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs: describe MCP transcript intake"
```

### Task 6: Validate and package the complete plugin

**Files:**
- Modify: `tests/test_plugin_contract.py`
- Regenerate: `dist/crm-brain.plugin`

**Interfaces:**
- Consumes: All source, skill, template, and documentation changes from Tasks 1-5.
- Produces: A validated `dist/crm-brain.plugin` containing configuration assets, updated skills, templates, and the repository license.

- [ ] **Step 1: Add a failing archive-content test**

Add imports and this class to `tests/test_plugin_contract.py`:

```python
import zipfile


class PackagedPluginTest(unittest.TestCase):
    def test_archive_contains_transcript_assets_and_updated_skills(self):
        archive = ROOT / "dist/crm-brain.plugin"
        with zipfile.ZipFile(archive) as plugin:
            names = set(plugin.namelist())
            for name in (
                "skills/setup/assets/vault/_config/transcripts.md",
                "skills/setup/assets/vault/_config/transcript-state.md",
                "skills/setup/SKILL.md",
                "skills/meeting-intake/SKILL.md",
                "skills/account-brief/SKILL.md",
                "LICENSE",
            ):
                self.assertIn(name, names)
            meeting_intake = plugin.read(
                "skills/meeting-intake/SKILL.md"
            ).decode()
            self.assertIn("## Scheduled mode", meeting_intake)
            self.assertNotIn("Fireflies", meeting_intake)
```

- [ ] **Step 2: Run the archive test before rebuilding**

Run: `python3 -m unittest tests.test_plugin_contract.PackagedPluginTest -v`

Expected: failure because the existing archive lacks the new configuration assets and scheduled-mode contract.

- [ ] **Step 3: Run the complete validation and rebuild**

Run: `python3 -m unittest discover -s tests -v`

Expected: every non-archive contract test passes; only the archive test may fail before rebuild.

Run: `./scripts/build.sh`

Expected: manifest reports `ok crm-brain 0.1.0`, every skill reports `ok`, and `dist/crm-brain.plugin` is rebuilt.

- [ ] **Step 4: Verify the rebuilt archive and repository diff**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass, including `PackagedPluginTest`.

Run: `unzip -l dist/crm-brain.plugin`

Expected: both transcript configuration assets, all updated skills and templates, and `LICENSE` are listed.

Run: `git diff --check`

Expected: no whitespace errors.

Run: `git status --short`

Expected: only the files named by this plan plus the pre-existing `.gitignore` modification appear; `.gitignore` remains unchanged by this work.

- [ ] **Step 5: Commit the test suite and rebuilt plugin**

```bash
git add tests/test_plugin_contract.py dist/crm-brain.plugin
git commit -m "test: verify packaged transcript intake"
```

- [ ] **Step 6: Run final verification from the committed tree**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass.

Run: `./scripts/build.sh`

Expected: manifest and skill validation succeed and the plugin archive is rebuilt.

Run: `git diff --check`

Expected: no whitespace errors are reported. If rebuilding changes `dist/crm-brain.plugin` after the commit, inspect the archive timestamps; commit the deterministic content change only if its bytes differ for reasons other than ZIP metadata.
