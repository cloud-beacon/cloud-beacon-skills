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
```

### Option 3: Global Installation
Copy to your global Claude Code config to make commands and skills available in all projects:

```powershell
Copy-Item -Path "cloud-beacon-skills\.claude\commands\*" -Destination "$env:USERPROFILE\.claude\commands\" -Force
Copy-Item -Path "cloud-beacon-skills\.claude\skills\*"   -Destination "$env:USERPROFILE\.claude\skills\"   -Force
```

## Available Skills (auto-triggering)

Skills load automatically when their description matches the context — no command needed.

| Skill | Trigger | Description |
|-------|---------|-------------|
| `cb-voice` | "rewrite in CB voice", customer-facing drafting/editing, proposals, SOWs, FDDs, reports | Cloud Beacon brand voice & tone — structural, language, and tone-by-document-type rules for external writing |
| `cb-brand` | Styling any CB-branded UI/HTML/Figma/SwiftUI/slide/marketing output, design tokens | Cloud Beacon visual identity — exact color palette, typography, spacing, and component patterns |
| `docx-survival` | `import { ... } from 'docx'`, building DOCX exporters, "Word found unreadable content" debugging | Hard-won gotchas for the `docx` npm package (v9) — image type, SVG handling, TextRun pitfalls, hyperlink bug |

## Available Slash Commands

### D365 Finance & Operations

#### Documentation & Automation
| Skill | Command | Description |
|-------|---------|-------------|
| Create Documentation | `/d365-create-docs` | Generate architecture, user guide, and functional guide for a module |

#### Create New Artifacts
| Skill | Command | Description |
|-------|---------|-------------|
| New Class | `/d365-new-class` | Create X++ class with proper metadata |
| New Table | `/d365-new-table` | Create table end-to-end (table, form, menu item, security) |
| New Form | `/d365-new-form` | Create form with standard patterns |
| New Data Entity | `/d365-new-entity` | Create data entity with staging table |
| New Enum | `/d365-new-enum` | Create enumeration |
| New EDT | `/d365-new-edt` | Create Extended Data Type |
| New Query | `/d365-new-query` | Create AOT query |
| New Service | `/d365-new-service` | Create web service (service class, contract, group) |
| New Menu | `/d365-new-menu` | Create menu and menu extension |
| New Workspace | `/d365-new-workspace` | Create workspace with tiles and lists |
| New Feature | `/d365-new-feature` | Create Feature Management class |
| New Number Sequence | `/d365-new-number-sequence` | Create number sequence with references |
| New Batch Job | `/d365-batch-job` | Create batch job (controller, service, contract) |

#### Extend Existing Artifacts
| Skill | Command | Description |
|-------|---------|-------------|
| Extend Table | `/d365-extend-table` | Create table extension |
| Extend Form | `/d365-extend-form` | Create form extension |
| Extend Class | `/d365-extend-class` | Create Chain of Command extension |
| Extend Enum | `/d365-extend-enum` | Create enum extension |
| Extend EDT | `/d365-extend-edt` | Create EDT extension |

#### Security & Utilities
| Skill | Command | Description |
|-------|---------|-------------|
| Security Model | `/d365-security` | Create privileges, duties, and roles |
| Fix Encoding | `/d365-fix-encoding` | Fix CRLF line endings on metadata XML files |

### Automation

| Skill | Command | Description |
|-------|---------|-------------|
| CB Agent | `/cb-agent` | Automated ADO work item processor for CloudBeacon development |

## Usage

**Slash commands** — invoke explicitly:

```
/d365-new-table
```

Claude will guide you through the process, asking for necessary parameters and creating all required artifacts.

**Skills** — load automatically when relevant. For example, asking Claude to "rewrite this section to be customer-facing" will auto-trigger `cb-voice` if installed. No invocation required.

## Repository Layout

```
.claude/
├── commands/                      # Slash commands (explicit invocation)
│   ├── d365-new-*.md              # Create new D365 artifacts
│   ├── d365-extend-*.md           # Extend existing D365 artifacts
│   ├── d365-batch-job.md          # Batch processing
│   ├── d365-security.md           # Security model
│   ├── d365-create-docs.md        # Documentation generation
│   ├── d365-fix-encoding.md       # Utility
│   ├── cb-agent.md                # ADO integration
│   └── D365-SKILLS-README.md      # Slash command reference
└── skills/                        # Auto-triggering skills (context-loaded)
    ├── cb-voice/SKILL.md          # Brand voice & tone for customer-facing writing
    ├── cb-brand/SKILL.md          # Visual identity tokens & component patterns
    └── docx-survival/SKILL.md     # `docx` npm package gotchas
```

## Requirements

- Claude Code CLI or VS Code extension
- For D365 skills: D365 F&O development environment, PowerShell
- For automation skills: Azure DevOps access (where applicable)

## Customization

Each skill is a markdown file in `.claude/commands/`. You can:
- Modify existing skills to match your naming conventions
- Add new skills following the same pattern
- Organize skills into subdirectories by category

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

1. Fork this repository
2. Create a feature branch
3. Add or modify skills
4. Test in your environment
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Maintainers

- Cloud Beacon Development Team
