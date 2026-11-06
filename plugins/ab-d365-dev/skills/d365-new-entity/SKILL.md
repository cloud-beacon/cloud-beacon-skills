---
name: d365-new-entity
description: Create a new Data Entity in D365 Finance & Operations for OData and Data Management Framework (DMF) integration. Use whenever the user asks to create, add, or expose a D365 data entity, OData endpoint, DMF entity, integration entity, or staging-table-backed entity — including key field selection and DMF staging.
---

# D365 F&O: Create Data Entity

You are helping create a Data Entity in D365 Finance & Operations for OData APIs and Data Management Framework (DMF) integration.

## Gather Requirements

Ask the user for:
1. **Entity name** (typically `<TableName>Entity`)
2. **Source table** the entity exposes
3. **Key fields** for the entity (usually the table's natural key)
4. **Fields to expose** (or all fields from source)
5. **OData collection name** (plural, e.g., `MyTableEntities`)
6. **Enable DMF?** (Data Management staging table)
7. **Company-specific?** (cross-company or filtered by DataAreaId)
8. **Label file ID** to use
9. **Visual Studio project file path** (.rnrproj)

## Artifacts to Create

1. **AxDataEntityView** - The data entity definition
2. **AxSecurityPrivilege** - Maintain + View privileges for the entity
3. **Labels** - Add to label file
4. **Update .rnrproj** - Add to VS project

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## AxDataEntityView Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxDataEntityView xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableEntity</Name>
	<SourceCode>
		<Declaration><![CDATA[
public class MyTableEntity extends common
{
}
]]></Declaration>
		<Methods />
	</SourceCode>
	<Label>@LabelFile:MyTableEntityLabel</Label>
	<SubscriberAccessLevel>
		<Read>Allow</Read>
	</SubscriberAccessLevel>
	<DataManagementEnabled>Yes</DataManagementEnabled>
	<DataManagementStagingTable>MyTableStaging</DataManagementStagingTable>
	<IsPublic>Yes</IsPublic>
	<PrimaryCompanyContext>DataAreaId</PrimaryCompanyContext>
	<PrimaryKey>EntityKey</PrimaryKey>
	<PublicCollectionName>MyTableEntities</PublicCollectionName>
	<PublicEntityName>MyTableEntity</PublicEntityName>
	<SupportsSetBasedSqlOperations>Yes</SupportsSetBasedSqlOperations>
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
	</FieldGroups>
	<Fields>
		<!-- Mapped fields go here -->
	</Fields>
	<Keys>
		<AxDataEntityViewKey>
			<Name>EntityKey</Name>
			<Fields>
				<AxDataEntityViewKeyField>
					<DataField>KeyFieldName</DataField>
				</AxDataEntityViewKeyField>
			</Fields>
		</AxDataEntityViewKey>
	</Keys>
	<Mappings />
	<Indexes />
	<Ranges />
	<Relations />
	<StateMachines />
	<ViewMetadata>
		<Name>MyTableEntity</Name>
		<SourceCode>
			<Methods />
		</SourceCode>
		<DataSources>
			<AxQuerySimpleRootDataSource>
				<Name>MyTable</Name>
				<DynamicFields>Yes</DynamicFields>
				<Table>MyTable</Table>
				<DataSources />
			</AxQuerySimpleRootDataSource>
		</DataSources>
	</ViewMetadata>
</AxDataEntityView>
```

### Key Properties Explained

| Property | Purpose |
|----------|---------|
| `DataManagementEnabled` | `Yes` to register with DMF (auto-generates staging table) |
| `DataManagementStagingTable` | Name for the auto-generated staging table |
| `IsPublic` | `Yes` makes entity available via OData |
| `PrimaryCompanyContext` | `DataAreaId` for company-specific; omit for cross-company |
| `PublicEntityName` | Singular name in OData URLs |
| `PublicCollectionName` | Plural name in OData URLs (e.g., `/data/MyTableEntities`) |
| `SupportsSetBasedSqlOperations` | `Yes` for better bulk performance |

### Cross-Company Entity

For tables with `SaveDataPerCompany: No`, omit `PrimaryCompanyContext`:

```xml
<!-- DO NOT include this line for cross-company entities -->
<!-- <PrimaryCompanyContext>DataAreaId</PrimaryCompanyContext> -->
```

### Mapped Field Examples

**Basic mapped field:**
```xml
<AxDataEntityViewField xmlns="" i:type="AxDataEntityViewMappedField">
	<Name>ItemNumber</Name>
	<DataField>ItemNumber</DataField>
	<DataSource>MyTable</DataSource>
</AxDataEntityViewField>
```

**Field with different entity name than table field:**
```xml
<AxDataEntityViewField xmlns="" i:type="AxDataEntityViewMappedField">
	<Name>ProductNumber</Name>
	<DataField>ItemId</DataField>
	<DataSource>MyTable</DataSource>
</AxDataEntityViewField>
```

**Computed/unmapped field (needs X++ method):**
```xml
<AxDataEntityViewField xmlns="" i:type="AxDataEntityViewUnmappedFieldString">
	<Name>ComputedField</Name>
	<IsComputedField>Yes</IsComputedField>
	<ComputedFieldMethod>computeComputedField</ComputedFieldMethod>
</AxDataEntityViewField>
```

Then add method to entity:
```xml
<Methods>
	<Method>
		<Name>computeComputedField</Name>
		<Source><![CDATA[
    private static str computeComputedField()
    {
        // Return computed value
        return '';
    }

]]></Source>
	</Method>
</Methods>
```

### Multi-Table Entity (Joined Data Sources)

```xml
<ViewMetadata>
	<Name>MyCompositeEntity</Name>
	<SourceCode>
		<Methods />
	</SourceCode>
	<DataSources>
		<AxQuerySimpleRootDataSource>
			<Name>MainTable</Name>
			<DynamicFields>Yes</DynamicFields>
			<Table>MainTable</Table>
			<DataSources>
				<AxQuerySimpleEmbeddedDataSource>
					<Name>RelatedTable</Name>
					<DynamicFields>Yes</DynamicFields>
					<Table>RelatedTable</Table>
					<DataSources />
					<Relations>
						<AxQuerySimpleDataSourceRelation>
							<Name>RelationName</Name>
							<Field>MainTableField</Field>
							<JoinDataSource>MainTable</JoinDataSource>
							<RelatedField>RelatedTableField</RelatedField>
						</AxQuerySimpleDataSourceRelation>
					</Relations>
				</AxQuerySimpleEmbeddedDataSource>
			</DataSources>
		</AxQuerySimpleRootDataSource>
	</DataSources>
</ViewMetadata>
```

## Security Privileges for Entity

### Maintain Privilege (Full CRUD)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableEntityMaintain</Name>
	<Label>@LabelFile:MyTableEntityMaintainLabel</Label>
	<DataEntityPermissions>
		<AxSecurityDataEntityPermission>
			<Grant>
				<Correct>Allow</Correct>
				<Create>Allow</Create>
				<Delete>Allow</Delete>
				<Read>Allow</Read>
				<Update>Allow</Update>
			</Grant>
			<Name>MyTableEntity</Name>
			<Fields />
			<Methods />
		</AxSecurityDataEntityPermission>
	</DataEntityPermissions>
	<DirectAccessPermissions />
	<EntryPoints />
	<FormControlOverrides />
</AxSecurityPrivilege>
```

### View Privilege (Read-Only)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableEntityView</Name>
	<Label>@LabelFile:MyTableEntityViewLabel</Label>
	<DataEntityPermissions>
		<AxSecurityDataEntityPermission>
			<Grant>
				<Read>Allow</Read>
			</Grant>
			<Name>MyTableEntity</Name>
			<Fields />
			<Methods />
		</AxSecurityDataEntityPermission>
	</DataEntityPermissions>
	<DirectAccessPermissions />
	<EntryPoints />
	<FormControlOverrides />
</AxSecurityPrivilege>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxDataEntityView\MyTableEntity.xml">
  <SubType>Content</SubType>
  <Name>MyTableEntity</Name>
  <Link>Data Entities\MyTableEntity</Link>
</Content>
<Content Include="AxSecurityPrivilege\MyTableEntityMaintain.xml">
  <SubType>Content</SubType>
  <Name>MyTableEntityMaintain</Name>
  <Link>Security Privileges\MyTableEntityMaintain</Link>
</Content>
<Content Include="AxSecurityPrivilege\MyTableEntityView.xml">
  <SubType>Content</SubType>
  <Name>MyTableEntityView</Name>
  <Link>Security Privileges\MyTableEntityView</Link>
</Content>
```

## Labels

Add to your label file:

```
MyTableEntityLabel=My Table Entity
 ;Data entity for MyTable
MyTableEntityMaintainLabel=Maintain my table entity
 ;Full CRUD access to MyTable via data entity
MyTableEntityViewLabel=View my table entity
 ;Read-only access to MyTable via data entity
```

## Post-Creation Steps

1. **Build** the model in Visual Studio
2. **Sync database** to create the staging table (if DMF enabled)
3. **Restart IIS** (`iisreset`) for OData registration
4. **Test OData:** `https://<environment>/data/MyTableEntities`
5. **Test DMF:** Data Management workspace → Import/Export with the entity

## Common Issues

### Entity Not Appearing in OData
- Verify `IsPublic: Yes`
- Check `PublicEntityName` and `PublicCollectionName` are set
- Restart IIS after build
- Check for build errors

### DMF Import Fails
- Verify `DataManagementEnabled: Yes`
- Check staging table was created (table named in `DataManagementStagingTable`)
- Verify key fields match between entity and staging

### Company Context Issues
- For cross-company data: Remove `PrimaryCompanyContext`
- For company-specific: Include `<PrimaryCompanyContext>DataAreaId</PrimaryCompanyContext>`

## Checklist

- [ ] Create AxDataEntityView with fields, keys, and view metadata
- [ ] Create Maintain and View security privileges
- [ ] Add labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build and sync database
- [ ] Restart IIS
- [ ] Test OData endpoint
- [ ] Test DMF import/export (if applicable)
