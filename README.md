# Cloud Beacon Skills

A collection of reusable Claude Code skills and slash commands for Cloud Beacon development, including D365 Finance & Operations, Azure, brand/voice standards, and automation workflows.

## Skills vs. Commands

This repo contains two flavors of Claude Code extension:

- **Slash commands** (`.claude/commands/*.md`) — Explicit, one-shot workflows you invoke by typing `/<name>`. Best for "do this thing now" generators (e.g. `/d365-new-table` scaffolds a new table).
- **Skills** (`.claude/skills/<name>/SKILL.md`) — Context that auto-loads when relevant, based on the skill's `description` frontmatter. Best for reference standards and gotchas that should apply across many requests without explicit invocation (e.g. `cb-voice` fires whenever the user is editing CB-facing content).

## Installation

### Option 1: Clone to Your Project
Clone this repo and copy the `.claude/` folder to your project:

```powershell
git clone https://github.com/cloud-beacon/cloud-beacon-skills.git
Copy-Item -Path "cloud-beacon-skills\.claude" -Destination "path\to\your\project\" -Recurse
```

### Option 2: Symlink (Recommended for Development)
Create symlinks so updates to the skills repo are immediately available:

```powershell
# From your project directory
New-Item -ItemType SymbolicLink -Path ".claude\commands" -Target "C:\Users\<you>\source\repos\cloud-beacon-skills\.claude\commands"
New-Item -ItemType SymbolicLink -Path ".claude\skills"   -Target "C:\Users\<you>\source\repos\cloud-beacon-skills\.claude\skills"
New-Item -ItemType SymbolicLink -Path ".claude\hooks"    -Target "C:\Users\<you>\source\repos\cloud-beacon-skills\.claude\hooks"
```

