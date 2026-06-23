---
name: d365-new-number-sequence
description: Create a new number sequence in D365 Finance & Operations for automatic sequential numbering of document IDs, transaction numbers, or other identifiers. Use whenever the user asks to add, create, or wire up a number sequence, auto-numbered ID, or sequence reference for a new field.
---

# D365 F&O: Create Number Sequence

You are helping create a number sequence in D365 Finance & Operations. Number sequences provide automatic, sequential numbering for document IDs, transaction numbers, and other identifiers.

## Gather Requirements

Ask the user for:
1. **Field/ID name** (e.g., `TemplateId`, `ImportBatchId`)
2. **Module** this belongs to (or create custom module reference)
3. **Format** requirements (prefix, length, alphanumeric vs numeric)
4. **Scope** (Shared, Company, Legal entity)
5. **Continuous?** (no gaps allowed, or gaps OK for performance)
6. **Label file ID** to use

Refer to **CLAUDE.md** for:
- Model name and naming prefix
- VS project file path

## Number Sequence Components

A complete number sequence implementation requires:

1. **EDT** - Extended data type for the ID field
2. **NumberSequenceModule enum extension** - Register your module
3. **NumberSequenceReference class** - Define the number sequence reference
4. **loadModule() method** - Register references at startup
5. **Parameters table integration** - Configure the number sequence
6. **Usage in code** - Generate numbers at runtime

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Step 1: Create the EDT

Create an EDT for the ID field that will use the number sequence:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEdt xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="" i:type="AxEdtString">
	<Name>cbTemplateId</Name>
	<Label>@CloudBeacon:TemplateIdLabel</Label>
	<HelpText>@CloudBeacon:TemplateIdHelp</HelpText>
	<StringSize>20</StringSize>
</AxEdt>
```

## Step 2: Extend NumberSequenceModule Enum

Add your module to the `NumberSequenceModule` enum:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxEnumExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>NumberSequenceModule.cbExtension</Name>
	<EnumValues>
		<AxEnumValue>
			<Name>cbCloudBeacon</Name>
			<Label>@CloudBeacon:ModuleName</Label>
			<Value>500</Value>
		</AxEnumValue>
	</EnumValues>
</AxEnumExtension>
```

**Note:** Use a high value (500+) to avoid conflicts with standard modules.

## Step 3: Create Number Sequence Reference Class

