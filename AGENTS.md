# AGENTS.md

## Repository purpose

This repository packages `crm-brain`, a Claude plugin that maintains a Markdown deal-memory vault next to Salesforce. The product is expressed primarily through Markdown skill instructions and vault templates, so wording changes can change runtime behavior.

## Working agreements

- Preserve unrelated working-tree changes. Never discard or overwrite user-authored files.
- Treat files excluded by Git as private. Do not read, stage, quote, reference, package, or publish them unless the user explicitly asks.
- Edit plugin sources under `plugins/crm-brain/`. Treat `dist/crm-brain.plugin` as generated output.
- Keep changes focused on the requested behavior; avoid unrelated restructuring.
- Never add credentials, customer data, real transcripts, or a real CRM Brain vault to the repository.

## Plugin contracts

- Skill descriptions must be no longer than 1,024 characters.
- Do not use angle-bracket placeholders in skill descriptions; the validator interprets them as XML tags.
- The vault stores conclusions and source links, never raw transcripts.
- Transcript-derived vault updates may be automatic, but uncertain claims must be marked `[unconfirmed]` and retain source evidence.
- Salesforce writes require the exact proposed change and explicit user approval. Scheduled intake never writes to Salesforce.

## Verification

- When `tests/` exists, run `python3 -m unittest discover -s tests -v`.
- Run `./scripts/build.sh` after changing plugin sources, templates, manifests, or packaging.
- Run `git diff --check` before completion.
- Inspect `git status --short` and ensure only intended files are staged or committed.
