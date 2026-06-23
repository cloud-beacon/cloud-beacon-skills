# D365 F&O: Extend Existing Form

You are helping extend an existing form in D365 Finance & Operations using form extensions. This adds controls, data sources, or methods to a base form WITHOUT modifying the original.

**Important:** This skill is for extending BASE objects (Microsoft or other ISV forms). To create a NEW form in your model, use `/d365-new-form` instead.

## Gather Requirements

Ask the user for:
1. **Base form** to extend (e.g., `InventTable`, `SalesTable`, `CustTable`)
2. **What to add:** Controls, data sources, and/or methods
3. **For controls:** Type, data binding, placement location
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
<BaseFormName>.<YourPrefix>Extension
```

Examples:
- `InventTable.cbExtension`
- `SalesTable.cbExtension`
- `CustTable.myExtension`

## AxFormExtension Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxFormExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns="Microsoft.Dynamics.AX.Metadata.V6">
	<Name>InventTable.cbExtension</Name>
	<Customizations />
	<ExtensionComponents>
		<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentControl">
			<!-- Control extensions go here -->
		</AxFormExtensionComponent>
	</ExtensionComponents>
	<FormControlOverrides />
	<PropertyModifications />
</AxFormExtension>
```

## Adding Controls to Existing Form

### Adding a Field to a Tab Page

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxFormExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns="Microsoft.Dynamics.AX.Metadata.V6">
	<Name>InventTable.cbExtension</Name>
	<Customizations />
	<ExtensionComponents>
		<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentControl">
			<Name>cbCustomField</Name>
			<ExtendedControl i:type="AxFormStringControl">
				<Name>cbCustomField</Name>
				<Type>String</Type>
				<DataField>cbCustomField</DataField>
				<DataSource>InventTable</DataSource>
			</ExtendedControl>
			<ParentControl>GeneralTab</ParentControl>
			<PositionType>End</PositionType>
		</AxFormExtensionComponent>
	</ExtensionComponents>
	<FormControlOverrides />
	<PropertyModifications />
</AxFormExtension>
```

### Control Position Types

| PositionType | Meaning |
|--------------|---------|
| `End` | Add at end of parent control |
| `Start` | Add at beginning of parent control |
| `AfterItem` | Place after `PreviousItem` control |
| `BeforeItem` | Place before `PreviousItem` control |

### Adding Multiple Controls

```xml
<ExtensionComponents>
	<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentControl">
		<Name>cbPLMStatus</Name>
		<ExtendedControl i:type="AxFormComboBoxControl">
			<Name>cbPLMStatus</Name>
			<Type>ComboBox</Type>
			<DataField>cbPLMStatus</DataField>
			<DataSource>InventTable</DataSource>
		</ExtendedControl>
		<ParentControl>DetailsTab</ParentControl>
		<PositionType>End</PositionType>
	</AxFormExtensionComponent>
	<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentControl">
		<Name>cbLastSyncDateTime</Name>
		<ExtendedControl i:type="AxFormDateTimeControl">
			<Name>cbLastSyncDateTime</Name>
			<Type>DateTime</Type>
			<DataField>cbLastSyncDateTime</DataField>
			<DataSource>InventTable</DataSource>
			<AllowEdit>No</AllowEdit>
		</ExtendedControl>
		<ParentControl>DetailsTab</ParentControl>
		<PositionType>AfterItem</PositionType>
		<PreviousItem>cbPLMStatus</PreviousItem>
	</AxFormExtensionComponent>
