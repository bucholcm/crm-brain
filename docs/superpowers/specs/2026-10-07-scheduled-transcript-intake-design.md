# Scheduled transcript intake design

## Purpose

CRM Brain will no longer depend on a Fireflies MCP connector. During setup, the user will choose an installed transcript-capable MCP connector and point CRM Brain to the specific source that contains meeting transcripts. The initial documented path is a Google Drive folder accessed through a Google Drive MCP connector.

CRM Brain will also offer a scheduled intake that runs twice per day. Scheduled intake will automatically update the local vault from new transcripts while keeping every Salesforce change as a proposal that requires explicit user approval.

## Goals

- Let a user configure a transcript source without modifying the packaged skill.
- Support a Google Drive folder through an MCP connector as the primary setup path.
- Leave room for another transcript MCP connector without redesigning meeting intake.
- Process new transcripts interactively or on a twice-daily schedule.
- Automatically write meeting stubs, vault knowledge, relevant contact and opportunity context, and the user's action items.
- Never write transcript-derived changes to Salesforce without explicit approval.
- Make scheduled processing idempotent and safe to retry.

## Non-goals

- Configuring Fireflies to export transcripts into Google Drive.
- Installing or authorizing an MCP connector on the user's behalf.
- Copying raw transcripts into the CRM Brain vault.
- Synchronizing or editing source transcripts.
- Providing a general connector framework outside transcript discovery and reading.

## Configuration

Setup will create `_config/transcripts.md`. The file will contain:

- `source-type`: initially `google-drive` or `recorder-mcp`.
- `source-name`: the user-facing connector or recorder name.
- `source-location`: a Google Drive folder URL or an equivalent recorder scope.
- `source-location-id`: the stable folder or collection ID when the connector exposes one.
- `schedule`: the intended intake cadence and timezone, defaulting to 08:30 and 16:30 in the user's local timezone.
- `last-successful-scan`: an informational timestamp, not the sole deduplication mechanism.

The configuration will describe the source, not hard-code MCP tool names. At runtime, the skill will inspect the available connector capabilities and require operations equivalent to:

1. List or search items within the configured location.
2. Read the selected transcript's content and metadata.
3. Return a stable source ID and a link when the connector supports them.

If the configured connector or required capabilities are unavailable, intake will stop without advancing state and report what is missing.

## Setup flow

Setup will:

1. Ask the user to install and authorize a transcript-capable MCP connector if none is available. CRM Brain will not install or authorize it automatically.
2. Present compatible connectors and ask which one contains the transcripts.
3. For Google Drive, ask the user to provide or select the single folder containing meeting transcripts.
4. Verify that Claude can list or search the location and read one representative file. The verification is read-only.
5. Write the validated source to `_config/transcripts.md`.
6. Offer scheduled intake, defaulting to 08:30 and 16:30 in the user's local timezone, and let the user choose different times.
7. Show the proposed scheduled-task name, cadence, instructions, approval mode, and working folder before creation. Create the task only after the user confirms it in Claude.
8. Warn that a scheduled task requiring a local vault folder must run locally. Connector-only sources can be queried remotely, but vault writes determine where the full task can run.

Re-running setup will preserve manual notes in the configuration, show the proposed source or schedule changes, and update them only after confirmation.

## Interactive and scheduled modes

`meeting-intake` will support two modes that share the same processing rules.

### Interactive mode

Interactive mode processes the transcript named or supplied by the user. It may use the configured source, an attached file, or pasted notes. It reports automatic vault writes and presents Salesforce proposals for approval.

### Scheduled mode

Scheduled mode searches only within the configured transcript source. It processes up to 20 eligible, unprocessed transcripts per run so that one unusually large backlog does not monopolize a run. Remaining items are left for the next run.

Each transcript is processed independently. Failure on one transcript does not mark it processed and does not prevent later transcripts from being attempted when that is safe.

## Discovery and deduplication

Each run will retry known failed items first, then query for transcripts created or modified since the last successful scan. Timestamps are only a discovery optimization. The durable deduplication key is:

1. The connector's stable file or transcript ID.
2. If unavailable, a canonical source URL.
3. As a last resort, a fingerprint derived from source name, meeting date, and title.

Every meeting stub will record the source type, stable source ID when available, and source link. Before processing, intake will search existing meeting stubs and the processing state for the deduplication key.

