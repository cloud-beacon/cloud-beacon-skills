---
name: xpp-code-review
description: Cloud Beacon's D365 Finance & Operations X++ code review framework — 19 categories of concrete, severity-rated checks (naming, performance, transactions, error handling, security, Chain of Command, labels, data entities/DMF, and more). Use this whenever reviewing, critiquing, or sanity-checking X++ or D365 F&O objects (classes, tables, forms, data entities, EDTs, enums, extension/augmentation classes), reviewing a TFVC shelveset or changeset or pull request, or even while writing or editing X++ and wanting it to conform to review standards — even if the user doesn't say the word "review". Trigger on D365 F&O, Dynamics 365 F&O, X++, AX, FinOps code quality, or "does this look right" questions about D365 objects.
---

# X++ Code Review Framework — D365 F&O

Apply this checklist when reviewing X++. Each category states what triggers a finding and at
what severity. Categories 1–14 are Cloud Beacon's standards plus Microsoft D365 FO guidance;
15–19 cover extension-based, integration-heavy delivery. Be specific and kind: cite evidence
as `path :: method/area`, prefer "consider X because Y" over bare verdicts, and separate
objective violations from taste.

## How to apply

1. Identify each changed artifact's type (Class, Table, Form, DataEntity, Query, EDT/Enum,
   Extension). Use the **artifact applicability matrix** to know which categories apply.
2. Walk the applicable categories; raise a finding only when the code in front of you
   supports it. If you can't verify something from the diff/code, mark it **Needs manual
   check** rather than asserting it.
3. Assign each finding a severity (below) and group findings by severity.
4. Give a verdict: any **Error** → *Blocked / Changes requested*; only Warning/Info →
   *Approve with nits*; clean → *Approve*.

## Context: pipeline vs standalone

- **In the `/cr-review` pipeline**, a client profile is in context. Read per-client values
  from it: `naming.object_prefix`, `naming.label_prefix`, `naming.model`,
  `naming.extension_suffix`, `naming.view_extension_suffix`, `naming.project_pattern`,
  `checkin_comment_pattern`, and `form_templates`.
- **Standalone** (someone pastes X++ and asks for a review with no profile), infer the
  prefix/casing convention from the surrounding code, or ask once if it's ambiguous. Skip
  Category 9 (no shelveset comment) unless a check-in comment is provided.

## Severity model

| Severity | Meaning |
|----------|---------|
| **Error** | Must fix — blocks check-in. Perf bugs, missing error handling, security, dropped base behavior. |
| **Warning** | Should fix — naming, missing comments on public API, deprecated patterns. |
| **Info** | Recommendation — organization, alternative patterns. |

---

## 0. Spec conformance (highest priority when a spec/work item exists)

Every functional requirement has corresponding code or is explicitly out of scope (**Error**
if a required behavior is missing). Behavior matches the spec's edge cases and error
handling, not just the happy path (**Error** for missed edge cases). No undocumented scope
creep (**Warning**). Data-model changes match the spec's data design (**Error** on mismatch).

## 1. Consistency (naming + formatting)

Custom *types* carry the client prefix; members are camelCase.

| Identifier | Expected | Severity |
|------------|----------|----------|
| Class / Table / EDT / Enum / View | `{object_prefix}` + PascalCase | Warning (Error if prefix missing on a public-facing object) |
| Extension/augmentation class | base name + `{extension_suffix}` | Warning |
| Data-entity view extension file | base + `{view_extension_suffix}` (e.g. `…Entity.Buddig.xml`) | Warning |
| Method / Variable / Field | camelCase | Warning |
| Object model placement | `{model}` | Warning if misplaced |

Formatting: tab indentation, Allman braces, consistent operator spacing → **Info**.

## 2. Code readability

Flag classes/public methods lacking a description comment (**Warning** on public API),
magic numbers/hardcoded strings without context (**Info**; user-facing strings → Category
16), methods over ~50 lines (**Info**), nesting 3+ levels deep (**Info**).

## 3. Performance optimization