> **Note:** `New-Item -ItemType SymbolicLink` on Windows requires either an elevated shell (Run as Administrator) or [Developer Mode enabled](https://learn.microsoft.com/en-us/windows/apps/get-started/developer-mode-features-and-debugging) (Settings → Privacy & security → For developers).

### Option 3: Global Installation
Copy to your global Claude Code config to make commands and skills available in all projects:

```powershell
Copy-Item -Path "cloud-beacon-skills\.claude\commands\*" -Destination "$env:USERPROFILE\.claude\commands\" -Force
Copy-Item -Path "cloud-beacon-skills\.claude\skills\*"   -Destination "$env:USERPROFILE\.claude\skills\"   -Force
```

## Available Skills (auto-triggering)

Skills load automatically when their description matches the context — no command needed.

### Cloud Beacon brand & engineering

| Skill | Trigger | Description |
|-------|---------|-------------|
| `cb-voice` | "rewrite in CB voice", customer-facing drafting/editing, proposals, SOWs, FDDs, reports | Brand voice & tone — structural, language, and tone-by-document-type rules for external writing |
| `cb-brand` | Styling any CB-branded UI/HTML/Figma/SwiftUI/slide/marketing output, design tokens | Visual identity — exact color palette, typography, spacing, and component patterns |
| `docx-survival` | `import { ... } from 'docx'`, building DOCX exporters, "Word found unreadable content" debugging | Hard-won gotchas for the `docx` npm package (v9) — image type, SVG handling, TextRun pitfalls, hyperlink bug |

### D365 Finance & Operations

See [D365-NOTES.md](D365-NOTES.md) for cross-cutting D365 knowledge (CRLF rules, `.rnrproj` layout, common gotchas, workflow examples).

**Review & Quality**

| Skill | Triggers on |
|-------|-------------|
| `xpp-code-review` | "review this X++", critiquing/sanity-checking D365 objects, PRs, shelvesets — 19-category severity-rated check framework |
| `tfvc-fetch` | "show me shelveset X", "diff for changeset 12345", fetching ADO TFVC changes as review-ready Markdown (read-only) |

**Create / Extend Artifacts**

| Skill | Triggers on |
|-------|-------------|
| `d365-new-table` | "create / add a new table", end-to-end table + form + menu + security |
| `d365-new-form` | "create a form", SimpleList / SimpleListDetails / custom patterns |
| `d365-new-class` | "create an X++ class", helpers, contracts, handlers, services |
| `d365-new-enum` | "create an enum" / extensibility setup |
| `d365-new-edt` | "create an EDT" / reusable typed field |
| `d365-new-entity` | "create a data entity", OData/DMF integration |
| `d365-new-service` | "expose a web service", SOAP/JSON service group |
| `d365-new-query` | "create an AOT query" |
| `d365-new-menu` | "add to navigation", menu / menu extension |
| `d365-new-workspace` | "create a workspace" / role center / tile-driven landing page |
| `d365-new-feature` | "add a feature flag" / Feature Management gate |
| `d365-new-number-sequence` | "wire up a number sequence" / auto-numbered ID |
| `d365-batch-job` | "create a batch job", SysOperation Controller → Contract → Service |
| `d365-extend-table` | "extend SalesTable" / add fields to a base table |
| `d365-extend-form` | "add a button/tab to an existing form", form extension |
| `d365-extend-class` | "wrap method with CoC", Chain of Command |
| `d365-extend-enum` | "add a value to a base enum" |
| `d365-extend-edt` | "change a property on a base EDT" |
| `d365-security` | "set up security for X", Role → Duty → Privilege → Entry Point |
| `d365-create-docs` | "write the Architecture / User / Functional guide for this module" |
| `d365-fix-encoding` | "files won't open in VS" / CRLF normalization / D365 metadata encoding |

## Available Slash Commands

Slash commands require explicit invocation (`/<name>`). Reserved for workflows with real side effects that shouldn't auto-fire from conversational drift.

| Command | Description |
|---------|-------------|
| `/cb-agent` | Automated Azure DevOps work item processor — creates branches, makes commits, opens PRs. Explicit invocation required because it modifies ADO state. |

## Hooks

Configured in [`.claude/settings.json`](.claude/settings.json). Hooks fire automatically on Claude Code tool events — they run reliably regardless of whether a skill remembered to mention them.

| Hook | Fires on | What it does |
|------|----------|--------------|
| `d365-normalize-crlf` | `PostToolUse` for `Write` / `Edit` / `MultiEdit` | Detects D365 metadata XML paths (`Ax<Type>\*.xml`) and normalizes line endings to CRLF immediately after write. No-ops silently on non-D365 files. |

Hooks travel with the `.claude/` folder — copying or symlinking the repo into your project activates them automatically.

## Usage

**Skills** load automatically when relevant. Just describe what you want:

> "let's add a new VendInvoiceLog table" → `d365-new-table` fires
>
> "rewrite this section to be customer-facing" → `cb-voice` fires
>
> "this exports a corrupt .docx" → `docx-survival` fires

**Slash commands** are typed explicitly:

```
/cb-agent
```

## Repository Layout

```
.
├── D365-NOTES.md                       # Cross-cutting D365 F&O knowledge
├── CONTRIBUTING.md                     # How to author skills, commands, and hooks
└── .claude/
    ├── settings.json                   # Hook registrations
    ├── hooks/
    │   └── d365-normalize-crlf.ps1     # PostToolUse CRLF normalizer
    ├── commands/                       # Slash commands (explicit invocation)
    │   └── cb-agent.md                 # ADO work item processor
    └── skills/                         # Auto-triggering skills (context-loaded)
        ├── cb-voice/SKILL.md           # Brand voice & tone
        ├── cb-brand/SKILL.md           # Visual identity tokens & patterns
        ├── docx-survival/SKILL.md      # `docx` npm package gotchas
        ├── xpp-code-review/SKILL.md    # X++ code review framework
        ├── tfvc-fetch/                 # TFVC shelveset/changeset diff fetcher
        │   ├── SKILL.md
        │   └── scripts/tfvc_review.py
        ├── d365-new-*/SKILL.md         # Create new D365 artifacts
        ├── d365-extend-*/SKILL.md      # Extend base D365 artifacts
        ├── d365-batch-job/SKILL.md
        ├── d365-security/SKILL.md
        ├── d365-create-docs/SKILL.md
        └── d365-fix-encoding/SKILL.md
```

## Requirements

- Claude Code CLI or VS Code extension
- For D365 skills: D365 F&O development environment, PowerShell
- For `/cb-agent`: Azure DevOps access and `az` CLI configured

## Customization

Skills live at `.claude/skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`). The `description` is what determines when the skill auto-loads — be specific. Slash commands live at `.claude/commands/<name>.md` as plain markdown. You can:

- Tighten or broaden a skill's `description` to control when it fires
- Modify templates inside each skill to match your naming conventions
- Add new skills or commands following the same pattern

### D365 Model Context

D365 skills reference a `Model Context` section from CLAUDE.md. Ensure your project's CLAUDE.md includes:

```markdown
## Model Context

| Property | Value |
|----------|-------|
| **Model Name** | YourModel |
| **Package Path** | `K:\AosService\PackagesLocalDirectory\YourModel\YourModel` |
| **Naming Prefix** | `ym` |
| **VS Project** | `C:\path\to\your.rnrproj` |
| **Label File ID** | `YourModel` |
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide — skill vs. command vs. hook decision tree, frontmatter rules, how to write a `description` that actually fires, and hook safety patterns.

Quick version:

1. Fork or branch off `main`
2. Add or modify the skill / command / hook
3. Test by symlinking your branch into a real project and verifying the trigger fires (or doesn't) where expected
4. Update [`README.md`](README.md) and [`D365-NOTES.md`](D365-NOTES.md) if applicable
5. Open a PR

## License

MIT License - See LICENSE file for details.

## Maintainers

- Cloud Beacon Development Team
