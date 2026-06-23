# D365 F&O: Extend Existing Table

You are helping extend an existing table in D365 Finance & Operations using table extensions. This adds fields, indexes, field groups, relations, or methods to a base table WITHOUT modifying the original.

**Important:** This skill is for extending BASE objects (Microsoft or other ISV tables). To create a NEW table in your model, use `/d365-new-table` instead.

## Gather Requirements

Ask the user for:
1. **Base table** to extend (e.g., `InventTable`, `SalesTable`)
2. **What to add:** Fields, indexes, field groups, relations, and/or methods
3. **For fields:** Name, type, EDT, mandatory, etc.
4. **Extension naming:** Check CLAUDE.md for model prefix

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
<BaseTableName>.<YourPrefix>Extension
```

Examples:
- `InventTable.cbExtension`
- `SalesTable.cbExtension`
- `CustTable.myExtension`

## AxTableExtension Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTableExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>InventTable.cbExtension</Name>
	<FieldGroups />
	<Fields />
	<Indexes />
	<Mappings />
	<PropertyModifications />
	<Relations />
</AxTableExtension>
```

## Adding Fields

Add fields inside the `<Fields>` element:

```xml
<Fields>
	<AxTableField xmlns="" i:type="AxTableFieldString">
		<Name>cbCustomField</Name>
		<ExtendedDataType>Description</ExtendedDataType>
		<Label>@LabelFile:cbCustomFieldLabel</Label>
	</AxTableField>
	<AxTableField xmlns="" i:type="AxTableFieldEnum">
		<Name>cbStatus</Name>
		<EnumType>cbMyStatusEnum</EnumType>
		<Label>@LabelFile:cbStatusLabel</Label>
	</AxTableField>
	<AxTableField xmlns="" i:type="AxTableFieldInt64">
		<Name>cbRelatedRecId</Name>
		<ExtendedDataType>RefRecId</ExtendedDataType>
		<Label>@LabelFile:cbRelatedRecIdLabel</Label>
	</AxTableField>
</Fields>
```

### Field Types

| Type | i:type | Key Property |
|------|--------|--------------|
| String | `AxTableFieldString` | `ExtendedDataType` |
| Integer | `AxTableFieldInt` | `ExtendedDataType` |
| Real | `AxTableFieldReal` | `ExtendedDataType` |
| Int64 | `AxTableFieldInt64` | `ExtendedDataType` |
| Enum | `AxTableFieldEnum` | `EnumType` |
| Date | `AxTableFieldDate` | `ExtendedDataType` |
| DateTime | `AxTableFieldUtcDateTime` | `ExtendedDataType` |
| Guid | `AxTableFieldGuid` | `ExtendedDataType` |
| Container | `AxTableFieldContainer` | — |

**Critical:** Field elements require `xmlns=""` alongside the `i:type` attribute.

## Adding Field Groups

Extend or create field groups:

```xml
<FieldGroups>
	<AxTableFieldGroup>
		<Name>cbCustomGroup</Name>
		<Label>@LabelFile:cbCustomGroupLabel</Label>
		<Fields>
			<AxTableFieldGroupField>
				<DataField>cbCustomField</DataField>
			</AxTableFieldGroupField>
			<AxTableFieldGroupField>
				<DataField>cbStatus</DataField>
			</AxTableFieldGroupField>
		</Fields>
	</AxTableFieldGroup>
</FieldGroups>
```

### Adding Fields to Existing Field Groups

To add your fields to an existing field group (like `AutoLookup`), you need to use field group extensions:

```xml
<FieldGroups>
	<AxTableFieldGroup>
		<Name>AutoLookup</Name>
		<Fields>
			<AxTableFieldGroupField>
				<DataField>cbCustomField</DataField>
			</AxTableFieldGroupField>
		</Fields>
	</AxTableFieldGroup>
</FieldGroups>
```

## Adding Indexes

```xml
<Indexes>
	<AxTableIndex>
		<Name>cbCustomIdx</Name>
		<AllowDuplicates>No</AllowDuplicates>
		<Fields>
			<AxTableIndexField>
				<DataField>cbCustomField</DataField>
			</AxTableIndexField>
		</Fields>
	</AxTableIndex>
</Indexes>
```

## Adding Relations

```xml
<Relations>
	<AxTableRelation>
		<Name>cbRelatedTable</Name>
		<RelatedTable>cbRelatedTable</RelatedTable>
		<Constraints>
			<AxTableRelationConstraint xmlns="" i:type="AxTableRelationConstraintField">
				<Name>RecIdConstraint</Name>
				<Field>cbRelatedRecId</Field>
				<RelatedField>RecId</RelatedField>
			</AxTableRelationConstraint>
		</Constraints>
	</AxTableRelation>
</Relations>
```