Missing `firstonly` on single-record queries → **Warning**. Nested `while select` (N+1) →
use a join, **Error**. Row-by-row DML in a loop → set-based (`update_recordset`,
`delete_from`, `insert_recordset`): **Error** for large/unbounded loops, **Warning** for
small bounded ones (but see Category 17). `display` methods over large datasets → compute in
the query, **Warning**.

## 4. Resource management

Every `ttsBegin`/`ttsCommit` must sit inside try-catch with specific handlers
(`UpdateConflict`, `DuplicateKeyException`, `Error`) — bare transaction block → **Error**.
Unused declared variables → **Warning**. Prefer local over class-level variables; `using`
blocks for disposables → **Info**.

## 5. Efficient data handling

Large intermediate sets should use temp tables (`Tmp*`) → **Warning**. Use field lists, not
whole-buffer selects → **Warning**. Row-based where set-based fits → cross-ref Category 3.

## 6. Error handling & validation

Catch specific exception types (no empty/bare catches); use `infolog.setPrefix()` for
context — empty catch → **Error**. Validate non-empty strings, numeric ranges, division-by-
zero, record existence before use — missing a guard that can fault → **Error**; missing
parameter validation → **Warning**.

## 7. Modularity & reusability

Duplicated logic (DRY) → **Warning**. God classes → **Info**. Extractable validation/error
patterns → **Info**.

## 8. Security — data protection

Sensitive data (passwords, keys, PII) in plain text → **Error**. Use
`Cryptography::encrypt()`/`decrypt()`; missing encryption on sensitive fields → **Warning**.
(AOT security objects are Category 18.)

## 9. Version control — check-in comment

Validate the shelveset's check-in comment (from the review-input header) against
`checkin_comment_pattern` (default `{TaskID} - {TaskName} - {Description} - {DevInitials}`).
Blank → **Error**. Object-name-only (e.g. `TPMSalesOrders_SFID_Update_Job`) or otherwise
non-conforming → **Warning**.

## 10. Query objects over direct SQL

Prefer `Query`/`QueryBuildDataSource`/`QueryRun` for complex, dynamic, or reusable queries;
simple `select firstonly` and static joins are fine as direct SQL. Recommendation → **Info**.

## 11. Form design templates

Forms should use a standard template. Check `form_templates` if the profile sets it,
otherwise the standard set: `DetailsFormMaster`, `DetailsFormTransaction`,
`SimpleListDetails`, `SimpleList`, `ListPage`, `TableOfContents`, `Dialog`, `DropDialog`,
`Lookup`, `FactBox`. No template → **Warning**; non-standard template → **Info**.

## 12. Table best practices *(Table artifacts only)*

| Check | Expected | Severity |
|-------|----------|----------|
| Primary key | `key DataAreaId; key RecId;` or equivalent | Error |
| CacheLookup | set appropriately | Warning |
| ClusterIndex | points to primary index | Warning |
| Label | label id (not literal — Category 16) | Warning |
| Field names | camelCase | Warning |
| Fields use EDTs | not primitives | Warning |
| Field groups | related fields grouped | Info |
| FK relations | defined for referenced tables | Warning |
| Index width | no oversized string fields indexed | Warning |
| validateWrite/validateDelete | rules enforced | Info |
| Purpose documented | table comment | Info |

## 13. SysOperation over RunBaseBatch

Batch classes extending `RunBaseBatch`/`RunBase` → recommend SysOperation (controller /
service / data contract). **Warning**.

## 14. Data entities for inserts

Direct table inserts where an entity would enforce validation/security → recommend the
entity. **Warning** (direct inserts can be justified for performance-critical batch — accept
with a rationale).

## 15. Extension & Chain of Command

The codebase is extension-based; review the mechanics:
- Augmentation classes are `final` with `[ExtensionOf(...)]`; CoC methods call `next` exactly
  once on the right path. Omitting `next` silently drops base behavior → **Error**.
