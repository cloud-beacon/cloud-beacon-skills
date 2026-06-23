# cb-agent: Automated ADO Work Item Processor

You are processing Azure DevOps work items tagged `cb-agent`. Follow each phase exactly. Process work items sequentially — one branch/PR per work item.

**ADO Process Template**: Agile (work item types: Bug, User Story, Task; states: New, Active, Resolved, Closed).
**Note**: `az boards work-item update` does NOT accept `--project` — rely on the configured defaults.

## Prerequisites

Before starting, verify the `az` CLI is authenticated:
```bash
az devops project show --project "Cloud Beacon Dev" --org https://dev.azure.com/cloudbeacondev --output json
```
If this fails, stop and tell the user to run `az login` and `az devops configure --defaults organization=https://dev.azure.com/cloudbeacondev project="Cloud Beacon Dev"`.

---

## Phase 0: Query & Select Work Items

Run this WIQL query to find all eligible work items:

```bash
az boards query --wiql "SELECT [System.Id],[System.Title],[System.WorkItemType],[System.State],[System.CreatedDate] FROM workitems WHERE [System.Tags] Contains 'cb-agent' AND [System.State] = 'New' ORDER BY [System.CreatedDate] ASC" --org https://dev.azure.com/cloudbeacondev --project "Cloud Beacon Dev" --output json
```

**If no results**: Report "No work items found with `cb-agent` tag in state `New`." and stop.

**If results found**:
1. Display a numbered list to the user: `[ID] [Type] — [Title]`
2. Ask the user to confirm processing (they may want to skip certain items)
3. Once confirmed, process each work item sequentially through Phases 1–4

---

## Phase 1: Fetch & Analyze (per work item)

### 1a. Fetch full details

```bash
az boards work-item show --id <ID> --org https://dev.azure.com/cloudbeacondev --project "Cloud Beacon Dev" --output json
```

Extract from the JSON response:
- `fields["System.Title"]` — title
- `fields["System.WorkItemType"]` — Bug, User Story, or Task
- `fields["System.Description"]` — description (HTML — strip tags to get text)
- `fields["Microsoft.VSTS.TCM.ReproSteps"]` — repro steps (Bugs only)
- `fields["Microsoft.VSTS.Common.AcceptanceCriteria"]` — acceptance criteria (User Stories)
- `fields["System.CreatedBy"]["uniqueName"]` — creator email (for PR assignment)
- `fields["System.Tags"]` — tags string

### 1b. Update work item to Active

```bash
az boards work-item update --id <ID> --state Active --discussion "cb-agent analysis started — fetching details and searching codebase." --org https://dev.azure.com/cloudbeacondev --output json
```

### 1c. Analyze the codebase

Based on the description and affected component:

1. **Identify affected files**: Use Grep and Glob to find relevant classes, tables, forms, and tests.
   - Search for class/table/form names mentioned in the description
   - Search for error messages or symptoms mentioned
   - Check the CLAUDE.md architecture sections to understand which subsystem is affected

2. **For Bugs**: Identify the root cause hypothesis by reading the relevant source files.

3. **For User Stories / Tasks**: Identify the implementation approach, affected files, and estimate scope.

4. **Read ALL relevant files** before proceeding — AxClass source, AxTable metadata, AxForm XML, test classes.

### 1d. Escape Hatch check

If ANY of these are true, go to **Phase 5 (Escape Hatch)** instead of Phase 2:
- Description is too vague to identify the affected component
- The change requires modifying standard D365 objects (not `cb`-prefixed)
- The change spans more than 15 files
- The change requires database schema migrations or data fixes
- The change requires human judgment on UX/business rules not specified in the work item
- You cannot identify a clear, testable fix or implementation

---

## Phase 2: Implement

### 2a. Create branch

Ensure you're on the latest `main`:
```bash
cd "K:/AosService/PackagesLocalDirectory/CloudBeacon/CloudBeacon"
git fetch origin
git checkout main
git pull origin main
```

Create and switch to a new branch:
- **Bug**: `git checkout -b bugfix/AB#<ID>`
- **User Story**: `git checkout -b feature/AB#<ID>`
- **Task**: `git checkout -b task/AB#<ID>`

### 2b. Implement the change

Follow ALL CLAUDE.md conventions:
- **CRLF line endings** on all XML metadata files — verify after every write
- **`cb` prefix** on all new artifacts
- **XML element order** must be alphabetical for DataContract serialization
- **EDT `i:type` attribute** required on root elements
- Update labels in `AxLabelFile/LabelResources/en-US/CloudBeacon.en-US.label.txt` if needed

### 2c. Update tests if needed

