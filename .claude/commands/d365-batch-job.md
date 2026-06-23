# D365 F&O: Create Batch Job

You are helping create a batch job in D365 Finance & Operations using the SysOperation framework (Controller → Contract → Service pattern).

## Gather Requirements

Ask the user for:
1. **Job name/prefix** (e.g., `MyProcess`)
2. **Purpose** of the batch job
3. **Parameters** needed (name, type, label for each)
4. **Default execution mode** (Synchronous, Asynchronous, ScheduledBatch)
5. **Show dialog?** (typically Yes for user-triggered jobs)
6. **Label file ID** to use
7. **Visual Studio project file path** (.rnrproj)

## Artifacts to Create

1. **Contract class** - Data contract holding job parameters
2. **Service class** - Business logic
3. **Controller class** - Entry point, configures batch dialog
4. **AxMenuItemAction** - Menu item to run the job
5. **AxSecurityPrivilege** - Security privilege for the job
6. **Labels** - Add to label file

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Contract Class Template

The contract holds parameters that appear in the batch dialog.

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyProcessContract</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Data contract for MyProcess batch job parameters.
/// </summary>
[DataContractAttribute]
class MyProcessContract
{
    NoYes       processAll;
    FromDate    fromDate;
    ToDate      toDate;
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>parmProcessAll</Name>
				<Source><![CDATA[
    [DataMemberAttribute('ProcessAll'),
     SysOperationLabelAttribute(literalStr("@LabelFile:ProcessAllLabel")),
     SysOperationHelpTextAttribute(literalStr("@LabelFile:ProcessAllHelp"))]
    public NoYes parmProcessAll(NoYes _processAll = processAll)
    {
        processAll = _processAll;
        return processAll;
    }

]]></Source>
			</Method>
			<Method>
				<Name>parmFromDate</Name>
				<Source><![CDATA[
    [DataMemberAttribute('FromDate'),
     SysOperationLabelAttribute(literalStr("@LabelFile:FromDateLabel")),
     SysOperationHelpTextAttribute(literalStr("@LabelFile:FromDateHelp"))]
    public FromDate parmFromDate(FromDate _fromDate = fromDate)
    {
        fromDate = _fromDate;
        return fromDate;
    }

]]></Source>
			</Method>
			<Method>
				<Name>parmToDate</Name>
				<Source><![CDATA[
    [DataMemberAttribute('ToDate'),
     SysOperationLabelAttribute(literalStr("@LabelFile:ToDateLabel")),
     SysOperationHelpTextAttribute(literalStr("@LabelFile:ToDateHelp"))]
    public ToDate parmToDate(ToDate _toDate = toDate)
    {
        toDate = _toDate;
        return toDate;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Contract Attributes

| Attribute | Purpose |
|-----------|---------|
| `[DataContractAttribute]` | Marks class as serializable contract |
| `[DataMemberAttribute('Name')]` | Exposes property for serialization |
| `[SysOperationLabelAttribute]` | Label shown in dialog |
| `[SysOperationHelpTextAttribute]` | Tooltip in dialog |
| `[SysOperationDisplayOrderAttribute(n)]` | Order in dialog (optional) |
| `[SysOperationGroupAttribute]` | Groups parameters (optional) |

### Common Parameter Types

```xpp
// Boolean toggle
NoYes includeArchived;

// Date range
FromDate fromDate;
ToDate toDate;

// Lookup to table
ItemId itemId;
CustAccount custAccount;

// Enum selection
MyStatusEnum status;

// Query (for complex filtering)
str packedQuery;
```

## Service Class Template

The service contains the actual business logic.

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyProcessService</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Service class containing business logic for MyProcess.
/// </summary>
class MyProcessService extends SysOperationServiceBase
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>run</Name>
				<Source><![CDATA[
    /// <summary>
    /// Main entry point for the batch job.
    /// </summary>
    /// <param name="_contract">The job parameters.</param>
    public void run(MyProcessContract _contract)
    {
        NoYes       processAll = _contract.parmProcessAll();
        FromDate    fromDate = _contract.parmFromDate();
        ToDate      toDate = _contract.parmToDate();

        this.processRecords(processAll, fromDate, toDate);
    }

]]></Source>
			</Method>
			<Method>
				<Name>processRecords</Name>
				<Source><![CDATA[
    /// <summary>
    /// Processes records based on parameters.
    /// </summary>
    protected void processRecords(NoYes _processAll, FromDate _fromDate, ToDate _toDate)
    {
        MyTable record;
        int processedCount = 0;

        while select forupdate record
            where (_processAll || (record.TransDate >= _fromDate && record.TransDate <= _toDate))
        {
            ttsbegin;

            try
            {
                this.processRecord(record);
                processedCount++;
            }
            catch (Exception::Error)
            {
                error(strFmt("@LabelFile:ProcessingError", record.RecId));
            }

            ttscommit;
        }

        info(strFmt("@LabelFile:ProcessingComplete", processedCount));
    }

]]></Source>
			</Method>
			<Method>
				<Name>processRecord</Name>
				<Source><![CDATA[
    /// <summary>
    /// Processes a single record.
    /// </summary>
    protected void processRecord(MyTable _record)
    {
        // Business logic here
        _record.Status = MyStatus::Processed;
        _record.update();
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Controller Class Template

The controller is the entry point that wires everything together.

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyProcessController</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Controller for MyProcess batch job.
/// </summary>
class MyProcessController extends SysOperationServiceController
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>main</Name>
				<Source><![CDATA[
    /// <summary>
    /// Entry point for the batch job.
    /// </summary>
    /// <param name="_args">Arguments from menu item.</param>
    public static void main(Args _args)
    {
        MyProcessController controller = new MyProcessController(
            classStr(MyProcessService),
            methodStr(MyProcessService, run),
            SysOperationExecutionMode::Synchronous);

        controller.parmDialogCaption("@LabelFile:MyProcessDialogCaption");
        controller.startOperation();
    }

]]></Source>
			</Method>
			<Method>
				<Name>new</Name>
				<Source><![CDATA[
    protected void new(
        IdentifierName _className,
        IdentifierName _methodName,
        SysOperationExecutionMode _executionMode)
    {
        super(_className, _methodName, _executionMode);
        this.parmShowDialog(true);
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Execution Modes

| Mode | Behavior |
|------|----------|
| `Synchronous` | Runs immediately, blocks UI until complete |
| `Asynchronous` | Runs in background, UI returns immediately |
| `ScheduledBatch` | Runs via batch framework, can be scheduled |

### Controller with Default Values

To set default parameter values:

```xpp
public static void main(Args _args)
{
    MyProcessController controller = new MyProcessController(
        classStr(MyProcessService),
        methodStr(MyProcessService, run),
        SysOperationExecutionMode::Synchronous);

    // Set default values
    MyProcessContract contract = controller.getDataContractObject();
    contract.parmProcessAll(NoYes::No);
    contract.parmFromDate(today() - 30);
    contract.parmToDate(today());

    controller.parmDialogCaption("@LabelFile:MyProcessDialogCaption");
    controller.startOperation();
}
```

## Menu Item Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxMenuItemAction xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                  xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyProcess</Name>
	<Label>@LabelFile:MyProcessMenuItemLabel</Label>
	<Object>MyProcessController</Object>
	<ObjectType>Class</ObjectType>
	<Parameters>MyProcessService.run</Parameters>
	<SubscriberAccessLevel>
		<Read xmlns="">Allow</Read>
	</SubscriberAccessLevel>
</AxMenuItemAction>
```

**Note:** The `<Parameters>` element specifies `ServiceClass.methodName`.

## Security Privilege Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyProcessRun</Name>
	<Label>@LabelFile:MyProcessRunLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyProcess</Name>
			<Grant>
				<Read>Allow</Read>
			</Grant>
			<ObjectName>MyProcess</ObjectName>
			<ObjectType>MenuItemAction</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxClass\MyProcessContract.xml">
  <SubType>Content</SubType>
  <Name>MyProcessContract</Name>
  <Link>Classes\MyProcessContract</Link>
</Content>
<Content Include="AxClass\MyProcessService.xml">
  <SubType>Content</SubType>
  <Name>MyProcessService</Name>
  <Link>Classes\MyProcessService</Link>
</Content>
<Content Include="AxClass\MyProcessController.xml">
  <SubType>Content</SubType>
  <Name>MyProcessController</Name>
  <Link>Classes\MyProcessController</Link>
</Content>
<Content Include="AxMenuItemAction\MyProcess.xml">
  <SubType>Content</SubType>
  <Name>MyProcess</Name>
  <Link>Action Menu Items\MyProcess</Link>
</Content>
<Content Include="AxSecurityPrivilege\MyProcessRun.xml">
  <SubType>Content</SubType>
  <Name>MyProcessRun</Name>
  <Link>Security Privileges\MyProcessRun</Link>
</Content>
```

## Labels

Add to your label file:

```
MyProcessDialogCaption=My Process
 ;Dialog caption for batch job
MyProcessMenuItemLabel=Run My Process
 ;Menu item label
MyProcessRunLabel=Run my process batch job
 ;Security privilege label
ProcessAllLabel=Process all records
 ;Parameter label
ProcessAllHelp=Select Yes to process all records regardless of date
 ;Parameter help text
FromDateLabel=From date
 ;Parameter label
FromDateHelp=Start date for processing
 ;Parameter help text
ToDateLabel=To date
 ;Parameter label
ToDateHelp=End date for processing
 ;Parameter help text
ProcessingError=Error processing record %1
 ;Error message with RecId
ProcessingComplete=Successfully processed %1 records
 ;Completion message with count
```

## Advanced Patterns

### Scheduled Batch with Recurrence

```xpp
public static void main(Args _args)
{
    MyProcessController controller = new MyProcessController(
        classStr(MyProcessService),
        methodStr(MyProcessService, run),
        SysOperationExecutionMode::ScheduledBatch);

    // Enable batch tab in dialog
    controller.parmShowDialog(true);
    controller.parmDialogCaption("@LabelFile:MyProcessDialogCaption");
    controller.startOperation();
}
```

### Query-Based Parameters

For complex filtering, use a query in the contract:

```xpp
// In contract
str packedQuery;

[DataMemberAttribute,
 AifQueryTypeAttribute('_packedQuery', queryStr(MyTableQuery))]
public str parmPackedQuery(str _packedQuery = packedQuery)
{
    packedQuery = _packedQuery;
    return packedQuery;
}
```

### Progress Indication

For long-running jobs:

```xpp
public void run(MyProcessContract _contract)
{
    SysOperationProgress progress = SysOperationProgress::newGeneral(
        #AviFile,
        "@LabelFile:ProcessingRecords",
        totalRecordCount);

    while select record
    {
        progress.incCount();
        progress.setText(strFmt("@LabelFile:ProcessingRecord", record.Name));

        // Process record...
    }
}
```

## Checklist

- [ ] Create Contract class with parameters
- [ ] Create Service class with business logic
- [ ] Create Controller class as entry point
- [ ] Create AxMenuItemAction pointing to controller
- [ ] Create security privilege for the action
- [ ] Add all labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build and test the batch job
- [ ] Wire menu item into appropriate menu (if needed)