This class defines the number sequence and its properties:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>cbNumberSeqModuleCloudBeacon</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Number sequence reference definitions for CloudBeacon module.
/// </summary>
class cbNumberSeqModuleCloudBeacon extends NumberSeqApplicationModule
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>loadModule</Name>
				<Source><![CDATA[
    /// <summary>
    /// Loads number sequence references for the CloudBeacon module.
    /// </summary>
    protected void loadModule()
    {
        NumberSeqDatatype datatype = NumberSeqDatatype::construct();

        // Template ID number sequence
        datatype.parmDatatypeId(extendedTypeNum(cbTemplateId));
        datatype.parmReferenceLabel(literalStr("@CloudBeacon:TemplateIdLabel"));
        datatype.parmReferenceHelp(literalStr("@CloudBeacon:TemplateIdNumSeqHelp"));
        datatype.parmWizardIsContinuous(false);
        datatype.parmWizardIsManual(NoYes::No);
        datatype.parmWizardIsChangeDownAllowed(NoYes::No);
        datatype.parmWizardIsChangeUpAllowed(NoYes::No);
        datatype.parmWizardHighest(999999);
        datatype.parmSortField(1);

        this.create(datatype);

        // Add more number sequences here if needed
        // Example: Import Batch ID
        /*
        datatype = NumberSeqDatatype::construct();
        datatype.parmDatatypeId(extendedTypeNum(cbImportBatchId));
        datatype.parmReferenceLabel(literalStr("@CloudBeacon:ImportBatchIdLabel"));
        datatype.parmReferenceHelp(literalStr("@CloudBeacon:ImportBatchIdNumSeqHelp"));
        datatype.parmWizardIsContinuous(false);
        datatype.parmWizardIsManual(NoYes::No);
        datatype.parmSortField(2);
        this.create(datatype);
        */
    }

]]></Source>
			</Method>
			<Method>
				<Name>numberSeqModule</Name>
				<Source><![CDATA[
    /// <summary>
    /// Returns the module for this number sequence group.
    /// </summary>
    /// <returns>The NumberSequenceModule enum value.</returns>
    public NumberSeqModule numberSeqModule()
    {
        return NumberSeqModule::cbCloudBeacon;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### NumberSeqDatatype Properties

| Property | Purpose |
|----------|---------|
| `parmDatatypeId` | EDT that uses this number sequence |
| `parmReferenceLabel` | Display name in setup forms |
| `parmReferenceHelp` | Help text for the reference |
| `parmWizardIsContinuous` | `true` = no gaps (slower), `false` = gaps allowed |
| `parmWizardIsManual` | Allow manual entry |
| `parmWizardIsChangeDownAllowed` | Allow decreasing the number |
| `parmWizardIsChangeUpAllowed` | Allow increasing the number |
| `parmWizardHighest` | Maximum value for the sequence |
| `parmSortField` | Display order in setup |

## Step 4: Register the Module at Startup

Extend `NumberSeqApplicationModule` to include your module:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>NumberSeqApplicationModule_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension to register CloudBeacon number sequence module.
/// </summary>
[ExtensionOf(classStr(NumberSeqApplicationModule))]
final class NumberSeqApplicationModule_cbExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>buildModulesMapSubscriber</Name>
				<Source><![CDATA[
    [SubscribesTo(classStr(NumberSeqGlobal), staticDelegateStr(NumberSeqGlobal, buildModulesMapDelegate))]
    public static void buildModulesMapSubscriber(Map _numberSeqModuleNamesMap)
    {
        NumberSeqApplicationModule::addModuleToMap(
            classNum(cbNumberSeqModuleCloudBeacon),
            NumberSeqModule::cbCloudBeacon,
            _numberSeqModuleNamesMap);
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Step 5: Add to Parameters Table

Add fields to your parameters table to store the number sequence reference:

### Table Extension (if using existing parameters table)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTableExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>cbParameters.cbNumSeqExtension</Name>
	<FieldGroups>
		<AxTableFieldGroup>
			<Name>cbNumberSequences</Name>
			<Label>@SYS21768</Label>
			<Fields>
				<AxTableFieldGroupField>
					<DataField>cbTemplateIdNumSeq</DataField>
				</AxTableFieldGroupField>
			</Fields>
		</AxTableFieldGroup>
	</FieldGroups>
	<Fields>
		<AxTableField xmlns="" i:type="AxTableFieldInt64">
			<Name>cbTemplateIdNumSeq</Name>
			<ExtendedDataType>RefRecId</ExtendedDataType>
			<Label>@CloudBeacon:TemplateIdLabel</Label>
		</AxTableField>
	</Fields>
	<Mappings />
	<PropertyModifications />
	<Relations>
		<AxTableRelation>
			<Name>cbTemplateIdNumSeqTable</Name>
			<RelatedTable>NumberSequenceTable</RelatedTable>
			<Constraints>
				<AxTableRelationConstraint xmlns="" i:type="AxTableRelationConstraintField">
					<Name>RecIdConstraint</Name>
					<Field>cbTemplateIdNumSeq</Field>
					<RelatedField>RecId</RelatedField>
				</AxTableRelationConstraint>
			</Constraints>
		</AxTableRelation>
	</Relations>
</AxTableExtension>
```

### Parameters Table Methods

Add a method to retrieve the number sequence reference:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>cbParameters_cbNumSeqExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension for cbParameters to support number sequence references.
/// </summary>
[ExtensionOf(tableStr(cbParameters))]
final class cbParameters_cbNumSeqExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>numRefTemplateId</Name>
				<Source><![CDATA[
    /// <summary>
    /// Gets the number sequence reference for Template ID.
    /// </summary>
    /// <returns>The number sequence reference.</returns>
    public static NumberSequenceReference numRefTemplateId()
    {
        return NumberSeqReference::findReference(extendedTypeNum(cbTemplateId));
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Step 6: Add Number Sequence Tab to Parameters Form

Extend the parameters form to include number sequence configuration:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>cbParametersForm_cbNumSeqExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Form extension to add number sequence tab to cbParameters form.
/// </summary>
[ExtensionOf(formStr(cbParameters))]
final class cbParametersForm_cbNumSeqExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>init</Name>
				<Source><![CDATA[
    public void init()
    {
        next init();

        // Initialize number sequence controls after form init
        // This enables the standard number sequence tab functionality
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

Alternatively, add a Number Sequences tab page to your parameters form with a grid bound to `NumberSequenceReference` filtered by your module.

## Step 7: Generate Numbers at Runtime

Use the number sequence in your business logic:

```xpp
/// <summary>
/// Generates a new template ID using the number sequence.
/// </summary>
/// <returns>The generated template ID.</returns>
public static cbTemplateId generateTemplateId()
{
    NumberSeq           numberSeq;
    NumberSequenceReference numRef;
    cbTemplateId        newId;

    numRef = cbParameters::numRefTemplateId();

    if (numRef)
    {
        numberSeq = NumberSeq::newGetNum(numRef);
        newId = numberSeq.num();
    }
    else
    {
        throw error("@CloudBeacon:NumSeqNotConfigured");
    }

    return newId;
}
```

### Using in Table insert()

```xpp
public void insert()
{
    if (!this.TemplateId)
    {
        this.TemplateId = cbTemplateHelper::generateTemplateId();
    }

    super();
}
```

### With Voucher (for journals/transactions)

```xpp
// For scenarios needing voucher-like behavior (can be released)
NumberSeq numberSeq = NumberSeq::newGetNumFromId(numRef.NumberSequenceId);

try
{
    ttsbegin;

    str num = numberSeq.num();
    // Use the number...

    ttscommit;
}
catch
{
    // Release the number back to the pool
    numberSeq.abort();
    throw;
}
```

## Running the Number Sequence Wizard

After deploying, users must run the number sequence wizard:

1. Go to **Organization administration > Number sequences > Number sequences**
2. Click **Generate** button
3. Select your module (CloudBeacon)
4. Follow the wizard to create sequence codes
5. Go to your parameters form to assign the sequences

Or use the **Number sequence wizard**:
1. **Organization administration > Number sequences > Number sequence wizard**
2. Select your references and configure format

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<!-- EDT -->
<Content Include="AxEdt\cbTemplateId.xml">
  <SubType>Content</SubType>
  <Name>cbTemplateId</Name>
  <Link>Extended Data Types\cbTemplateId</Link>
</Content>

<!-- Enum Extension -->
<Content Include="AxEnumExtension\NumberSequenceModule.cbExtension.xml">
  <SubType>Content</SubType>
  <Name>NumberSequenceModule.cbExtension</Name>
  <Link>Enum Extensions\NumberSequenceModule.cbExtension</Link>
</Content>

<!-- Number Sequence Module Class -->
<Content Include="AxClass\cbNumberSeqModuleCloudBeacon.xml">
  <SubType>Content</SubType>
  <Name>cbNumberSeqModuleCloudBeacon</Name>
  <Link>Classes\cbNumberSeqModuleCloudBeacon</Link>
</Content>

<!-- Registration Extension -->
<Content Include="AxClass\NumberSeqApplicationModule_cbExtension.xml">
  <SubType>Content</SubType>
  <Name>NumberSeqApplicationModule_cbExtension</Name>
  <Link>Classes\NumberSeqApplicationModule_cbExtension</Link>
</Content>

<!-- Parameters Table Extension -->
<Content Include="AxTableExtension\cbParameters.cbNumSeqExtension.xml">
  <SubType>Content</SubType>
  <Name>cbParameters.cbNumSeqExtension</Name>
  <Link>Table Extensions\cbParameters.cbNumSeqExtension</Link>
</Content>

<!-- Parameters Table CoC -->
<Content Include="AxClass\cbParameters_cbNumSeqExtension.xml">
  <SubType>Content</SubType>
  <Name>cbParameters_cbNumSeqExtension</Name>
  <Link>Classes\cbParameters_cbNumSeqExtension</Link>
</Content>
```

## Labels

Add to your label file:

```
TemplateIdLabel=Template ID
 ;EDT and field label
TemplateIdHelp=Unique identifier for the template
 ;EDT help text
TemplateIdNumSeqHelp=Number sequence for generating template IDs
 ;Number sequence reference help
ModuleName=Cloud Beacon
 ;Module name for number sequence setup
NumSeqNotConfigured=Number sequence for Template ID is not configured. Please set up number sequences in parameters.
 ;Error when number sequence not configured
```

## Common Number Sequence Formats

| Format | Example | Use Case |
|--------|---------|----------|
| `TMPL-######` | TMPL-000001 | Template IDs with prefix |
| `IMP-########` | IMP-00000001 | Import batch IDs |
| `CB-####-####` | CB-0001-0001 | Segmented IDs |
| `###########` | 00000000001 | Pure numeric |
| `@@@#######` | ABC0000001 | Alphanumeric prefix |

**Format characters:**
- `#` = Numeric digit
- `@` = Alphabetic character
- `?` = Alphanumeric
- Literal characters are kept as-is

## Troubleshooting

### Number Sequence Not Appearing in Wizard
1. Verify `NumberSeqModule` enum extension is deployed
2. Check `loadModule()` is called (set breakpoint)
3. Verify `buildModulesMapSubscriber` is registered
4. Rebuild and restart IIS

### "Number sequence not found" Error
1. Verify wizard was run and sequence created
2. Check parameters table has the reference assigned
3. Verify `numRefXxx()` method returns valid reference

### Numbers Have Gaps When Continuous Expected
1. Set `parmWizardIsContinuous(true)` in `loadModule()`
2. Existing sequences may need to be recreated
3. Note: Continuous sequences have performance impact

## Checklist

- [ ] Create EDT for the ID field
- [ ] Extend `NumberSequenceModule` enum with your module
- [ ] Create `NumberSeqModule*` class with `loadModule()` method
- [ ] Create subscriber class for `buildModulesMapDelegate`
- [ ] Add number sequence reference field(s) to parameters table
- [ ] Add `numRefXxx()` method to parameters table
- [ ] Add number sequence generation helper method
- [ ] Integrate into table `insert()` or business logic
- [ ] Add labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build and restart IIS
- [ ] Run number sequence wizard
- [ ] Configure sequence in parameters
- [ ] Test number generation
