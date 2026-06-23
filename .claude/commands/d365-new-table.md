# D365 F&O: Create New Table End-to-End

You are helping create a new table in D365 Finance & Operations with full UI and security integration.

## Gather Requirements

Ask the user for:
1. **Table name** (use their naming prefix, e.g., `myTable`)
2. **Purpose/description** of the table
3. **Key fields** needed (names, types, whether mandatory)
4. **Table group** (Main, Transaction, WorksheetHeader, WorksheetLine, Reference, Parameter, Group, Miscellaneous)
5. **Company-specific?** (SaveDataPerCompany: Yes/No)
6. **Label file ID** to use for labels
7. **Visual Studio project file path** (.rnrproj) to add artifacts to

## Artifacts to Create

Create these in order:

1. **AxTable** - Table metadata with fields, indexes, field groups
2. **AxForm** - Form to display/edit data (SimpleList or SimpleListDetails pattern)
3. **AxMenuItemDisplay** - Menu item to open the form
4. **AxSecurityPrivilege** - Maintain + View privileges
5. **AxSecurityDuty** - Duties grouping the privileges
6. **Labels** - Add to the label .txt file

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## AxTable Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTable xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTable</Name>
	<SourceCode>
		<Declaration><![CDATA[public class MyTable extends common { }]]></Declaration>
		<Methods />
	</SourceCode>
	<Label>@LabelFile:MyTableLabel</Label>
	<DeveloperDocumentation>@LabelFile:MyTableDevDoc</DeveloperDocumentation>
	<FormRef>MyTableForm</FormRef>
	<SubscriberAccessLevel>
		<Read>Allow</Read>
	</SubscriberAccessLevel>
	<TableGroup>Main</TableGroup>
	<TitleField1>KeyFieldName</TitleField1>
	<ReplacementKey>KeyFieldIdx</ReplacementKey>
	<AllowRowVersionChangeTracking>Yes</AllowRowVersionChangeTracking>
	<CacheLookup>Found</CacheLookup>
	<ClusteredIndex>KeyFieldIdx</ClusteredIndex>
	<ModifiedDateTime>Yes</ModifiedDateTime>
	<PrimaryIndex>KeyFieldIdx</PrimaryIndex>
	<SaveDataPerCompany>Yes</SaveDataPerCompany>
	<DeleteActions />
	<FieldGroups>
		<AxTableFieldGroup>
			<Name>AutoReport</Name>
			<Fields />
		</AxTableFieldGroup>
		<AxTableFieldGroup>
			<Name>AutoLookup</Name>
			<Fields />
		</AxTableFieldGroup>
		<AxTableFieldGroup>
			<Name>AutoIdentification</Name>
			<AutoPopulate>Yes</AutoPopulate>
			<Fields />
		</AxTableFieldGroup>
		<AxTableFieldGroup>
			<Name>AutoSummary</Name>
			<Fields />
		</AxTableFieldGroup>
		<AxTableFieldGroup>
			<Name>AutoBrowse</Name>
			<Fields />
		</AxTableFieldGroup>
		<AxTableFieldGroup>
			<Name>Overview</Name>
			<Label>@SYS9039</Label>
			<Fields>
				<!-- Add AxTableFieldGroupField entries here -->
			</Fields>
		</AxTableFieldGroup>
	</FieldGroups>
	<Fields>
		<!-- Add field definitions here -->
	</Fields>
	<FullTextIndexes />
	<Indexes>
		<AxTableIndex>
			<Name>KeyFieldIdx</Name>
			<AlternateKey>Yes</AlternateKey>
			<Fields>
				<AxTableIndexField>
					<DataField>KeyFieldName</DataField>
				</AxTableIndexField>
			</Fields>
		</AxTableIndex>
	</Indexes>
	<Mappings />
	<Relations />
	<StateMachines />
</AxTable>
```

### Field Type Examples

**String field:**
```xml
<AxTableField xmlns="" i:type="AxTableFieldString">
	<Name>ItemNumber</Name>
	<AllowEdit>No</AllowEdit>
	<ExtendedDataType>ItemId</ExtendedDataType>
	<Mandatory>Yes</Mandatory>
</AxTableField>
```

**Integer field:**
```xml
<AxTableField xmlns="" i:type="AxTableFieldInt">
	<Name>Quantity</Name>
	<ExtendedDataType>Qty</ExtendedDataType>
</AxTableField>
```

**Enum field:**
```xml
<AxTableField xmlns="" i:type="AxTableFieldEnum">
	<Name>Status</Name>
	<EnumType>MyStatusEnum</EnumType>
</AxTableField>
```

**DateTime field:**
```xml
<AxTableField xmlns="" i:type="AxTableFieldUtcDateTime">
	<Name>ProcessedDateTime</Name>
	<ExtendedDataType>TransDateTime</ExtendedDataType>
</AxTableField>
```

**Int64 field (RecId references):**
```xml
<AxTableField xmlns="" i:type="AxTableFieldInt64">
	<Name>RelatedRecId</Name>
	<ExtendedDataType>RefRecId</ExtendedDataType>
