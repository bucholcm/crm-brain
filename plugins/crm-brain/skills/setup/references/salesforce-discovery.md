# Salesforce discovery: read-only fingerprint

Run these in order. All are SELECTs. Replace `[version]` with the API version the connector uses. `[scope]` stands for the scope filter **including its leading `AND`**, for example `AND (OwnerId = '005...' OR Owner.ManagerId = '005...')`, or nothing at all when the scope is the whole org. If a query fails, note the error in `_config/salesforce.md` and continue; a partial fingerprint is still useful.

Keep responses small. Use `COUNT()` and `GROUP BY` where possible. If the connector has a response size limit, page with `LIMIT` and `OFFSET`.

## 1. Who is asking

Ask the user for their name as it appears in Salesforce.

```sql
SELECT Id, Name, Title, ManagerId, Profile.Name FROM User
WHERE IsActive = true AND Name LIKE '[First Last]%'
```

Direct reports, one level:

```sql
SELECT Id, Name, Title FROM User WHERE IsActive = true AND ManagerId = '[my Id]'
```

`Manager` gives the direct manager, not the whole line. If someone the user expects is missing, the Manager field on that user is wrong. Say so; do not patch around it with a hand-made list.

## 2. Scope

Ask how the user thinks about "my pipeline": their own deals, their team's, a business unit, a region. If a picklist value is involved, check the exact value:

```sql
SELECT [Field__c], COUNT(Id) FROM Opportunity WHERE IsClosed = false GROUP BY [Field__c]
```

Connector quirk worth testing early: some connectors cut the query string at `&`. If a picklist value contains `&`, use `LIKE` with `_` in that position (`LIKE 'Food _ Beverage'`), which matches exactly one character. Record the quirk.

Team scope filter that works on most orgs:

```sql
AND (OwnerId = '[my Id]' OR Owner.ManagerId = '[my Id]')
```

## 3. Where the money is

```sql
SELECT COUNT() FROM Opportunity WHERE IsClosed = false [scope]
SELECT COUNT() FROM Opportunity WHERE IsClosed = false AND Amount > 1 [scope]
```

Then list currency fields on Opportunity. Prefer the UI API over a full describe (a full describe can be hundreds of thousands of characters):

```
GET /services/data/[version]/ui-api/object-info/Opportunity
```

Pick fields with `dataType` Currency, plus Double fields whose label contains Amount, Value or Revenue. For each candidate, count fill on open deals:

```sql
SELECT COUNT() FROM Opportunity WHERE IsClosed = false AND [Candidate__c] > 1 [scope]
```

Values of 0 or 1 are usually placeholders. Report the fill rates and **ask the user which number their pipeline report shows**. That answer wins over fill rates.

## 4. Where the next step is

```sql
SELECT COUNT() FROM Opportunity WHERE IsClosed = false AND NextStep != null [scope]
```

Then measure how many open deals have a dated next action. Task and Event cannot be used in a subquery, so do it in two steps: fetch the Ids of open deals in scope, then

```sql
SELECT WhatId, COUNT(Id) FROM Task
WHERE WhatId IN ([open deal Ids]) AND IsClosed = false AND ActivityDate >= TODAY GROUP BY WhatId

SELECT WhatId, COUNT(Id) FROM Event
WHERE WhatId IN ([open deal Ids]) AND StartDateTime >= TODAY GROUP BY WhatId
```

The share of open deals that appear in either result is the real next step coverage.

If `NextStep` is under 20% filled, it is probably not on the page layout. Record "next step = open Task with a date or a future Event" and tell the user. Never report an empty field nobody can see as a person's failure.

## 5. Stages and closed reasons

```sql
SELECT MasterLabel, ApiName, SortOrder, DefaultProbability, IsClosed, IsWon, IsActive, ForecastCategoryName
FROM OpportunityStage ORDER BY SortOrder
```

```sql
SELECT StageName, COUNT(Id) FROM Opportunity
WHERE CreatedDate = LAST_N_DAYS:730 [scope] GROUP BY StageName
```

Build the stage table with vault slugs (lowercase, hyphens). Open stages with zero use in two years go to the "unused" list. A **zombie** is an open deal whose stage is inactive in the picklist or missing from the "Stages in use" table. Count them and write the count in the config.

Lost reasons: look for a field with Loss or Reason in its name. Many orgs encode the reason in the stage name instead (`Closed Lost - Price`). Either way, record the mapping. If a single "Other" reason holds a large share of lost value, mention it: that is lost learning.

## 6. Record types and layouts

```sql
SELECT RecordType.Name, RecordTypeId, COUNT(Id) FROM Opportunity
WHERE IsClosed = false [scope] GROUP BY RecordType.Name, RecordTypeId
```

For each record type with open deals, read the layout through the UI API (much smaller than a describe):

```
GET /services/data/[version]/ui-api/layout/Opportunity?recordTypeId=[Id]&mode=Edit
```

Record in the config, per record type: which fields are on the layout, which are required in the UI, and which look like qualification fields (labels such as Compelling Event, Business Problem, Decision Criteria, Budget). The API does not enforce UI requirements, so deals created by integrations or imports can miss them.

A field that is not on a record type's layout is never a gap on that record type.

## 7. Activity logging

```sql
SELECT TaskSubtype, COUNT(Id) FROM Task WHERE CreatedDate = LAST_N_DAYS:90 GROUP BY TaskSubtype
```

Many Email subtype Tasks suggest automatic email logging. Few or none suggest manual logging, or a capture tool that stores emails outside Tasks (Einstein Activity Capture does this). Ask the user which it is. Record the conclusion, not just the counts: it decides whether "no activity" means nobody talked.

## 8. Contact hygiene on live accounts

```sql
SELECT COUNT() FROM Contact
WHERE AccountId IN (SELECT AccountId FROM Opportunity WHERE IsClosed = false [scope])

SELECT COUNT() FROM Contact
WHERE AccountId IN (SELECT AccountId FROM Opportunity WHERE IsClosed = false [scope]) AND Title = null

SELECT COUNT() FROM Contact
WHERE AccountId IN (SELECT AccountId FROM Opportunity WHERE IsClosed = false [scope]) AND Owner.IsActive = false
```

Also check for your own colleagues filed as client contacts:

```sql
SELECT Account.Name, COUNT(Id) FROM Contact
WHERE Email LIKE '%@[company-email-domain]' GROUP BY Account.Name
```

Contacts on your own company's internal Account are normal. The ones on client accounts are the finding.

Report the numbers without blame. These records are where unknown decision makers hide: a contact with no title, no activity and an owner who left can turn out to be the most senior person on the account.

## 9. Fields that lie

Ask the user one question: "Is there a field everyone assumes is right but is not?" Common answers: Industry, Account Owner after a reorganisation, Last Activity. Write them under "Fields that look trustworthy but are not".

## Writing the file

Fill `_config/salesforce.md` from the vault template. Put the date in `verified-against-org`. Keep numbers as found; do not round away the uncomfortable ones.
