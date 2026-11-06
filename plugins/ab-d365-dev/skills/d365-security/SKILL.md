---
name: d365-security
description: Build a D365 Finance & Operations security model following Role → Duty → Privilege → Entry Point. Use whenever the user asks to set up, scaffold, or wire security for a functional area — privileges, duties, roles, securing forms/menu items/data entities, or Maintain vs View access.
---

# D365 F&O: Create Security Model

You are helping create a security model in D365 Finance & Operations following the Role → Duty → Privilege → Entry Point hierarchy.

## Gather Requirements

Ask the user for:
1. **Functional area name** (e.g., `MyArea`)
2. **Entry points to secure** (forms, menu items, data entities)
3. **Access levels needed** (Maintain = full CRUD, View = read-only)
4. **Label file ID** to use
5. **Visual Studio project file path** (.rnrproj)

## Security Hierarchy

```
Role (assigned to users)
  └── Duty (functional grouping)
        └── Privilege (specific permission)
              └── Entry Point (menu item, form, entity)
```

**Best Practice:** Create matching Maintain/View pairs at each level.

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Privilege Templates

### Maintain Privilege (Full CRUD via Menu Item)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaMaintain</Name>
	<Label>@LabelFile:MyAreaMaintainLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyAreaForm</Name>
			<Grant>
				<Correct>Allow</Correct>
				<Create>Allow</Create>
				<Delete>Allow</Delete>
				<Read>Allow</Read>
				<Update>Allow</Update>
			</Grant>
			<ObjectName>MyAreaForm</ObjectName>
			<ObjectType>MenuItemDisplay</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

### View Privilege (Read-Only via Menu Item)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaView</Name>
	<Label>@LabelFile:MyAreaViewLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyAreaForm</Name>
			<Grant>
				<Read>Allow</Read>
			</Grant>
			<ObjectName>MyAreaForm</ObjectName>
			<ObjectType>MenuItemDisplay</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

### Privilege for Action Menu Item (Batch Job)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaProcessRun</Name>
	<Label>@LabelFile:MyAreaProcessRunLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyAreaProcess</Name>
			<Grant>
				<Read>Allow</Read>
			</Grant>
			<ObjectName>MyAreaProcess</ObjectName>
			<ObjectType>MenuItemAction</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

### Privilege for Data Entity

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaEntityMaintain</Name>
	<Label>@LabelFile:MyAreaEntityMaintainLabel</Label>
	<DataEntityPermissions>
		<AxSecurityDataEntityPermission>
			<Grant>
				<Correct>Allow</Correct>
				<Create>Allow</Create>
				<Delete>Allow</Delete>
				<Read>Allow</Read>
				<Update>Allow</Update>
			</Grant>
			<Name>MyAreaEntity</Name>
			<Fields />
			<Methods />
		</AxSecurityDataEntityPermission>
	</DataEntityPermissions>
	<DirectAccessPermissions />
	<EntryPoints />
	<FormControlOverrides />
</AxSecurityPrivilege>
```

### Entry Point Object Types

| ObjectType | Use For |
|------------|---------|
| `MenuItemDisplay` | Display menu items (open forms) |
| `MenuItemAction` | Action menu items (run classes/batch) |
| `MenuItemOutput` | Output menu items (reports) |

## Duty Templates

### Maintain Duty

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityDuty xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaDutyMaintain</Name>
	<Label>@LabelFile:MyAreaDutyMaintainLabel</Label>
	<Privileges>
		<AxSecurityPrivilegeReference>
			<Name>MyAreaMaintain</Name>
		</AxSecurityPrivilegeReference>
		<AxSecurityPrivilegeReference>
			<Name>MyAreaEntityMaintain</Name>
		</AxSecurityPrivilegeReference>
		<AxSecurityPrivilegeReference>
			<Name>MyAreaProcessRun</Name>
		</AxSecurityPrivilegeReference>
	</Privileges>
</AxSecurityDuty>
```

### View Duty

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityDuty xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaDutyView</Name>
	<Label>@LabelFile:MyAreaDutyViewLabel</Label>
	<Privileges>
		<AxSecurityPrivilegeReference>
			<Name>MyAreaView</Name>
		</AxSecurityPrivilegeReference>
		<AxSecurityPrivilegeReference>
			<Name>MyAreaEntityView</Name>
		</AxSecurityPrivilegeReference>
	</Privileges>
</AxSecurityDuty>
```

## Role Templates

### Maintain Role

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityRole xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaRoleMaintain</Name>
	<Label>@LabelFile:MyAreaRoleMaintainLabel</Label>
	<Duties>
		<AxSecurityDutyReference>
			<Name>MyAreaDutyMaintain</Name>
		</AxSecurityDutyReference>
	</Duties>
</AxSecurityRole>
```

### View Role

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityRole xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaRoleView</Name>
	<Label>@LabelFile:MyAreaRoleViewLabel</Label>
	<Duties>
		<AxSecurityDutyReference>
			<Name>MyAreaDutyView</Name>
		</AxSecurityDutyReference>
	</Duties>
