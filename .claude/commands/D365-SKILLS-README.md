# D365 F&O Development Skills for Claude Code

This collection of skills helps developers create D365 Finance & Operations artifacts using Claude Code. Each skill provides templates, guidance, and best practices learned from real-world D365 development.

## Quick Start

1. Copy the `d365-*.md` files to your project's `.claude/commands/` folder
2. In Claude Code, type `/d365-` to see all available skills
3. Invoke a skill like `/d365-new-table` and follow the prompts

## Available Skills

### Core Artifacts

| Skill | Command | Description |
|-------|---------|-------------|
| **New Table** | `/d365-new-table` | Complete table with fields, indexes, form, menu item, and security |
| **New Form** | `/d365-new-form` | Forms with SimpleList, SimpleListDetails, or custom patterns |
| **New Class** | `/d365-new-class` | X++ classes with common patterns (data contracts, helpers, handlers) |
| **New Enum** | `/d365-new-enum` | Enumerations with values and extensibility options |
| **New EDT** | `/d365-new-edt` | Extended Data Types (String, Int, Real, DateTime, etc.) |

### Integration & APIs

| Skill | Command | Description |
|-------|---------|-------------|
| **Data Entity** | `/d365-new-entity` | OData entities with DMF staging for data import/export |
| **Service** | `/d365-new-service` | Web services with service groups for external integration |
| **Batch Job** | `/d365-batch-job` | SysOperation batch jobs (Controller → Contract → Service) |
| **Number Sequence** | `/d365-new-number-sequence` | Auto-numbering with module registration and wizard setup |

### Navigation & UI

| Skill | Command | Description |
|-------|---------|-------------|
| **Workspace** | `/d365-new-workspace` | Operational workspaces with tiles, lists, and links |
| **Menu** | `/d365-new-menu` | Menus and menu extensions for navigation integration |

### Security & Features

| Skill | Command | Description |
|-------|---------|-------------|
| **Security Model** | `/d365-security` | Role → Duty → Privilege → Entry Point hierarchy |
| **Feature Management** | `/d365-new-feature` | Feature toggle classes for Feature Management workspace |

### Extensions (Modify Base Objects)

| Skill | Command | Description |
|-------|---------|-------------|
| **Extend Table** | `/d365-extend-table` | Add fields, indexes, relations to base tables |
| **Extend Form** | `/d365-extend-form` | Add controls, data sources to base forms |
| **Extend Class** | `/d365-extend-class` | Chain of Command for base classes |
| **Extend Enum** | `/d365-extend-enum` | Add values to extensible base enums |
| **Extend EDT** | `/d365-extend-edt` | Modify properties of base EDTs |

### Utilities

| Skill | Command | Description |
|-------|---------|-------------|
| **Fix Encoding** | `/d365-fix-encoding` | Diagnose and fix CRLF line ending issues |

## Critical Knowledge

### New vs Extend

- **`/d365-new-*` skills:** Create NEW objects in YOUR model
- **`/d365-extend-*` skills:** Extend BASE objects (Microsoft/ISV) via extensions

**Never overlay base objects.** Always use extensions when modifying standard D365 functionality.

### File Encoding (CRLF)

**All D365 XML files MUST use CRLF line endings** (Windows `\r\n`). Files with LF-only endings will:
- Fail to open in Visual Studio
- Cause "file not found" or metadata errors during build
- Be silently ignored by D365 toolchain

Claude Code's Write tool uses LF by default. **Always run CRLF normalization after creating files:**

```powershell
Get-ChildItem -Path ".\AxClass",".\AxTable",".\AxForm" -Recurse -Filter "*.xml" | ForEach-Object {
    $c = [System.IO.File]::ReadAllText($_.FullName)
    $c = $c.Replace("`r`n", "`n").Replace("`n", "`r`n")
    [System.IO.File]::WriteAllText($_.FullName, $c, [System.Text.UTF8Encoding]::new($false))
}
```

Use `/d365-fix-encoding` for detailed guidance.

### Visual Studio Project File (.rnrproj)

After creating artifacts, add them to your Visual Studio project file:

```xml
<Content Include="AxClass\MyClass.xml">
  <SubType>Content</SubType>
  <Name>MyClass</Name>
  <Link>Classes\MyClass</Link>
</Content>
```

**Link folder names by artifact type:**
- Classes: `Classes\`
- Tables: `Tables\`
- Forms: `Forms\`
- Enums: `Base Enums\`
- EDTs: `Extended Data Types\`
- Data Entities: `Data Entities\`
- Display Menu Items: `Display Menu Items\`
- Action Menu Items: `Action Menu Items\`
- Security Privileges: `Security Privileges\`
- Security Duties: `Security Duties\`
- Security Roles: `Security Roles\`
- Menus: `Menus\`
- Menu Extensions: `Menu Extensions\`
- Tiles: `Tiles\`
- Services: `Services\`
- Service Groups: `Service Groups\`

### Common Gotchas

| Issue | Solution |
|-------|----------|
| "Cannot create abstract class" for EDTs | Add `i:type="AxEdtString"` (or appropriate type) to root element |
| Feature not appearing in Feature Management | Class must be `internal final class` |
| Form integer control errors | Use `AxFormIntegerControl` not `AxFormIntControl` |
| XML elements ignored | Check alphabetical order (DataContract serialization) |
| Polymorphic fields | Add `xmlns=""` alongside `i:type` attribute |

## Workflow Example

Here's a typical workflow for adding a new feature:

```
1. /d365-new-enum        → Create status enum
2. /d365-new-edt         → Create custom EDTs
3. /d365-new-table       → Create table with fields
4. /d365-new-entity      → Create data entity for OData/DMF
5. /d365-new-form        → Create form (or included in table skill)
6. /d365-new-menu        → Add to navigation
7. /d365-security        → Create privileges, duties, roles
8. /d365-new-feature     → (Optional) Gate behind Feature Management
9. /d365-fix-encoding    → Normalize all files to CRLF
```

## Labels

All skills reference labels using `@LabelFileId:key` syntax. Add labels to your label file:

```
Location: AxLabelFile/LabelResources/en-US/<LabelFileId>.en-US.label.txt

Format:
myLabelKey=The display text
 ;Comment describing this label
```

**Note:** Space before semicolon on comment line is required.

## Environment Requirements

- **Windows Server** with Visual Studio
- **D365 F&O** development environment
- **PowerShell** for scripting (Python/Node.js typically not available)
- Build via Visual Studio or `xppc.exe`/MSBuild

## Extending These Skills

These skills are markdown files that Claude Code loads as context. You can:

1. **Customize templates** to match your naming conventions
2. **Add company-specific patterns** (prefixes, label file IDs)
3. **Include additional gotchas** you discover
4. **Create new skills** for patterns specific to your project

## Troubleshooting

### Skill Not Found
- Verify `.md` file is in `.claude/commands/` folder
- Check filename matches `d365-*.md` pattern
- Restart Claude Code if recently added

### Build Errors After Creating Files
1. Run `/d365-fix-encoding` to normalize line endings
2. Verify XML is well-formed (check for missing closing tags)
3. Check `i:type` and `xmlns` attributes on polymorphic elements
4. Verify artifacts are added to `.rnrproj` file

### Forms/Tables Not Appearing in AOT
1. Check file encoding (CRLF)
2. Verify file is in correct folder (e.g., `AxTable\` not `AxClass\`)
3. Clean and rebuild the model
4. Check for XML parsing errors in build output

## Contributing

Found an issue or have an improvement? These skills evolved from real D365 development experience. Update the skill files and share with your team.

---

*These skills were created based on D365 F&O 10.0.x development patterns.*
