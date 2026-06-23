# D365 F&O: Create Workspace

You are helping create a Workspace in D365 Finance & Operations. Workspaces are role-centric landing pages that aggregate key information, actions, and links for a functional area.

## Gather Requirements

Ask the user for:
1. **Workspace name** (e.g., `MyAreaWorkspace`)
2. **Purpose/functional area** it serves
3. **Key tiles** to display (KPIs, counts, navigation)
4. **Links** to forms/reports
5. **Lists** to show (recent records, pending items, etc.)
6. **Label file ID** to use
7. **Visual Studio project file path** (.rnrproj)

## Artifacts to Create

1. **AxForm** - The workspace form (Pattern: `OperationalWorkspace`)
2. **AxTile** - Tiles for KPIs and navigation (optional)
3. **AxMenuItemDisplay** - Menu item to open the workspace
4. **AxMenuExtension** - Add workspace to navigation (NavPaneMenu)
5. **AxSecurityPrivilege** - Security for the workspace
6. **Labels** - Add to label file

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Workspace Form Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxForm xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
        xmlns="Microsoft.Dynamics.AX.Metadata.V6">
	<Name>MyAreaWorkspace</Name>
	<SourceCode>
		<Methods xmlns="">
			<Method>
				<Name>classDeclaration</Name>
				<Source><![CDATA[
[Form]
public class MyAreaWorkspace extends FormRun
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
		<!-- Add data sources for lists here -->
	</DataSources>
	<Design>
		<Caption xmlns="">@LabelFile:MyAreaWorkspaceCaption</Caption>
		<Pattern xmlns="">OperationalWorkspace</Pattern>
		<PatternVersion xmlns="">1.2</PatternVersion>
		<Style xmlns="">OperationalWorkspace</Style>
		<WorkspaceActivityRequired xmlns="">Yes</WorkspaceActivityRequired>
		<Controls xmlns="">
			<!-- Page Title Group -->
			<AxFormControl xmlns="" i:type="AxFormGroupControl">
				<Name>PageTitleGroup</Name>
				<Pattern>WorkspacePageTitleGroup</Pattern>
				<PatternVersion>1.2</PatternVersion>
				<Type>Group</Type>
				<Controls>
					<AxFormControl xmlns="" i:type="AxFormGroupControl">
						<Name>WorkspaceName</Name>
						<Type>Group</Type>
						<FrameType>None</FrameType>
						<Controls>
							<AxFormControl xmlns="" i:type="AxFormStaticTextControl">
								<Name>WorkspaceNameText</Name>
								<Type>StaticText</Type>
								<Text>@LabelFile:MyAreaWorkspaceCaption</Text>
							</AxFormControl>
						</Controls>
					</AxFormControl>
					<AxFormControl xmlns="" i:type="AxFormGroupControl">
						<Name>WorkspaceActions</Name>
						<Type>Group</Type>
						<Controls />
					</AxFormControl>
				</Controls>
			</AxFormControl>
			<!-- Panorama Body -->
			<AxFormControl xmlns="" i:type="AxFormGroupControl">
				<Name>PanoramaBody</Name>
				<Type>Group</Type>
				<Style>PanoramaBody</Style>
				<Controls>
					<!-- Summary Section (Tiles) -->
					<AxFormControl xmlns="" i:type="AxFormGroupControl">
						<Name>SummarySection</Name>
						<Pattern>Section</Pattern>
						<PatternVersion>1.2</PatternVersion>
						<Type>Group</Type>
						<Controls>
							<AxFormControl xmlns="" i:type="AxFormGroupControl">
								<Name>SummarySectionHeader</Name>
								<Type>Group</Type>
								<Controls>
									<AxFormControl xmlns="" i:type="AxFormStaticTextControl">
										<Name>SummarySectionTitle</Name>
										<Type>StaticText</Type>
										<Text>@SYS313338</Text>
									</AxFormControl>
								</Controls>
							</AxFormControl>
							<AxFormControl xmlns="" i:type="AxFormGroupControl">
								<Name>SummarySectionBody</Name>
								<Type>Group</Type>
								<Controls>
									<AxFormControl xmlns="" i:type="AxFormGroupControl">
										<Name>SummarySectionTiles</Name>
										<Pattern>TileContainer</Pattern>
										<PatternVersion>1.2</PatternVersion>
										<Type>Group</Type>
										<Controls>
											<!-- Tiles go here -->
										</Controls>
									</AxFormControl>
								</Controls>
							</AxFormControl>
						</Controls>
					</AxFormControl>
					<!-- Tabbed Lists Section -->
					<AxFormControl xmlns="" i:type="AxFormGroupControl">
						<Name>TabbedListSection</Name>
						<Pattern>Section</Pattern>
						<PatternVersion>1.2</PatternVersion>
						<Type>Group</Type>
						<Controls>
							<AxFormControl xmlns="" i:type="AxFormGroupControl">
								<Name>TabbedListSectionHeader</Name>
								<Type>Group</Type>
								<Controls>
									<AxFormControl xmlns="" i:type="AxFormStaticTextControl">
										<Name>TabbedListSectionTitle</Name>
										<Type>StaticText</Type>
										<Text>@LabelFile:RecordsLabel</Text>
									</AxFormControl>
								</Controls>
							</AxFormControl>
							<AxFormControl xmlns="" i:type="AxFormGroupControl">
								<Name>TabbedListSectionBody</Name>
								<Type>Group</Type>
								<Controls>
									<AxFormControl xmlns="" i:type="AxFormTabControl">
										<Name>TabbedLists</Name>
										<Pattern>TabbedList</Pattern>
										<PatternVersion>1.2</PatternVersion>
										<Type>Tab</Type>
										<Controls>
											<AxFormControl xmlns="" i:type="AxFormTabPageControl">
												<Name>RecentTab</Name>
												<Pattern>TabularList</Pattern>
												<PatternVersion>1.2</PatternVersion>
												<Type>TabPage</Type>
												<Caption>@LabelFile:RecentLabel</Caption>
												<Controls>
													<AxFormControl xmlns="" i:type="AxFormGroupControl">
														<Name>RecentFilters</Name>
														<Type>Group</Type>
														<Controls />
													</AxFormControl>
													<AxFormControl xmlns="" i:type="AxFormGridControl">
														<Name>RecentGrid</Name>
														<Type>Grid</Type>
														<Controls>
															<!-- Grid columns -->
														</Controls>
														<DataSource>MyTableRecent</DataSource>
													</AxFormControl>
												</Controls>
											</AxFormControl>
										</Controls>
									</AxFormControl>
								</Controls>
							</AxFormControl>
						</Controls>
					</AxFormControl>
					<!-- Links Section -->
					<AxFormControl xmlns="" i:type="AxFormGroupControl">
						<Name>LinksSection</Name>
						<Pattern>Section</Pattern>
						<PatternVersion>1.2</PatternVersion>
						<Type>Group</Type>
						<Controls>
							<AxFormControl xmlns="" i:type="AxFormGroupControl">
								<Name>LinksSectionHeader</Name>
								<Type>Group</Type>
								<Controls>
									<AxFormControl xmlns="" i:type="AxFormStaticTextControl">
										<Name>LinksSectionTitle</Name>
										<Type>StaticText</Type>
										<Text>@SYS126618</Text>
									</AxFormControl>
								</Controls>
							</AxFormControl>
							<AxFormControl xmlns="" i:type="AxFormGroupControl">
								<Name>LinksSectionBody</Name>
								<Type>Group</Type>
								<Controls>
									<AxFormControl xmlns="" i:type="AxFormGroupControl">
										<Name>LinksGroup</Name>
										<Pattern>Links</Pattern>
										<PatternVersion>1.2</PatternVersion>
										<Type>Group</Type>
										<Controls>
											<!-- Link buttons go here -->
										</Controls>
									</AxFormControl>
								</Controls>
							</AxFormControl>
						</Controls>
					</AxFormControl>
				</Controls>
			</AxFormControl>
		</Controls>
	</Design>
</AxForm>
```

## Workspace Sections

### Summary Section (Tiles)

Add tile buttons inside `SummarySectionTiles`:

```xml
<AxFormControl xmlns="" i:type="AxFormGroupControl">
	<Name>SummarySectionTiles</Name>
	<Pattern>TileContainer</Pattern>
	<PatternVersion>1.2</PatternVersion>
	<Type>Group</Type>
	<Controls>
		<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
			<Name>NewRecordsTile</Name>
			<Type>MenuFunctionButton</Type>
			<ButtonDisplay>TextAndImageAbove</ButtonDisplay>
			<MenuItemName>MyAreaNewRecords</MenuItemName>
			<MenuItemType>Display</MenuItemType>
			<NormalImage>365_Line_TileCount</NormalImage>
			<Text>@LabelFile:NewRecordsLabel</Text>
			<Tile>Yes</Tile>
			<TileDisplay>TextOnly</TileDisplay>
		</AxFormControl>
		<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
			<Name>PendingTile</Name>
			<Type>MenuFunctionButton</Type>
			<ButtonDisplay>TextAndImageAbove</ButtonDisplay>
			<MenuItemName>MyAreaPending</MenuItemName>
			<MenuItemType>Display</MenuItemType>
			<NormalImage>365_Line_TileCount</NormalImage>
			<Text>@LabelFile:PendingLabel</Text>
			<Tile>Yes</Tile>
			<TileDisplay>TextOnly</TileDisplay>
		</AxFormControl>
	</Controls>
</AxFormControl>
```

### Links Section

Add link buttons inside `LinksGroup`:

```xml
<AxFormControl xmlns="" i:type="AxFormGroupControl">
	<Name>LinksGroup</Name>
	<Pattern>Links</Pattern>
	<PatternVersion>1.2</PatternVersion>
	<Type>Group</Type>
	<Controls>
		<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
			<Name>AllRecordsLink</Name>
			<Type>MenuFunctionButton</Type>
			<MenuItemName>MyTableForm</MenuItemName>
			<MenuItemType>Display</MenuItemType>
			<Text>@LabelFile:AllRecordsLabel</Text>
		</AxFormControl>
		<AxFormControl xmlns="" i:type="AxFormMenuFunctionButtonControl">
			<Name>ParametersLink</Name>
			<Type>MenuFunctionButton</Type>
			<MenuItemName>MyAreaParameters</MenuItemName>
			<MenuItemType>Display</MenuItemType>
			<Text>@LabelFile:ParametersLabel</Text>
		</AxFormControl>
	</Controls>
</AxFormControl>
```

### Data Source for Lists

Add data sources for workspace lists:

```xml
<DataSources>
	<AxFormDataSource xmlns="">
		<Name>MyTableRecent</Name>
		<Table>MyTable</Table>
		<InsertAtEnd>No</InsertAtEnd>
		<InsertIfEmpty>No</InsertIfEmpty>
		<AllowCreate>No</AllowCreate>
		<AllowDelete>No</AllowDelete>
		<Fields />
		<ReferencedDataSources />
		<DataSourceLinks />
		<DerivedDataSources />
	</AxFormDataSource>
</DataSources>
```

## AxTile Template (Optional - for KPI Tiles)

For tiles that show calculated values (counts, KPIs):

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxTile xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaNewRecordsTile</Name>
	<Label>@LabelFile:NewRecordsLabel</Label>
	<Query>MyAreaNewRecordsQuery</Query>
	<Refresh>60</Refresh>
	<Size>Half</Size>
	<TileDisplay>Auto</TileDisplay>
	<Type>Count</Type>
</AxTile>
```

**Tile Properties:**

| Property | Values | Description |
|----------|--------|-------------|
| `Size` | `Half`, `Regular`, `Wide`, `Tall` | Tile size |
| `Type` | `Count`, `Sum`, `Average`, `Min`, `Max`, `Link` | What value to show |
| `TileDisplay` | `Auto`, `TextOnly`, `BackgroundImage` | Visual style |
| `Refresh` | number | Refresh interval in seconds |
| `Query` | query name | Query to count/aggregate |

## Menu Item for Workspace

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuItemDisplay xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyAreaWorkspace</Name>
	<Label>@LabelFile:MyAreaWorkspaceCaption</Label>
	<Object>MyAreaWorkspace</Object>
	<SubscriberAccessLevel>
		<Read xmlns="">Allow</Read>
	</SubscriberAccessLevel>
</AxMenuItemDisplay>
```

## Adding Workspace to Navigation (Dashboard)

To add your workspace to the dashboard/navigation, extend `NavPaneMenu`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuExtension xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>NavPaneMenu.MyAreaExtension</Name>
	<Customizations />
	<Elements>
		<AxMenuExtensionElement xmlns="">
			<PositionType>AfterItem</PositionType>
			<PreviousSibling>AccountsPayable</PreviousSibling>
			<MenuElement xmlns="" i:type="AxMenuElementMenuItemDisplay">
				<Name>MyAreaWorkspace</Name>
				<MenuItemName>MyAreaWorkspace</MenuItemName>
			</MenuElement>
		</AxMenuExtensionElement>
	</Elements>
	<MenuElementModifications />
	<PropertyModifications />
</AxMenuExtension>
```

**Note:** `NavPaneMenu` is the main navigation pane. Use `PreviousSibling` to position your workspace near related modules.

### Adding Workspace Tile to Dashboard

To add a tile for your workspace on the dashboard:

```xml
<AxMenuExtensionElement xmlns="">
	<PositionType>AtEnd</PositionType>
	<MenuElement xmlns="" i:type="AxMenuElementTile">
		<Name>MyAreaWorkspaceTile</Name>
		<Tile>MyAreaWorkspaceTile</Tile>
	</MenuElement>
</AxMenuExtensionElement>
```

This requires creating an AxTile with `Type="Link"` pointing to your workspace.

## Security Privilege

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyAreaWorkspaceView</Name>
	<Label>@LabelFile:MyAreaWorkspaceViewLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyAreaWorkspace</Name>
			<Grant>
				<Read>Allow</Read>
			</Grant>
			<ObjectName>MyAreaWorkspace</ObjectName>
			<ObjectType>MenuItemDisplay</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxForm\MyAreaWorkspace.xml">
  <SubType>Content</SubType>
  <Name>MyAreaWorkspace</Name>
  <Link>Forms\MyAreaWorkspace</Link>
</Content>
<Content Include="AxMenuItemDisplay\MyAreaWorkspace.xml">
  <SubType>Content</SubType>
  <Name>MyAreaWorkspace</Name>
  <Link>Display Menu Items\MyAreaWorkspace</Link>
</Content>
<Content Include="AxMenuExtension\NavPaneMenu.MyAreaExtension.xml">
  <SubType>Content</SubType>
  <Name>NavPaneMenu.MyAreaExtension</Name>
  <Link>Menu Extensions\NavPaneMenu.MyAreaExtension</Link>
</Content>
<Content Include="AxSecurityPrivilege\MyAreaWorkspaceView.xml">
  <SubType>Content</SubType>
  <Name>MyAreaWorkspaceView</Name>
  <Link>Security Privileges\MyAreaWorkspaceView</Link>
</Content>
```

If using tiles:
```xml
<Content Include="AxTile\MyAreaNewRecordsTile.xml">
  <SubType>Content</SubType>
  <Name>MyAreaNewRecordsTile</Name>
  <Link>Tiles\MyAreaNewRecordsTile</Link>
</Content>
```

## Labels

Add to your label file:

```
MyAreaWorkspaceCaption=My Area
 ;Workspace title
NewRecordsLabel=New records
 ;Tile label
PendingLabel=Pending
 ;Tile label
RecordsLabel=Records
 ;Section header
RecentLabel=Recent
 ;Tab label
AllRecordsLabel=All records
 ;Link label
ParametersLabel=Parameters
 ;Link label
MyAreaWorkspaceViewLabel=View my area workspace
 ;Security privilege label
```

## Workspace Pattern Requirements

The `OperationalWorkspace` pattern expects this structure:

```
Form
├── PageTitleGroup (WorkspacePageTitleGroup pattern)
│   ├── WorkspaceName group
│   │   └── StaticText with title
│   └── WorkspaceActions group (optional buttons)
└── PanoramaBody
    ├── SummarySection (Section pattern) - Tiles
    │   ├── Header with title
    │   └── Body with TileContainer
    ├── TabbedListSection (Section pattern) - Lists
    │   ├── Header with title
    │   └── Body with TabbedList
    └── LinksSection (Section pattern) - Links
        ├── Header with title
        └── Body with Links group
```

## Common Gotchas

### Workspace Not Appearing in Navigation
- Verify `NavPaneMenu` extension is correctly named: `NavPaneMenu.YourExtension`
- Check `PreviousSibling` references an existing menu element
- Rebuild and restart IIS
- Clear browser cache

### Tiles Not Showing Values
- Tiles with `Type="Count"` need a valid Query
- Verify query returns results
- Check `Refresh` interval

### Pattern Validation Warnings
- Each section must follow the Section pattern exactly
- TileContainer, TabbedList, and Links have specific sub-patterns
- Check Visual Studio for pattern compliance warnings

## Checklist

- [ ] Create workspace AxForm with OperationalWorkspace pattern
- [ ] Add data sources for any lists
- [ ] Add tile buttons in SummarySection (or AxTile artifacts)
- [ ] Add tabbed lists with grids
- [ ] Add navigation links
- [ ] Create AxMenuItemDisplay for the workspace
- [ ] Create NavPaneMenu extension to add to navigation
- [ ] Create security privilege
- [ ] Add all labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build and restart IIS
- [ ] Test workspace appears in navigation
- [ ] Test all tiles and links work
