# Review rules and queries

Thresholds come from the Settings block of the vault `CLAUDE.md` (`no-activity-days`, `stuck-stage-days`). Defaults are shown in brackets. Compute "today" from the session date.

Replace `[value]` with the value field from `_config/salesforce.md` and `[scope]` with the scope filter from the same file. `[scope]` includes its leading `AND`, or is empty.

## Queries

Open deals in scope:

```sql
SELECT Id, Name, Account.Name, Owner.Name, Owner.IsActive, RecordType.Name, StageName,
  Probability, ForecastCategoryName, [value], CloseDate, CreatedDate, LastActivityDate,
  LastStageChangeDate, NextStep, Type, LeadSource
FROM Opportunity WHERE IsClosed = false [scope]
ORDER BY Id LIMIT 20 OFFSET [n]
```

Long text, fetched separately: `SELECT Id, Description FROM Opportunity WHERE Id IN (...)`. Add the org's qualification fields if the config lists any.

Open Tasks:

```sql
SELECT WhatId, Subject, ActivityDate, Owner.Name FROM Task
WHERE WhatId IN (...) AND IsClosed = false
```

Future Events:

```sql
SELECT WhatId, Subject, StartDateTime FROM Event
WHERE WhatId IN (...) AND StartDateTime >= TODAY
```

History (top 10 only in set mode):

```sql
SELECT OpportunityId, Field, OldValue, NewValue, CreatedDate FROM OpportunityFieldHistory
WHERE OpportunityId IN (...) AND Field IN ('StageName', 'CloseDate')
ORDER BY CreatedDate DESC
```

`OpportunityFieldHistory` exists only when field history tracking is on. If it returns nothing, fall back to `OpportunityHistory`, which always records stage and close date changes:

```sql
SELECT OpportunityId, StageName, CloseDate, CreatedDate FROM OpportunityHistory
WHERE OpportunityId IN (...) ORDER BY CreatedDate DESC
```

A custom value field is often not tracked; do not report "value never changed" from an untracked field.

Single deal, recent activity: the last five Tasks (`Subject`, `TaskSubtype`, `ActivityDate`) and Events (`Subject`, `EventSubtype`, `StartDateTime`) to describe what happened.

## 🔴 Critical

1. **No next step**: nothing in the configured next step location, no future Event, no vault `next-step`.
2. **Next step overdue**: open Tasks exist but all are dated before today, and there is no future Event. Rules 1 and 2 exclude each other. One dated Task from today onward or one future Event clears both.
3. **Close date in the past** on an open deal.
4. **No activity**: `LastActivityDate` empty or older than `no-activity-days` [30]. If the config says activity is logged by hand, downgrade to 🟡 and say why.
5. **No value**: value field empty, 0 or 1. Exception: record types whose layout has no value field (staff augmentation often); then 🟡 and check whether the assumptions are in Description.
6. **Zombie stage**: the deal's stage is inactive in the picklist or missing from the config's "Stages in use" table.

## 🟡 Important

7. **Qualification fields empty** from the middle stages onward, using the "Qualification fields" column of the config's Layouts table. No such fields listed: skip the rule. Before that stage, empty is normal.
8. **Stage stuck**: `LastStageChangeDate` older than `stuck-stage-days` [45]. Empty `LastStageChangeDate` means the stage never moved since creation, so count from `CreatedDate`. Parking stages (for example "Pending" or "On hold") get a longer threshold of 180 days.
9. **Close date pushed two or more times** (from history).
10. **Empty Description.**
11. **Probability far from the stage default** (more than 20 points): not an error, ask for the reason.
12. **Fields required in the UI but empty**: the API does not enforce layout requirements, so deals created by integrations or imports can have them empty. Only fields in the "Required in the UI" column of the config's Layouts table for that record type.
13. **Owner inactive**: the deal is owned by a user who has left.
14. **Said but not logged**: see the skill body.

## ⚪ Cosmetic (single deal only)

15. Empty fields from the "Housekeeping fields" column of the config's Layouts table (lead source, document folder link and similar).

## Patterns worth naming

- More than half the deals without a next step: a process problem, not a people problem. Say that.
- Many deals with an empty value field and a well filled other currency field: the mapping in the config is probably wrong. Stop and ask before reporting.
- One owner with most of the 🔴: report the numbers, no adjectives.
