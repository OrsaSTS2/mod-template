using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Modding;

namespace ModTemplate;

[ModInitializer(nameof(Initialize))]
public partial class Main : Node
{
    public const string ModId = "ModTemplate";

    public static MegaCrit.Sts2.Core.Logging.Logger Logger { get; } = new(ModId, MegaCrit.Sts2.Core.Logging.LogType.Generic);

    public static void Initialize()
    {
        #if DEBUG
        System.Diagnostics.Debugger.Launch();
        #endif
        Harmony harmony = new(ModId);

        harmony.PatchAll();
    }
}
