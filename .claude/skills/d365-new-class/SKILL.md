---
name: d365-new-class
description: Create a new X++ class in D365 Finance & Operations with correct metadata, naming, and labels. Use when the user asks to create, add, or scaffold a new X++ class — helper, utility, data contract, event handler, table/form extension class, service class, or general class — in a D365 F&O model.
---

# D365 F&O: Create X++ Class

You are helping create an X++ class in D365 Finance & Operations.

## Gather Requirements

Ask the user for:
1. **Class name** (e.g., `MyHelperClass`)
2. **Purpose** of the class
3. **Class type** (Helper/Utility, Data Contract, Event Handler, Table Extension, Form Extension, Service, other)
4. **Label file ID** to use (if labels needed)
5. **Visual Studio project file path** (.rnrproj)

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Basic Class Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyClassName</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Description of what this class does.
/// </summary>
class MyClassName
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>myMethod</Name>
				<Source><![CDATA[
    /// <summary>
    /// Description of this method.
    /// </summary>
    /// <param name="_param">Parameter description.</param>
    /// <returns>Return value description.</returns>
    public ReturnType myMethod(ParamType _param)
    {
        // Implementation
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

**Note:** A trailing blank line inside `<Source>` CDATA (before `]]>`) is standard D365 convention.

## Class Templates by Type

### Helper/Utility Class (Static Methods)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyHelper</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Helper class providing utility methods for [area].
/// </summary>
class MyHelper
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>formatValue</Name>
				<Source><![CDATA[
    /// <summary>
    /// Formats the value for display.
    /// </summary>
    /// <param name="_value">The value to format.</param>
    /// <returns>The formatted string.</returns>
    public static str formatValue(anytype _value)
    {
        str result;
        // Implementation
        return result;
    }

]]></Source>
			</Method>
			<Method>
				<Name>validateInput</Name>
				<Source><![CDATA[
    /// <summary>
    /// Validates the input value.
    /// </summary>
    /// <param name="_input">The input to validate.</param>
    /// <returns>true if valid; otherwise, false.</returns>
    public static boolean validateInput(str _input)
    {
        if (!_input)
        {
            return false;
        }
        // Additional validation
        return true;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Data Contract Class

For use with SysOperation framework or data serialization:

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyDataContract</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Data contract for [purpose].
/// </summary>
[DataContractAttribute]
class MyDataContract
{
    str         fieldA;
    int         fieldB;
    NoYes       fieldC;
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>parmFieldA</Name>
				<Source><![CDATA[
    [DataMemberAttribute('FieldA'),
     SysOperationLabelAttribute(literalStr("@LabelFile:FieldALabel")),
     SysOperationHelpTextAttribute(literalStr("@LabelFile:FieldAHelp"))]
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
    [DataMemberAttribute('FieldB'),
     SysOperationLabelAttribute(literalStr("@LabelFile:FieldBLabel"))]
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
    [DataMemberAttribute('FieldC'),
     SysOperationLabelAttribute(literalStr("@LabelFile:FieldCLabel"))]
    public NoYes parmFieldC(NoYes _fieldC = fieldC)
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

### Event Handler Class (Chain of Command / Delegates)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTableEventHandler</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Event handler for MyTable events.
/// </summary>
class MyTableEventHandler
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>onInserted</Name>
				<Source><![CDATA[
    /// <summary>
    /// Handles the onInserted event for MyTable.
    /// </summary>
    /// <param name="_args">Event arguments.</param>
    [DataEventHandler(tableStr(MyTable), DataEventType::Inserted)]
    public static void onInserted(Common _sender, DataEventArgs _args)
    {
        MyTable record = _sender as MyTable;
        // Handle insert event
    }

]]></Source>
			</Method>
			<Method>
				<Name>onValidatedWrite</Name>
				<Source><![CDATA[
    /// <summary>
    /// Handles the onValidatedWrite event for MyTable.
    /// </summary>
    [DataEventHandler(tableStr(MyTable), DataEventType::ValidatedWrite)]
    public static void onValidatedWrite(Common _sender, DataEventArgs _args)
    {
        ValidateEventArgs validateArgs = _args as ValidateEventArgs;
        MyTable record = _sender as MyTable;

        if (!record.validateCustomLogic())
        {
            validateArgs.parmValidateResult(false);
        }
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Chain of Command (CoC) Extension Class

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyTable_Extension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension class for MyTable using Chain of Command.
/// </summary>
[ExtensionOf(tableStr(MyTable))]
final class MyTable_Extension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>insert</Name>
				<Source><![CDATA[
    public void insert()
    {
        // Pre-insert logic
        this.MyCustomField = this.calculateCustomValue();

        next insert();

        // Post-insert logic
        this.logInsert();
    }

]]></Source>
			</Method>
			<Method>
				<Name>validateWrite</Name>
				<Source><![CDATA[
    public boolean validateWrite()
    {
        boolean ret = next validateWrite();

        if (ret)
        {
            ret = this.validateCustomRules();
        }

        return ret;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Form Extension Class (CoC)

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyForm_Extension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension class for MyForm.
/// </summary>
[ExtensionOf(formStr(MyForm))]
final class MyForm_Extension
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

        // Post-init logic
        this.initCustomControls();
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### Singleton Pattern

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyService</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Singleton service class for [purpose].
/// </summary>
class MyService
{
    static MyService instance;
    // Instance variables
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>instance</Name>
				<Source><![CDATA[
    /// <summary>
    /// Gets the singleton instance.
    /// </summary>
    /// <returns>The singleton instance.</returns>
    public static MyService instance()
    {
        if (!instance)
        {
            instance = new MyService();
        }
        return instance;
    }

]]></Source>
			</Method>
			<Method>
				<Name>new</Name>
				<Source><![CDATA[
    /// <summary>
    /// Private constructor for singleton.
    /// </summary>
    protected void new()
    {
        // Initialize instance
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

### RunBase Pattern (Legacy Batch)

For older-style batch jobs (prefer SysOperation for new code):

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyRunBaseJob</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// RunBase batch job for [purpose].
/// </summary>
class MyRunBaseJob extends RunBaseBatch
{
    DialogField     dlgProcessAll;
    NoYes           processAll;

    #define.CurrentVersion(1)
    #localmacro.CurrentList
        processAll
    #endmacro
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>dialog</Name>
				<Source><![CDATA[
    public Object dialog()
    {
        DialogRunbase dialog = super();

        dlgProcessAll = dialog.addFieldValue(enumStr(NoYes), processAll, "@LabelFile:ProcessAllLabel");

        return dialog;
    }

]]></Source>
			</Method>
			<Method>
				<Name>getFromDialog</Name>
				<Source><![CDATA[
    public boolean getFromDialog()
    {
        processAll = dlgProcessAll.value();
        return super();
    }

]]></Source>
			</Method>
			<Method>
				<Name>run</Name>
				<Source><![CDATA[
    public void run()
    {
        // Business logic here
        info("@LabelFile:JobComplete");
    }

]]></Source>
			</Method>
			<Method>
				<Name>pack</Name>
				<Source><![CDATA[
    public container pack()
    {
        return [#CurrentVersion, #CurrentList];
    }

]]></Source>
			</Method>
			<Method>
				<Name>unpack</Name>
				<Source><![CDATA[
    public boolean unpack(container _packedClass)
    {
        Version version = RunBase::getVersion(_packedClass);

        switch (version)
        {
            case #CurrentVersion:
                [version, #CurrentList] = _packedClass;
                break;
            default:
                return false;
        }

        return true;
    }

]]></Source>
			</Method>
			<Method>
				<Name>description</Name>
				<Source><![CDATA[
    public static ClassDescription description()
    {
        return "@LabelFile:MyRunBaseJobDescription";
    }

]]></Source>
			</Method>
			<Method>
				<Name>main</Name>
				<Source><![CDATA[
    public static void main(Args _args)
    {
        MyRunBaseJob job = new MyRunBaseJob();

        if (job.prompt())
        {
            job.runOperation();
        }
    }

]]></Source>
			</Method>
			<Method>
				<Name>canGoBatch</Name>
				<Source><![CDATA[
    public boolean canGoBatch()
    {
        return true;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Common Attributes

| Attribute | Purpose |
|-----------|---------|
| `[ExtensionOf(tableStr(X))]` | Chain of Command for table |
| `[ExtensionOf(classStr(X))]` | Chain of Command for class |
| `[ExtensionOf(formStr(X))]` | Chain of Command for form |
| `[DataContractAttribute]` | Marks class for serialization |
| `[DataMemberAttribute('Name')]` | Marks property for serialization |
| `[DataEventHandler(...)]` | Subscribes to table data events |
| `[PostHandlerFor(...)]` | Runs after target method |
| `[PreHandlerFor(...)]` | Runs before target method |
| `[Hookable(false)]` | Prevents extension of method |
| `[Replaceable]` | Allows method replacement |
| `[Wrappable(false)]` | Prevents CoC wrapping |
| `[SysEntryPointAttribute]` | Marks service operation entry |

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxClass\MyClassName.xml">
  <SubType>Content</SubType>
  <Name>MyClassName</Name>
  <Link>Classes\MyClassName</Link>
</Content>
```

## Class Naming Conventions

| Pattern | Naming | Example |
|---------|--------|---------|
| Helper/Utility | `<Area>Helper` | `ProductHelper` |
| Data Contract | `<Name>Contract` | `ImportContract` |
| Event Handler | `<Table/Class>EventHandler` | `SalesOrderEventHandler` |
| CoC Extension | `<Target>_Extension` | `SalesTable_Extension` |
| Service | `<Area>Service` | `ImportService` |
| Controller | `<Name>Controller` | `ImportController` |
| Factory | `<Type>Factory` | `DocumentFactory` |
| Builder | `<Type>Builder` | `QueryBuilder` |

## Checklist

- [ ] Create AxClass with appropriate declaration
- [ ] Add methods with XML documentation comments
- [ ] Use appropriate attributes (DataContract, ExtensionOf, etc.)
- [ ] Include trailing blank line in method Source CDATA
- [ ] Normalize XML file to CRLF
- [ ] Add to .rnrproj file
- [ ] Build and verify class compiles
