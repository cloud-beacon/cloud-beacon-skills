# D365 F&O: Create Enumeration (Enum)

You are helping create an enumeration (enum) in D365 Finance & Operations.

## Gather Requirements

Ask the user for:
1. **Enum name** (e.g., `MyStatusEnum`)
2. **Purpose/description**
3. **Values** (name, label, optional integer value for each)
4. **Is extensible?** (can other models add values?)
5. **Label file ID** to use
6. **Visual Studio project file path** (.rnrproj)

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## AxEnum Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEnum xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyStatusEnum</Name>
	<Label>@LabelFile:MyStatusEnumLabel</Label>
	<Help>@LabelFile:MyStatusEnumHelp</Help>
	<UseEnumValue>No</UseEnumValue>
	<IsExtensible>true</IsExtensible>
	<EnumValues>
		<AxEnumValue>
			<Name>None</Name>
			<Label>@LabelFile:MyStatusNoneLabel</Label>
		</AxEnumValue>
		<AxEnumValue>
			<Name>Pending</Name>
			<Label>@LabelFile:MyStatusPendingLabel</Label>
			<Value>1</Value>
		</AxEnumValue>
		<AxEnumValue>
			<Name>InProgress</Name>
			<Label>@LabelFile:MyStatusInProgressLabel</Label>
			<Value>2</Value>
		</AxEnumValue>
		<AxEnumValue>
			<Name>Complete</Name>
			<Label>@LabelFile:MyStatusCompleteLabel</Label>
			<Value>3</Value>
		</AxEnumValue>
		<AxEnumValue>
			<Name>Error</Name>
			<Label>@LabelFile:MyStatusErrorLabel</Label>
			<Value>4</Value>
		</AxEnumValue>
	</EnumValues>
</AxEnum>
```

## Key Properties

| Property | Description |
|----------|-------------|
| `Label` | Display name for the enum type |
| `Help` | Tooltip/help text |
| `UseEnumValue` | `Yes` to use explicit values in DB; `No` for auto-assigned |
| `IsExtensible` | `true` allows other models to add values |

## Enum Value Rules

1. **First value** implicitly starts at 0 (no `<Value>` element needed)
2. **Subsequent values** should be explicitly set if gaps are needed
3. **Values must be unique** within the enum
4. **Values must be positive integers** (0 or greater)

### Sequential Values (Simple)

```xml
<EnumValues>
	<AxEnumValue>
		<Name>Value1</Name>
		<Label>@LabelFile:Value1Label</Label>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Value2</Name>
		<Label>@LabelFile:Value2Label</Label>
		<Value>1</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Value3</Name>
		<Label>@LabelFile:Value3Label</Label>
		<Value>2</Value>
	</AxEnumValue>
</EnumValues>
```

### Gapped Values (For Extension)

If you want to leave room for future values or extensions:

```xml
<EnumValues>
	<AxEnumValue>
		<Name>None</Name>
		<Label>@LabelFile:NoneLabel</Label>
	</AxEnumValue>
	<AxEnumValue>
		<Name>TypeA</Name>
		<Label>@LabelFile:TypeALabel</Label>
		<Value>10</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>TypeB</Name>
		<Label>@LabelFile:TypeBLabel</Label>
		<Value>20</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>TypeC</Name>
		<Label>@LabelFile:TypeCLabel</Label>
		<Value>30</Value>
	</AxEnumValue>
</EnumValues>
```

## Common Enum Patterns

### Yes/No/Unknown

```xml
<EnumValues>
	<AxEnumValue>
		<Name>Unknown</Name>
		<Label>@SYS26584</Label>
	</AxEnumValue>
	<AxEnumValue>
		<Name>No</Name>
		<Label>@SYS12664</Label>
		<Value>1</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Yes</Name>
		<Label>@SYS12663</Label>
		<Value>2</Value>
	</AxEnumValue>
