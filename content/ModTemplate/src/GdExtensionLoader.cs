using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Debug;
using Logger = MegaCrit.Sts2.Core.Logging.Logger;

namespace ModTemplate;

public static class GdExtensionLoader
{
    private static Logger Logger => Main.Logger;

    private static bool _extensionLoaded;

    public static void LoadGdExtension(string addonName)
    {
        string modFolder = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location) ?? "";
        string addonFolder = System.IO.Path.Combine(modFolder, "addons", addonName);

        if (!System.IO.Directory.Exists(addonFolder))
        {
            Logger.Error($"Addon folder not found: {addonFolder}");
            return;
        }

        string[] manifests = System.IO.Directory.GetFiles(addonFolder, "*.gdextension");

        if (manifests.Length == 0)
        {
            Logger.Error($"No .gdextension found in addon '{addonName}'");
            return;
        }

        string extensionPath = manifests[0];

        if (GDExtensionManager.IsExtensionLoaded(extensionPath))
        {
            _extensionLoaded = true;
            return;
        }

        GDExtensionManager.LoadStatus status = GDExtensionManager.LoadExtension(extensionPath);

        if (status != GDExtensionManager.LoadStatus.Ok)
        {
            Logger.Error($"Failed to load extension '{addonName}' ({status}) from {extensionPath}");
            return;
        }

        _extensionLoaded = true;
    }
}
