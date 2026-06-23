# D365 F&O: Create Query

You are helping create a query in D365 Finance & Operations. Queries define reusable data retrieval logic for forms, reports, tiles, and data entities.

## Gather Requirements

Ask the user for:
1. **Query name** (e.g., `MyTableQuery`)
2. **Root table(s)** to query
3. **Joins** needed (related tables)
4. **Filters/ranges** to apply
5. **Fields** to include (or all fields)
6. **Sort order**
7. **Visual Studio project file path** (.rnrproj)

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## AxQuery Template (Simple)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxQuery xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableQuery</Name>
	<Title>@LabelFile:MyTableQueryTitle</Title>
	<DataSources>
		<AxQuerySimpleRootDataSource>
			<Name>MyTable</Name>
			<DynamicFields>Yes</DynamicFields>
			<Table>MyTable</Table>
			<DataSources />
			<Fields />
			<Ranges />
			<Sorting>
				<AxQuerySimpleSorting>
					<Field>CreatedDateTime</Field>
					<Order>Descending</Order>
				</AxQuerySimpleSorting>
			</Sorting>
		</AxQuerySimpleRootDataSource>
	</DataSources>
</AxQuery>
```

## Query With Joins

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxQuery xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyOrderQuery</Name>
	<Title>@LabelFile:MyOrderQueryTitle</Title>
	<DataSources>
		<AxQuerySimpleRootDataSource>
			<Name>OrderHeader</Name>
			<DynamicFields>Yes</DynamicFields>
			<Table>SalesTable</Table>
			<DataSources>
				<AxQuerySimpleEmbeddedDataSource>
					<Name>OrderLines</Name>
					<DynamicFields>Yes</DynamicFields>
					<Table>SalesLine</Table>
					<JoinMode>InnerJoin</JoinMode>
					<DataSources />
					<Fields />
					<Ranges />
					<Relations>
						<AxQuerySimpleDataSourceRelation>
							<Name>SalesIdRelation</Name>
							<Field>SalesId</Field>
							<JoinDataSource>OrderHeader</JoinDataSource>
							<RelatedField>SalesId</RelatedField>
						</AxQuerySimpleDataSourceRelation>
					</Relations>
					<Sorting />
				</AxQuerySimpleEmbeddedDataSource>
			</DataSources>
			<Fields />
			<Ranges />
			<Sorting />
		</AxQuerySimpleRootDataSource>
	</DataSources>
</AxQuery>
```

## Query Properties

### Join Modes

| JoinMode | SQL Equivalent | Use Case |
|----------|---------------|----------|
| `InnerJoin` | INNER JOIN | Only matching records |
| `OuterJoin` | LEFT OUTER JOIN | All parent + matching child |
| `ExistsJoin` | EXISTS subquery | Filter parent by child existence |
| `NotExistsJoin` | NOT EXISTS subquery | Filter parent by child absence |

### Dynamic Fields

| Value | Behavior |
|-------|----------|
| `Yes` | Include all table fields |
| `No` | Only explicitly listed fields |

## Adding Ranges (Filters)

```xml
<Ranges>
	<AxQuerySimpleDataSourceRange>
		<Name>StatusRange</Name>
		<Field>Status</Field>
		<Value>Open,InProgress</Value>
	</AxQuerySimpleDataSourceRange>
	<AxQuerySimpleDataSourceRange>
		<Name>ActiveRange</Name>
		<Field>IsActive</Field>
		<Value>1</Value>
	</AxQuerySimpleDataSourceRange>
</Ranges>
```

### Range Value Syntax

| Pattern | Meaning |
|---------|---------|
| `value` | Equals |
| `!value` | Not equals |
| `value1..value2` | Range |
| `>value` | Greater than |
| `>=value` | Greater than or equal |
| `<value` | Less than |
| `<=value` | Less than or equal |
| `*value*` | Contains |
| `value*` | Starts with |
| `value1,value2` | In list |

## Adding Sorting

```xml
<Sorting>
	<AxQuerySimpleSorting>
		<Field>CreatedDateTime</Field>
		<Order>Descending</Order>
	</AxQuerySimpleSorting>
	<AxQuerySimpleSorting>
		<Field>Name</Field>
		<Order>Ascending</Order>
	</AxQuerySimpleSorting>
</Sorting>
```

## Specifying Fields (When DynamicFields=No)

```xml
<Fields>
	<AxQuerySimpleDataSourceField>
		<Field>RecId</Field>
	</AxQuerySimpleDataSourceField>
	<AxQuerySimpleDataSourceField>
		<Field>ItemNumber</Field>
	</AxQuerySimpleDataSourceField>
	<AxQuerySimpleDataSourceField>
		<Field>Status</Field>
	</AxQuerySimpleDataSourceField>
</Fields>
```