</ExtensionComponents>
```

### Control Types

| Type | i:type | Notes |
|------|--------|-------|
| String | `AxFormStringControl` | Text input |
| Integer | `AxFormIntegerControl` | NOT `AxFormIntControl` |
| Real | `AxFormRealControl` | Decimal input |
| ComboBox | `AxFormComboBoxControl` | Enum dropdown |
| CheckBox | `AxFormCheckBoxControl` | Boolean toggle |
| Date | `AxFormDateControl` | Date picker |
| DateTime | `AxFormDateTimeControl` | DateTime picker |
| Group | `AxFormGroupControl` | Container |
| Button | `AxFormButtonControl` | Clickable button |
| MenuFunctionButton | `AxFormMenuFunctionButtonControl` | Opens form/runs action |

## Adding a New Group with Controls

```xml
<ExtensionComponents>
	<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentControl">
		<Name>cbPLMGroup</Name>
		<ExtendedControl i:type="AxFormGroupControl">
			<Name>cbPLMGroup</Name>
			<Type>Group</Type>
			<Caption>@CloudBeacon:PLMIntegration</Caption>
			<Controls>
				<AxFormControl xmlns="" i:type="AxFormComboBoxControl">
					<Name>cbPLMStatus</Name>
					<Type>ComboBox</Type>
					<DataField>cbPLMStatus</DataField>
					<DataSource>InventTable</DataSource>
				</AxFormControl>
				<AxFormControl xmlns="" i:type="AxFormDateTimeControl">
					<Name>cbLastSyncDateTime</Name>
					<Type>DateTime</Type>
					<DataField>cbLastSyncDateTime</DataField>
					<DataSource>InventTable</DataSource>
					<AllowEdit>No</AllowEdit>
				</AxFormControl>
			</Controls>
		</ExtendedControl>
		<ParentControl>LineViewTab</ParentControl>
		<PositionType>End</PositionType>
	</AxFormExtensionComponent>
</ExtensionComponents>
```

## Adding a New Tab Page

```xml
<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentControl">
	<Name>cbPLMTabPage</Name>
	<ExtendedControl i:type="AxFormTabPageControl">
		<Name>cbPLMTabPage</Name>
		<Type>TabPage</Type>
		<Caption>@CloudBeacon:PLMIntegration</Caption>
		<Controls>
			<AxFormControl xmlns="" i:type="AxFormGroupControl">
				<Name>cbPLMFieldsGroup</Name>
				<Type>Group</Type>
				<Controls>
					<AxFormControl xmlns="" i:type="AxFormComboBoxControl">
						<Name>cbPLMStatus</Name>
						<Type>ComboBox</Type>
						<DataField>cbPLMStatus</DataField>
						<DataSource>InventTable</DataSource>
					</AxFormControl>
				</Controls>
				<DataSource>InventTable</DataSource>
			</AxFormControl>
		</Controls>
	</ExtendedControl>
	<ParentControl>DetailsHeaderTab</ParentControl>
	<PositionType>End</PositionType>
</AxFormExtensionComponent>
```

## Adding a Button to Action Pane

```xml
<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentControl">
	<Name>cbSyncButton</Name>
	<ExtendedControl i:type="AxFormMenuFunctionButtonControl">
		<Name>cbSyncButton</Name>
		<Type>MenuFunctionButton</Type>
		<Text>@CloudBeacon:SyncWithPLM</Text>
		<MenuItemName>cbPLMSync</MenuItemName>
		<MenuItemType>Action</MenuItemType>
	</ExtendedControl>
	<ParentControl>MaintenanceButtonGroup</ParentControl>
	<PositionType>End</PositionType>
</AxFormExtensionComponent>
```

## Modifying Existing Control Properties

Use `FormControlOverrides` to change properties of existing controls:

```xml
<FormControlOverrides>
	<AxFormControlExtensionOverride>
		<ControlName>ItemId</ControlName>
		<PropertyModifications>
			<AxFormControlExtensionPropertyModification>
				<Name>AllowEdit</Name>
				<Value>No</Value>
			</AxFormControlExtensionPropertyModification>
		</PropertyModifications>
	</AxFormControlExtensionOverride>
