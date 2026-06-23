# D365 F&O: Create Menu & Menu Extension

You are helping create menus and menu extensions in D365 Finance & Operations to integrate features into the navigation system.

## Gather Requirements

Ask the user for:
1. **What to add:** New menu, submenu, or extend existing menu
2. **Menu items** to include (forms, actions, reports)
3. **Target location** in navigation (which module/area)
4. **Label file ID** to use
5. **Visual Studio project file path** (.rnrproj)

## Navigation Structure

D365 navigation hierarchy:
```
NavPaneMenu (Dashboard navigation)
├── Module Menus (AccountsPayable, Inventory, etc.)
│   ├── Submenus
│   │   └── Menu Items (Display, Action, Output)
│   └── Menu Items
└── Workspaces
```

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## AxMenu Template (New Menu)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenu xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyAreaMenu</Name>
	<Label>@LabelFile:MyAreaMenuLabel</Label>
	<Elements>
		<AxMenuElement i:type="AxMenuElementSubMenu">
			<Name>SetupSubmenu</Name>
			<Label>@SYS12687</Label>
			<Elements>
				<AxMenuElement i:type="AxMenuElementMenuItemDisplay">
					<Name>MyParametersMenuItem</Name>
					<MenuItemName>MyParameters</MenuItemName>
				</AxMenuElement>
				<AxMenuElement i:type="AxMenuElementMenuItemDisplay">
					<Name>MySetupFormMenuItem</Name>
					<MenuItemName>MySetupForm</MenuItemName>
				</AxMenuElement>
			</Elements>
		</AxMenuElement>
		<AxMenuElement i:type="AxMenuElementSubMenu">
			<Name>PeriodicSubmenu</Name>
			<Label>@SYS10207</Label>
			<Elements>
				<AxMenuElement i:type="AxMenuElementMenuItemAction">
					<Name>MyProcessMenuItem</Name>
					<MenuItemName>MyProcess</MenuItemName>
				</AxMenuElement>
				<AxMenuElement i:type="AxMenuElementMenuItemAction">
					<Name>MyCleanupMenuItem</Name>
					<MenuItemName>MyCleanup</MenuItemName>
				</AxMenuElement>
			</Elements>
		</AxMenuElement>
		<AxMenuElement i:type="AxMenuElementSubMenu">
			<Name>InquiriesSubmenu</Name>
			<Label>@SYS8952</Label>
			<Elements>
				<AxMenuElement i:type="AxMenuElementMenuItemDisplay">
					<Name>MyLogFormMenuItem</Name>
					<MenuItemName>MyLogForm</MenuItemName>
				</AxMenuElement>
			</Elements>
		</AxMenuElement>
	</Elements>
</AxMenu>
```

## Menu Element Types

| i:type | Purpose | Key Property |
|--------|---------|--------------|
| `AxMenuElementMenuItemDisplay` | Opens a form | `MenuItemName` (display menu item) |
| `AxMenuElementMenuItemAction` | Runs a class/batch | `MenuItemName` (action menu item) |
| `AxMenuElementMenuItemOutput` | Runs a report | `MenuItemName` (output menu item) |
| `AxMenuElementSubMenu` | Container for nested items | `Label`, `Elements` |
| `AxMenuElementMenuReference` | Reference to another menu | `MenuName` |
| `AxMenuElementSeparator` | Visual separator line | — |
| `AxMenuElementTile` | Tile (for workspaces) | `Tile` |

### Menu Element Examples

**Display menu item (opens form):**
```xml
<AxMenuElement i:type="AxMenuElementMenuItemDisplay">
	<Name>MyFormMenuItem</Name>
	<MenuItemName>MyForm</MenuItemName>
</AxMenuElement>
```

**Action menu item (runs batch/class):**
```xml
<AxMenuElement i:type="AxMenuElementMenuItemAction">
	<Name>MyProcessMenuItem</Name>
	<MenuItemName>MyProcess</MenuItemName>
</AxMenuElement>
```

**Output menu item (runs report):**
```xml
<AxMenuElement i:type="AxMenuElementMenuItemOutput">
	<Name>MyReportMenuItem</Name>
	<MenuItemName>MyReport</MenuItemName>
</AxMenuElement>
```

**Submenu:**
```xml
<AxMenuElement i:type="AxMenuElementSubMenu">
	<Name>MySubmenu</Name>
	<Label>@LabelFile:MySubmenuLabel</Label>
	<Elements>
		<!-- Child menu elements -->
	</Elements>
