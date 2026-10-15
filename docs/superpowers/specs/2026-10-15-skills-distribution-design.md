# Skills distribution design

## Goal

Make the seven CRM Brain skills easy to install through the `skills` CLI and discoverable on skills.sh, while linking the repository to its existing M8ven trust listing. Keep the Claude plugin installation path intact and avoid maintaining duplicate copies of any skill.

## Distribution model

The canonical skill sources remain under `plugins/crm-brain/skills/`. The `skills` CLI supports the `plugins/*/skills/*/SKILL.md` layout, so CRM Brain does not need a second top-level `skills/` tree or a separate distribution repository.

Users install the collection with:

```sh
npx skills add bucholcm/crm-brain
```

They can select one skill with the CLI's `--skill` option. The existing Claude plugin marketplace and release artifact remain separate installation choices for users who want the complete Claude plugin experience.

## Repository presentation

Add two badges near the top of the root README:

- the standard skills.sh repository badge linked to the CRM Brain page on skills.sh;
- the supplied M8ven score badge linked to the existing CRM Brain listing.

The M8ven badge is trust-listing metadata only. Documentation must not describe CRM Brain as an MCP server or present the M8ven page as an installation method.

Update the installation section so Agent Skills installation is a first-class option alongside Cowork and Claude Code. State the shared runtime requirements once: users still need a Salesforce connector and may optionally connect Fireflies or another transcript source.

## skills.sh metadata

Add `skills.sh.json` at the repository root using the published skills.sh schema. Group all seven existing skills into concise sections:

- Get started: `setup`
- Sales workflows: `meeting-intake`, `account-brief`, `opp-review`, `contact-sync`, `vault-update`
- Maintenance: `vault-lint`

The configuration changes only the skills.sh repository page. It does not alter skill contents or installation behavior.

## Validation and release

Validation must confirm:

1. `skills.sh.json` is valid JSON and every listed slug matches an existing skill directory exactly once.
2. The current plugin build still succeeds.
3. `git diff --check` reports no whitespace errors.
4. `git status --short` contains only intended changes.
5. The official `skills` CLI discovers all seven skills from this repository.

The skills.sh directory is driven by CLI installation telemetry. After the change reaches the public default branch, run an installation or listing flow with telemetry enabled and allow for the skills.sh cache to refresh. Repository changes alone cannot guarantee immediate appearance in the public index.

## Non-goals

- Building or publishing an MCP server.
- Duplicating skill sources at the repository root.
- Moving the existing Claude plugin layout.
- Changing skill behavior, vault templates, or Salesforce permissions.
- Claiming or changing the external M8ven listing.