</FormControlOverrides>
```

## Adding Data Sources

To add a new data source (e.g., for a related table with extended fields):

```xml
<ExtensionComponents>
	<AxFormExtensionComponent xmlns="" i:type="AxFormExtensionComponentDataSource">
		<Name>cbRelatedTable</Name>
		<ExtendedDataSource>
			<Name>cbRelatedTable</Name>
			<Table>cbRelatedTable</Table>
			<JoinSource>InventTable</JoinSource>
			<LinkType>OuterJoin</LinkType>
			<InsertIfEmpty>No</InsertIfEmpty>
			<Fields />
			<ReferencedDataSources />
			<DataSourceLinks>
				<AxFormDataSourceLink>
					<Name>InventTableLink</Name>
					<Field>cbRelatedRecId</Field>
					<RelatedField>RecId</RelatedField>
				</AxFormDataSourceLink>
			</DataSourceLinks>
			<DerivedDataSources />
		</ExtendedDataSource>
	</AxFormExtensionComponent>
</ExtensionComponents>
```

## Adding Methods (Chain of Command)

Methods are NOT added in the form extension XML. Instead, create a separate **extension class** using Chain of Command:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>InventTableForm_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension class for InventTable form.
/// </summary>
[ExtensionOf(formStr(InventTable))]
final class InventTableForm_cbExtension
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

        // Custom initialization after form init
        this.cbInitCustomControls();
    }

]]></Source>
			</Method>
			<Method>
				<Name>cbInitCustomControls</Name>
				<Source><![CDATA[
    /// <summary>
    /// Initializes custom controls added by extension.
    /// </summary>
    private void cbInitCustomControls()
    {
        // Custom control initialization
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Form Data Source Method Extension

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>InventTableFormDS_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension for InventTable form data source.
/// </summary>
[ExtensionOf(formDataSourceStr(InventTable, InventTable))]
final class InventTableFormDS_cbExtension
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

        // Add custom query ranges
        QueryBuildDataSource qbds = this.query().dataSourceTable(tableNum(InventTable));
        qbds.addRange(fieldNum(InventTable, cbPLMStatus)).value(queryValue(cbSyncStatus::Pending));
    }

]]></Source>
			</Method>
			<Method>
				<Name>active</Name>
				<Source><![CDATA[
    public int active()
    {
        int ret = next active();

        // Custom logic when record becomes active
        InventTable inventTable = this.cursor();
        // Do something with inventTable.cbCustomField

        return ret;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Form Control Method Extension

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>InventTableFormCtrl_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension for specific form control.
/// </summary>
[ExtensionOf(formControlStr(InventTable, ItemId))]
final class InventTableFormCtrl_cbExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>modified</Name>
				<Source><![CDATA[
    public boolean modified()
    {
        boolean ret = next modified();

        if (ret)
        {
            // Custom logic when ItemId is modified
        }

        return ret;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Finding Parent Control Names

To place controls correctly, you need to know existing control names. Use these methods:

1. **Visual Studio AOT:** Navigate to the form and examine control hierarchy
2. **Debugger:** Set breakpoint and inspect form controls
3. **X++ code:** Use `formRun.design().controlName(controlName)`

Common parent control patterns:
- `ActionPane`, `MainActionPane` - Top action pane
- `*ButtonGroup` - Button groups in action pane
- `*Tab`, `DetailsHeaderTab`, `LineViewTab` - Tab controls
- `*TabPage`, `GeneralTab`, `DetailsTab` - Tab pages
- `*Group`, `HeaderGroup`, `LineGroup` - Group controls

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxFormExtension\InventTable.cbExtension.xml">
  <SubType>Content</SubType>
  <Name>InventTable.cbExtension</Name>
  <Link>Form Extensions\InventTable.cbExtension</Link>
</Content>
```

If you also created CoC extension classes:

```xml
<Content Include="AxClass\InventTableForm_cbExtension.xml">
  <SubType>Content</SubType>
  <Name>InventTableForm_cbExtension</Name>
  <Link>Classes\InventTableForm_cbExtension</Link>
</Content>
```

## Checklist

- [ ] Identify base form to extend
- [ ] Identify parent control names for placement
- [ ] Create AxFormExtension with proper naming (`BaseForm.prefixExtension`)
- [ ] Add controls with correct type, data binding, and position
- [ ] Create CoC extension class for method overrides/additions
- [ ] Add labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add artifacts to .rnrproj file
- [ ] Build and test form extension
- [ ] Verify controls appear in correct location
