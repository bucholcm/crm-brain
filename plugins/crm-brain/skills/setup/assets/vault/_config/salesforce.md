---
owner: [your-slug]
last-updated: YYYY-MM-DD
verified-against-org: YYYY-MM-DD
---

# Salesforce: what this org really looks like

**Summary**: Conventions that cannot be read from metadata alone. Which field holds the money, where next steps really live, which stages are in use. Written by `crm-brain:setup`, corrected by you. Every Salesforce skill reads this before judging anything.

**Sources**: Queries run by setup on the date above, plus your answers.

---

## Connector

- API path for SOQL: `/services/data/[version]/query`
- Known quirks: [e.g. "query string is cut at `&`, use `LIKE` with `_` for picklist values containing `&`"]
- Response size limit: [e.g. "about 25k tokens, page with LIMIT/OFFSET"]

## Me and my scope

- My user: [Name] · `[User Id]`
- My direct reports in Salesforce (Manager field, one level): [names]
- Default scope for reviews: [e.g. "my opportunities and my direct reports'", or a filter such as `Region__c = 'EMEA'`]
- Scope filter in SOQL, including the leading AND: `[e.g. AND (OwnerId = '...' OR Owner.ManagerId = '...'), or empty for the whole org]`

## Field mapping

| Concept | Field in this org | Fill rate on open opps | Note |
|---|---|---|---|
| Deal value | `[Amount or a custom field]` | [x%] | The number your pipeline report shows. |
| Currency | `[CurrencyIsoCode or custom]` | | |
| Next step | `[NextStep or "open Task with a date"]` | [x%] | If NextStep is below 20% filled, it is probably not on the layout. Use open Tasks and future Events instead. |
| Lost reason | `[field, or "encoded in stage name"]` | | |
| Description | `Description` | [x%] | |

Fields that look trustworthy but are not: [e.g. "`Account.Industry` is unreliable, do not segment on it"]

## Stages in use

| Slug (vault) | Salesforce value | Default probability | Open / closed |
|---|---|---|---|
| | | | |

Stages present in the picklist but unused in the last 24 months: [list].

Zombies (open deals in an inactive stage or a stage missing from this table): [n] on YYYY-MM-DD.

## Closed reasons

| Slug | Salesforce value | Used in last 24 months |
|---|---|---|
| | | |

## Record types in use

| Record type | Id | Open opps | Note |
|---|---|---|---|
| | | | |

## Layouts

Per record type. Skills judge only fields listed here.

| Record type | On the layout | Required in the UI | Qualification fields | Housekeeping fields |
|---|---|---|---|---|
| | | | | |

## Activity logging

- Emails logged automatically: [yes / no]
- Calls logged automatically: [yes / no]
- Meaning: [e.g. "no Tasks on a deal really means nobody wrote or called from Salesforce" or "activity is logged by hand, so absence proves little"]

## Contact hygiene snapshot (accounts with open deals)

- Contacts: [n]
- Without a title: [n]
- Owned by inactive users: [n]
- Colleagues filed on client accounts: [n]
- Last snapshot: YYYY-MM-DD

These are not errors to hide. They are where the unknown decision makers are.

## Changes

What a re-run of setup changed, newest first. Manual corrections you make above are kept on re-runs.

- YYYY-MM-DD · first setup
