---
name: d365-new-edt
description: Create a new Extended Data Type (EDT) in D365 Finance & Operations — string, integer, real, int64, enum, date, datetime, container, or guid. Use whenever the user asks to create, add, or scaffold a new D365 EDT, reusable field type, or typed identifier (e.g. MyFieldId, MyCode).
---

# D365 F&O: Create Extended Data Type (EDT)

You are helping create an Extended Data Type (EDT) in D365 Finance & Operations. EDTs define reusable field types with consistent properties like length, labels, and formatting.

## Gather Requirements

Ask the user for:
1. **EDT name** (e.g., `MyFieldId`)
2. **Base type** (String, Integer, Real, Int64, Enum, Date, DateTime, Container, Guid)
3. **Label** and **help text**
4. **For strings:** maximum length
5. **For reals:** decimal places
6. **Extends existing EDT?** (e.g., extends `Description` or `ItemId`)
7. **Label file ID** to use
8. **Visual Studio project file path** (.rnrproj)

## Critical: EDT Root Element MUST Have i:type

**CRITICAL:** The root `<AxEdt>` element MUST include the `i:type` attribute. Without it, D365 throws "Cannot create an abstract class" because `AxEdt` is an abstract base class.

```xml
<!-- CORRECT -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtString">

<!-- WRONG - will fail with "Cannot create an abstract class" -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
```

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## EDT Types and i:type Values

| Base Type | i:type Value | Key Properties |
|-----------|--------------|----------------|
| String | `AxEdtString` | `StringSize` |
| Integer | `AxEdtInt` | — |
| Real | `AxEdtReal` | `NoOfDecimals` |
| Int64 | `AxEdtInt64` | — |
| Enum | `AxEdtEnum` | `EnumType` |
| Date | `AxEdtDate` | — |
| DateTime | `AxEdtUtcDateTime` | — |
| Container | `AxEdtContainer` | — |
| Guid | `AxEdtGuid` | — |

## String EDT Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtString">
	<Name>MyFieldId</Name>
	<Label>@LabelFile:MyFieldIdLabel</Label>
	<HelpText>@LabelFile:MyFieldIdHelp</HelpText>
	<StringSize>20</StringSize>
</AxEdt>
```

### String EDT with Reference Table (Lookup)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtString">
	<Name>MyTableId</Name>
	<Label>@LabelFile:MyTableIdLabel</Label>
	<HelpText>@LabelFile:MyTableIdHelp</HelpText>
	<StringSize>20</StringSize>
	<ReferenceTable>MyTable</ReferenceTable>
</AxEdt>
```

### String EDT Extending Another EDT

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtString">
	<Name>MyDescription</Name>
	<Extends>Description</Extends>
	<Label>@LabelFile:MyDescriptionLabel</Label>
	<HelpText>@LabelFile:MyDescriptionHelp</HelpText>
</AxEdt>
```

**Note:** When extending, you inherit properties from the base EDT. Only specify properties you want to override.

## Integer EDT Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtInt">
	<Name>MyQuantity</Name>
	<Label>@LabelFile:MyQuantityLabel</Label>
	<HelpText>@LabelFile:MyQuantityHelp</HelpText>
</AxEdt>
```

## Real (Decimal) EDT Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtReal">
	<Name>MyAmount</Name>
	<Label>@LabelFile:MyAmountLabel</Label>
	<HelpText>@LabelFile:MyAmountHelp</HelpText>
	<NoOfDecimals>2</NoOfDecimals>
</AxEdt>
```

### Real EDT with Display Properties

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtReal">
	<Name>MyPercentage</Name>
	<Label>@LabelFile:MyPercentageLabel</Label>
	<HelpText>@LabelFile:MyPercentageHelp</HelpText>
	<NoOfDecimals>2</NoOfDecimals>
	<DisplayLength>8</DisplayLength>
</AxEdt>
```

## Int64 EDT Template (RecId References)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtInt64">
	<Name>MyRefRecId</Name>
	<Extends>RefRecId</Extends>
	<Label>@LabelFile:MyRefRecIdLabel</Label>
	<HelpText>@LabelFile:MyRefRecIdHelp</HelpText>
	<ReferenceTable>MyTable</ReferenceTable>
