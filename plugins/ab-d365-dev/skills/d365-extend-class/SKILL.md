---
name: d365-extend-class
description: Extend an existing D365 Finance & Operations class using Chain of Command (CoC) — wrapping base methods or adding new methods without modifying the base. Use whenever the user asks to extend, wrap, or hook a base class (e.g. SalesFormLetter, InventMov_Transfer), write Chain of Command code, or add CoC overrides. Do not use for new classes — see d365-new-class for that.
---

# D365 F&O: Extend Existing Class (Chain of Command)

You are helping extend an existing class in D365 Finance & Operations using Chain of Command (CoC). This wraps or adds methods to a base class WITHOUT modifying the original.

**Important:** This skill is for extending BASE objects (Microsoft or other ISV classes). To create a NEW class in your model, use `/d365-new-class` instead.

## Gather Requirements

Ask the user for:
1. **Base class** to extend (e.g., `SalesFormLetter`, `InventMov_Transfer`)
2. **Methods to override** (wrap existing methods)
3. **New methods to add** (extend functionality)
4. **Extension naming:** Check CLAUDE.md for model prefix

Refer to **CLAUDE.md** for:
- Model name and naming prefix
- VS project file path
- Label file ID

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## Extension Naming Convention

```
<BaseClassName>_<YourPrefix>Extension
```

Examples:
- `SalesFormLetter_cbExtension`
- `InventMov_Transfer_cbExtension`
- `PurchLineType_myExtension`

