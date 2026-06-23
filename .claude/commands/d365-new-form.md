# D365 F&O: Create Form

You are helping create a form in D365 Finance & Operations for displaying and editing data.

## Gather Requirements

Ask the user for:
1. **Form name** (e.g., `MyTableForm`)
2. **Data source table(s)** to display
3. **Form pattern** (SimpleList, SimpleListDetails, DetailsFormMaster, Custom)
4. **Key fields** to show in grid/header
5. **Label file ID** to use
6. **Visual Studio project file path** (.rnrproj)

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Form Patterns Overview

| Pattern | Use Case | Structure |
|---------|----------|-----------|
| `SimpleList` | Basic list without details | Action pane → Filter → Grid |
| `SimpleListDetails` | List with detail pane | Action pane → Filter → Grid + Details |
| `DetailsFormMaster` | Full master data form | Action pane → Header → Tabs with fields |
| `ListPage` | Navigation list pages | Action pane → Filter → Grid (read-only navigation) |
| `Custom` | Non-standard layouts | Flexible structure |

## SimpleList Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxForm xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="Microsoft.Dynamics.AX.Metadata.V6">
	<Name>MyTableForm</Name>
	<SourceCode>
		<Methods xmlns="">
			<Method>
				<Name>classDeclaration</Name>
				<Source><![CDATA[
[Form]
public class MyTableForm extends FormRun
{
}
]]></Source>
			</Method>
		</Methods>
		<DataSources xmlns="" />
		<DataControls xmlns="" />
		<Members xmlns="" />
	</SourceCode>
	<DataSources>
		<AxFormDataSource xmlns="">
			<Name>MyTable</Name>
			<Table>MyTable</Table>
			<InsertIfEmpty>No</InsertIfEmpty>
			<Fields />
			<ReferencedDataSources />
			<DataSourceLinks />
			<DerivedDataSources />
		</AxFormDataSource>
	</DataSources>
	<Design>
		<Caption xmlns="">@LabelFile:MyTableFormCaption</Caption>
		<Pattern xmlns="">SimpleList</Pattern>
		<PatternVersion xmlns="">1.1</PatternVersion>
		<Style xmlns="">SimpleList</Style>
		<Controls xmlns="">
			<AxFormControl xmlns="" i:type="AxFormActionPaneControl">
				<Name>MainActionPane</Name>
				<Type>ActionPane</Type>
				<FormControlExtension>
					<Name>MainActionPane</Name>
					<ExtensionComponents />
				</FormControlExtension>
				<Controls>
					<AxFormControl xmlns="" i:type="AxFormButtonGroupControl">
						<Name>NewDeleteGroup</Name>
						<Type>ButtonGroup</Type>
						<Controls>
							<AxFormControl xmlns="" i:type="AxFormCommandButtonControl">
								<Name>NewButton</Name>
								<Type>CommandButton</Type>
								<Command>New</Command>
							</AxFormControl>
							<AxFormControl xmlns="" i:type="AxFormCommandButtonControl">
								<Name>DeleteButton</Name>
								<Type>CommandButton</Type>
								<Command>DeleteRecord</Command>
							</AxFormControl>
						</Controls>
					</AxFormControl>
				</Controls>
			</AxFormControl>
			<AxFormControl xmlns="" i:type="AxFormGroupControl">
				<Name>FilterGroup</Name>
				<Pattern>CustomAndQuickFilters</Pattern>
				<PatternVersion>1.1</PatternVersion>
				<Type>Group</Type>
				<Controls>
					<AxFormControl xmlns="" i:type="AxFormControlExtensionHost">
						<Name>QuickFilterControl</Name>
						<FormControlExtension>
							<Name>QuickFilterControl</Name>
							<ExtensionComponents>
								<AxFormControlExtensionComponent i:type="AxFormControlQuickFilterExtension">
									<Name>QuickFilter</Name>
									<TargetControl>MainGrid</TargetControl>
								</AxFormControlExtensionComponent>
							</ExtensionComponents>
						</FormControlExtension>
					</AxFormControl>
				</Controls>
			</AxFormControl>
			<AxFormControl xmlns="" i:type="AxFormGridControl">
				<Name>MainGrid</Name>
				<Type>Grid</Type>
				<Controls>
					<!-- Grid columns go here -->
				</Controls>
				<DataSource>MyTable</DataSource>
			</AxFormControl>
		</Controls>
	</Design>
