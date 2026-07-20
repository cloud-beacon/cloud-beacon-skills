#!/usr/bin/env bash
# submit.sh — read a unified diff from stdin, POST to cr.cloudbeacon.com/review.
#
# Auth: acquires an Entra ID bearer token via `az account get-access-token`
# against the cbcr-service app. Azure CLI is pre-authorized on the app so
# this works silently for any signed-in Cloud Beacon user — no interactive
# prompt after the initial `az login`.
#
# JSON assembly: probes for jq → node → python3 → python → py -3, uses the
# first one it finds. Never uses shell string concat because diffs contain
# every quote/newline/backslash pain point imaginable. On Windows, `python3`
# is usually the Store stub — real Pythons live under `py -3` or `python`.
#
# Exit codes:
#    0   submitted (and, with --wait, review completed)
#    2   usage error
#    3   az CLI not installed
#    4   empty diff (stdin was empty)
#    5   token acquisition failed (run `az login`)
#    6   no JSON encoder available (need jq, node, python3, python, or py)
#    7   endpoint returned non-202
#    8   --wait poll saw the job fail

set -euo pipefail

CBCR_APP_ID="357ad426-0779-493a-a55f-e0bb3894d4b1"
CBCR_URL="${CBCR_URL:-https://cr.cloudbeacon.com}"
WAIT=0

while [ $# -gt 0 ]; do
    case "$1" in
        --wait) WAIT=1; shift ;;
        --help|-h)
            cat <<USAGE
usage: submit.sh [--wait] < diff.patch

Reads a unified diff from stdin, submits it to the cbcr endpoint, and
prints the job_id. With --wait, polls the endpoint until the job
reaches a terminal state (done|failed).

Requires: az CLI signed in to the Cloud Beacon tenant, plus one of
jq / node / python3 / python / py for JSON assembly.
USAGE
            exit 0
            ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

# --- 1. Preflight ---------------------------------------------------------

if ! command -v az >/dev/null 2>&1; then
    echo "error: az CLI not on PATH. Install:" >&2
    echo "  https://learn.microsoft.com/cli/azure/install-azure-cli" >&2
    exit 3
fi
if ! command -v curl >/dev/null 2>&1; then
    echo "error: curl not on PATH." >&2
    exit 3
fi

# --- 2. Diff from stdin ---------------------------------------------------

DIFF=$(cat)
DIFF_BYTES=${#DIFF}
if [ "$DIFF_BYTES" -eq 0 ]; then
    echo "error: no diff on stdin. Pipe a unified diff, e.g.:" >&2
    echo "  git diff HEAD | submit.sh" >&2
    exit 4
fi

# --- 3. Token acquisition -------------------------------------------------

TOKEN_ERR=$(mktemp)
trap 'rm -f "$TOKEN_ERR"' EXIT
TOKEN=$(az account get-access-token \
    --resource "api://$CBCR_APP_ID" \
    --query accessToken -o tsv 2>"$TOKEN_ERR") || {
    echo "error: az token acquisition failed. Run:" >&2
    echo "  az login --tenant cloudbeacon.dev" >&2
    echo "and try again. Underlying error:" >&2
    cat "$TOKEN_ERR" >&2
    exit 5
}

# --- 4. Assemble JSON payload --------------------------------------------

# Probe encoders in order of preference. Windows Store stubs for python*
# print a "Python was not found" line to stderr but exit 49 — treat any
# non-zero exit as "not really there" and fall through.
encode_diff() {
    if command -v jq >/dev/null 2>&1; then
        printf '%s' "$DIFF" | jq -Rs '{diff: .}' && return 0
    fi
    if command -v node >/dev/null 2>&1 && node --version >/dev/null 2>&1; then
        printf '%s' "$DIFF" | node -e 'process.stdout.write(JSON.stringify({diff: require("fs").readFileSync(0,"utf8")}))' && return 0
    fi
    for py in python3 python "py -3" py; do
        if $py --version >/dev/null 2>&1; then
            printf '%s' "$DIFF" | $py -c 'import json,sys;sys.stdout.write(json.dumps({"diff":sys.stdin.read()}))' && return 0
        fi
    done
    return 1
}

PAYLOAD=$(encode_diff) || {
    echo "error: no working JSON encoder found (tried jq, node, python3, python, py -3)" >&2
    echo "  install one:  choco install jq   |   winget install OpenJS.NodeJS" >&2
    exit 6
}

# --- 5. POST /review -----------------------------------------------------

RESP_BODY=$(mktemp)
trap 'rm -f "$TOKEN_ERR" "$RESP_BODY"' EXIT
HTTP_CODE=$(curl -sS -o "$RESP_BODY" -w "%{http_code}" \
    -X POST "$CBCR_URL/review" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

if [ "$HTTP_CODE" != "202" ]; then
    echo "error: endpoint returned HTTP $HTTP_CODE" >&2
    cat "$RESP_BODY" >&2
    echo >&2
    exit 7
fi

# Parse a scalar JSON field. Same encoder probe as encode_diff — same
# tools, just reading instead of writing.
json_field() {
    local field=$1
    local file=$2
    local default=${3:-}
    if command -v jq >/dev/null 2>&1; then
        local out
        out=$(jq -r --arg d "$default" ".$field // \$d" <"$file")
        printf '%s' "$out"
        return
    fi
    if command -v node >/dev/null 2>&1 && node --version >/dev/null 2>&1; then
        node -e "const o=JSON.parse(require('fs').readFileSync(process.argv[1],'utf8'));process.stdout.write(String(o.$field ?? process.argv[2] ?? ''))" "$file" "$default"
        return
    fi
    for py in python3 python "py -3" py; do
        if $py --version >/dev/null 2>&1; then
            $py -c "import json,sys;d=json.load(open(sys.argv[1]));sys.stdout.write(str(d.get(sys.argv[2], sys.argv[3])))" "$file" "$field" "$default"
            return
        fi
    done
    return 1
}

JOB_ID=$(json_field job_id "$RESP_BODY")
DEDUP=$(json_field dedup  "$RESP_BODY" "false")

echo "Submitted."
echo "  job:  $JOB_ID"
echo "  size: $DIFF_BYTES bytes"
if [ "$DEDUP" = "true" ]; then
    echo "  note: identical diff already in queue; showing existing job."
fi
echo
echo "The review report will arrive by email (from cdalton@cloudbeacon.dev,"
echo "delivered to your inbox) in 1-2 minutes."

# --- 6. Optional --wait --------------------------------------------------

if [ "$WAIT" = "0" ]; then
    exit 0
fi

echo
echo "Polling until done..."
POLL_FILE=$(mktemp)
trap 'rm -f "$TOKEN_ERR" "$RESP_BODY" "$POLL_FILE"' EXIT
while true; do
    sleep 5
    curl -sS -H "Authorization: Bearer $TOKEN" "$CBCR_URL/review/$JOB_ID" -o "$POLL_FILE"
    STATE=$(json_field state "$POLL_FILE" "unknown")
    case "$STATE" in
        done)
            echo "  → done. Check your inbox for the report."
            exit 0
            ;;
        failed)
            echo "  → failed. See email for the alert." >&2
            echo "  response: $(cat "$POLL_FILE")" >&2
            exit 8
            ;;
        pending|running)
            echo "  ...state: $STATE"
            ;;
        *)
            echo "  ...state: $STATE (unexpected)" >&2
            ;;
    esac
done
