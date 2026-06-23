# Cloud Beacon: PostToolUse hook
# Normalizes line endings to CRLF on D365 F&O metadata XML files immediately
# after Claude writes or edits them. Silently no-ops for any non-D365 file.
#
# Wired up by .claude/settings.json.
# Reads the Claude Code hook payload from stdin (JSON on a single line).

$ErrorActionPreference = 'Stop'

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    $payload = $raw | ConvertFrom-Json
    $path = $payload.tool_input.file_path
    if (-not $path) { exit 0 }

    # Match D365 metadata XML: any path segment of the form Ax<ArtifactType>\<file>.xml
    # e.g. ...\AxTable\MyTable.xml, ...\AxClass\MyClass.xml, ...\AxFormExtension\Foo.xml
    if ($path -notmatch '[\\/]Ax[A-Z][A-Za-z]+[\\/][^\\/]+\.xml$') { exit 0 }
    if (-not (Test-Path -LiteralPath $path)) { exit 0 }

    $content = [System.IO.File]::ReadAllText($path)
    $normalized = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")

    if ($content -ne $normalized) {
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($path, $normalized, $utf8NoBom)
        # Hook stdout is surfaced to Claude as context — useful trail.
        Write-Output "d365-normalize-crlf: normalized $path"
    }
    exit 0
}
catch {
    # Never block tool use because of the hook — log and exit clean.
    Write-Error "d365-normalize-crlf failed: $_"
    exit 0
}