</AxTableField>
```

**Critical:** Field elements require `xmlns=""` alongside the `i:type` attribute.

### Field Group Field Entry

```xml
<AxTableFieldGroupField>
	<DataField>FieldName</DataField>
</AxTableFieldGroupField>
```

## AxForm Template (SimpleList)

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
				<Controls />
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
					<!-- Add bound controls here -->
				</Controls>
				<DataSource>MyTable</DataSource>
			</AxFormControl>
		</Controls>
	</Design>
</AxForm>
```

### Grid Field Control (String)

```xml
<AxFormControl xmlns="" i:type="AxFormStringControl">
	<Name>MyTable_FieldName</Name>
	<Type>String</Type>
	<DataField>FieldName</DataField>
	<DataSource>MyTable</DataSource>
</AxFormControl>
```

**Note:** Integer fields use `AxFormIntegerControl` (NOT `AxFormIntControl` - that's invalid).

## AxMenuItemDisplay Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuItemDisplay xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyTableForm</Name>
	<Label>@LabelFile:MyTableMenuItemLabel</Label>
	<Object>MyTableForm</Object>
	<SubscriberAccessLevel>
		<Read xmlns="">Allow</Read>
	</SubscriberAccessLevel>
</AxMenuItemDisplay>
```

## Security Templates

### Maintain Privilege

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableMaintain</Name>
	<Label>@LabelFile:MyTableMaintainLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyTableForm</Name>
			<Grant>
				<Correct>Allow</Correct>
				<Create>Allow</Create>
				<Delete>Allow</Delete>
				<Read>Allow</Read>
				<Update>Allow</Update>
			</Grant>
			<ObjectName>MyTableForm</ObjectName>
			<ObjectType>MenuItemDisplay</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

### View Privilege

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableView</Name>
	<Label>@LabelFile:MyTableViewLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyTableForm</Name>
			<Grant>
				<Read>Allow</Read>
			</Grant>
			<ObjectName>MyTableForm</ObjectName>
			<ObjectType>MenuItemDisplay</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

### Duty

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityDuty xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableDutyMaintain</Name>
	<Label>@LabelFile:MyTableDutyMaintainLabel</Label>
	<Privileges>
		<AxSecurityPrivilegeReference>
			<Name>MyTableMaintain</Name>
		</AxSecurityPrivilegeReference>
	</Privileges>
</AxSecurityDuty>
```

## Visual Studio Project File (.rnrproj)

After creating all artifacts, add them to the Visual Studio project file:

```xml
<ItemGroup>
  <Content Include="AxTable\MyTable.xml">
    <SubType>Content</SubType>
    <Name>MyTable</Name>
    <Link>Tables\MyTable</Link>
  </Content>
  <Content Include="AxForm\MyTableForm.xml">
    <SubType>Content</SubType>
    <Name>MyTableForm</Name>
    <Link>Forms\MyTableForm</Link>
  </Content>
  <Content Include="AxMenuItemDisplay\MyTableForm.xml">
    <SubType>Content</SubType>
    <Name>MyTableForm</Name>
    <Link>Display Menu Items\MyTableForm</Link>
  </Content>
  <Content Include="AxSecurityPrivilege\MyTableMaintain.xml">
    <SubType>Content</SubType>
    <Name>MyTableMaintain</Name>
    <Link>Security Privileges\MyTableMaintain</Link>
  </Content>
  <Content Include="AxSecurityPrivilege\MyTableView.xml">
    <SubType>Content</SubType>
    <Name>MyTableView</Name>
    <Link>Security Privileges\MyTableView</Link>
  </Content>
  <Content Include="AxSecurityDuty\MyTableDutyMaintain.xml">
    <SubType>Content</SubType>
    <Name>MyTableDutyMaintain</Name>
    <Link>Security Duties\MyTableDutyMaintain</Link>
  </Content>
</ItemGroup>
```

**Link folder names:** `Tables\`, `Forms\`, `Display Menu Items\`, `Action Menu Items\`, `Security Privileges\`, `Security Duties\`, `Classes\`, `Base Enums\`, `Extended Data Types\`, `Data Entities\`

## Labels

Add entries to your label file (e.g., `AxLabelFile/LabelResources/en-US/MyLabels.en-US.label.txt`):

```
MyTableLabel=My Table
 ;The display name for MyTable
MyTableDevDoc=Table storing my data
 ;Developer documentation for MyTable
MyTableFormCaption=My Table List
 ;Form caption for MyTable form
MyTableMenuItemLabel=My Table
 ;Menu item label
MyTableMaintainLabel=Maintain my table data
 ;Maintain privilege label
MyTableViewLabel=View my table data
 ;View privilege label
MyTableDutyMaintainLabel=Maintain my table
 ;Maintain duty label
```

**Rules:**
- Each label: `key=value` on one line
- Comment on next line: ` ;Comment` (space before semicolon)
- Reference in XML: `@LabelFileId:key`
- Label files also need CRLF line endings

## Checklist

- [ ] Create AxTable with fields, indexes, field groups
- [ ] Create AxForm with data source and grid
- [ ] Create AxMenuItemDisplay pointing to form
- [ ] Create Maintain and View privileges
- [ ] Create duties grouping privileges
- [ ] Add all labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build in Visual Studio and verify
