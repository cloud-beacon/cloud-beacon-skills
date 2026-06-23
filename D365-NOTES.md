# D365 F&O Development Notes

Shared knowledge that applies across the D365 F&O skills in this repo. Skills auto-trigger based on the user's intent (no slash command needed) — these notes capture the cross-cutting D365 facts every skill assumes.

## How the skills load

These are auto-triggering skills, not slash commands. Describe what you're trying to do in plain English and the matching skill loads on its own:

- "let's add a new VendInvoiceLog table" → `d365-new-table` fires
- "extend SalesTable with a custom field" → `d365-extend-table` fires
- "wrap SalesFormLetter.run with a CoC method" → `d365-extend-class` fires
- "create a data entity for that table" → `d365-new-entity` fires
- "the XML files won't open in VS" → `d365-fix-encoding` fires

## Available D365 skills

### Core Artifacts

| Skill | Description |
|-------|-------------|
| `d365-new-table` | Complete table with fields, indexes, form, menu item, and security |
| `d365-new-form` | Forms with SimpleList, SimpleListDetails, or custom patterns |
| `d365-new-class` | X++ classes with common patterns (data contracts, helpers, handlers) |
| `d365-new-enum` | Enumerations with values and extensibility options |
| `d365-new-edt` | Extended Data Types (String, Int, Real, DateTime, etc.) |

### Integration & APIs

| Skill | Description |
|-------|-------------|
| `d365-new-entity` | OData entities with DMF staging for data import/export |
| `d365-new-service` | Web services with service groups for external integration |
| `d365-batch-job` | SysOperation batch jobs (Controller → Contract → Service) |
| `d365-new-number-sequence` | Auto-numbering with module registration and wizard setup |

### Navigation & UI

| Skill | Description |
|-------|-------------|
| `d365-new-workspace` | Operational workspaces with tiles, lists, and links |
| `d365-new-menu` | Menus and menu extensions for navigation integration |

### Security & Features

| Skill | Description |
|-------|-------------|
| `d365-security` | Role → Duty → Privilege → Entry Point hierarchy |
| `d365-new-feature` | Feature toggle classes for Feature Management workspace |

### Extensions (Modify Base Objects)

| Skill | Description |
|-------|-------------|
| `d365-extend-table` | Add fields, indexes, relations to base tables |
| `d365-extend-form` | Add controls, data sources to base forms |
| `d365-extend-class` | Chain of Command for base classes |
| `d365-extend-enum` | Add values to extensible base enums |
| `d365-extend-edt` | Modify properties of base EDTs |

### Documentation & Utilities

| Skill | Description |
|-------|-------------|
| `d365-create-docs` | Generate Architecture / User / Functional guides for a module |
| `d365-fix-encoding` | Diagnose and fix CRLF line ending issues |

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

The `d365-fix-encoding` skill auto-loads when you mention encoding issues or finalize newly-written D365 XML files.

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

A typical end-to-end feature build hits these skills in order — each loads automatically as you describe the step:

```
1. d365-new-enum             → Status enum
2. d365-new-edt              → Custom EDTs
3. d365-new-table            → Table with fields
4. d365-new-entity           → Data entity for OData/DMF
5. d365-new-form             → Form (or included in table skill)
6. d365-new-menu             → Navigation entry
7. d365-security             → Privileges, duties, roles
8. d365-new-feature          → (Optional) Feature Management gate
9. d365-fix-encoding         → Normalize CRLF on all written files
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

### Skill Not Loading
- Verify `SKILL.md` is at `.claude/skills/<name>/SKILL.md` (not in `.claude/commands/`)
- Confirm the YAML frontmatter has `name` and `description` fields
- Restart Claude Code if recently installed
- If a skill should be firing but isn't, describe your intent more concretely — skills match on description keywords

### Build Errors After Creating Files
1. Let `d365-fix-encoding` normalize line endings (mention encoding/CRLF and it loads)
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
