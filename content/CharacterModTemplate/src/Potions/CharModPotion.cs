using BaseLib.Abstracts;
using BaseLib.Utils;
using CharMod.Character;

namespace CharMod.Potions;

[Pool(typeof(CharModPotionPool))]
public abstract class CharModPotion : CustomPotionModel;