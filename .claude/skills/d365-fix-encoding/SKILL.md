---
name: d365-fix-encoding
description: Fix CRLF line endings on D365 Finance & Operations metadata XML files. Use whenever the user reports D365 / X++ XML files failing to open in Visual Studio, metadata parsing errors, files silently ignored by the D365 toolchain, or mentions LF / Unix line endings on AxTable / AxForm / AxClass / other D365 metadata. Also trigger when finalizing newly-written D365 XML files to normalize encoding.
---

# D365 F&O: Fix File Encoding (CRLF)

You are helping fix file encoding issues in D365 Finance & Operations. This is a CRITICAL issue that causes files to become unreadable by Visual Studio and D365 tooling.

## The Problem

**All D365 F&O metadata XML files MUST use CRLF line endings** (Windows `\r\n`).

Files with LF-only line endings (Unix-style `\n`) will:
- Fail to open correctly in Visual Studio
- Cause metadata parsing errors
- Result in "file not found" or corruption errors during build
- Be silently ignored by the D365 toolchain

This commonly happens when:
- AI coding assistants write files (Claude Code's Write tool uses LF by default)
- Files are transferred from Unix/Mac systems
- Git's autocrlf setting converts line endings
- Editors are configured for Unix line endings

## Quick Fix: Single File

```powershell
$filePath = "K:\AosService\PackagesLocalDirectory\MyPackage\MyModel\AxClass\MyClass.xml"
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

**How it works:**
1. First replaces all CRLF with LF (normalizes mixed endings)
2. Then replaces all LF with CRLF (ensures Windows endings)
3. Writes with UTF-8 encoding without BOM

## Quick Fix: Entire Model/Folder

```powershell
$modelPath = "K:\AosService\PackagesLocalDirectory\MyPackage\MyModel"

Get-ChildItem -Path $modelPath -Recurse -Include "*.xml","*.label.txt" | ForEach-Object {
    $content = [System.IO.File]::ReadAllText($_.FullName)
    $content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
    [System.IO.File]::WriteAllText($_.FullName, $content, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Fixed: $($_.FullName)"
}
```

## Reusable PowerShell Script

Create a file `fix-crlf.ps1`:

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$Path,

    [switch]$Recurse,

    [string[]]$Include = @("*.xml", "*.label.txt")
)

function Fix-LineEndings {
    param([string]$FilePath)

    $content = [System.IO.File]::ReadAllText($FilePath)
    $originalLength = $content.Length

    # Normalize to LF first, then convert to CRLF
    $content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")

    if ($content.Length -ne $originalLength) {
        [System.IO.File]::WriteAllText($FilePath, $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "Fixed: $FilePath" -ForegroundColor Green
        return $true
    } else {
        Write-Host "OK: $FilePath" -ForegroundColor Gray
        return $false
    }
}

$files = if ($Recurse) {
    Get-ChildItem -Path $Path -Recurse -Include $Include
} else {
    Get-ChildItem -Path $Path -Include $Include
}

$fixedCount = 0
$totalCount = 0

foreach ($file in $files) {
    $totalCount++
    if (Fix-LineEndings -FilePath $file.FullName) {
        $fixedCount++
    }
}

Write-Host "`nSummary: Fixed $fixedCount of $totalCount files" -ForegroundColor Cyan
```

**Usage:**

```powershell
# Single file
powershell.exe -ExecutionPolicy Bypass -File fix-crlf.ps1 -Path ".\AxClass\MyClass.xml"

# Single folder (non-recursive)
powershell.exe -ExecutionPolicy Bypass -File fix-crlf.ps1 -Path ".\AxClass"

# Entire model (recursive)
powershell.exe -ExecutionPolicy Bypass -File fix-crlf.ps1 -Path "K:\AosService\PackagesLocalDirectory\MyPackage\MyModel" -Recurse

# Custom file types
powershell.exe -ExecutionPolicy Bypass -File fix-crlf.ps1 -Path ".\AxLabelFile" -Recurse -Include "*.txt"
```

## Check File Encoding Without Fixing

To inspect files without modifying them:

```powershell
$modelPath = "K:\AosService\PackagesLocalDirectory\MyPackage\MyModel"

Get-ChildItem -Path $modelPath -Recurse -Include "*.xml" | ForEach-Object {
    $content = [System.IO.File]::ReadAllText($_.FullName)
    $hasCRLF = $content.Contains("`r`n")
    $hasLFOnly = $content.Contains("`n") -and -not $hasCRLF

    if ($hasLFOnly) {
        Write-Host "BAD (LF): $($_.FullName)" -ForegroundColor Red
    } elseif ($hasCRLF) {
        Write-Host "OK (CRLF): $($_.FullName)" -ForegroundColor Green
    } else {
        Write-Host "NO NEWLINES: $($_.FullName)" -ForegroundColor Yellow
    }
}
```

## Files That Need CRLF

All D365 metadata files require CRLF:

| Folder | File Types |
|--------|------------|
| `AxClass\` | `*.xml` |
| `AxTable\` | `*.xml` |
| `AxForm\` | `*.xml` |
| `AxEnum\` | `*.xml` |
| `AxEdt\` | `*.xml` |
| `AxDataEntityView\` | `*.xml` |
| `AxMenuItemDisplay\` | `*.xml` |
| `AxMenuItemAction\` | `*.xml` |
| `AxMenu\` | `*.xml` |
| `AxMenuExtension\` | `*.xml` |
| `AxSecurityPrivilege\` | `*.xml` |
| `AxSecurityDuty\` | `*.xml` |
| `AxSecurityRole\` | `*.xml` |
| `AxLabelFile\` | `*.xml` |
| `AxLabelFile\LabelResources\` | `*.label.txt` |
| `AxQuery\` | `*.xml` |
| `AxView\` | `*.xml` |
| `AxTile\` | `*.xml` |
| `AxResource\` | `*.xml` |

## Preventing the Problem

### After Using AI Tools

Always run CRLF normalization after Claude Code (or other AI tools) writes or edits XML files:

```powershell
# After creating/editing files in MyModel
Get-ChildItem -Path "K:\AosService\PackagesLocalDirectory\MyPackage\MyModel" -Recurse -Include "*.xml","*.label.txt" | ForEach-Object {
    $c = [System.IO.File]::ReadAllText($_.FullName)
    $c = $c.Replace("`r`n", "`n").Replace("`n", "`r`n")
    [System.IO.File]::WriteAllText($_.FullName, $c, [System.Text.UTF8Encoding]::new($false))
}
```

### Git Configuration

If using Git, configure it to preserve CRLF:

```bash
# Repository-level .gitattributes
*.xml text eol=crlf
*.label.txt text eol=crlf
```

Or global setting (not recommended for cross-platform teams):
```bash
git config --global core.autocrlf false
```

## Symptoms of CRLF Issues

If you see these problems, check line endings:

1. **"Could not find file" errors** when file clearly exists
2. **"Root element is missing" XML errors**
3. **Files appear empty or corrupted in Visual Studio**
4. **Build errors referencing specific XML files**
5. **Metadata not recognized** (forms, tables not found)
6. **Feature Management class not appearing** (MEF discovery fails)

## Recovery Steps

If you've already built with broken files:

1. **Fix line endings** using scripts above
2. **Clean XppMetadata folder** (optional but recommended):
   ```powershell
   Remove-Item "K:\AosService\PackagesLocalDirectory\MyPackage\XppMetadata" -Recurse -Force
   ```
3. **Rebuild** the model in Visual Studio (full rebuild, not incremental)
4. **Restart IIS** (`iisreset`)

## Checklist After Creating Files

- [ ] Run CRLF normalization on all new/edited XML files
- [ ] Run CRLF normalization on label.txt files
- [ ] Verify files open correctly in Visual Studio
- [ ] Build succeeds without metadata errors
- [ ] Forms/tables/classes appear in AOT explorer