## Query With Aggregation

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxQuery xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyCountQuery</Name>
	<Title>@LabelFile:MyCountQueryTitle</Title>
	<DataSources>
		<AxQuerySimpleRootDataSource>
			<Name>MyTable</Name>
			<DynamicFields>No</DynamicFields>
			<Table>MyTable</Table>
			<DataSources />
			<Fields>
				<AxQuerySimpleDataSourceField>
					<Field>RecId</Field>
					<SelectionField>Count</SelectionField>
				</AxQuerySimpleDataSourceField>
			</Fields>
			<Ranges>
				<AxQuerySimpleDataSourceRange>
					<Name>PendingStatus</Name>
					<Field>Status</Field>
					<Value>Pending</Value>
				</AxQuerySimpleDataSourceRange>
			</Ranges>
			<Sorting />
		</AxQuerySimpleRootDataSource>
	</DataSources>
</AxQuery>
```

### Selection Field (Aggregation)

| SelectionField | SQL Function |
|----------------|--------------|
| `Count` | COUNT() |
| `Sum` | SUM() |
| `Avg` | AVG() |
| `Max` | MAX() |
| `Min` | MIN() |

## Complex Query Example

Query with multiple joins and ranges:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxQuery xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>PendingOrdersQuery</Name>
	<Title>Pending Orders</Title>
	<DataSources>
		<AxQuerySimpleRootDataSource>
			<Name>SalesHeader</Name>
			<DynamicFields>Yes</DynamicFields>
			<Table>SalesTable</Table>
			<DataSources>
				<AxQuerySimpleEmbeddedDataSource>
					<Name>SalesLines</Name>
					<DynamicFields>Yes</DynamicFields>
					<Table>SalesLine</Table>
					<JoinMode>InnerJoin</JoinMode>
					<DataSources />
					<Fields />
					<Ranges />
					<Relations>
						<AxQuerySimpleDataSourceRelation>
							<Name>SalesIdRel</Name>
							<Field>SalesId</Field>
							<JoinDataSource>SalesHeader</JoinDataSource>
							<RelatedField>SalesId</RelatedField>
						</AxQuerySimpleDataSourceRelation>
					</Relations>
					<Sorting />
				</AxQuerySimpleEmbeddedDataSource>
				<AxQuerySimpleEmbeddedDataSource>
					<Name>Customer</Name>
					<DynamicFields>Yes</DynamicFields>
					<Table>CustTable</Table>
					<JoinMode>OuterJoin</JoinMode>
					<DataSources />
					<Fields />
					<Ranges />
					<Relations>
						<AxQuerySimpleDataSourceRelation>
							<Name>CustAccountRel</Name>
							<Field>CustAccount</Field>
							<JoinDataSource>SalesHeader</JoinDataSource>
							<RelatedField>CustAccount</RelatedField>
						</AxQuerySimpleDataSourceRelation>
					</Relations>
					<Sorting />
				</AxQuerySimpleEmbeddedDataSource>
			</DataSources>
			<Fields />
			<Ranges>
				<AxQuerySimpleDataSourceRange>
					<Name>StatusRange</Name>
					<Field>SalesStatus</Field>
					<Value>None,Backorder</Value>
				</AxQuerySimpleDataSourceRange>
			</Ranges>
			<Sorting>
				<AxQuerySimpleSorting>
					<Field>CreatedDateTime</Field>
					<Order>Descending</Order>
				</AxQuerySimpleSorting>
			</Sorting>
		</AxQuerySimpleRootDataSource>
	</DataSources>
</AxQuery>
```

## Using Queries

### In X++ Code

```xpp
Query query = new Query(queryStr(MyTableQuery));
QueryRun queryRun = new QueryRun(query);

// Add runtime range
QueryBuildDataSource qbds = query.dataSourceTable(tableNum(MyTable));
qbds.addRange(fieldNum(MyTable, Status)).value(queryValue(MyStatus::Pending));

while (queryRun.next())
{
    MyTable record = queryRun.get(tableNum(MyTable));
    // Process record
}
```

### In Form Data Source

```xpp
public void init()
{
    super();

    // Override form query
    QueryBuildDataSource qbds = this.query().dataSourceTable(tableNum(MyTable));
    qbds.addRange(fieldNum(MyTable, Status)).value(queryValue(MyStatus::Active));
}
```

### For Tiles (Count Query)

Reference in AxTile:
```xml
<AxTile>
	<Name>PendingItemsTile</Name>
	<Label>@LabelFile:PendingItems</Label>
	<Query>MyPendingCountQuery</Query>
	<Type>Count</Type>
</AxTile>
```

### For Data Entities

Reference in ViewMetadata:
```xml
<ViewMetadata>
	<Name>MyEntity</Name>
	<Query>MyEntityQuery</Query>
</ViewMetadata>
```

Or use inline DataSources (more common for entities).

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxQuery\MyTableQuery.xml">
  <SubType>Content</SubType>
  <Name>MyTableQuery</Name>
  <Link>Simple Queries\MyTableQuery</Link>
</Content>
```

## Checklist

- [ ] Create AxQuery with root data source
- [ ] Add joins (embedded data sources) if needed
- [ ] Configure DynamicFields or explicit field list
- [ ] Add ranges for filtering
- [ ] Add sorting as needed
- [ ] Set Title for display purposes
- [ ] Normalize XML file to CRLF
- [ ] Add to .rnrproj file
- [ ] Build and test query in AOT or X++