Consult the test mapping table in CLAUDE.md:
- If you changed `cbPLMProcessService` → check `cbPLMProcessServiceTest`
- If you changed template classes → check `cbProductTemplateEngineTest`
- etc.

Test classes are at `K:\AosService\PackagesLocalDirectory\CloudBeaconTests\CloudBeaconTests\AxClass\`.

### 2d. Update VS project file if needed

If new files were created, ask the user which `.rnrproj` to update. Known projects:
- `C:\Users\Adminfc5989bec4\source\repos\cb_PIM\cb_PIM.rnrproj` (CloudBeacon model)
- `C:\Users\Adminfc5989bec4\source\repos\cb_PIM\cb_PIM_Tests.rnrproj` (CloudBeaconTests model)

### 2e. Verify CRLF (inline gate)

After all edits, verify CRLF on all modified/created XML files:
```bash
powershell.exe -ExecutionPolicy Bypass -Command "Get-ChildItem -Recurse -Include '*.xml' -Path 'K:\AosService\PackagesLocalDirectory\CloudBeacon\CloudBeacon' | Where-Object { (Get-Content $_.FullName -Raw) -match '(?<!\r)\n' } | Select-Object FullName"
```

If any files have LF-only line endings, fix them:
```bash
powershell.exe -ExecutionPolicy Bypass -Command "$file = 'PATH'; (Get-Content $file -Raw) -replace '(?<!\r)\n', \"`r`n\" | Set-Content $file -NoNewline"
```

**Do NOT commit or push yet** — the local build (Phase 3, Gate 1) must pass first.

---

## Phase 3: Validate

### Gate 1 — Local X++ Build (mandatory, fast)

Run a local compile using `xppc.exe` to catch errors quickly before pushing to the pipeline:

```bash
"K:/AosService/PackagesLocalDirectory/bin/xppc.exe" -metadata="K:/AosService/PackagesLocalDirectory" -compilermetadata="K:/AosService/PackagesLocalDirectory" -modelmodule=CloudBeacon -output="K:/AosService/PackagesLocalDirectory/CloudBeacon/bin" -log="K:/AosService/PackagesLocalDirectory/CloudBeacon/BuildLog.xml" -xmllog="K:/AosService/PackagesLocalDirectory/CloudBeacon/BuildLog.xml" 2>&1
```

- On **success** (exit code 0, no errors in output): proceed to Gate 2
- On **failure**: analyze the compiler errors, fix, and retry locally
- **Max retries**: 3 attempts. After 3 local build failures → **Phase 5 (Escape Hatch)**

If tests were changed, also build `CloudBeaconTests`:
```bash
"K:/AosService/PackagesLocalDirectory/bin/xppc.exe" -metadata="K:/AosService/PackagesLocalDirectory" -compilermetadata="K:/AosService/PackagesLocalDirectory" -modelmodule=CloudBeaconTests -output="K:/AosService/PackagesLocalDirectory/CloudBeaconTests/bin" -log="K:/AosService/PackagesLocalDirectory/CloudBeaconTests/BuildLog.xml" -xmllog="K:/AosService/PackagesLocalDirectory/CloudBeaconTests/BuildLog.xml" 2>&1
```

### Commit and push (after local build passes)

```bash
git add -A
git commit -m "$(cat <<'EOF'
<Type> AB#<ID>: <Short description>

<Detailed explanation of the change>

AB#<ID>

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
git push -u origin <branch-name>
```

Where `<Type>` is `Fix` for bugs, `Implement` for user stories, or the task action verb for tasks.

### Gate 2 — ADO Pipeline Build (mandatory)

Trigger the pipeline:

```bash
az pipelines run --id 2 --branch <branch-name> --org https://dev.azure.com/cloudbeacondev --project "Cloud Beacon Dev" --output json
```

Capture the `id` from the response, then poll until complete:
```bash
az pipelines runs show --id <run-id> --org https://dev.azure.com/cloudbeacondev --project "Cloud Beacon Dev" --output json
```

Poll every 30 seconds. Check `status` field:
- `completed` + `result: succeeded` → proceed to Gate 3
- `completed` + `result: failed` → analyze build logs, fix, rebuild locally, commit, push, retry
- Still running → wait and poll again

**Max wait**: 20 minutes. **Max retries**: 3 attempts.

If the pipeline build fails 3 times → go to **Phase 5 (Escape Hatch)**.

### Gate 3 — Playwright E2E (conditional)

**Only run if** the change touches any of:
- `AxForm/` files
- `AxMenuItemDisplay/` or `AxMenuItemAction/` files
- Feature management classes
- Playwright test files

```bash
cd "C:\Users\Adminfc5989bec4\source\repos\CloudBeacon-D365FO\CloudBeacon.PlaywrightTests"
dotnet test --filter Category=E2E
```

Check if auth state is fresh (skip E2E with a note if stale):
```bash
powershell.exe -ExecutionPolicy Bypass -Command "$f = 'C:\Users\Adminfc5989bec4\source\repos\CloudBeacon-D365FO\CloudBeacon.PlaywrightTests\.auth\storageState.json'; if (Test-Path $f) { $age = (Get-Date) - (Get-Item $f).LastWriteTime; if ($age.TotalHours -gt 12) { Write-Output 'STALE' } else { Write-Output 'FRESH' } } else { Write-Output 'MISSING' }"
```

If STALE or MISSING: skip E2E tests, note this in the PR description.

**Max retries**: 2 attempts. On repeated failure → note in PR (not an escape hatch trigger).

---

## Phase 4: PR + ADO Update

### 4a. Create Pull Request

```bash
az repos pr create \
  --repository "Cloud Beacon Dev" \
  --source-branch <branch-name> \
  --target-branch main \
  --title "<PR Title>" \
  --description "$(cat <<'EOF'
