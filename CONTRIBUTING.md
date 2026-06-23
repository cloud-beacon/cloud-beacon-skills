# Contributing to Cloud Beacon Skills

This repo holds two kinds of Claude Code extensions plus shared hooks. Pick the right format, write a description that actually fires, and keep the surface area tight.

## Skill vs. command vs. hook

| Kind | Fires when | Use for |
|------|------------|---------|
| **Skill** (`.claude/skills/<name>/SKILL.md`) | Claude judges the description matches the conversation context | Reference standards, gotchas, generators, patterns — anything that should apply whenever a topic comes up, no slash needed |
| **Command** (`.claude/commands/<name>.md`) | User types `/<name>` | Workflows with real side effects (writes to ADO, sends mail, runs deploys) — anything where unintended firing would be costly |
| **Hook** (`.claude/settings.json` + `.claude/hooks/*`) | Claude Code itself fires the configured tool event (`PreToolUse`, `PostToolUse`, etc.) | Mechanical actions that must always run, never forgotten by Claude — formatters, linters, encoding fixers |

**Skills are the default.** Reach for a command only when explicit invocation is a feature (ADO writes, destructive ops). Reach for a hook only when "Claude should remember to do X" is fragile and "the harness always does X" is the actual requirement.

## Writing a SKILL.md

```yaml
---
name: <skill-name>            # kebab-case, must match the folder name
description: <one paragraph>  # the entire trigger mechanism — see below
---

# <Skill Title>

<skill body — instructions for Claude>
```

### The description field is the whole game

Claude only loads a skill when its `description` plausibly matches the conversation. The description does double duty: it tells Claude *what the skill does* AND *when to fire*. Get this wrong and the skill never loads, or it loads constantly and pollutes context.

**Good description structure:**

1. **What it does** in one clear sentence — concrete artifacts, technologies, file types
2. **Use this whenever** clause — natural-language phrases the user is likely to actually say
3. **Negative scope** if there's a sibling skill it could be confused with ("do not use for X — see `other-skill` for that")

**Examples from this repo:**

> `d365-new-table` — "Scaffold a new D365 Finance & Operations table end-to-end — AxTable, AxForm, AxMenuItemDisplay, AxSecurityPrivilege, AxSecurityDuty, and labels. Use whenever the user asks to create, add, scaffold, or stand up a new D365 / X++ / AX table or persistent entity..."

> `docx-survival` — "...Use this whenever code imports from `docx` (`import { Document, Paragraph, TextRun, ImageRun, ... } from 'docx'`), builds or modifies .docx export logic, embeds images or SVGs into Word documents, sets hyperlinks/underlines/styles in DOCX, or debugs 'Word found unreadable content'..."

Notice both list concrete vocabulary the user might type. Vague descriptions like "Helps with D365 development" never fire — there's no specific intent to match against.

### Common description mistakes

- **Too generic:** "Useful for D365 work." → Won't reliably fire.
- **Marketing voice:** "A powerful framework for..." → Claude isn't a buyer; it's matching intent.
- **Only listing technologies, not actions:** "X++, AX, D365" → No action verb, no phrase to match.
- **No negative scope:** Sibling skills (e.g. `d365-new-table` vs `d365-extend-table`) end up competing — say what each is NOT for.

### Skill folder layout

```
.claude/skills/<skill-name>/
├── SKILL.md           # required
└── scripts/           # optional — bundled scripts the skill invokes
    └── ...
```

Bundled scripts should be self-contained (Python stdlib only, PowerShell with no module imports, etc.) so the skill works in any environment without a setup step.

## Writing a slash command

Slash commands are plain markdown — no frontmatter required, no auto-trigger. Name the file `<command>.md`; the user invokes with `/<command>`. Use commands sparingly — see [`.claude/commands/cb-agent.md`](.claude/commands/cb-agent.md) for the kind of explicit-invocation workflow that fits.

## Writing a hook

Hooks live in two pieces:

1. **`.claude/settings.json`** — declares which tool events fire which commands
2. **`.claude/hooks/<name>.<ext>`** — the script Claude Code executes

The hook command receives a JSON payload on stdin describing the tool call (`tool_name`, `tool_input.file_path`, etc.). See [`.claude/hooks/d365-normalize-crlf.ps1`](.claude/hooks/d365-normalize-crlf.ps1) for the canonical pattern.

### Hook safety rules

- **Never block** the tool call due to a hook bug — wrap the body in try/catch and exit 0 on internal errors. A broken hook should fail open, not lock the user out.
- **Filter aggressively in the script,** not just the `matcher`. Matchers select by tool name; path/content filtering happens in the script. A `Write|Edit|MultiEdit` hook fires on every write — do your "does this apply?" check first and exit 0 fast if not.
- **Be idempotent.** PostToolUse hooks may re-run if the user retries an edit. The hook should produce the same result on the second run.
- **Use `$CLAUDE_PROJECT_DIR`** to locate bundled scripts — never assume a cwd.

## Workflow

1. Branch off `main`.
2. Add or modify the skill/command/hook. Bump the description if the trigger behavior changed.
3. Test by symlinking your branch into a project and seeing whether the skill loads on the intended phrase. (For hooks: write a test file and watch the hook fire.)
4. Update [`README.md`](README.md) — and [`D365-NOTES.md`](D365-NOTES.md) if it's a D365 skill — with one row describing what you added.
5. Open a PR. The reviewer's first question will be "does the description fire on the right phrases and *only* the right phrases?" — be ready to defend it.

## When in doubt

- Skill before command. Command only when side effects make auto-firing dangerous.
- Hook before skill, *if* you find yourself writing "remind Claude to..." — that's a sign the action should be automatic, not a remembered instruction.
- One skill per coherent topic. Don't bundle "create + extend + review" into one mega-skill; descriptions get diluted and triggers misfire.
