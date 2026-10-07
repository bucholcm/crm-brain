# crm-brain

**A deal memory next to your CRM.** Salesforce keeps the fields. CRM Brain keeps what was actually said.

A Claude plugin for people who sell with Salesforce and record calls with Fireflies. It keeps a plain markdown vault next to your CRM, fills it from meetings, and uses it to tell you what the CRM cannot: who really decides, what was promised on a call and never logged, which "empty" contact record is in fact the CFO.

Built on Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) idea. Generalised from a private setup I have run every working day since May 2026.

---

## What it does

| You say | What happens |
|---|---|
| "set up crm-brain" | Creates the vault, checks your connectors, and inspects your Salesforce org to learn where the money and the next steps really live. Read only. |
| "process my call with Acme" | Splits a transcript into four streams: a meeting stub, proposed updates to the account, proposed Salesforce follow ups, and your own action items. |
| "brief me on Acme, I meet them tomorrow" | A five minute brief that puts Salesforce, past transcripts and the vault side by side, and says where they disagree. |
| "review my pipeline" | An honest health check: no next step, no activity, stuck stages, empty values, and commitments made in meetings that never reached the CRM. |
| "I met Jane Doe from Acme" | Creates or updates her page and checks Salesforce both ways: missing title, duplicate records, owner who left. |
| "we submitted the proposal" | Updates the opportunity card with read before write, and proposes the matching CRM change. |
| "lint the vault" | Weekly drift audit: conflict copies, contradictions, cards out of sync with Salesforce, orphans, stale deals. |

Nothing is written to Salesforce without showing you the exact change and getting a "yes".

## What you learn that you did not know

All of these came up in my own data in the first weeks after connecting Salesforce.

- **The pipeline review was wrong, not the team.** A report read the standard Amount field. The org keeps deal value in a custom field. Everyone looked like they skipped amounts. Setup now checks which field your pipeline really uses before anything gets judged.
- **Next Step was empty on every deal** because the field was not on the page layout. The real next steps were open Tasks.
- **A contact with no title, no activity and an owner who had left the company** was the most senior decision maker on the account.
- **One of our own colleagues was filed as the client's champion.**
- **The CRM was right about job titles and wrong about time.** "Last activity" was empty, months behind, or set to a year that has not happened yet. The last real conversation lived in the transcripts.
- **"Too expensive" was the most common explanation in conversation and one of the smallest reasons by value in the closed lost data.**

## Install

You need Claude with a folder connected (the Claude desktop app in Cowork mode, or Claude Code), a Salesforce connector, and optionally a Fireflies connector.

**Cowork (Claude desktop app)**

1. Download `crm-brain.plugin` from the [latest release](https://github.com/bucholcm/crm-brain/releases/latest).
2. Drop it into a Cowork chat and press Install.
3. Connect Salesforce and Fireflies from the connector directory.
4. Connect a folder where the vault should live.
5. Say **"set up crm-brain"**.

**Claude Code**

```
/plugin marketplace add bucholcm/crm-brain
/plugin install crm-brain@crm-brain
```

Then connect your Salesforce and Fireflies MCP servers and say "set up crm-brain" inside the folder you want to use.

Setup ends with one real result, usually a brief for your next client meeting, not an empty folder.

## The vault

```
crm-brain-vault/
├── CLAUDE.md          the contract every skill reads first
├── index.md           one line per page
├── accounts/          one file per client
├── opportunities/     one card per deal
├── contacts/          people who came up in a conversation
├── meetings/          stubs with a link to the transcript, never the transcript
├── briefs/            generated briefs and reviews, dated
├── todos/inbox.md     your action items
├── _config/           what setup learned about your Salesforce org
├── _templates/        page structures
└── _log/              one change log per person per month
```

Plain markdown. Open it in Obsidian, VS Code or Finder. Put it on a shared drive or in a git repo for a team.

**The schema lives in the vault, not in the plugin.** Change a rule in `CLAUDE.md` or a section in `_templates/`, and every skill follows it on the next run. No plugin update, no reinstall for the rest of the team.

## The rules that matter

From five months of getting it wrong first:

1. **Do not mirror the CRM.** A contact page exists because someone came up in a conversation.
2. **Numbers belong to the CRM, context belongs to the vault.**
3. **A disagreement is a note, not an overwrite.** Write both versions, mark it unconfirmed.
4. **Every claim has a source.** No source, no claim.
5. **Transcripts are proposals, not facts.** Speech to text drops the word "not".
6. **One copy of every page.** Copies drift, and the stale one gets read.
7. **Read before you write.** Shared drives do not merge.
8. **Check the layout before you blame a person.**
9. **No raw material.** Conclusions and links, not pasted emails.
10. **People pages are professional only.** Would they read it without surprise?

The full contract is in [`CLAUDE.md`](plugins/crm-brain/skills/setup/assets/vault/CLAUDE.md).

## Privacy

The vault is yours: local files or a drive you control. The plugin ships no server and sends nothing anywhere beyond the connectors you have already authorised. Skills refuse to store secrets, raw emails or personal data outside professional context, and the weekly lint looks for them.

Treat a vault like your CRM: it holds commercial information about your clients. Do not commit a real vault to a public repository.

## Roadmap

- Pipeline snapshot over time (what moved this week, what did not)
- Gmail and Outlook intake alongside meetings
- Closed lost retrospective across all lost deals
- HubSpot and Dynamics mappings in setup

Issues and pull requests are welcome. If your org breaks setup in an interesting way, I want to hear about it.

## Credits

- Andrej Karpathy, [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (April 2026): the raw sources, compiled wiki, index and log pattern this is built on.
- Built with Claude.

## Licence

MIT. See [LICENSE](LICENSE).