</AxForm>
```

## SimpleListDetails Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxForm xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="Microsoft.Dynamics.AX.Metadata.V6">
	<Name>MyTableDetailsForm</Name>
	<SourceCode>
		<Methods xmlns="">
			<Method>
				<Name>classDeclaration</Name>
				<Source><![CDATA[
[Form]
public class MyTableDetailsForm extends FormRun
{
}
]]></Source>
			</Method>
		</Methods>
		<DataSources xmlns="" />
		<DataControls xmlns="" />
		<Members xmlns="" />
	</SourceCode>
	<DataSources>
		<AxFormDataSource xmlns="">
			<Name>MyTable</Name>
			<Table>MyTable</Table>
			<InsertIfEmpty>No</InsertIfEmpty>
			<Fields />
			<ReferencedDataSources />
			<DataSourceLinks />
			<DerivedDataSources />
		</AxFormDataSource>
	</DataSources>
	<Design>
		<Caption xmlns="">@LabelFile:MyTableFormCaption</Caption>
		<Pattern xmlns="">SimpleListDetails</Pattern>
		<PatternVersion xmlns="">1.1</PatternVersion>
		<Style xmlns="">SimpleListDetails</Style>
		<Controls xmlns="">
			<AxFormControl xmlns="" i:type="AxFormActionPaneControl">
				<Name>MainActionPane</Name>
				<Type>ActionPane</Type>
				<FormControlExtension>
					<Name>MainActionPane</Name>
					<ExtensionComponents />
				</FormControlExtension>
				<Controls />
			</AxFormControl>
			<AxFormControl xmlns="" i:type="AxFormGroupControl">
				<Name>NavigationList</Name>
				<Type>Group</Type>
				<Controls>
					<AxFormControl xmlns="" i:type="AxFormGroupControl">
						<Name>FilterGroup</Name>
						<Pattern>CustomAndQuickFilters</Pattern>
						<PatternVersion>1.1</PatternVersion>
						<Type>Group</Type>
						<Controls>
							<AxFormControl xmlns="" i:type="AxFormControlExtensionHost">
								<Name>QuickFilterControl</Name>
								<FormControlExtension>
									<Name>QuickFilterControl</Name>
									<ExtensionComponents>
										<AxFormControlExtensionComponent i:type="AxFormControlQuickFilterExtension">
											<Name>QuickFilter</Name>
											<TargetControl>MainGrid</TargetControl>
										</AxFormControlExtensionComponent>
									</ExtensionComponents>
								</FormControlExtension>
							</AxFormControl>
						</Controls>
					</AxFormControl>
					<AxFormControl xmlns="" i:type="AxFormGridControl">
						<Name>MainGrid</Name>
						<Type>Grid</Type>
						<Controls>
							<!-- Grid columns -->
						</Controls>
						<DataSource>MyTable</DataSource>
					</AxFormControl>
				</Controls>
			</AxFormControl>
			<AxFormControl xmlns="" i:type="AxFormGroupControl">
				<Name>DetailsPanel</Name>
				<Type>Group</Type>
				<Controls>
					<AxFormControl xmlns="" i:type="AxFormGroupControl">
						<Name>DetailsHeader</Name>
						<Type>Group</Type>
						<Controls>
							<!-- Key fields shown at top of details -->
						</Controls>
						<DataSource>MyTable</DataSource>
					</AxFormControl>
					<AxFormControl xmlns="" i:type="AxFormTabControl">
						<Name>DetailsTabs</Name>
						<Type>Tab</Type>
						<Controls>
							<AxFormControl xmlns="" i:type="AxFormTabPageControl">
								<Name>GeneralTab</Name>
								<Type>TabPage</Type>
								<Caption>@SYS2952</Caption>
								<Controls>
									<!-- Detail fields -->
								</Controls>
								<DataSource>MyTable</DataSource>
							</AxFormControl>
						</Controls>
					</AxFormControl>
				</Controls>
			</AxFormControl>
		</Controls>
	</Design>
</AxForm>
```

## Form Control Types

### String Field
```xml
<AxFormControl xmlns="" i:type="AxFormStringControl">
	<Name>MyTable_Name</Name>
	<Type>String</Type>
	<DataField>Name</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

### Integer Field
**IMPORTANT:** Use `AxFormIntegerControl` (NOT `AxFormIntControl` - that's invalid)
```xml
<AxFormControl xmlns="" i:type="AxFormIntegerControl">
	<Name>MyTable_Quantity</Name>
	<Type>Integer</Type>
	<DataField>Quantity</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

### Real (Decimal) Field
```xml
<AxFormControl xmlns="" i:type="AxFormRealControl">
	<Name>MyTable_Amount</Name>
	<Type>Real</Type>
	<DataField>Amount</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

### Enum (ComboBox) Field
```xml
<AxFormControl xmlns="" i:type="AxFormComboBoxControl">
	<Name>MyTable_Status</Name>
	<Type>ComboBox</Type>
	<DataField>Status</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