## Chain of Command Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>SalesFormLetter_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension class for SalesFormLetter using Chain of Command.
/// </summary>
[ExtensionOf(classStr(SalesFormLetter))]
final class SalesFormLetter_cbExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>run</Name>
				<Source><![CDATA[
    public void run()
    {
        // Pre-execution logic
        this.cbBeforeRun();

        next run();

        // Post-execution logic
        this.cbAfterRun();
    }

]]></Source>
			</Method>
			<Method>
				<Name>cbBeforeRun</Name>
				<Source><![CDATA[
    /// <summary>
    /// Custom logic executed before base run().
    /// </summary>
    private void cbBeforeRun()
    {
        // Custom pre-processing
    }

]]></Source>
			</Method>
			<Method>
				<Name>cbAfterRun</Name>
				<Source><![CDATA[
    /// <summary>
    /// Custom logic executed after base run().
    /// </summary>
    private void cbAfterRun()
    {
        // Custom post-processing
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Key Rules for Chain of Command

### Required Elements

1. **`[ExtensionOf(...)]` attribute** - Specifies the target class
2. **`final` class modifier** - Extension classes must be final
3. **`next` keyword** - Calls the base implementation (for wrapped methods)

### The `next` Keyword

```xpp
// CORRECT - always call next for wrapped methods
public void myMethod()
{
    // Pre-logic (before base)

    next myMethod(); // Calls base + any other extensions

    // Post-logic (after base)
}

// For methods with return values
public boolean validate()
{
    boolean ret = next validate();

    if (ret)
    {
        ret = this.cbCustomValidation();
    }

    return ret;
}

// For methods with parameters
public void doSomething(str _param1, int _param2)
{
    // Can modify parameters before passing to base
    str modifiedParam = this.cbProcessParam(_param1);

    next doSomething(modifiedParam, _param2);
}
```

### Adding New Methods

New methods don't use `next` - they're just regular methods:

```xpp
/// <summary>
/// New custom method added by extension.
/// </summary>
public str cbGetCustomValue()
{
    // This is a completely new method
    return "Custom value";
}
```

## Common Extension Patterns

### Wrapping with Pre/Post Logic

```xml
<Method>
	<Name>insert</Name>
	<Source><![CDATA[
    public void insert()
    {
        // Pre-insert validation or field population
        this.cbPopulateDefaultFields();

        next insert();

        // Post-insert logging or related record creation
        this.cbLogInsert();
    }

]]></Source>
</Method>
```

### Conditional Bypass

```xml
<Method>
	<Name>validateWrite</Name>
	<Source><![CDATA[
    public boolean validateWrite()
    {
        // Skip validation under certain conditions
        if (this.cbShouldSkipValidation())
        {
            return true;
        }

        boolean ret = next validateWrite();

        if (ret)
        {
            ret = this.cbAdditionalValidation();
        }

        return ret;
    }

]]></Source>
</Method>
```

### Extending Static Methods

```xml
<Method>
	<Name>main</Name>
	<Source><![CDATA[
    public static void main(Args _args)
    {
        // Pre-main logic

        next main(_args);

        // Post-main logic
    }

]]></Source>
</Method>
```

### Accessing Private Members via Wrapper Methods

You cannot directly access private members. Use protected/public methods or create wrapper approach:

```xpp
// If base class has: private str myPrivateField;
// You CANNOT access it directly

// Instead, rely on public/protected methods if available
// Or use SysDictClass to access via reflection (use sparingly)
```

## Extension Target Types

### Class Extension

```xpp
[ExtensionOf(classStr(SalesFormLetter))]
final class SalesFormLetter_cbExtension
```

### Table Extension (for table methods)

```xpp
[ExtensionOf(tableStr(SalesTable))]
final class SalesTable_cbExtension
```

### Form Extension

```xpp
[ExtensionOf(formStr(SalesTable))]
final class SalesTableForm_cbExtension
```

### Form Data Source Extension

```xpp
[ExtensionOf(formDataSourceStr(SalesTable, SalesTable))]
final class SalesTableFormDS_cbExtension
```

### Form Control Extension

```xpp
[ExtensionOf(formControlStr(SalesTable, SalesId))]
final class SalesTableSalesIdCtrl_cbExtension
```

### Data Entity Extension

```xpp
[ExtensionOf(dataEntityViewStr(SalesOrderEntity))]
final class SalesOrderEntity_cbExtension
```

## Complete Extension Example

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>InventMovement_cbExtension</Name>
	<SourceCode>
		<Declaration><![CDATA[
/// <summary>
/// Extension class for InventMovement to add PLM integration.
/// </summary>
[ExtensionOf(classStr(InventMovement))]
final class InventMovement_cbExtension
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>checkDimPhysical</Name>
				<Source><![CDATA[
    protected boolean checkDimPhysical(
        InventDim _inventDim,
        boolean _checkOnlyPhysicalDimensions)
    {
        boolean ret = next checkDimPhysical(_inventDim, _checkOnlyPhysicalDimensions);

        if (ret)
        {
            ret = this.cbValidatePLMDimensions(_inventDim);
        }

        return ret;
    }

]]></Source>
			</Method>
			<Method>
				<Name>cbValidatePLMDimensions</Name>
				<Source><![CDATA[
    /// <summary>
    /// Validates inventory dimensions against PLM requirements.
    /// </summary>
    /// <param name="_inventDim">The inventory dimensions to validate.</param>
    /// <returns>true if valid; otherwise, false.</returns>
    private boolean cbValidatePLMDimensions(InventDim _inventDim)
    {
        boolean ret = true;

        // Custom PLM validation logic
        if (this.cbRequiresPLMValidation())
        {
            // Validation implementation
        }

        return ret;
    }

]]></Source>
			</Method>
			<Method>
				<Name>cbRequiresPLMValidation</Name>
				<Source><![CDATA[
    /// <summary>
    /// Determines if PLM validation is required.
    /// </summary>
    /// <returns>true if PLM validation is required; otherwise, false.</returns>
    private boolean cbRequiresPLMValidation()
    {
        // Check if PLM feature is enabled
        return cbPLMIntegrationFeature::isEnabled();
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## What CAN'T Be Extended

1. **Private methods** - Cannot be wrapped (only public/protected)
2. **Final methods** - Methods marked `[Wrappable(false)]` or `final`
3. **Static constructors** - `new()` with `static` modifier
4. **Delegates** - Use event handlers instead
5. **Private fields** - Cannot access directly

## Alternative: Event Handlers

For methods that can't be wrapped, use event handlers:

```xpp
/// <summary>
/// Event handler for SalesTable onInserting.
/// </summary>
[DataEventHandler(tableStr(SalesTable), DataEventType::Inserting)]
public static void SalesTable_onInserting(Common _sender, DataEventArgs _args)
{
    SalesTable salesTable = _sender as SalesTable;
    // Handle inserting event
}
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxClass\SalesFormLetter_cbExtension.xml">
  <SubType>Content</SubType>
  <Name>SalesFormLetter_cbExtension</Name>
  <Link>Classes\SalesFormLetter_cbExtension</Link>
</Content>
```

## Debugging Chain of Command

1. **Call stack** shows all extensions in chain
2. **Breakpoints** work in extension methods
3. **`next` calls** appear as separate stack frames
4. **Order** of extensions is non-deterministic (don't rely on it)

## Checklist

- [ ] Identify base class/table/form to extend
- [ ] Determine which methods to wrap
- [ ] Create extension class with `[ExtensionOf(...)]` attribute
- [ ] Mark class as `final`
- [ ] Use `next` keyword for wrapped methods
- [ ] Add new methods without `next`
- [ ] Normalize XML file to CRLF
- [ ] Add to .rnrproj file
- [ ] Build and test extension behavior
- [ ] Verify `next` is called in all wrapped methods
