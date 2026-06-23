# D365 F&O: Create Feature Management Class

You are helping create a Feature Management class in D365 Finance & Operations to gate functionality behind the Feature Management workspace.

## Gather Requirements

Ask the user for:
1. **Feature class name** (e.g., `MyFeatureClass`)
2. **Feature display name** (shown in Feature Management UI)
3. **Feature summary/description**
4. **Module** (usually ISV for custom features)
5. **Enabled by default?** (typically No for new features)
6. **Can be disabled?** (typically Yes)
7. **Label file ID** for labels
8. **Visual Studio project file path** (.rnrproj)

## Critical Requirements

**The feature class MUST be declared `internal final class`.** Without BOTH modifiers, the MEF discovery mechanism will silently skip the class — it compiles without errors but the feature never appears in Feature Management. This is the single most common cause of "my feature doesn't show up."

## Critical: File Encoding

**All D365 XML files MUST use CRLF line endings.** After writing any XML file, normalize it:

```powershell
$content = [System.IO.File]::ReadAllText($filePath)
$content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")
[System.IO.File]::WriteAllText($filePath, $content, [System.Text.UTF8Encoding]::new($false))
```

## AxClass Template

```xml
<?xml version="1.0" encoding="utf-8"?>
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>MyFeatureClass</Name>
	<SourceCode>
		<Declaration><![CDATA[
using System.ComponentModel.Composition;
using Microsoft.Dynamics.ApplicationPlatform.FeatureExposure;
using Microsoft.Dynamics.BusinessPlatform.SharedTypes;
using Microsoft.Dynamics.ApplicationPlatform.FeatureExposure.Implementation;

/// <summary>
/// Feature management class for My Feature.
/// </summary>
[ExportAttribute(identifierStr(Microsoft.Dynamics.ApplicationPlatform.FeatureExposure.IFeatureMetadata))]
internal final class MyFeatureClass implements IFeatureMetadata, IFeatureLifecycle
{
    static MyFeatureClass featureInstance;
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>instance</Name>
				<Source><![CDATA[
    [Hookable(false)]
    public static MyFeatureClass instance()
    {
        if (!featureInstance)
        {
            featureInstance = new MyFeatureClass();
        }
        return featureInstance;
    }

]]></Source>
			</Method>
			<Method>
				<Name>isEnabled</Name>
				<Source><![CDATA[
    /// <summary>
    /// Checks if this feature is enabled.
    /// </summary>
    /// <returns>true if enabled; otherwise, false.</returns>
    public static boolean isEnabled()
    {
        return Dynamics.AX.Application.FeatureStateProvider::isFeatureEnabled(MyFeatureClass::instance());
    }

]]></Source>
			</Method>
			<Method>
				<Name>label</Name>
				<Source><![CDATA[
    [Hookable(false)]
    public FeatureLabelId label()
    {
        return literalStr("@LabelFile:MyFeatureLabel");
    }

]]></Source>
			</Method>
			<Method>
				<Name>module</Name>
				<Source><![CDATA[
    [Hookable(false)]
    public int module()
    {
        return FeatureModuleV0::ISV;
    }

]]></Source>
			</Method>
			<Method>
				<Name>summary</Name>
				<Source><![CDATA[
    [Hookable(false)]
    public FeatureLabelId summary()
    {
        return literalStr("@LabelFile:MyFeatureSummary");
    }

]]></Source>
			</Method>
			<Method>
				<Name>isEnabledByDefault</Name>
				<Source><![CDATA[
    [Hookable(false)]
    public boolean isEnabledByDefault()
    {
        return false;
    }

]]></Source>
			</Method>
			<Method>
				<Name>canDisable</Name>
				<Source><![CDATA[
    [Hookable(false)]
    public boolean canDisable()
    {
        return true;
    }

]]></Source>
			</Method>
			<Method>
				<Name>learnMoreUrl</Name>
				<Source><![CDATA[
    public WebSiteURL learnMoreUrl()
    {
        return '';
    }

]]></Source>
			</Method>
			<Method>
				<Name>onEnabled</Name>
				<Source><![CDATA[
    public void onEnabled()
    {
        // Called when feature is enabled
        // Add initialization logic here if needed
    }

]]></Source>
			</Method>
			<Method>
				<Name>onDisabled</Name>
				<Source><![CDATA[
    public void onDisabled()
    {
        // Called when feature is disabled
        // Add cleanup logic here if needed
    }

]]></Source>
			</Method>
			<Method>
				<Name>featureStage</Name>
				<Source><![CDATA[
    public FeatureLifecycleStage featureStage()
    {
        return FeatureLifecycleStage::Released;
    }

]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

## Key Requirements Explained

### Class Declaration

```xpp
[ExportAttribute(identifierStr(Microsoft.Dynamics.ApplicationPlatform.FeatureExposure.IFeatureMetadata))]
internal final class MyFeatureClass implements IFeatureMetadata, IFeatureLifecycle
```

| Element | Requirement |
|---------|-------------|
| `[ExportAttribute(...)]` | Required for MEF discovery |
| `internal` | **REQUIRED** - Class must not be public |
| `final` | **REQUIRED** - Class must be sealed |
| `IFeatureMetadata` | Interface with label, summary, module methods |
| `IFeatureLifecycle` | Optional - adds onEnabled/onDisabled/featureStage |

### Module Constants

The `FeatureModuleV0` enum is **NOT extensible**. Use the appropriate value:

| Value | Display Name | Use For |
|-------|--------------|---------|
| `FeatureModuleV0::ISV` | Third party | **Custom/ISV features** |
| `FeatureModuleV0::ProductInformationManagement` | Product information management | PIM features |
| `FeatureModuleV0::InventoryManagement` | Inventory management | Inventory features |
| `FeatureModuleV0::AccountsReceivable` | Accounts receivable | AR features |
| `FeatureModuleV0::AccountsPayable` | Accounts payable | AP features |
| `FeatureModuleV0::GeneralLedger` | General ledger | GL features |
| `FeatureModuleV0::Warehouse` | Warehouse management | WMS features |

### Feature Lifecycle Stages

```xpp
public FeatureLifecycleStage featureStage()
{
    return FeatureLifecycleStage::Released;
}
```

| Stage | Meaning |
|-------|---------|
| `Preview` | Early testing, may change |
| `Released` | Generally available |
| `MandatoryByDate` | Will become mandatory |

### Label References

**CRITICAL:** Use `literalStr()` for label references in feature classes:

```xpp
// CORRECT
return literalStr("@LabelFile:MyFeatureLabel");

