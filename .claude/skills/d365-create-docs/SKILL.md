---
name: d365-create-docs
description: Generate Cloud Beacon's standardized D365 F&O module documentation set — Architecture (developer-focused), User Guide (end-user), and Functional Guide (consultant/analyst) — following the PLM/SOV patterns. Use whenever the user asks to create, write, or generate documentation for a D365 module, write the architecture/user/functional guides, or document a feature area for a customer deliverable.
---

# D365 F&O: Create Module Documentation

<command-name>d365-create-docs</command-name>

<description>
Generate standardized documentation for a CloudBeacon D365 F&O module. Creates three coordinated guides following the established PLM/SOV documentation patterns: Architecture (for developers), User Guide (for end users), and Functional Guide (for consultants/analysts).
</description>

## Instructions

When invoked with a module name or topic, create comprehensive documentation in the `.reference/` folder following this process:

### Step 1: Gather Module Information

Before writing, explore the codebase to understand:

1. **Core classes**: Service classes, controllers, feature management class
2. **Tables**: Main tables, parameters tables, extension tables
3. **Enums**: Status enums, type enums, configuration enums
4. **Forms**: Main forms, list pages, setup forms
5. **Menu structure**: Where does this fit in the CloudBeacon menu?
6. **Security**: Privileges, duties, roles
7. **Batch jobs**: Controllers, services, queries
8. **Integration points**: Extensions to standard D365 tables/forms

Use Grep and Glob to find all related artifacts with the module prefix (e.g., `cbSOV*`, `cbPLM*`).

### Step 2: Create Documentation Folder

Create folder at: `.reference/<ModuleName>/`

Example: `.reference/OrderValidation/`, `.reference/PLM/`, `.reference/Pricing/`

### Step 3: Create Architecture Document

**File**: `<prefix>-architecture.md`

**Target audience**: Internal developers, solution architects

**Required sections**:

```markdown
# Cloud Beacon <Module Name> — Architecture Document

**Audience**: Internal Developers, Solution Architects
**Version**: 1.0
**Last Updated**: <YYYY-MM-DD>

## Overview
Brief description of the module's purpose and key capabilities (bullet list).

## Data Flow
ASCII diagram showing the processing pipeline:
- Entry points (services, entities, forms)
- Processing stages
- Target outputs
- Error handling paths

## Service Classes
Table of main classes with purpose:
| Class | Purpose |
|-------|---------|
| <ServiceName> | <Description> |

### <MainServiceName>
Detailed breakdown of key methods.

## Tables
Tables organized by category:
- Main data tables
- Parameters/configuration tables
- Extension tables (to standard D365 tables)

Include field descriptions for key tables.

## Enums
List enums with values and descriptions.

## Query
Document any batch job queries with joins and filters.

## Feature Management
Feature class name, label, module, default state, lifecycle hooks.

## Menu Structure
ASCII tree showing navigation path.

## Batch Processing
Controller, service, scheduling recommendations.

## Error Handling
Error logging approach, retry logic, categorization.

## Security Model
Privileges, duties, roles with descriptions.

## Key Design Decisions
Numbered list of architectural choices and rationale.

## Future Enhancements (if applicable)
Known pending work or enhancement areas.

## Related Reference Documents
Links to other relevant docs.
```

### Step 4: Create User Guide

**File**: `<prefix>-user-guide.md`

**Target audience**: End users and administrators

**Required sections**:

```markdown
# Cloud Beacon <Module Name> — User Guide

**Audience**: End users and administrators
**Version**: 1.0
**Last Updated**: <YYYY-MM-DD>

## Getting Started

### What Does This Module Do?
Non-technical explanation of value proposition (3-4 bullet points).

### Prerequisites
Security roles needed, feature enablement, license requirements.

### Enabling the Feature
Step-by-step for Feature Management.

## How <Module> Works
Explain the core workflow in user-friendly terms.

### <Key Concept 1>
Explain status values, states, or categorizations the user will see.

### What Gets <Processed/Validated/Created>
List of what the module does, organized logically.

### When <Processing> Runs
Explain triggers (batch job, manual action, automatic).

## <Reviewing/Viewing> Results

### <Main Form>
How to navigate, key columns, filters.

### <Supporting Forms>
Additional views and their purposes.

## <Resolving Issues / Taking Action>

### Step 1: <First Step>
### Step 2: <Second Step>
### Step 3: <Third Step>

Tables showing common issues and resolutions.

## <Optional: Bypasses/Exceptions>
If the module has override capabilities, explain them.

## Setup

### <Parameters Form>
Explain configuration options in user-friendly terms.

### <Supporting Setup>
Additional configuration options.

## Scheduling the Batch Job
Step-by-step for batch job setup with recommended frequency.

## Common Questions
FAQ format addressing typical user questions.

## Troubleshooting
| Symptom | Likely Cause | Resolution |
Table format for common issues.

## Tips
Bullet list of best practices for users.
```

### Step 5: Create Functional Guide

**File**: `<prefix>-functional-guide.md`

**Target audience**: Implementation consultants, business analysts, IT administrators

**Required sections**:

```markdown
# Cloud Beacon <Module Name> — Functional Guide

**Audience**: Implementation consultants, business analysts, and IT administrators
**Version**: 1.0
**Last Updated**: <YYYY-MM-DD>

## Introduction

### What Is Cloud Beacon <Module Name>?
One paragraph positioning statement.

### Key Capabilities
Bullet list of functional capabilities.

## Module Overview

### The Problem
Describe the business problem this solves.

### The Solution
High-level explanation of how the module solves it.

## <Core Functionality Section>
Detailed breakdown of features with configuration tables:

| Check/Feature | Configuration Field | Description |
|---------------|--------------------| ------------|

## Configuration

### <Primary Parameters>
Detailed field-by-field explanation.

### <Secondary Configuration>
Additional setup options.

### <Customer/Item-Level Overrides>
If applicable, explain override patterns.

## Processing Flow

### <Batch Job Name>
Menu path, query description, execution flow.

### <Per-Record Processing>
Step-by-step of what happens to each record.

### <Completion/Output>
What happens after processing.

## <Categories/Types/Classifications>
If the module has classification system, explain each category.

## <Resolution/Action Workflow>
Standard workflow for handling module outputs.

### Standard Resolution
1. Step...
2. Step...

### Exception Handling
How to handle edge cases.

### Bulk Operations
If applicable, explain batch actions.

## Security Model

### Privileges
| Privilege | Description |
Table of all privileges.

## Integration with D365 Standard
How module integrates with standard D365 functionality.

## Monitoring

### Key Indicators
| Metric | Where to Check | Healthy State |
Table of KPIs.

### Recommended Reporting
Suggestions for dashboards/alerts.

## Troubleshooting
| Symptom | Likely Cause | Resolution |
Comprehensive troubleshooting table.

## Best Practices

### Configuration
Best practices for setup.

### Operations
Best practices for daily use.

### Error Handling
Best practices for issue resolution.

## Feature Management
Feature class details.

## Version History
| Date | Change |
Change log.
```

### Step 6: Update README (if exists)

If `.reference/README.md` exists, add entry for the new documentation folder.

---

## Usage Examples

```
User: /d365-create-docs for the Order Validation module
User: /d365-create-docs Pricing
User: /d365-create-docs cbLicense
```

## Output

Creates three files in `.reference/<ModuleName>/`:
- `<prefix>-architecture.md` — Technical architecture
- `<prefix>-user-guide.md` — End user guide
- `<prefix>-functional-guide.md` — Functional specification

Each document follows the established CloudBeacon documentation patterns and is ready for review.
