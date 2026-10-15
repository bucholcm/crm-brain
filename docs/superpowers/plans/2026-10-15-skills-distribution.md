# Skills Distribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all seven CRM Brain skills installable and discoverable through skills.sh.

**Architecture:** Keep `plugins/crm-brain/skills/` as the only source of skill content because the official `skills` CLI discovers the existing plugin layout. Add root-level skills.sh presentation metadata, document Agent Skills installation alongside the existing Claude options, and pin the public distribution contract with a small standard-library test suite.

**Tech Stack:** Markdown, JSON, Python 3 `unittest`, Bash, `npx skills`

**Spec:** `docs/superpowers/specs/2026-10-15-skills-distribution-design.md`

## Global Constraints

- Canonical skill sources remain under `plugins/crm-brain/skills/`; do not create a second skill tree.
- Do not add an M8ven badge or listing link; CRM Brain is distributed as Agent Skills and a Claude plugin, not an MCP server.
- Preserve the Cowork and Claude Code installation paths.
- Do not change skill behavior, vault templates, or Salesforce permissions.
- Skill descriptions remain at most 1,024 characters and contain no angle-bracket placeholders.
- Preserve unrelated working-tree changes, including the concurrent transcript-source wording edits already present in `README.md`, and never inspect or package Git-excluded private files.

## Review Focus

- Nested plugin layout: all seven `plugins/crm-brain/skills/*/SKILL.md` directories must appear in skills.sh metadata exactly once.
- Metadata drift: a missing, duplicate, or unknown skill slug must fail the distribution contract test.
- Invalid public metadata: `skills.sh.json` must be valid JSON with the published schema URL and non-empty groups.
- Link drift: the README must retain the canonical skills.sh badge/link and contain no M8ven link.
- Product classification: the README must present CRM Brain as Agent Skills and a Claude plugin, not an MCP server.

---

### Task 1: Pin the skills.sh distribution contract

**Files:**
- Create: `tests/test_distribution_metadata.py`
- Create: `skills.sh.json`

**Interfaces:**
- Consumes: skill directories matching `plugins/crm-brain/skills/*/SKILL.md`
- Produces: root `skills.sh.json` with the schema URL and a one-to-one grouping of every published skill slug

- [ ] **Step 1: Write the failing metadata tests**

Create `tests/test_distribution_metadata.py`:

```python
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "plugins" / "crm-brain" / "skills"
EXPECTED_GROUPS = [
    {
        "title": "Get started",
        "description": "Create and configure a CRM Brain vault.",
        "skills": ["setup"],
    },
    {
        "title": "Sales workflows",
        "description": "Turn customer activity into sourced deal knowledge and follow-ups.",
        "skills": [
            "meeting-intake",
            "account-brief",
            "opp-review",
            "contact-sync",
            "vault-update",
        ],
    },
    {
        "title": "Maintenance",
        "description": "Find drift, contradictions, and stale CRM Brain records.",
        "skills": ["vault-lint"],
    },
]


class DistributionMetadataTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "skills.sh.json").read_text())

    def test_uses_published_schema_and_grouping(self):
        self.assertEqual(
            self.config["$schema"],
            "https://skills.sh/schemas/skills.sh.schema.json",
        )
        self.assertEqual(self.config["notGrouped"], "bottom")
        self.assertEqual(self.config["groupings"], EXPECTED_GROUPS)

    def test_every_skill_is_listed_exactly_once(self):
        discovered = {
            path.parent.name for path in SKILLS_ROOT.glob("*/SKILL.md")
        }
        listed = [
            skill
            for grouping in self.config["groupings"]
            for skill in grouping["skills"]
        ]
        self.assertEqual(set(listed), discovered)
        self.assertEqual(len(listed), len(set(listed)))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the metadata tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_distribution_metadata -v
```

Expected: ERROR because `skills.sh.json` does not exist.

- [ ] **Step 3: Add the skills.sh repository metadata**

Create `skills.sh.json`:

```json
{
  "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
  "notGrouped": "bottom",
  "groupings": [
    {
      "title": "Get started",
      "description": "Create and configure a CRM Brain vault.",
      "skills": [
        "setup"
      ]
    },
    {
      "title": "Sales workflows",
      "description": "Turn customer activity into sourced deal knowledge and follow-ups.",
      "skills": [
        "meeting-intake",
        "account-brief",
        "opp-review",
        "contact-sync",
        "vault-update"
      ]
    },
    {
      "title": "Maintenance",
      "description": "Find drift, contradictions, and stale CRM Brain records.",
      "skills": [
        "vault-lint"
      ]
    }
  ]
}
```

- [ ] **Step 4: Run the metadata tests to verify they pass**

Run:

```bash
python3 -m unittest tests.test_distribution_metadata -v
```

Expected: 2 tests pass.

- [ ] **Step 5: Commit the distribution metadata**

```bash
git add tests/test_distribution_metadata.py skills.sh.json
git commit -m "feat: add skills.sh distribution metadata"
```

---

### Task 2: Document public installation and trust links

**Files:**
- Modify: `README.md`
- Create: `tests/test_readme_distribution.py`

