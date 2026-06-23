---
name: d365-extend-edt
description: Extend an existing D365 Finance & Operations EDT by modifying allowed properties (Label, HelpText, StringSize, FormHelp). Use whenever the user asks to extend an existing EDT, change properties on a base EDT (e.g. Description, ItemId), or create an EDT extension. Do not use for new EDTs — see d365-new-edt for that.
---

# D365 F&O: Extend Existing EDT

You are helping extend an existing Extended Data Type (EDT) in D365 Finance & Operations using EDT extensions. This modifies properties of a base EDT WITHOUT modifying the original.

**Important:** This skill is for extending BASE objects (Microsoft or other ISV EDTs). To create a NEW EDT in your model, use `/d365-new-edt` instead.

**Note:** EDT extensions have LIMITED capabilities compared to other extensions. You can only modify certain properties, not add new ones.

## Gather Requirements

Ask the user for:
1. **Base EDT** to extend (e.g., `Description`, `ItemId`)
2. **Properties to modify** (Label, HelpText, StringSize, FormHelp, etc.)
3. **Extension naming:** Check CLAUDE.md for model prefix

Refer to **CLAUDE.md** for:
- Model name and naming prefix
- VS project file path
- Label file ID

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Extension Naming Convention

```
<BaseEdtName>.<YourPrefix>Extension
```

Examples:
- `Description.cbExtension`
- `ItemId.cbExtension`
- `CustAccount.myExtension`

## AxEdtExtension Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdtExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>Description.cbExtension</Name>
	<PropertyModifications>
		<AxEdtExtensionPropertyModification>
			<Name>Label</Name>
			<Value>@CloudBeacon:ExtendedDescriptionLabel</Value>
		</AxEdtExtensionPropertyModification>
		<AxEdtExtensionPropertyModification>
			<Name>HelpText</Name>
			<Value>@CloudBeacon:ExtendedDescriptionHelp</Value>
		</AxEdtExtensionPropertyModification>
	</PropertyModifications>
</AxEdtExtension>
```

## Properties That CAN Be Modified

| Property | Description | Applicable To |
|----------|-------------|---------------|
| `Label` | Display label | All EDTs |
| `HelpText` | Tooltip/help text | All EDTs |
| `FormHelp` | Form opened for lookup | All EDTs |
| `DisplayLength` | Display width | String, Int, Real |
| `StringSize` | Maximum length | String EDTs only |
| `ReferenceTable` | Lookup table | All EDTs |

## Properties That CANNOT Be Modified

- **Base type** (String, Int, Real, etc.)
- **Extends** (parent EDT)
- **Array element count**
- **Enum type** (for enum EDTs)

If you need to change these, create a NEW EDT instead.

## Common Extension Scenarios

### Extending String Size

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdtExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>Description.cbExtension</Name>
	<PropertyModifications>
		<AxEdtExtensionPropertyModification>
			<Name>StringSize</Name>
			<Value>120</Value>
		</AxEdtExtensionPropertyModification>
	</PropertyModifications>
</AxEdtExtension>
```

**Warning:** Increasing StringSize affects database column size. This requires a database sync and may fail if existing data exceeds the original size.

### Adding Custom Lookup

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdtExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>ItemId.cbExtension</Name>
	<PropertyModifications>
		<AxEdtExtensionPropertyModification>
			<Name>FormHelp</Name>
			<Value>cbItemLookup</Value>
		</AxEdtExtensionPropertyModification>
	</PropertyModifications>
</AxEdtExtension>
```

### Changing Reference Table

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdtExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>cbCustomId.cbExtension</Name>
	<PropertyModifications>
		<AxEdtExtensionPropertyModification>
			<Name>ReferenceTable</Name>
			<Value>cbCustomTable</Value>
		</AxEdtExtensionPropertyModification>
	</PropertyModifications>
</AxEdtExtension>
```

### Multiple Property Modifications

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdtExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>Description.cbExtension</Name>
	<PropertyModifications>
		<AxEdtExtensionPropertyModification>
			<Name>Label</Name>
			<Value>@CloudBeacon:EnhancedDescription</Value>
		</AxEdtExtensionPropertyModification>
		<AxEdtExtensionPropertyModification>
			<Name>HelpText</Name>
			<Value>@CloudBeacon:EnhancedDescriptionHelp</Value>
		</AxEdtExtensionPropertyModification>
		<AxEdtExtensionPropertyModification>
			<Name>StringSize</Name>
			<Value>100</Value>
		</AxEdtExtensionPropertyModification>
		<AxEdtExtensionPropertyModification>
			<Name>DisplayLength</Name>
			<Value>50</Value>
		</AxEdtExtensionPropertyModification>
	</PropertyModifications>
</AxEdtExtension>
```

## When to Use EDT Extension vs New EDT

### Use EDT Extension When:
- Changing labels/help text for localization
- Increasing string size for existing EDT
- Adding custom lookup form
- Modifying display properties

### Create New EDT When:
- Need different base type
- Need to extend a different parent EDT
- Need fundamentally different behavior
- Base EDT changes would break other functionality

## Alternative: Create Derived EDT

Instead of extending, you can create a new EDT that extends the base:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtString">
	<Name>cbEnhancedDescription</Name>
	<Extends>Description</Extends>
	<Label>@CloudBeacon:EnhancedDescription</Label>
	<HelpText>@CloudBeacon:EnhancedDescriptionHelp</HelpText>
	<StringSize>120</StringSize>
</AxEdt>
```

This creates a NEW EDT that inherits from Description but has custom properties. Use this on new fields in your tables rather than modifying the base EDT.

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxEdtExtension\Description.cbExtension.xml">
  <SubType>Content</SubType>
  <Name>Description.cbExtension</Name>
  <Link>EDT Extensions\Description.cbExtension</Link>
</Content>
```

## Labels

Add to your label file:

```
ExtendedDescriptionLabel=Enhanced Description
 ;Extended EDT label
ExtendedDescriptionHelp=Enter an enhanced description with additional details
 ;Extended EDT help text
```

## Impact Considerations

### StringSize Changes
- **Increasing:** Safe, but requires DB sync. Large increases may impact performance.
- **Decreasing:** DANGEROUS - may truncate existing data. Avoid in production.

### Label/HelpText Changes
- Affects ALL fields using this EDT across the system
- Consider if this is really what you want
- May affect other ISV modules using the same EDT

### FormHelp Changes
- Changes lookup behavior for ALL fields using this EDT
- May break expected functionality in other areas

## Best Practice: Prefer Derived EDTs

In most cases, creating a **derived EDT** (new EDT that extends the base) is safer than extending the base EDT directly:

1. Your changes only affect fields using YOUR EDT
2. No risk of breaking other modules
3. Clear separation of customizations
4. Easier to track what you've changed

Reserve EDT extensions for cases where you truly need to change behavior across ALL usages of the base EDT.

## Checklist

- [ ] Confirm EDT extension is the right approach (vs derived EDT)
- [ ] Identify properties to modify
- [ ] Create AxEdtExtension with proper naming
- [ ] Add property modifications
- [ ] Consider impact on all fields using this EDT
- [ ] Add labels to label file
- [ ] Normalize XML file to CRLF
- [ ] Add to .rnrproj file
- [ ] Sync database (if StringSize changed)
- [ ] Test affected forms and reports
