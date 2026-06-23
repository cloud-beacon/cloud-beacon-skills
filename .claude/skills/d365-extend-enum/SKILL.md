---
name: d365-extend-enum
description: Extend an existing D365 Finance & Operations enum by adding new values, when the base enum is IsExtensible. Use whenever the user asks to extend a base enum, add new values to an existing enum (e.g. SalesStatus, InventTransType), or create an enum extension. Do not use for new enums — see d365-new-enum for that.
---

# D365 F&O: Extend Existing Enum

You are helping extend an existing enumeration in D365 Finance & Operations using enum extensions. This adds new values to a base enum WITHOUT modifying the original.

**Important:** This skill is for extending BASE objects (Microsoft or other ISV enums). To create a NEW enum in your model, use `/d365-new-enum` instead.

**Prerequisite:** The base enum must have `IsExtensible = true`. Standard Microsoft enums are typically extensible, but some are not.

## Gather Requirements

Ask the user for:
1. **Base enum** to extend (e.g., `SalesStatus`, `InventTransType`)
2. **New values** to add (name, label, integer value)
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
<BaseEnumName>.<YourPrefix>Extension
```

Examples:
- `SalesStatus.cbExtension`
- `InventTransType.cbExtension`
- `ModuleInventPurchSales.myExtension`

## AxEnumExtension Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEnumExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>SalesStatus.cbExtension</Name>
	<EnumValues>
		<AxEnumValue>
			<Name>cbPLMPending</Name>
			<Label>@CloudBeacon:PLMPending</Label>
			<Value>100</Value>
		</AxEnumValue>
		<AxEnumValue>
			<Name>cbPLMSynced</Name>
			<Label>@CloudBeacon:PLMSynced</Label>
			<Value>101</Value>
		</AxEnumValue>
	</EnumValues>
</AxEnumExtension>
```

## Key Rules for Enum Extensions

### Value Selection

1. **Use high values** (100+) to avoid conflicts with base enum values
2. **Leave gaps** between your values for future additions
3. **Values must be unique** across base enum + all extensions
4. **Document your value ranges** in CLAUDE.md or comments

Recommended value ranges:
```
Base enum:      0-49
Future base:    50-99
Extension 1:    100-149
Extension 2:    150-199
Extension 3:    200-249
```

### Checking If Enum Is Extensible

Before extending, verify the enum allows extensions:

1. **In Visual Studio AOT:** Check `IsExtensible` property on the enum
2. **In X++:** `DictEnum::isExtensible(enumNum(EnumName))`

If the enum is NOT extensible, you cannot add values. Consider:
- Creating a new enum in your model
- Using a different approach (lookup table, configuration)
- Requesting Microsoft make it extensible (via Ideas portal)

## Adding Multiple Values

```xml
<EnumValues>
	<AxEnumValue>
		<Name>cbStatusA</Name>
		<Label>@CloudBeacon:StatusALabel</Label>
		<Value>100</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>cbStatusB</Name>
		<Label>@CloudBeacon:StatusBLabel</Label>
		<Value>101</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>cbStatusC</Name>
		<Label>@CloudBeacon:StatusCLabel</Label>
		<Value>102</Value>
	</AxEnumValue>
</EnumValues>
```

## Using Extended Enum Values in X++

```xpp
// Reference extended enum value like any other
SalesTable salesTable;
salesTable.SalesStatus = SalesStatus::cbPLMPending;

// In switch statements
switch (salesTable.SalesStatus)
{
    case SalesStatus::None:
        // Handle None
        break;
    case SalesStatus::Backorder:
        // Handle Backorder
        break;
    case SalesStatus::cbPLMPending:
        // Handle custom value
        this.cbHandlePLMPending();
        break;
    case SalesStatus::cbPLMSynced:
        // Handle custom value
        this.cbHandlePLMSynced();
        break;
}

// In if statements
if (salesTable.SalesStatus == SalesStatus::cbPLMPending)
{
    // Handle PLM pending
}
```

## Handling Extended Values in Base Code

Since base code doesn't know about your extended values, you may need to handle them via Chain of Command:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>SalesTableType_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension to handle custom SalesStatus values.
/// </summary>
[ExtensionOf(classStr(SalesTableType))]
final class SalesTableType_cbExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>canInvoiceBeUpdated</Name>
				<Source><![CDATA[
    protected boolean canInvoiceBeUpdated()
    {
        SalesTable salesTable = this.salesTable();

        // Handle custom status values
        if (salesTable.SalesStatus == SalesStatus::cbPLMPending)
        {
            return false; // Block invoice while PLM sync pending
        }

        return next canInvoiceBeUpdated();
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Common Enums to Extend

| Enum | Purpose | Typical Extensions |
|------|---------|-------------------|
| `ModuleInventPurchSales` | Module context | Custom module types |
| `ItemType` | Product types | Custom product classifications |
| `SalesStatus` | Sales order status | Custom workflow states |
| `PurchStatus` | Purchase order status | Custom workflow states |
| `InventTransType` | Inventory transaction types | Custom transaction types |
| `WHSWorkType` | Warehouse work types | Custom work operations |

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxEnumExtension\SalesStatus.cbExtension.xml">
  <SubType>Content</SubType>
  <Name>SalesStatus.cbExtension</Name>
  <Link>Enum Extensions\SalesStatus.cbExtension</Link>
</Content>
```

## Labels

Add to your label file:

```
PLMPending=PLM Sync Pending
 ;Extended enum value label
PLMSynced=PLM Synced
 ;Extended enum value label
```

## Debugging Enum Extension Issues

### Value Conflicts

If you get errors about duplicate values:
1. Check all extensions of the same enum
2. Verify your values don't overlap with base or other extensions
3. Use `DictEnum` to enumerate all values at runtime:

```xpp
DictEnum dictEnum = new DictEnum(enumNum(SalesStatus));
for (int i = 0; i < dictEnum.values(); i++)
{
    info(strFmt("Value: %1, Name: %2, Label: %3",
        dictEnum.index2Value(i),
        dictEnum.index2Name(i),
        dictEnum.index2Label(i)));
}
```

### Extension Not Appearing

1. Verify base enum has `IsExtensible = true`
2. Check CRLF line endings
3. Rebuild the model
4. Restart Visual Studio / IIS

## Checklist

- [ ] Verify base enum is extensible
- [ ] Create AxEnumExtension with proper naming
- [ ] Use high integer values (100+) for new entries
- [ ] Add labels to label file
- [ ] Normalize XML file to CRLF
- [ ] Add to .rnrproj file
- [ ] Create CoC extensions to handle custom values in base code
- [ ] Build and verify values appear in AOT
- [ ] Test enum values work correctly at runtime