- Use CoC or event handlers, never overlayering. Any over-layered change → **Error**.
- Wrapped methods must be hookable (`public`/`protected`, base wrappable); wrapping something
  that won't reliably hook → **Warning**.
- Event-handler subscriptions match the delegate signature and target stable events →
  **Warning**.
- Don't re-implement base behavior you could call → **Info**.

## 16. Labels over hardcoded strings

User-facing text (captions, error/info messages, table/field labels) uses label ids from the
client label file (`@{label_prefix}…`), not literals. Literal where a label is required →
**Warning**. New label ids follow `{label_prefix}` and live in the client label file →
**Warning** if misplaced.

## 17. Set-based operation caveat

Set-based DML **bypasses** `insert()`/`update()`/`validateWrite()` overrides and CoC unless
`skipDataMethods`/`skipDatabaseLog` etc. are handled deliberately.
- Set-based DML on a table whose `insert`/`update` carries required business logic, without
  acknowledging the bypass → **Error**.
- Row-by-row used *because* table-method logic must fire is acceptable — don't flag it as a
  perf issue; note the trade-off. (Prevents a false Category-3 Error.)

## 18. AOT security objects

Beyond encryption (Category 8): new tables/forms/menu items/entities need privileges/duties
and menu-item permissions — a new entry point with no security artifact → **Warning**
(**Error** if it exposes financial or PII data). Entities set an appropriate `securityKey` /
`public` scope; missing or overly broad → **Warning**. Field-level security intact on
sensitive fields → **Warning** if dropped.

## 19. Data entity & DMF specifics

For entity work (the common case): `postLoad`/`mapEntityToDataSource`/
`mapDataSourceToEntity` overrides are null-safe and don't assume a record exists — unsafe
deref → **Error**. Computed columns use `SysComputedColumn` correctly; no per-row
computation that belongs in the view → **Warning**. Cross-company entities handle
`changeCompany`/`DataAreaId` explicitly where required → **Warning**. Staging-table
transforms run set-based/batched, not row-by-row in `DMFEntityWriter` hooks → **Warning**.

---

## Artifact applicability matrix

| Category | Class | Table | Form | DataEntity | Query | EDT/Enum |
|----------|:----:|:----:|:----:|:----------:|:----:|:--------:|
| 0 Spec conformance | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 Consistency | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 Readability | ✓ | ✓ | – | ✓ | – | – |
| 3 Performance | ✓ | ✓ | – | ✓ | – | – |
| 4 Resource mgmt | ✓ | ✓ | – | – | – | – |
| 5 Data handling | ✓ | – | – | ✓ | ✓ | – |
| 6 Error handling | ✓ | ✓ | – | ✓ | – | – |
| 7 Modularity | ✓ | – | – | – | – | – |
| 8 Security (data) | ✓ | ✓ | – | ✓ | – | – |
| 9 Version control | once per review (check-in comment) ||||||
| 10 Query objects | ✓ | – | – | – | – | – |
| 11 Form templates | – | – | ✓ | – | – | – |
| 12 Table practices | – | ✓ | – | – | – | – |
| 13 SysOperation | ✓ | – | – | – | – | – |
| 14 Data entities | ✓ | – | – | – | – | – |
| 15 Extension/CoC | ✓ | ✓ | ✓ | ✓ | – | – |
| 16 Labels | ✓ | ✓ | ✓ | ✓ | – | ✓ |
| 17 Set-based caveat | ✓ | ✓ | – | ✓ | – | – |
| 18 AOT security | ✓ | ✓ | ✓ | ✓ | – | – |
| 19 Entity/DMF | – | – | – | ✓ | – | – |

## Report shape (when producing a full review)

Verdict (Approve / Approve with nits / Changes requested / Blocked) + 2–3 sentence summary →
Spec conformance traceability (one row per requirement: Met / Partial / Missing / Deviates)
→ Findings grouped Error / Warning / Info (each: `file::area` — what's wrong — why — fix) →
What looks good → Open questions for the author. For a quick standalone review, the findings
+ verdict are enough.