// WRONG - will not work
return "@LabelFile:MyFeatureLabel";
return "@MyFeatureLabel";
```

### Method Attributes

All methods should have `[Hookable(false)]` to prevent extension hooks:

```xpp
[Hookable(false)]
public FeatureLabelId label()
```

## Linking Menu Items to the Feature

Add `<FeatureClass>` to menu items to hide them when the feature is disabled:

```xml
<AxMenuItemDisplay xmlns:i="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns="Microsoft.Dynamics.AX.Metadata.V1">
	<Name>MyForm</Name>
	<FeatureClass>MyFeatureClass</FeatureClass>
	<Label>@LabelFile:MyFormLabel</Label>
	<Object>MyForm</Object>
	<!-- ... -->
</AxMenuItemDisplay>
```

**Note:** `<FeatureClass>` goes directly after `<Name>`.

## Checking Feature State in X++ Code

```xpp
if (MyFeatureClass::isEnabled())
{
    // Feature-gated logic
}
else
{
    // Fallback or skip
}
```

## Visual Studio Project File (.rnrproj)

Add to the ItemGroup:

```xml
<Content Include="AxClass\MyFeatureClass.xml">
  <SubType>Content</SubType>
  <Name>MyFeatureClass</Name>
  <Link>Classes\MyFeatureClass</Link>
</Content>
```

## Labels

Add to your label file:

```
MyFeatureLabel=My Feature Name
 ;Feature display name shown in Feature Management
MyFeatureSummary=Enables the My Feature functionality including XYZ capabilities.
 ;Feature summary description
```

## Post-Creation Steps

1. **Build** the model in Visual Studio
2. **Restart IIS** (`iisreset`) or restart the AOS
3. Go to **Feature Management** workspace
4. Click **Check for updates** button
5. Search for your feature by name
6. Enable/disable as needed

## Troubleshooting

### Feature Not Appearing in Feature Management

Most common causes (in order of likelihood):

1. **Class not `internal final`** - This is the #1 cause. Check the declaration.
2. **Missing `[ExportAttribute]`** - MEF won't discover the class.
3. **Build not deployed** - Restart IIS after building.
4. **Didn't click "Check for updates"** - Feature list is cached.

### Feature Toggle Not Taking Effect

- Verify menu items have `<FeatureClass>MyFeatureClass</FeatureClass>`
- Check that X++ code uses `MyFeatureClass::isEnabled()` correctly
- Clear browser cache and refresh

## Checklist

- [ ] Create AxClass with `internal final class` declaration
- [ ] Include all required methods (label, summary, module, isEnabled, etc.)
- [ ] Use `literalStr()` for label references
- [ ] Add `[Hookable(false)]` to methods
- [ ] Add labels to label file
- [ ] Normalize XML file to CRLF
- [ ] Add class to .rnrproj file
- [ ] Build and restart IIS
- [ ] Click "Check for updates" in Feature Management
- [ ] Link menu items to feature class (optional)
- [ ] Test enable/disable behavior
