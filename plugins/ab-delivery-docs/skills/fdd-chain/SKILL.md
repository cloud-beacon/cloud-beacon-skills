---
name: fdd-chain
description: Generate an Alta Beacon Functional Design Document (FDD) from a discovery transcript, requirements outline, or notes. Use whenever the user asks to draft / write / create / structure / outline an FDD, functional design document, functional design doc, or "FDD from this transcript / meeting / discovery." Chains cb-voice for narrative tone and emits the full Alta Beacon FDD template populated from the source material.
type: chain
fires:
  - cb-voice
---

# Alta Beacon FDD Chain

You are producing a Functional Design Document (FDD) in Alta Beacon's standard format. An FDD is an **external-facing consulting deliverable** — it captures the business problem, the assumed system behavior, the customizations required, and how they'll be tested and secured. Treat it like a contract artifact, not an engineering scratchpad.

## How this chain runs

1. **`cb-voice`** — apply Alta Beacon's customer-facing voice across every section. FDDs are read by client SMEs, project leads, and developers; the prose has to land for all three.
2. **FDD template (this skill)** — assemble the body into the canonical 10-section structure below.

If the user has not installed `cb-voice` locally, fall back to a neutral consulting register: precise, second-person rare, no marketing flourish.

## Gather inputs

Before generating, confirm you have:

1. **Client name** (e.g., Liquid I.V.)
2. **Project name** (e.g., D365 Order to Cash Implementation)
3. **FDD number** (e.g., 27) — ask if not supplied
4. **FDD title** — short noun phrase describing the change (e.g., "Re-Baseline of Invoice Due Date upon Delivery Confirmation")
5. **Source material** — a discovery transcript, meeting notes, requirements outline, or email thread
6. **Author + effective date** (optional — surface in cover block if supplied)
7. **Focus areas / known constraints** (optional)

If the source material is silent on something material, write `[CONFIRM WITH CLIENT]` inline rather than inventing the answer.

## Output structure

Emit markdown only. Use H2 (`##`) for top-level sections, H3 (`###`) for subsections, H4 (`####`) for FR entries.

The cover page, Document Information block, Version History table, and Table of Contents are populated by the portal (or by Word) from inputs — **do not emit them**. Start your output at Section 1.

```markdown
## 1. Introduction

### 1.1 Purpose of the Document
(one short paragraph — the role of this FDD inside the project)

### 1.2 Purpose and Intended Audience of this Solution
Audience: …
Purpose of this solution: …

### 1.3 Business Requirements
(numbered BR01, BR02, … or write "No business requirements apply for this FDD." if nothing material surfaces)

### 1.4 Business and System Assumptions
(numbered BSA01, BSA02, … each with a short bolded title and a one-sentence explanation)

## 2. Data Migration
("Not applicable in this FDD." unless the source clearly demands a migration step.)

## 3. Design

### 3.1 Functional Requirements
(one-paragraph overview of how the customizations fit together end-to-end.)

#### FR01 – Business Process Flow
(walk through the end-to-end flow as numbered or bulleted steps; reference EDIs, integrations, manual actions explicitly.)

### 3.2 Customization

#### FR02 – <descriptive title>
(rules and behavior; reference D365 forms, fields, menu items by exact path when known; flag screenshot insertion points with the literal token `[SCREENSHOT]`.)

#### FR03 – <descriptive title>
… continue sequentially (FR04, FR05, …) for every distinct customization the source material surfaces.

### 3.3 Menu Items

| # | MenuItem Type | Object | Description |
|---|---------------|--------|-------------|
(one row per new menu item)

### 3.4 Configuration
(reference the Functional Set Up Document or list specific parameter values.)

### 3.5 Data Requirements
(any master/reference data that must exist for the customization to work.)

## 4. Test Scenarios Proposed
(numbered scenarios — at least one per FR plus any cross-cutting end-to-end scenarios.)

## 5. Permissions for Test Scenarios
(security privileges/roles required per FR. **Pair every new menu item and data entity from Section 3.3 with a named privilege here — this is a hard Alta Beacon rule.**)

## 6. Dev Feedback
_Pending dev review._
```

## Hard rules

- **Security pairing.** Every menu item or data entity introduced in Section 3.3 must have a corresponding security privilege named in Section 5. If you can't find or invent the privilege, write `[PRIVILEGE TBD]` and call it out explicitly — never silently omit.
- **No invented requirements.** If the source doesn't say it, write `[CONFIRM WITH CLIENT]`. FDDs that fabricate scope cause downstream rework.
- **Stay in reference register.** Use "the user", "the customer", "the system" — not "you". FDDs read like specs, not tutorials.
- **Field paths are concrete.** When the source supplies a D365 path (e.g., "Accounts receivable > All customers > Payment defaults tab"), quote it verbatim. Don't paraphrase.
- **BSA and BR entries are short.** One bolded title + one sentence each. If you need more, that's an FR, not an assumption.

## Style cues

- Use sentence case for headings except the section numbers (`1. Introduction`, `2. Data Migration`).
- Bold the leading clause of BR / BSA entries: `**BSA01 – Shipments:** An SO line can only have one shipment.`
- Tables get full sentences in cells, not fragments.
- FR sections often need 2–4 short paragraphs plus a bulleted rule list. Don't pad.
- Close ambiguity with `[CONFIRM WITH CLIENT]` — never with a hedge ("may", "could possibly", "is sometimes").
