---
name: tfvc-fetch
description: Pull a TFVC shelveset or changeset diff from Azure DevOps as review-ready Markdown, with X++ extracted from D365 F&O metadata XML and the linked work item resolved as the spec. Use this whenever the user wants to see, fetch, retrieve, diff, or inspect what changed in a TFVC shelveset or changeset (e.g. "what's in shelveset X", "show me the diff for changeset 12345", "pull the changes from this code review request", "get the diff so I can review it"). Works for Azure DevOps Services and Server TFVC (not Git). Read-only — it fetches and formats; it never modifies Azure DevOps.
---

# TFVC Fetch — shelveset / changeset diff retrieval

Bundled script: `scripts/tfvc_review.py` (Python 3, standard library only — no `pip install`).
It fetches a TFVC shelveset's (or changeset's) changed files from the Azure DevOps REST API,
builds a unified diff in Markdown, extracts X++ source from `<![CDATA[…]]>` in D365 metadata
`.xml` so the diff reads as code, and resolves the linked work item as the spec.

This skill only **retrieves and formats**. To then *review* the X++, apply the
`xpp-code-review` skill to the output. For the full email-triggered, multi-client review
pipeline, use the `/cr-review` command instead.

## Interpreter

Invoke with this machine's Python 3 launcher: `python3` (macOS/Linux) or `python` / `py -3`
(Windows). Shown as `<python>` below.

## Inputs

Provide the shelveset id and how to reach the org + authenticate, by one of two routes:

- **With a client profile** (the `/cr-review` project's `clients/<id>.json`): pass
  `--profile <path>`. The base URL comes from `ado_base_url`; the PAT comes from the env var
  named by `pat_env`, or from `pat_file` if set.
- **Without a profile** (ad-hoc): pass `--org-base-url https://<org>.visualstudio.com` and
  set the PAT in an env var, naming it with `--pat-env <VARNAME>` (default `AZDO_PAT`).

The PAT needs scopes **Code (Read)** + **Work Items (Read)**. Never pass it on the command
line.

**Azure DevOps Services vs Server.** Services orgs use `https://<org>.visualstudio.com` or
`https://dev.azure.com/<org>` and support api-version `7.1` (the default). An on-prem
**Azure DevOps Server** collection uses a different host (often behind VPN) and may need an
older api-version — pass `--api-version <v>` or set `api_version` in the profile. If a
notification footer says "Azure DevOps Server," confirm the host and api-version before the
first run.

## Common invocations

Shelveset (the artifact behind a TFVC "Code review" request), id is `"name;owner"`:

```
<python> scripts/tfvc_review.py --profile clients/buddig.json --shelveset "ADO868_FixLegalEntityField_20260616_0030;ohuerta@cloudbeacon.dev" --cr-id 2471 --out review-2471.md
```

Ad-hoc, no profile:

```
<python> scripts/tfvc_review.py --org-base-url https://buddigd365.visualstudio.com --pat-env AZDO_PAT_BUDDIG --shelveset "MyShelveset;dev@client.com"
```

With an explicit spec work item (otherwise auto-discovered from the shelveset's links):

```
<python> scripts/tfvc_review.py --profile clients/buddig.json --shelveset "Name;owner" --workitem 868
```

Offline fallback (a locally generated diff, e.g. `tf diff /format:unified > my.diff`):

```
<python> scripts/tfvc_review.py --difffile my.diff --cr-id 2471
```

Omit `--out` to print to stdout. `--out` creates its parent directory automatically.

## Output

Markdown with: a header (shelveset name, owner, check-in comment, file count, spec work
item), the work-item spec (HTML stripped), and per-file diffs. For D365 metadata `.xml`, the
extracted **X++ source** diff leads and the full XML diff is tucked in a collapsible
`<details>` block, so nothing is lost but code reads first.

## Troubleshooting

- **HTTP 401/403** — the PAT is missing, expired, or lacks Code/Work-Items read scope.
- **HTTP 404 on a shelveset** — it was likely unshelved (checked in); the content no longer
  exists under that name. Use a current shelveset, or fetch the changeset instead.
- **Content came back as JSON metadata** — the script already digs the `content` field out of
  a JSON response, but if a server variant still returns metadata, that's the place to look.
