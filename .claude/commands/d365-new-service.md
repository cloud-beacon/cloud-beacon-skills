# D365 F&O: Create Web Service

You are helping create a web service in D365 Finance & Operations for external integration via SOAP or JSON endpoints.

## Gather Requirements

Ask the user for:
1. **Service class name** (e.g., `MyIntegrationService`)
2. **Service group name** (e.g., `MyIntegrationServices`)
3. **Operations** to expose (method names and purposes)
4. **Request/Response contracts** (data structures for each operation)
5. **Authentication** requirements (typically AOS handles this)
6. **Label file ID** to use
7. **Visual Studio project file path** (.rnrproj)

## Artifacts to Create

1. **Service class** (AxClass) - Contains service operations
2. **Request contract(s)** (AxClass) - Input data structures
3. **Response contract(s)** (AxClass) - Output data structures
4. **Service definition** (AxService) - Declares service metadata
5. **Service group** (AxServiceGroup) - Groups related services
6. **Security privilege** - Access control for service operations

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Service Class Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyIntegrationService</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Service class providing integration operations for [purpose].
/// </summary>
class MyIntegrationService
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>createRecord</Name>
				<Source><![CDATA[
    /// <summary>
    /// Creates a new record from the request data.
    /// </summary>
    /// <param name="_request">The request containing record data.</param>
    /// <returns>Response with created record ID or error.</returns>
    [SysEntryPointAttribute(true)]
    public MyCreateResponse createRecord(MyCreateRequest _request)
    {
        MyCreateResponse response = new MyCreateResponse();

        try
        {
            ttsbegin;

            MyTable record;
            record.FieldA = _request.parmFieldA();
            record.FieldB = _request.parmFieldB();
            record.insert();

            ttscommit;

            response.parmSuccess(true);
            response.parmRecordId(record.RecId);
            response.parmMessage("Record created successfully");
        }
        catch (Exception::Error)
        {
            response.parmSuccess(false);
            response.parmMessage(infolog.text(infologLine()));
        }

        return response;
    }

]]></Source>
			</Method>
			<Method>
				<Name>getRecord</Name>
				<Source><![CDATA[
    /// <summary>
    /// Retrieves a record by ID.
    /// </summary>
    /// <param name="_request">The request containing record ID.</param>
    /// <returns>Response with record data or error.</returns>
    [SysEntryPointAttribute(false)]
    public MyGetResponse getRecord(MyGetRequest _request)
    {
        MyGetResponse response = new MyGetResponse();
        MyTable record;

        select firstonly record
            where record.RecId == _request.parmRecordId();

        if (record)
        {
            response.parmSuccess(true);
            response.parmFieldA(record.FieldA);
            response.parmFieldB(record.FieldB);
        }
        else
        {
            response.parmSuccess(false);
            response.parmMessage("Record not found");
        }

        return response;
    }

]]></Source>
			</Method>
			<Method>
				<Name>processBatch</Name>
				<Source><![CDATA[
    /// <summary>
    /// Processes a batch of records.
    /// </summary>
    /// <param name="_requests">List of requests to process.</param>
    /// <returns>List of responses.</returns>
    [SysEntryPointAttribute(true)]
    public List processBatch(List _requests)
    {
        List responses = new List(Types::Class);
        ListEnumerator enumerator = _requests.getEnumerator();

        while (enumerator.moveNext())
        {
            MyCreateRequest request = enumerator.current();
            MyCreateResponse response = this.createRecord(request);
            responses.addEnd(response);
        }

        return responses;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### SysEntryPointAttribute

| Parameter | Meaning |
|-----------|---------|
| `[SysEntryPointAttribute(true)]` | Operation modifies data (uses transaction) |
| `[SysEntryPointAttribute(false)]` | Read-only operation |

## Request Contract Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyCreateRequest</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Request contract for creating a record.
/// </summary>
[DataContractAttribute]
class MyCreateRequest
{
    str     fieldA;
    int     fieldB;
    str     fieldC;
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>parmFieldA</Name>
				<Source><![CDATA[
    [DataMemberAttribute('FieldA')]
    public str parmFieldA(str _fieldA = fieldA)
    {
        fieldA = _fieldA;
        return fieldA;
    }

]]></Source>
			</Method>
			<Method>
				<Name>parmFieldB</Name>
				<Source><![CDATA[
    [DataMemberAttribute('FieldB')]
    public int parmFieldB(int _fieldB = fieldB)
    {
        fieldB = _fieldB;
        return fieldB;
    }

]]></Source>
			</Method>
			<Method>
				<Name>parmFieldC</Name>
				<Source><![CDATA[
    [DataMemberAttribute('FieldC')]
    public str parmFieldC(str _fieldC = fieldC)
    {
        fieldC = _fieldC;
        return fieldC;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Response Contract Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyCreateResponse</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Response contract for create operation.
/// </summary>
[DataContractAttribute]
class MyCreateResponse
{
    boolean     success;
    str         message;
    RecId       recordId;
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>parmSuccess</Name>
				<Source><![CDATA[
    [DataMemberAttribute('Success')]
    public boolean parmSuccess(boolean _success = success)
    {
        success = _success;
        return success;
    }

]]></Source>
			</Method>
			<Method>
				<Name>parmMessage</Name>
				<Source><![CDATA[
    [DataMemberAttribute('Message')]
    public str parmMessage(str _message = message)
    {
        message = _message;
        return message;
    }

]]></Source>
			</Method>
			<Method>
				<Name>parmRecordId</Name>
				<Source><![CDATA[
    [DataMemberAttribute('RecordId')]
    public RecId parmRecordId(RecId _recordId = recordId)
    {
        recordId = _recordId;
        return recordId;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## AxService Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxService xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyIntegrationService</Name>
	<Class>MyIntegrationService</Class>
	<Description>@LabelFile:MyIntegrationServiceDesc</Description>
	<ExternalName>MyIntegrationService</ExternalName>
	<Operations>
		<AxServiceOperation>
			<Name>createRecord</Name>
			<Description>@LabelFile:CreateRecordDesc</Description>
			<Method>createRecord</Method>
		</AxServiceOperation>
		<AxServiceOperation>
			<Name>getRecord</Name>
			<Description>@LabelFile:GetRecordDesc</Description>
			<Method>getRecord</Method>
		</AxServiceOperation>
		<AxServiceOperation>
			<Name>processBatch</Name>
			<Description>@LabelFile:ProcessBatchDesc</Description>
			<Method>processBatch</Method>
		</AxServiceOperation>
	</Operations>
</AxService>
```

## AxServiceGroup Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxServiceGroup xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyIntegrationServices</Name>
	<AutoDeploy>Yes</AutoDeploy>
	<Description>@LabelFile:MyIntegrationServicesDesc</Description>
	<Services>
		<Name>MyIntegrationService</Name>
	</Services>
</AxServiceGroup>
```

### Service Group Properties

| Property | Values | Description |
|----------|--------|-------------|
| `AutoDeploy` | `Yes` / `No` | Auto-deploy when model is deployed |

## Security Privilege for Service

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxSecurityPrivilege xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyIntegrationServiceInvoke</Name>
	<Label>@LabelFile:MyIntegrationServiceInvokeLabel</Label>
	<DataEntityPermissions />
	<DirectAccessPermissions />
	<EntryPoints>
		<AxSecurityEntryPointReference>
			<Name>MyIntegrationService.createRecord</Name>
			<Grant>
				<Invoke>Allow</Invoke>
			</Grant>
			<ObjectName>MyIntegrationService</ObjectName>
			<ObjectType>ServiceOperation</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
		<AxSecurityEntryPointReference>
			<Name>MyIntegrationService.getRecord</Name>
			<Grant>
				<Invoke>Allow</Invoke>
			</Grant>
			<ObjectName>MyIntegrationService</ObjectName>
			<ObjectType>ServiceOperation</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
		<AxSecurityEntryPointReference>
			<Name>MyIntegrationService.processBatch</Name>
			<Grant>
				<Invoke>Allow</Invoke>
			</Grant>
			<ObjectName>MyIntegrationService</ObjectName>
			<ObjectType>ServiceOperation</ObjectType>
			<Forms />
		</AxSecurityEntryPointReference>
	</EntryPoints>
	<FormControlOverrides />
</AxSecurityPrivilege>
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<!-- Service class -->
<Content Include="AxClass\MyIntegrationService.xml">
  <SubType>Content</SubType>
  <Name>MyIntegrationService</Name>
  <Link>Classes\MyIntegrationService</Link>
</Content>

<!-- Request/Response contracts -->
<Content Include="AxClass\MyCreateRequest.xml">
  <SubType>Content</SubType>
  <Name>MyCreateRequest</Name>
  <Link>Classes\MyCreateRequest</Link>
</Content>
<Content Include="AxClass\MyCreateResponse.xml">
  <SubType>Content</SubType>
  <Name>MyCreateResponse</Name>
  <Link>Classes\MyCreateResponse</Link>
</Content>

<!-- Service definition -->
<Content Include="AxService\MyIntegrationService.xml">
  <SubType>Content</SubType>
  <Name>MyIntegrationService</Name>
  <Link>Services\MyIntegrationService</Link>
</Content>

<!-- Service group -->
<Content Include="AxServiceGroup\MyIntegrationServices.xml">
  <SubType>Content</SubType>
  <Name>MyIntegrationServices</Name>
  <Link>Service Groups\MyIntegrationServices</Link>
</Content>

<!-- Security -->
<Content Include="AxSecurityPrivilege\MyIntegrationServiceInvoke.xml">
  <SubType>Content</SubType>
  <Name>MyIntegrationServiceInvoke</Name>
  <Link>Security Privileges\MyIntegrationServiceInvoke</Link>
</Content>
```

## Labels

Add to your label file:

```
MyIntegrationServiceDesc=Integration service for external systems
 ;Service description
CreateRecordDesc=Creates a new record
 ;Operation description
GetRecordDesc=Retrieves a record by ID
 ;Operation description
ProcessBatchDesc=Processes a batch of records
 ;Operation description
MyIntegrationServicesDesc=Integration services group
 ;Service group description
MyIntegrationServiceInvokeLabel=Invoke my integration service
 ;Security privilege label
```

## Endpoint URLs

After deployment, services are available at:

**SOAP:**
```
https://<environment>/soap/services/<ServiceGroupName>?wsdl
```

**JSON:**
```
https://<environment>/api/services/<ServiceGroupName>/<ServiceName>/<Operation>
```

**Example:**
```
POST https://myenv.operations.dynamics.com/api/services/MyIntegrationServices/MyIntegrationService/createRecord
Content-Type: application/json
Authorization: Bearer <token>

{
  "request": {
    "FieldA": "value",
    "FieldB": 123
  }
}
```

## Common Patterns

### Returning Collections

```xpp
[SysEntryPointAttribute(false)]
public List getRecords(MySearchRequest _request)
{
    List results = new List(Types::Class);
    MyTable record;

    while select record
        where record.Status == _request.parmStatus()
    {
        MyRecordContract item = new MyRecordContract();
        item.parmRecordId(record.RecId);
        item.parmFieldA(record.FieldA);
        results.addEnd(item);
    }

    return results;
}
```

### Error Handling

```xpp
[SysEntryPointAttribute(true)]
public MyResponse processRecord(MyRequest _request)
{
    MyResponse response = new MyResponse();

    try
    {
        ttsbegin;
        // Business logic
        ttscommit;
        response.parmSuccess(true);
    }
    catch (Exception::Error)
    {
        response.parmSuccess(false);
        response.parmErrorCode("ERR001");
        response.parmMessage(infolog.text(infologLine()));
    }
    catch (Exception::CLRError)
    {
        response.parmSuccess(false);
        response.parmErrorCode("ERR002");
        response.parmMessage(CLRInterop::getLastException().ToString());
    }

    return response;
}
```

### Nested Data Contracts

```xpp
[DataContractAttribute]
class MyOrderRequest
{
    MyOrderHeaderContract header;
    List lines; // List of MyOrderLineContract
}

[DataMemberAttribute('Header')]
public MyOrderHeaderContract parmHeader(MyOrderHeaderContract _header = header)
{
    header = _header;
    return header;
}

[DataMemberAttribute('Lines'),
 AifCollectionTypeAttribute('Lines', Types::Class, classStr(MyOrderLineContract))]
public List parmLines(List _lines = lines)
{
    lines = _lines;
    return lines;
}
```

## Checklist

- [ ] Create service class with `[SysEntryPointAttribute]` operations
- [ ] Create request contract(s) with `[DataContractAttribute]`
- [ ] Create response contract(s) with `[DataContractAttribute]`
- [ ] Create AxService definition
- [ ] Create AxServiceGroup with AutoDeploy=Yes
- [ ] Create security privilege for service operations
- [ ] Add labels to label file
- [ ] Normalize all XML files to CRLF
- [ ] Add all artifacts to .rnrproj file
- [ ] Build and restart IIS
- [ ] Test endpoints with Postman or similar tool