</EnumValues>
```

### Status Workflow

```xml
<EnumValues>
	<AxEnumValue>
		<Name>Draft</Name>
		<Label>@LabelFile:StatusDraft</Label>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Submitted</Name>
		<Label>@LabelFile:StatusSubmitted</Label>
		<Value>1</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Approved</Name>
		<Label>@LabelFile:StatusApproved</Label>
		<Value>2</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Rejected</Name>
		<Label>@LabelFile:StatusRejected</Label>
		<Value>3</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Cancelled</Name>
		<Label>@LabelFile:StatusCancelled</Label>
		<Value>4</Value>
	</AxEnumValue>
</EnumValues>
```

### Type Classification

```xml
<EnumValues>
	<AxEnumValue>
		<Name>Standard</Name>
		<Label>@LabelFile:TypeStandard</Label>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Service</Name>
		<Label>@LabelFile:TypeService</Label>
		<Value>1</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>BOM</Name>
		<Label>@LabelFile:TypeBOM</Label>
		<Value>2</Value>
	</AxEnumValue>
	<AxEnumValue>
		<Name>Formula</Name>
		<Label>@LabelFile:TypeFormula</Label>
		<Value>3</Value>
	</AxEnumValue>
</EnumValues>
```

## Using Enums in Tables

In table field definition:

```xml
<AxTableField xmlns="" i:type="AxTableFieldEnum">
	<Name>Status</Name>
	<EnumType>MyStatusEnum</EnumType>
</AxTableField>
```

**Note:** Enum fields use `EnumType` property, NOT `ExtendedDataType`.

## Using Enums in X++ Code

```xpp
// Check specific value
if (record.Status == MyStatusEnum::Complete)
{
    // ...
}

// Switch statement
switch (record.Status)
{
    case MyStatusEnum::Pending:
        // handle pending
        break;
    case MyStatusEnum::InProgress:
        // handle in progress
        break;
    case MyStatusEnum::Complete:
        // handle complete
        break;
}

// Get enum label
str statusLabel = enum2Str(record.Status);

// Parse from string
MyStatusEnum status = str2Enum(MyStatusEnum::None, statusString);

// Iterate all values
DictEnum dictEnum = new DictEnum(enumNum(MyStatusEnum));
for (int i = 0; i < dictEnum.values(); i++)
{
    int enumValue = dictEnum.index2Value(i);
    str enumLabel = dictEnum.index2Label(i);
}
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxEnum\MyStatusEnum.xml">
  <SubType>Content</SubType>
  <Name>MyStatusEnum</Name>
  <Link>Base Enums\MyStatusEnum</Link>
</Content>
```

## Labels

Add to your label file:

```
MyStatusEnumLabel=My Status
 ;Enum type label
MyStatusEnumHelp=Status of the record
 ;Enum help text
MyStatusNoneLabel=None
 ;Enum value label
MyStatusPendingLabel=Pending
 ;Enum value label
MyStatusInProgressLabel=In Progress
 ;Enum value label
MyStatusCompleteLabel=Complete
 ;Enum value label
MyStatusErrorLabel=Error
 ;Enum value label
```

## Extensibility Considerations

### Making Enums Extensible

Set `<IsExtensible>true</IsExtensible>` when:
- Other ISV modules might need to add values
- Your own model might be extended by customers
- The enum represents an open-ended classification

### Non-Extensible Enums

Set `<IsExtensible>false</IsExtensible>` when:
- Values are fixed and should never change (Yes/No)
- Business logic depends on exhaustive pattern matching
- Security or compliance requires controlled values

### Extending Existing Enums

To add values to an extensible enum from another model:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEnumExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>BaseModuleEnum.MyExtension</Name>
	<EnumValues>
		<AxEnumValue>
			<Name>MyCustomValue</Name>
			<Label>@LabelFile:MyCustomValueLabel</Label>
			<Value>100</Value>
		</AxEnumValue>
	</EnumValues>
</AxEnumExtension>
```

**Note:** Use a high value (100+) to avoid conflicts with base enum values.

## Checklist

- [ ] Create AxEnum with appropriate name
- [ ] Add all values with labels
- [ ] Set `IsExtensible` appropriately
- [ ] First value at 0 (no explicit Value), subsequent values explicit
- [ ] Add labels to label file
- [ ] Normalize XML file to CRLF
- [ ] Add to .rnrproj file
- [ ] Build and verify enum appears in AOT
