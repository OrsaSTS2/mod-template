A template for an empty Slay the Spire 2 mod (no dependencies).

This fork is for more experienced developers that might not want to rely on BaseLib. Use the original if you are a beginner.

Two branches: `master` for the release branch of the game, `beta` for the beta branch.

## Differences with the original

Added:
- Loads godot addons with your mod
- Rider launch configs for easy debugging

Removed:
- Only one template instead of 3
- No dependency on BaseLib

## How to use

Using the python script (requires Python 3.10 or newer) (recommended):
- Launch `new_mod.py`

As a template:
- Create a new solution using `content\ModTemplate` as a template
- Manually edit the 'Launch STS2 (Debug)' run config in Rider with your game path

## Credits

Original by [Alchyr](https://github.com/Alchyr/ModTemplate-StS2).