**Interfaces:**
- Consumes: the canonical repository slug `bucholcm/crm-brain` and the existing Claude marketplace commands
- Produces: a public skills.sh README badge and Agent Skills installation commands

- [ ] **Step 1: Write the failing README tests**

Create `tests/test_readme_distribution.py`:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReadmeDistributionTests(unittest.TestCase):
    def setUp(self):
        self.readme = (ROOT / "README.md").read_text()

    def test_readme_has_canonical_skills_badge_without_m8ven(self):
        self.assertIn(
            "[![skills.sh](https://skills.sh/b/bucholcm/crm-brain)]"
            "(https://skills.sh/bucholcm/crm-brain)",
            self.readme,
        )
        self.assertNotIn("m8ven.ai", self.readme.lower())

    def test_readme_documents_skills_cli(self):
        install = self.readme.split("## Install", 1)[1].split("## The vault", 1)[0]
        self.assertIn("npx skills add bucholcm/crm-brain", install)
        self.assertIn(
            "npx skills add bucholcm/crm-brain --skill account-brief",
            install,
        )
        self.assertNotIn("M8ven", install)
        self.assertNotIn("MCP server", install)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the README tests to verify they fail**

Run:

```bash
python3 -m unittest tests.test_readme_distribution -v
```

Expected: 2 failures because the badges and `npx skills` commands are absent.

- [ ] **Step 3: Add the canonical skills.sh badge below the README title**

Insert immediately below `# crm-brain`:

```markdown
[![skills.sh](https://skills.sh/b/bucholcm/crm-brain)](https://skills.sh/bucholcm/crm-brain)
```

- [ ] **Step 4: Add Agent Skills as a first-class installation option**

Keep the existing opening requirements paragraph and add this block before the Cowork instructions:

````markdown
**Agent Skills (Codex, Claude Code, Cursor and other supported agents)**

Install all CRM Brain skills:

```sh
npx skills add bucholcm/crm-brain
```

Or install one workflow:

```sh
npx skills add bucholcm/crm-brain --skill account-brief
```

Connect Salesforce and, optionally, a transcript source in your agent, then say **"set up crm-brain"** in the folder where you want the vault.
````

Retain the existing Cowork and Claude Code command blocks after the new Agent Skills option. Do not mention or link to M8ven anywhere in the README.

- [ ] **Step 5: Run the README tests to verify they pass**

Run:

```bash
python3 -m unittest tests.test_readme_distribution -v
```

Expected: 2 tests pass.

- [ ] **Step 6: Run the full repository test suite**

Run:

```bash
python3 -m unittest discover -s tests -v
```

Expected: all 4 distribution tests pass.

- [ ] **Step 7: Build the Claude plugin**

Run:

```bash
./scripts/build.sh
```

Expected: manifest validation passes, all seven skill descriptions report `ok`, and `dist/crm-brain.plugin` is rebuilt.

- [ ] **Step 8: Verify official CLI discovery**

Run:

```bash
npx --yes skills add . --list
```

Expected: output lists exactly `account-brief`, `contact-sync`, `meeting-intake`, `opp-review`, `setup`, `vault-lint`, and `vault-update`. If the package download is blocked by the sandbox, rerun the same command with network approval; do not replace it with a custom discovery script.

- [ ] **Step 9: Verify the final diff and working tree**

Run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors. Compare `git status --short` with the pre-task baseline: this task adds only the intended README hunks and `tests/test_readme_distribution.py`. Concurrent transcript-source edits remain untouched. The generated `dist/crm-brain.plugin` remains ignored and must not be staged.

- [ ] **Step 10: Commit the README documentation and tests**

```bash
git add tests/test_readme_distribution.py
git add -p README.md
git diff --cached --check
git diff --cached
git commit -m "docs: publish Agent Skills install path"
```

At the interactive staging prompt, stage only the badge and Agent Skills installation additions. If they share a hunk with pre-existing transcript-source wording, use the patch editor to exclude those pre-existing lines. The cached diff must contain no unrelated changes before committing.

---

### Task 3: Activate and verify the public listing after publication

**Files:**
- No repository files changed

**Interfaces:**
- Consumes: the public default branch containing Tasks 1 and 2
- Produces: a skills.sh indexing event and evidence that the public GitHub source exposes all seven skills

- [ ] **Step 1: Confirm the implementation commits are on the public default branch**

Run:

```bash
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
```

Expected: both revisions are identical. Do not push unless the user explicitly authorizes publication.

- [ ] **Step 2: Trigger public discovery with telemetry enabled**

Run from a temporary directory outside the repository:

```bash
npx --yes skills add bucholcm/crm-brain --list
```

Expected: output lists the same seven skills. Do not set `DISABLE_TELEMETRY` or `DO_NOT_TRACK`; the install/list event is what allows skills.sh to index the repository.

- [ ] **Step 3: Check the public repository page after cache refresh**

Open:

```text
https://skills.sh/bucholcm/crm-brain
```

Expected: the repository page displays the configured groups and links each of the seven skills. A delay is acceptable because skills.sh processes telemetry and caches repository pages.