### Date Field
```xml
<AxFormControl xmlns="" i:type="AxFormDateControl">
	<Name>MyTable_TransDate</Name>
	<Type>Date</Type>
	<DataField>TransDate</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

### DateTime Field
```xml
<AxFormControl xmlns="" i:type="AxFormDateTimeControl">
	<Name>MyTable_CreatedDateTime</Name>
	<Type>DateTime</Type>
	<DataField>CreatedDateTime</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

### CheckBox Field
```xml
<AxFormControl xmlns="" i:type="AxFormCheckBoxControl">
	<Name>MyTable_IsActive</Name>
	<Type>CheckBox</Type>
	<DataField>IsActive</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

## Action Pane with Menu Function Button

To add a button that opens another form or runs an action:

```xml
<AxFormControl xmlns="" i:type="AxFormActionPaneControl">
	<Name>MainActionPane</Name>
	<Type>ActionPane</Type>
	<FormControlExtension>
		<Name>MainActionPane</Name>
		<ExtensionComponents />
	</FormControlExtension>
	<Controls>
		<AxFormControl xmlns="" i:type="AxFormButtonGroupControl">
			<Name>ActionGroup</Name>
			<Type>ButtonGroup</Type>
			<Controls>
				<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
					<Name>OpenRelatedForm</Name>
					<Type>MenuFunctionButton</Type>
					<Text>@LabelFile:OpenRelatedLabel</Text>
					<MenuItemName>RelatedForm</MenuItemName>
					<MenuItemType>Display</MenuItemType>
				</AxFormControl>
				<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
					<Name>RunProcess</Name>
					<Type>MenuFunctionButton</Type>
					<Text>@LabelFile:RunProcessLabel</Text>
					<MenuItemName>MyProcess</MenuItemName>
					<MenuItemType>Action</MenuItemType>
				</AxFormControl>
			</Controls>
		</AxFormControl>
	</Controls>
</AxFormControl>
```

## Form Methods (X++ Code-Behind)

### Override init()
```xml
<Method>
	<Name>init</Name>
	<Source><![CDATA[
    public void init()
    {
        super();
        // Initialization logic
    }

]]></Source>
</Method>
```

### Override run()
```xml
<Method>
	<Name>run</Name>
	<Source><![CDATA[
    public void run()
    {
        super();
        // After form loads
    }

]]></Source>
</Method>
```

### Data Source Methods

Add to `<DataSources xmlns="" />` in SourceCode:
```xml
<DataSources xmlns="">
	<DataSource>
		<Name>MyTable</Name>
		<Methods>
			<Method>
				<Name>init</Name>
				<Source><![CDATA[
    public void init()
    {
        super();
        // Data source initialization
    }

]]></Source>
			</Method>
			<Method>
				<Name>executeQuery</Name>
				<Source><![CDATA[
    public void executeQuery()
    {
        // Modify query before execution
        super();
    }

]]></Source>
			</Method>
		</Methods>
	</DataSource>
</DataSources>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxForm\MyTableForm.xml">
  <SubType>Content</SubType>
  <Name>MyTableForm</Name>
  <Link>Forms\MyTableForm</Link>
</Content>
```

## Labels

Add to your label file:

```
MyTableFormCaption=My Table
 ;Form caption
OpenRelatedLabel=Open related
 ;Button label
RunProcessLabel=Run process
 ;Button label
```

## Common Gotchas

### Control Type Errors
- **Integer:** Use `AxFormIntegerControl` (NOT `AxFormIntControl`)
- **All controls need** `xmlns=""` when using `i:type`

### Pattern Compliance
- Each pattern expects specific control hierarchy
- Missing required controls cause pattern validation warnings
- Check pattern documentation in Visual Studio

### Data Source Issues
- `InsertIfEmpty="No"` prevents phantom empty records
- Link child data sources properly with `DataSourceLinks`

## Checklist

- [ ] Create AxForm with appropriate pattern
- [ ] Add data source(s) linked to table(s)
- [ ] Add action pane with common buttons (New, Delete, etc.)
- [ ] Add filter group with quick filter
- [ ] Add grid with bound columns
- [ ] Add detail fields/tabs (if SimpleListDetails or DetailsFormMaster)
- [ ] Create AxMenuItemDisplay pointing to form
- [ ] Add labels to label file
- [ ] Normalize XML files to CRLF
- [ ] Add artifacts to .rnrproj file
- [ ] Build and test form behavior