## Summary

<1-3 bullet point summary of the change>

## Work Item

Fixes AB#<ID>: <work item title>

## Files Changed

<Bulleted list of files modified/created/deleted>

## Validation

- [x] X++ Build: <passed/failed — pipeline run link>
- [<x or space>] Playwright E2E: <passed/skipped — reason>
- [x] CRLF verification: passed

## Test Coverage

<Note any test additions/modifications, or "No test changes needed">

---
Generated by cb-agent (Claude Code)
EOF
)" \
  --work-items <ID> \
  --delete-source-branch true \
  --org https://dev.azure.com/cloudbeacondev \
  --project "Cloud Beacon Dev" \
  --output json
```

**PR Title format**:
- Bug: `Fix AB#<ID>: <short description>`
- User Story: `Implement AB#<ID>: <short description>`
- Task: `AB#<ID>: <short description>`

### 4b. Update work item

Get the creator's email from Phase 1 (`System.CreatedBy.uniqueName`), then:

```bash
az boards work-item update \
  --id <ID> \
  --state Resolved \
  --assigned-to "<creator-email>" \
  --discussion "cb-agent completed. PR created: <PR-URL>. Please review and merge." \
  --org https://dev.azure.com/cloudbeacondev \
  --output json
```

### 4c. Report and continue

Report to the user:
- Work item ID and title
- PR URL
- Build result
- E2E result (if applicable)

Then move to the next work item in the queue.

---

## Phase 5: Escape Hatch

When a work item cannot be completed automatically.

### 5a. Clean up branch

```bash
git checkout main
git branch -D <branch-name> 2>/dev/null
git push origin --delete <branch-name> 2>/dev/null
```

### 5b. Post analysis comment

```bash
az boards work-item update \
  --id <ID> \
  --state New \
  --discussion "$(cat <<'EOF'
## cb-agent Analysis

**Status**: Could not complete automatically.

**What was found**:
<List findings — affected files, root cause hypothesis, code patterns observed>

**What was attempted** (if any):
<List any implementation attempts and why they failed>

**Recommended next steps**:
<Specific actionable steps for a human developer>

**Files to investigate**:
<List of file paths with line numbers>

---
Generated by cb-agent (Claude Code)
EOF
)" \
  --org https://dev.azure.com/cloudbeacondev \
  --output json
```

### 5c. Swap tags

Remove `cb-agent` tag and add `cb-agent-failed`:

```bash
# Get current tags
CURRENT_TAGS=$(az boards work-item show --id <ID> --org https://dev.azure.com/cloudbeacondev --query "fields.\"System.Tags\"" -o tsv)

# Replace cb-agent with cb-agent-failed
NEW_TAGS=$(echo "$CURRENT_TAGS" | sed 's/cb-agent/cb-agent-failed/g')

az boards work-item update \
  --id <ID> \
  --fields "System.Tags=$NEW_TAGS" \
  --org https://dev.azure.com/cloudbeacondev \
  --output json
```

### 5d. Continue processing

Report the escape to the user, then move to the next work item in the queue. Do NOT stop the entire run because of one failed work item.

---

## Important Notes

- **Never skip the build gate** — a failing build means the change is broken.
- **Always verify CRLF** on XML files — LF-only breaks D365 tooling.
- **One work item = one branch = one PR** — never batch multiple work items into a single PR.
- **Respect the escape hatch** — it's better to leave a detailed analysis comment than to push broken code.
- **Follow CLAUDE.md** — all coding conventions, naming patterns, and architecture guidelines apply.
- **Ask the user** if anything is ambiguous — the escape hatch is for genuinely unclear situations, not for skipping confirmation.