</AxSecurityRole>
```

### Role with Multiple Duties

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityRole xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaAdmin</Name>
	<Label>@LabelFile:MyAreaAdminLabel</Label>
	<Duties>
		<AxSecurityDutyReference>
			<Name>MyAreaDutyMaintain</Name>
		</AxSecurityDutyReference>
		<AxSecurityDutyReference>
			<Name>MyAreaSetupDutyMaintain</Name>
		</AxSecurityDutyReference>
		<AxSecurityDutyReference>
			<Name>MyAreaReportsDutyView</Name>
		</AxSecurityDutyReference>
	</Duties>
</AxSecurityRole>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<!-- Privileges -->
<Content Include="AxSecurityPrivilege\MyAreaMaintain.xml">
  <SubType>Content</SubType>
  <Name>MyAreaMaintain</Name>
  <Link>Security Privileges\MyAreaMaintain</Link>
</Content>
<Content Include="AxSecurityPrivilege\MyAreaView.xml">
  <SubType>Content</SubType>
  <Name>MyAreaView</Name>
  <Link>Security Privileges\MyAreaView</Link>
</Content>

<!-- Duties -->
<Content Include="AxSecurityDuty\MyAreaDutyMaintain.xml">
  <SubType>Content</SubType>
  <Name>MyAreaDutyMaintain</Name>
  <Link>Security Duties\MyAreaDutyMaintain</Link>
</Content>
<Content Include="AxSecurityDuty\MyAreaDutyView.xml">
  <SubType>Content</SubType>
  <Name>MyAreaDutyView</Name>
  <Link>Security Duties\MyAreaDutyView</Link>
</Content>

<!-- Roles -->
<Content Include="AxSecurityRole\MyAreaRoleMaintain.xml">
  <SubType>Content</SubType>
  <Name>MyAreaRoleMaintain</Name>
  <Link>Security Roles\MyAreaRoleMaintain</Link>
</Content>
<Content Include="AxSecurityRole\MyAreaRoleView.xml">
  <SubType>Content</SubType>
  <Name>MyAreaRoleView</Name>
  <Link>Security Roles\MyAreaRoleView</Link>
</Content>
```

## Labels

Add to your label file:

```
MyAreaMaintainLabel=Maintain my area data
 ;Privilege for full CRUD on MyArea form
MyAreaViewLabel=View my area data
 ;Privilege for read-only access to MyArea form
MyAreaEntityMaintainLabel=Maintain my area via data entity
 ;Privilege for full CRUD on MyArea data entity
MyAreaEntityViewLabel=View my area via data entity
 ;Privilege for read-only access to MyArea data entity
MyAreaProcessRunLabel=Run my area process
 ;Privilege to execute batch job
MyAreaDutyMaintainLabel=Maintain my area
 ;Duty grouping all maintain privileges
MyAreaDutyViewLabel=View my area
 ;Duty grouping all view privileges
MyAreaRoleMaintainLabel=My area maintainer
 ;Role for users who need edit access
MyAreaRoleViewLabel=My area viewer
 ;Role for users who need read-only access
```

## Naming Conventions

| Artifact | Naming Pattern | Example |
|----------|---------------|---------|
| Maintain Privilege | `<Area>Maintain` | `MyAreaMaintain` |
| View Privilege | `<Area>View` | `MyAreaView` |
| Entity Privilege | `<Entity>Maintain/View` | `MyAreaEntityMaintain` |
| Action Privilege | `<Action>Run` | `MyAreaProcessRun` |
| Maintain Duty | `<Area>DutyMaintain` | `MyAreaDutyMaintain` |
| View Duty | `<Area>DutyView` | `MyAreaDutyView` |
| Maintain Role | `<Area>RoleMaintain` | `MyAreaRoleMaintain` |
| View Role | `<Area>RoleView` | `MyAreaRoleView` |

## Complete Security Model Example

For a functional area with a form, entity, and batch job:

### Privileges (5 total)
1. `MyAreaMaintain` - Form CRUD
2. `MyAreaView` - Form read-only
3. `MyAreaEntityMaintain` - Entity CRUD
4. `MyAreaEntityView` - Entity read-only
5. `MyAreaProcessRun` - Batch job execution

### Duties (2 total)
1. `MyAreaDutyMaintain` - Groups: MyAreaMaintain, MyAreaEntityMaintain, MyAreaProcessRun
2. `MyAreaDutyView` - Groups: MyAreaView, MyAreaEntityView

### Roles (2 total)
1. `MyAreaRoleMaintain` - Contains: MyAreaDutyMaintain
2. `MyAreaRoleView` - Contains: MyAreaDutyView

## Testing Security

1. Build and restart IIS
2. Go to **System administration > Security > Security roles**
3. Find your new role
4. Assign to a test user
5. Log in as test user and verify access

## Checklist

- [ ] Identify all entry points (forms, menu items, entities)
- [ ] Create Maintain and View privileges for each entry point
- [ ] Create Maintain and View duties grouping privileges
- [ ] Create Maintain and View roles grouping duties
- [ ] Add all labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build and test with different user roles