</AxMenuElement>
```

**Separator:**
```xml
<AxMenuElement i:type="AxMenuElementSeparator">
	<Name>Separator1</Name>
</AxMenuElement>
```

**Menu reference (include another menu):**
```xml
<AxMenuElement i:type="AxMenuElementMenuReference">
	<Name>IncludedMenuRef</Name>
	<MenuName>AnotherMenu</MenuName>
</AxMenuElement>
```

## AxMenuExtension Template

Use menu extensions to add items to existing menus without modifying the base menu.

### Extending MainMenu

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MainMenu.MyAreaExtension</Name>
	<Customizations />
	<Elements>
		<AxMenuExtensionElement xmlns="">
			<PositionType>AfterItem</PositionType>
			<PreviousSibling>InventoryManagement</PreviousSibling>
			<MenuElement xmlns="" i:type="AxMenuElementMenuReference">
				<Name>MyAreaMenuRef</Name>
				<MenuName>MyAreaMenu</MenuName>
			</MenuElement>
		</AxMenuExtensionElement>
	</Elements>
	<MenuElementModifications />
	<PropertyModifications />
</AxMenuExtension>
```

### Extending a Module Menu

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>InventoryManagement.MyExtension</Name>
	<Customizations />
	<Elements>
		<AxMenuExtensionElement xmlns="">
			<PositionType>AtEnd</PositionType>
			<MenuElement xmlns="" i:type="AxMenuElementSubMenu">
				<Name>MyFeatureSubmenu</Name>
				<Label>@LabelFile:MyFeatureLabel</Label>
				<Elements>
					<AxMenuElement i:type="AxMenuElementMenuItemDisplay">
						<Name>MyFeatureForm</Name>
						<MenuItemName>MyFeatureForm</MenuItemName>
					</AxMenuElement>
				</Elements>
			</MenuElement>
		</AxMenuExtensionElement>
	</Elements>
	<MenuElementModifications />
	<PropertyModifications />
</AxMenuExtension>
```

### Extending NavPaneMenu (Dashboard)

Add workspace or tile to the main navigation:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>NavPaneMenu.MyAreaExtension</Name>
	<Customizations />
	<Elements>
		<AxMenuExtensionElement xmlns="">
			<PositionType>AfterItem</PositionType>
			<PreviousSibling>ProductInformationManagement</PreviousSibling>
			<MenuElement xmlns="" i:type="AxMenuElementMenuItemDisplay">
				<Name>MyWorkspace</Name>
				<MenuItemName>MyWorkspace</MenuItemName>
			</MenuElement>
		</AxMenuExtensionElement>
	</Elements>
	<MenuElementModifications />
	<PropertyModifications />
</AxMenuExtension>
```

## Position Types

| PositionType | Meaning |
|--------------|---------|
| `AfterItem` | Place after `PreviousSibling` |
| `BeforeItem` | Place before `PreviousSibling` |
| `AtStart` | Place at beginning of menu |
| `AtEnd` | Place at end of menu |

## Common Parent Menus

| Menu Name | Purpose |
|-----------|---------|
| `MainMenu` | Top-level module selector |
| `NavPaneMenu` | Dashboard navigation pane |
| `AccountsPayable` | AP module menu |
| `AccountsReceivable` | AR module menu |
| `GeneralLedger` | GL module menu |
| `InventoryManagement` | Inventory module menu |
| `ProductInformationManagement` | PIM module menu |
| `ProcurementAndSourcing` | Procurement module menu |
| `SalesAndMarketing` | Sales module menu |
| `SystemAdministration` | System admin menu |
| `OrganizationAdministration` | Org admin menu |

## Standard Submenu Labels

Use these system labels for consistency:

| Purpose | System Label |
|---------|--------------|
| Setup | `@SYS12687` |
| Periodic tasks | `@SYS10207` |
| Inquiries | `@SYS8952` |
| Reports | `@SYS4711` |
| Journals | `@SYS4539` |

## Menu Item Display Template

Create menu items that point to forms:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuItemDisplay xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyForm</Name>
	<Label>@LabelFile:MyFormLabel</Label>
	<Object>MyForm</Object>
	<SubscriberAccessLevel>
		<Read xmlns="">Allow</Read>
	</SubscriberAccessLevel>
