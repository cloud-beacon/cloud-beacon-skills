---
name: cr
description: Shorthand alias for cbcr-review — submit working changes (diff, TFVC shelveset, or ADO Git PR) to Cloud Beacon's pre-submit review endpoint. Trigger on `/cr` exactly as you would `/cbcr-review`. Not the same as `/cr-review` (the admin inbox-sweep command in the Cloud-Beacon-CR repo).
---

# /cr — alias for cbcr-review

This skill is a shorthand entry point only. It contains no logic of its
own and must not duplicate any.

**Do this:** invoke the `cbcr-review` skill via the Skill tool, passing
through any arguments the user gave `/cr` verbatim (e.g. `/cr --wait`,
`/cr --workitem 2538 for buddig`, `/cr review shelveset "Name;owner"
for buddig`). Then follow `cbcr-review`'s instructions exactly.

If the `cbcr-review` skill is not installed, tell the user to copy
`cloud-beacon-skills/.claude/skills/cbcr-review/` to
`~/.claude/skills/cbcr-review/` — this alias depends on it.
