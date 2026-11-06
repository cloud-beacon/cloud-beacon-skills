<#
    run_merge.ps1 — Windows Task Scheduler entry point for tfvc-merge.

    Invokes the orchestrator's `run` subcommand and exits with its return code
    so Task Scheduler reflects success/failure accurately.

    Required parameters:
      -Profile <path>     Path to the client profile JSON.
      -Merge <name>       Merge name (e.g. dev-to-test) — must match profile.merges[].name.

    Optional:
      -RunsDir <path>     Where to write run logs. Default: ~/.tfvc-merge/runs.
      -PythonExe <path>   Python launcher (default: py -3). Use python.exe path for unattended.
      -NotifyVia <mcp|smtp>
                          Defaults to whatever the profile specifies, else 'mcp'.
                          For pure Task Scheduler runs (no Claude in the loop) use 'smtp'
                          and set SMTP_USER/SMTP_PASS/SMTP_FROM env vars.
      -Notify <email>     Override profile recipients (repeatable: pass an array).

    Logs:
      Stdout/stderr stream to a timestamped .log file alongside the run log dir.

    Example Task Scheduler action:
      Program/script: powershell.exe
      Arguments: -NoProfile -ExecutionPolicy Bypass -File
                 "C:\Users\ChadDalton\source\repos\cloud-beacon-skills\plugins\ab-code-review\skills\tfvc-merge\scripts\scheduled\run_merge.ps1"
                 -Profile "C:\path\to\clients\acme.json"
                 -Merge dev-to-test
                 -PythonExe "C:\Python313\python.exe"
#>

param(
    [Parameter(Mandatory = $true)] [string] $Profile,
    [Parameter(Mandatory = $true)] [string] $Merge,
    [string]   $RunsDir,
    [string]   $PythonExe,
    [string]   $NotifyVia,
    [string[]] $Notify
)

$ErrorActionPreference = 'Stop'

# Resolve script and orchestrator paths relative to this script's location so the
# scheduled task doesn't have to hardcode them beyond the .ps1 path itself.
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptsDir  = Split-Path -Parent $ScriptDir
$Orchestrator = Join-Path $ScriptsDir 'tfvc_merge.py'

if (-not (Test-Path -LiteralPath $Orchestrator)) {
    Write-Error "tfvc_merge.py not found at $Orchestrator"
    exit 1
}

# Log file under <RunsDir>/_logs (or ~/.tfvc-merge/runs/_logs if unspecified).
if (-not $RunsDir) {
    $RunsDir = Join-Path $HOME '.tfvc-merge\runs'
}
$LogsDir = Join-Path $RunsDir '_logs'
New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
$Stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$Slug   = ([IO.Path]::GetFileNameWithoutExtension($Profile)) + '.' + $Merge
$LogPath = Join-Path $LogsDir "$Slug.$Stamp.log"

# Choose interpreter — explicit override, else `py -3`, else `python.exe`.
$Args = @()
if ($PythonExe) {
    $Cmd = $PythonExe
} elseif (Get-Command 'py' -ErrorAction SilentlyContinue) {
    $Cmd = 'py'
    $Args += '-3'
} else {
    $Cmd = 'python'
}

$Args += @(
    $Orchestrator, 'run',
    '--profile', $Profile,
    '--merge',   $Merge
)
if ($RunsDir)    { $Args += @('--runs-dir', $RunsDir) }
if ($NotifyVia)  { $Args += @('--notify-via', $NotifyVia) }
if ($Notify) {
    foreach ($n in $Notify) { $Args += @('--notify', $n) }
}

"=== tfvc-merge scheduled run ===" | Out-File -FilePath $LogPath -Encoding utf8
"start:    $((Get-Date).ToString('o'))" | Out-File -FilePath $LogPath -Append -Encoding utf8
"command:  $Cmd $($Args -join ' ')"    | Out-File -FilePath $LogPath -Append -Encoding utf8
""                                     | Out-File -FilePath $LogPath -Append -Encoding utf8

# Stream stdout+stderr to the log; preserve the exit code for Task Scheduler.
& $Cmd @Args 2>&1 | Tee-Object -FilePath $LogPath -Append
$Code = $LASTEXITCODE

"" | Out-File -FilePath $LogPath -Append -Encoding utf8
"exit:     $Code"                          | Out-File -FilePath $LogPath -Append -Encoding utf8
"finished: $((Get-Date).ToString('o'))"   | Out-File -FilePath $LogPath -Append -Encoding utf8

exit $Code