Processing state will live in `_config/transcript-state.md` as an append-only table with the source ID, source link, meeting date, processed timestamp, resulting meeting stub, and status. A transcript receives `processed` status only after all intended automatic vault writes for that transcript succeed. Failed attempts are logged with a short error and fetched directly by their recorded source ID on the next run, so advancing the scan timestamp cannot hide them.

## Automatic writes

For each successfully read transcript, intake will automatically:

- Create or update the meeting stub under `meetings/`.
- Update relevant account and opportunity context in the vault.
- Create or update professional contact pages for people who spoke or were discussed with substance.
- Add only the user's own action items to the configured todo inbox.
- Update the vault index, timestamps, and change log according to the existing write protocol.

The raw transcript will never be copied into the vault. All derived claims will cite the source link and meeting date. Ambiguous speaker attribution, uncertain names, unclear negations, and other questionable transcript-derived claims will be marked `[unconfirmed]` instead of being silently normalized into facts.

Automatic writes must still follow read-before-write behavior so that shared-folder changes are not overwritten. Existing user-authored content is preserved. Conflicts are recorded as dated alternatives rather than resolved silently.

Retries will reconcile each destination using the transcript's stable source ID before adding content. Meeting sections, facts, contacts, and action items already written from that source will be updated or skipped rather than duplicated.

## Salesforce approval boundary

Meeting intake may read Salesforce to identify the account, opportunity, contacts, existing activities, and duplicate tasks. It will not perform any Salesforce write during scheduled processing.

For each run, intake will write a dated report such as `briefs/YYYY-MM-DD-HHMM-meeting-intake.md`. The report will contain:

- Transcripts processed, skipped, and failed.
- Vault files changed and action items created.
- Exact proposed Salesforce changes, including current and proposed values where applicable.
- The transcript evidence and source link supporting each proposal.
- Ambiguities that require the user's judgment.

Salesforce proposals remain pending until the user explicitly approves them in a later interactive session. Amount changes are never proposed from a transcript. Before applying an approved proposal, CRM Brain will re-read the Salesforce record and detect whether its current value has changed since the proposal was produced.

## Scheduled task instructions

The scheduled task created during setup will instruct Claude to:

1. Open the configured CRM Brain vault.
2. Invoke `meeting-intake` in scheduled mode.
3. Read `_config/transcripts.md` and `_config/transcript-state.md`.
4. Search only the configured transcript location.
5. Apply the automatic vault-write rules.
6. Produce the dated intake report containing all pending Salesforce proposals.
7. Never perform a Salesforce write.

If the installed Claude experience cannot express two daily run times in one schedule, setup will propose two daily scheduled tasks using the same instructions and different times.

## Documentation and packaging changes

User-facing documentation, plugin metadata, examples, setup instructions, and source labels will be changed from Fireflies-specific language to Google Drive or configurable transcript-source language. Fireflies will not be a requirement or plugin keyword.

The meeting template will use a generic transcript source URL. Todo source values will use the configured source name, such as `google-drive` or `granola`, rather than `fireflies`.

The packaged `dist/crm-brain.plugin` artifact will be rebuilt after the source files pass validation.

## Error handling

- Missing connector: stop before discovery and explain which configured capability is unavailable.
- Inaccessible folder or collection: stop without changing the scan checkpoint.
- Unreadable transcript: record it as failed in the run report and leave it eligible for retry.
- Unknown account: create the meeting stub with `[unconfirmed]` account linkage and report the ambiguity rather than guessing.
- Partial vault-write failure: do not mark the transcript processed; report the files already changed so the retry can reconcile them through read-before-write and deduplication.
- Salesforce unavailable: complete vault processing and record that CRM comparison and proposals could not be produced.
- No new transcripts: produce a short successful run result without creating an empty intake report.

## Verification

Implementation verification will include:

- Plugin manifest and skill validation through `scripts/build.sh`.
- Repository-wide checks that user-facing Fireflies dependencies, setup steps, keywords, examples, and fixed source labels have been removed.
- Scenario tests or documented fixtures covering first-time Google Drive setup, an unavailable connector, duplicate discovery, retry after a partial failure, an unknown account, and generation of Salesforce proposals without Salesforce writes.
- Inspection of the rebuilt plugin archive to confirm it contains the updated skills, templates, configuration assets, and license.

## Success criteria

A new user with a compatible MCP connector can run setup, point CRM Brain to one transcript location, and opt into twice-daily intake without editing a skill file. New transcripts update the vault and personal action list exactly once. Each run leaves reviewable Salesforce proposals with evidence, and Salesforce remains unchanged until the user explicitly approves those proposals.
