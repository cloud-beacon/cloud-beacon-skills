# Cloud Beacon Skills

A collection of reusable Claude Code skills for Cloud Beacon development, including D365 Finance & Operations, Azure, and automation workflows.

## Installation

### Option 1: Clone to Your Project
Clone this repo and copy the `.claude/commands/` folder to your project:

```powershell
git clone https://github.com/cloudbeacondev/cloud-beacon-skills.git
Copy-Item -Path "cloud-beacon-skills\.claude" -Destination "path\to\your\project\" -Recurse
```

### Option 2: Symlink (Recommended for Development)
Create a symlink so updates to the skills repo are immediately available:

```powershell
# From your project directory
New-Item -ItemType SymbolicLink -Path ".claude\commands" -Target "C:\Users\<you>\source\repos\cloud-beacon-skills\.claude\commands"
```

### Option 3: Global Installation
Copy to your global Claude Code config to make skills available in all projects:

```powershell
Copy-Item -Path "cloud-beacon-skills\.claude\commands\*" -Destination "$env:USERPROFILE\.claude\commands\" -Force
```

## Available Skills

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

After installation, invoke any skill by typing its command in Claude Code:

```
/d365-new-table
```

Claude will guide you through the process, asking for necessary parameters and creating all required artifacts.

## Skill Categories

```
.claude/commands/
├── D365 Development
│   ├── d365-new-*.md       # Create new artifacts
│   ├── d365-extend-*.md    # Extend existing artifacts
│   ├── d365-batch-job.md   # Batch processing
│   ├── d365-security.md    # Security model
│   ├── d365-create-docs.md # Documentation generation
│   └── d365-fix-encoding.md# Utility
├── Automation
│   └── cb-agent.md         # ADO integration
└── D365-SKILLS-README.md   # Skills reference
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