## Adding Methods (Chain of Command)

Methods are NOT added in the table extension XML. Instead, create a separate **extension class** using Chain of Command:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>InventTable_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension class for InventTable.
/// </summary>
[ExtensionOf(tableStr(InventTable))]
final class InventTable_cbExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>validateWrite</Name>
				<Source><![CDATA[
    public boolean validateWrite()
    {
        boolean ret = next validateWrite();

        if (ret)
        {
            // Custom validation
            if (!this.cbCustomField)
            {
                ret = checkFailed("@LabelFile:cbCustomFieldRequired");
            }
        }

        return ret;
    }

]]></Source>
			</Method>
			<Method>
				<Name>cbCustomMethod</Name>
				<Source><![CDATA[
    /// <summary>
    /// Custom method added to the table.
    /// </summary>
    /// <returns>Calculated value.</returns>
    public str cbCustomMethod()
    {
        return strFmt("%1 - %2", this.ItemId, this.cbCustomField);
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

**Key points:**
- Use `[ExtensionOf(tableStr(TableName))]` attribute
- Class must be `final`
- Use `next` keyword to call base implementation
- New methods can be added directly (no `next` needed)
- Access table fields via `this.FieldName`

## Complete Table Extension Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTableExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>InventTable.cbExtension</Name>
	<FieldGroups>
		<AxTableFieldGroup>
			<Name>cbPLMGroup</Name>
			<Label>@CloudBeacon:PLMFields</Label>
			<Fields>
				<AxTableFieldGroupField>
					<DataField>cbPLMStatus</DataField>
				</AxTableFieldGroupField>
				<AxTableFieldGroupField>
					<DataField>cbLastSyncDateTime</DataField>
				</AxTableFieldGroupField>
			</Fields>
		</AxTableFieldGroup>
	</FieldGroups>
	<Fields>
		<AxTableField xmlns="" i:type="AxTableFieldEnum">
			<Name>cbPLMStatus</Name>
			<EnumType>cbSyncStatus</EnumType>
			<Label>@CloudBeacon:PLMStatus</Label>
		</AxTableField>
		<AxTableField xmlns="" i:type="AxTableFieldUtcDateTime">
			<Name>cbLastSyncDateTime</Name>
			<ExtendedDataType>TransDateTime</ExtendedDataType>
			<Label>@CloudBeacon:LastSyncDateTime</Label>
		</AxTableField>
	</Fields>
	<Indexes>
		<AxTableIndex>
			<Name>cbPLMStatusIdx</Name>
			<AllowDuplicates>Yes</AllowDuplicates>
			<Fields>
				<AxTableIndexField>
					<DataField>cbPLMStatus</DataField>
				</AxTableIndexField>
			</Fields>
		</AxTableIndex>
	</Indexes>
	<Mappings />
	<PropertyModifications />
	<Relations />
</AxTableExtension>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxTableExtension\InventTable.cbExtension.xml">
  <SubType>Content</SubType>
  <Name>InventTable.cbExtension</Name>
  <Link>Table Extensions\InventTable.cbExtension</Link>
</Content>
```

If you also created a CoC extension class:

```xml
<Content Include="AxClass\InventTable_cbExtension.xml">
  <SubType>Content</SubType>
  <Name>InventTable_cbExtension</Name>
  <Link>Classes\InventTable_cbExtension</Link>
</Content>
```

## Accessing Extended Fields in X++

```xpp
// Extended fields are accessed like regular fields
InventTable inventTable;
select firstonly inventTable where inventTable.ItemId == "ITEM001";

// Access extension field
cbSyncStatus status = inventTable.cbPLMStatus;

// Update extension field
ttsbegin;
inventTable.selectForUpdate(true);
inventTable.cbPLMStatus = cbSyncStatus::Complete;
inventTable.cbLastSyncDateTime = DateTimeUtil::utcNow();
inventTable.update();
ttscommit;
```

## Checklist

- [ ] Identify base table to extend
- [ ] Create AxTableExtension with proper naming (`BaseTable.prefixExtension`)
- [ ] Add fields with `xmlns=""` and correct `i:type`
- [ ] Add field groups for UI organization
- [ ] Add indexes for query performance
- [ ] Create CoC extension class for method overrides/additions
- [ ] Add labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add artifacts to .rnrproj file
- [ ] Build and sync database
- [ ] Verify fields appear on table in AOT
