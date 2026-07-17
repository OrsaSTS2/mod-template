using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Debug;
using Logger = MegaCrit.Sts2.Core.Logging.Logger;

namespace CharMod;

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
    
    // --- Fix Sentry shutdown crashing when loading a GDExtension ---
    
    [HarmonyPatch(typeof(SentryService), nameof(SentryService.Shutdown))]
    public static class SentryNativeShutdownSuppressor
    {
        private static Node? _nativeSentryNode;

        public static bool Prepare()
        {
            bool extensionLoaded = _extensionLoaded;

            return extensionLoaded;
        }

        [HarmonyPrefix]
        public static void Prefix()
        {
            _nativeSentryNode = SentryService._sentryInit;
            SentryService._sentryInit = null;
        }

        [HarmonyPostfix]
        public static void Postfix()
        {
            SentryService._sentryInit = _nativeSentryNode;
        }
    }

    [HarmonyPatch(typeof(SentryService), "ShouldSampleEvent")]
    public static class SentryEventSuppressor
    {
        public static bool Prepare()
        {
            bool extensionLoaded = _extensionLoaded;

            return extensionLoaded;
        }

        [HarmonyPostfix]
        public static void Postfix(ref bool __result)
        {
            __result = false;
        }
    }
}
