# Alta Beacon Skills

Alta Beacon's Claude Code skills, agents, commands and hooks, grouped into plugins by
team: sales, marketing, D365 development, code review and delivery documents. Install
only the groups you need.

## Install

In Claude Code (CLI, desktop or VS Code), add this repo as a plugin marketplace once:

```
/plugin marketplace add cloud-beacon/cloud-beacon-skills
```

Then install the groups you want:

```
/plugin install ab-sales@altabeacon
/plugin install ab-marketing@altabeacon
/plugin install ab-d365-dev@altabeacon
/plugin install ab-code-review@altabeacon
/plugin install ab-delivery-docs@altabeacon
```

Or run `/plugin`, open the **altabeacon** marketplace and pick from the list. To get
updates later: `/plugin marketplace update altabeacon`.

You don't type the skill names. Describe what you want ("update the WellBoss proposal",
"create an X++ table for vendor invoice logs") and the matching skill loads. Plugin skills
and commands can also be called explicitly as `/<plugin>:<name>`, e.g. `/ab-code-review:cr`.

**Working from a repo?** A project can ask Claude Code to offer these plugins to everyone
who opens it. Add this to the project's `.claude/settings.json` (the Proposals repo does):

```json
{
  "extraKnownMarketplaces": {
    "altabeacon": { "source": { "source": "github", "repo": "cloud-beacon/cloud-beacon-skills" } }
  },
  "enabledPlugins": { "ab-sales@altabeacon": true }
}
```

## The plugins

### ab-sales: client proposals

| Skill / agent | Use it for |
|---|---|
| `client-proposal` | "Create a proposal for Acme from this email": a new client-branded proposal page, published as a link |
| `proposal-update` | "Change the rate on the WellBoss proposal", "make it live": edits an existing proposal and publishes it |
| `proposal-writer` (agent) | Hand off a whole proposal job; it works from the two skills above |

Proposals live in the private `cloud-beacon/Proposals` repo. Both skills check your access
first. Without access, Claude gives you a ready-to-send request to Chad.

### ab-marketing: brand and content

| Skill | Use it for |
|---|---|
| `cb-voice` | Customer-facing writing in Alta Beacon's voice: proposals, SOWs, FDDs, reports |
| `cb-brand` | Styling anything Alta Beacon-branded: palette, type, spacing, logos |
| `alta-beacon-brand` | The design system distilled from the website build |
| `cb-image-intake` | Putting images onto Alta Beacon web properties |
| `cb-photo-background` | Replacing or recoloring a photo background |
| `deck-to-page` | Turning a methodology deck into a website Approach page |
| `linkedin-quote-card` | A LinkedIn quote card from the Canva template |

### ab-d365-dev: X++ development

See [D365-NOTES.md](D365-NOTES.md) for cross-cutting D365 knowledge (CRLF rules, `.rnrproj`
layout, common gotchas, workflow examples).

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
| `d365-fix-encoding` | "files won't open in VS" / CRLF normalization / D365 metadata encoding |

Also in this plugin:

- **Command `/ab-d365-dev:cb-agent`**: automated Azure DevOps work-item processor (creates
  branches, commits, opens PRs). Explicit invocation only, because it changes ADO state.
  Needs the `az` CLI signed in.
- **Hook `d365-normalize-crlf`**: after every Write/Edit, normalizes D365 metadata XML
  (`Ax<Type>\*.xml`) to CRLF. It does nothing for any other file, so it's safe to leave on.

### ab-code-review: X++ review and TFVC

| Skill | Use it for |
|---|---|
| `xpp-code-review` | Reviewing X++ / D365 objects, PRs, shelvesets: the 19-category, severity-rated framework |
| `cbcr-review` | Sending your working changes to the pre-submit review service (report by email) |
| `cr` | Shorthand for `cbcr-review` (`/ab-code-review:cr`) |
| `tfvc-fetch` | "Show me shelveset X", "diff for changeset 12345", as review-ready Markdown (read-only) |
| `tfvc-merge` | Unattended TFVC merges, promoting changesets from a lower branch to a higher one |

### ab-delivery-docs: delivery documents

| Skill | Use it for |
|---|---|
| `fdd-chain` | A Functional Design Document from a discovery transcript, requirements or notes |
| `d365-create-docs` | The standard module documentation set: Architecture, User Guide, Functional |
| `docx-survival` | Gotchas for the `docx` npm package when generating Word documents |

## Repository layout

```
.
├── .claude-plugin/marketplace.json   # Lists the plugins below
├── plugins/
│   ├── ab-sales/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/<name>/SKILL.md
│   │   └── agents/proposal-writer.md
│   ├── ab-marketing/       (skills/)
│   ├── ab-d365-dev/        (skills/, commands/cb-agent.md, hooks/hooks.json + d365-normalize-crlf.ps1)
│   ├── ab-code-review/     (skills/)
│   └── ab-delivery-docs/   (skills/)
├── D365-NOTES.md                     # Cross-cutting D365 F&O knowledge
└── CONTRIBUTING.md                   # How to author skills, commands, hooks and plugins
```

Claude Code only finds skills one folder deep, so grouping works through plugins, not
subfolders of `.claude/skills/`.

## Requirements

- Claude Code CLI or VS Code extension
- For D365 skills: D365 F&O development environment, PowerShell
- For `/cb-agent`: Azure DevOps access and `az` CLI configured

## Customization

Skills live at `plugins/<plugin>/skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`). The `description` is what determines when the skill auto-loads, so be specific. Commands live at `plugins/<plugin>/commands/<name>.md`. You can:

- Tighten or broaden a skill's `description` to control when it fires
- Modify templates inside each skill to match your naming conventions
- Add new skills or commands to the plugin they belong to (or a new plugin, listed in `.claude-plugin/marketplace.json`)

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
3. Test with `claude --plugin-dir plugins/<plugin>` in a real project and check the trigger fires (or doesn't) where expected; run `claude plugin validate .`
4. Update [`README.md`](README.md) and [`D365-NOTES.md`](D365-NOTES.md) if applicable
5. Open a PR

## License

MIT License - See LICENSE file for details.

## Maintainers

- Alta Beacon Development Team
