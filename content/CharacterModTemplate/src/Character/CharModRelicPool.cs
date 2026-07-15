using BaseLib.Abstracts;
using CharMod.Extensions;
using Godot;

namespace CharMod.Character;

public class CharModRelicPool : CustomRelicPoolModel
{
    public override Color LabOutlineColor => CharMod.Color;

    public override string BigEnergyIconPath => "charui/big_energy.png".ImagePath();
    public override string TextEnergyIconPath => "charui/text_energy.png".ImagePath();
}