</AxMenuItemDisplay>
```

## Menu Item Action Template

Create menu items that run classes:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuItemAction xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                  xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyProcess</Name>
	<Label>@LabelFile:MyProcessLabel</Label>
	<Object>MyProcessController</Object>
	<ObjectType>Class</ObjectType>
	<Parameters>MyProcessService.run</Parameters>
	<SubscriberAccessLevel>
		<Read xmlns="">Allow</Read>
	</SubscriberAccessLevel>
</AxMenuItemAction>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<!-- Menus -->
<Content Include="AxMenu\MyAreaMenu.xml">
  <SubType>Content</SubType>
  <Name>MyAreaMenu</Name>
  <Link>Menus\MyAreaMenu</Link>
</Content>

<!-- Menu Extensions -->
<Content Include="AxMenuExtension\MainMenu.MyAreaExtension.xml">
  <SubType>Content</SubType>
  <Name>MainMenu.MyAreaExtension</Name>
  <Link>Menu Extensions\MainMenu.MyAreaExtension</Link>
</Content>

<!-- Menu Items (Display) -->
<Content Include="AxMenuItemDisplay\MyForm.xml">
  <SubType>Content</SubType>
  <Name>MyForm</Name>
  <Link>Display Menu Items\MyForm</Link>
</Content>

<!-- Menu Items (Action) -->
<Content Include="AxMenuItemAction\MyProcess.xml">
  <SubType>Content</SubType>
  <Name>MyProcess</Name>
  <Link>Action Menu Items\MyProcess</Link>
</Content>
```

## Labels

Add to your label file:

```
MyAreaMenuLabel=My Area
 ;Module menu label
MyFeatureLabel=My Feature
 ;Submenu label
MyFormLabel=My Form
 ;Display menu item label
MyProcessLabel=Run My Process
 ;Action menu item label
```

## Naming Conventions

| Artifact | Convention | Example |
|----------|------------|---------|
| Menu | `<Area>Menu` | `CloudBeaconMenu` |
| Menu Extension | `<TargetMenu>.<YourPrefix>Extension` | `MainMenu.CloudBeaconExtension` |
| Display Menu Item | Same as form name | `MyProductList` |
| Action Menu Item | Describes action | `RunProductSync` |

## Common Patterns

### Module Menu with Standard Sections

```xml
<AxMenu ...>
	<Name>MyModuleMenu</Name>
	<Label>@LabelFile:MyModuleLabel</Label>
	<Elements>
		<!-- Common/Daily Tasks -->
		<AxMenuElement i:type="AxMenuElementSubMenu">
			<Name>CommonSubmenu</Name>
			<Label>@SYS314717</Label>
			<Elements>
				<!-- Main forms users access daily -->
			</Elements>
		</AxMenuElement>

		<!-- Periodic Tasks -->
		<AxMenuElement i:type="AxMenuElementSubMenu">
			<Name>PeriodicSubmenu</Name>
			<Label>@SYS10207</Label>
			<Elements>
				<!-- Batch jobs, scheduled processes -->
			</Elements>
		</AxMenuElement>

		<!-- Inquiries and Reports -->
		<AxMenuElement i:type="AxMenuElementSubMenu">
			<Name>InquiriesSubmenu</Name>
			<Label>@SYS8952</Label>
			<Elements>
				<!-- Read-only views, logs, history -->
			</Elements>
		</AxMenuElement>

		<!-- Setup -->
		<AxMenuElement i:type="AxMenuElementSubMenu">
			<Name>SetupSubmenu</Name>
			<Label>@SYS12687</Label>
			<Elements>
				<!-- Parameters, configuration tables -->
			</Elements>
		</AxMenuElement>
	</Elements>
</AxMenu>
```

### Adding Feature-Gated Items

Include `FeatureClass` on menu items for Feature Management integration:

```xml
<AxMenuItemDisplay xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyFeatureForm</Name>
	<FeatureClass>MyFeatureClass</FeatureClass>
	<Label>@LabelFile:MyFeatureFormLabel</Label>
	<Object>MyFeatureForm</Object>
	<!-- ... -->
</AxMenuItemDisplay>
```

## Checklist

- [ ] Determine menu structure (new menu vs extension)
- [ ] Create AxMenu or AxMenuExtension
- [ ] Create necessary AxMenuItemDisplay entries
- [ ] Create necessary AxMenuItemAction entries
- [ ] Use appropriate PositionType and PreviousSibling for extensions
- [ ] Add labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build and restart IIS
- [ ] Verify items appear in navigation