</AxEdt>
```

## Enum EDT Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtEnum">
	<Name>MyStatusType</Name>
	<Label>@LabelFile:MyStatusTypeLabel</Label>
	<HelpText>@LabelFile:MyStatusTypeHelp</HelpText>
	<EnumType>MyStatusEnum</EnumType>
</AxEdt>
```

## DateTime EDT Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtUtcDateTime">
	<Name>MyProcessedDateTime</Name>
	<Extends>TransDateTime</Extends>
	<Label>@LabelFile:MyProcessedDateTimeLabel</Label>
	<HelpText>@LabelFile:MyProcessedDateTimeHelp</HelpText>
</AxEdt>
```

## Date EDT Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtDate">
	<Name>MyEffectiveDate</Name>
	<Extends>TransDate</Extends>
	<Label>@LabelFile:MyEffectiveDateLabel</Label>
	<HelpText>@LabelFile:MyEffectiveDateHelp</HelpText>
</AxEdt>
```

## Guid EDT Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtGuid">
	<Name>MyExternalGuid</Name>
	<Label>@LabelFile:MyExternalGuidLabel</Label>
	<HelpText>@LabelFile:MyExternalGuidHelp</HelpText>
</AxEdt>
```

## Common Base EDTs to Extend

| Base EDT | Type | Purpose |
|----------|------|---------|
| `Description` | String | 60-char descriptions |
| `Name` | String | 60-char names |
| `ItemId` | String | 20-char item identifiers |
| `CustAccount` | String | Customer account numbers |
| `VendAccount` | String | Vendor account numbers |
| `Qty` | Real | Quantities with decimals |
| `AmountCur` | Real | Currency amounts |
| `Percent` | Real | Percentages |
| `RefRecId` | Int64 | Record ID references |
| `TableId` | Int | Table ID references |
| `TransDate` | Date | Transaction dates |
| `TransDateTime` | DateTime | Transaction timestamps |

## Using EDTs in Table Fields

```xml
<AxTableField xmlns="" i:type="AxTableFieldString">
	<Name>MyField</Name>
	<ExtendedDataType>MyFieldId</ExtendedDataType>
</AxTableField>
```

For enum fields, use `EnumType` instead of `ExtendedDataType`:
```xml
<AxTableField xmlns="" i:type="AxTableFieldEnum">
	<Name>Status</Name>
	<EnumType>MyStatusEnum</EnumType>
</AxTableField>
```

## Common String Sizes

| Size | Use For |
|------|---------|
| 10 | Short codes (ItemGroupId, CustGroup) |
| 20 | Standard IDs (ItemId, CustAccount) |
| 40 | Names, short descriptions |
| 60 | Standard descriptions |
| 100 | Extended names |
| 255 | Long descriptions, URLs |
| 1000 | Notes, comments |

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxEdt\MyFieldId.xml">
  <SubType>Content</SubType>
  <Name>MyFieldId</Name>
  <Link>Extended Data Types\MyFieldId</Link>
</Content>
```

## Labels

Add to your label file:

```
MyFieldIdLabel=My Field
 ;EDT label
MyFieldIdHelp=Enter the field value
 ;EDT help text
```

## Common Gotchas

### Missing i:type Attribute
```xml
<!-- WRONG - causes "Cannot create an abstract class" -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance">

<!-- CORRECT -->
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtString">
```

### Wrong i:type for EDT Type
Make sure the `i:type` matches your intended data type:
- Strings: `AxEdtString`
- Integers: `AxEdtInt`
- Reals: `AxEdtReal`
- Int64: `AxEdtInt64`
- Enums: `AxEdtEnum`
- Dates: `AxEdtDate`
- DateTimes: `AxEdtUtcDateTime`

### Extends vs New EDT
- **Extends** inherits all properties; only override what differs
- **New EDT** needs all properties defined

## Checklist

- [ ] Create AxEdt with correct `i:type` attribute
- [ ] Set appropriate base type properties (StringSize, NoOfDecimals, etc.)
- [ ] Consider extending existing EDT if appropriate
- [ ] Add ReferenceTable for lookup behavior (optional)
- [ ] Add labels to label file
- [ ] Normalize XML file to CRLF
- [ ] Add to .rnrproj file
- [ ] Build and verify EDT appears in AOT
