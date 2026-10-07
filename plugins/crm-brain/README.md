# crm-brain plugin

Seven skills that keep a markdown deal memory next to Salesforce. Full documentation, the story behind it and install steps are in the [repository README](../../README.md).

| Skill | Say something like |
|---|---|
| `setup` | "set up crm-brain" |
| `meeting-intake` | "process my call with Acme" |
| `account-brief` | "brief me on Acme, I meet them tomorrow" |
| `opp-review` | "review my pipeline" |
| `contact-sync` | "I met Jane Doe from Acme" |
| `vault-update` | "we submitted the proposal to Acme" |
| `vault-lint` | "lint the vault" |

The schema lives in the vault (`CLAUDE.md`, `_templates/`, `_config/`), not in the skills. Change a rule there and every skill follows it on the next run.

## Requirements

- Claude with a folder connected (Cowork or Claude Code).
- A Salesforce connector that can run SOQL. Recommended, not required.
- A Fireflies connector. Optional; pasted notes work too.

## Safety

Skills read Salesforce freely and write to it only after showing the exact change and getting a "yes".
