import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_URL = "git@github.com:OrsaSTS2/mod-template.git"
REPO_BRANCH = "beta"
DEFAULT_TARGET_DIR = "./"
REQUIRED_DLLS = ("sts2.dll", "0Harmony.dll")

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".dll",
    ".exe",
    ".pdb",
    ".pck",
    ".zip",
    ".gz",
    ".tar",
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
}


def prompt(message, default=None):
    if default:
        hint = f" [{default}]"
    else:
        hint = ""
    while True:
        result = input(f"{message}{hint}: ").strip()
        if result:
            return result
        if default:
            return default
        print("  This field is required.")


def to_kebab_case(pascal: str) -> str:
    kebab = re.sub(r"(?<!^)(?=[A-Z])", "-", pascal).lower()
    return kebab


def find_sts2_exe() -> Path | None:
    if sys.platform != "win32":
        return None
    import winreg

    for access in (
        winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
    ):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 2868840",
                access=access,
            )
            install_dir, _ = winreg.QueryValueEx(key, "InstallLocation")
            winreg.CloseKey(key)
            exe = Path(install_dir) / "SlayTheSpire2.exe"
            if exe.exists():
                return exe
        except OSError:
            pass
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        winreg.CloseKey(key)
        exe = (
            Path(steam_path)
            / "steamapps"
            / "common"
            / "Slay the Spire 2"
            / "SlayTheSpire2.exe"
        )
        if exe.exists():
            return exe
    except OSError:
        pass
    return None


def escape_backslashes(replacements: dict) -> dict:
    escaped = {}
    for old_value, new_value in replacements.items():
        escaped[old_value] = new_value.replace("\\", "\\\\")

    return escaped


def replace_in_file(path: Path, replacements: dict):
    extension = path.suffix.lower()
    if extension in BINARY_EXTENSIONS:
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return
    new_text = text
    for old_value, new_value in replacements.items():
        new_text = new_text.replace(old_value, new_value)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")


def apply_replacements(folder: Path, replacements: dict, old_name: str, new_name: str):
    json_replacements = escape_backslashes(replacements)

    for root, dirs, files in os.walk(folder, topdown=False):
        root_path = Path(root)

        for file_name in files:
            file_path = root_path / file_name
            if file_path.suffix.lower() == ".json":
                replace_in_file(file_path, json_replacements)
            else:
                replace_in_file(file_path, replacements)

            if old_name in file_name:
                new_file_name = file_name.replace(old_name, new_name)
                file_path.rename(file_path.with_name(new_file_name))

        if old_name in root_path.name:
            new_dir_name = root_path.name.replace(old_name, new_name)
            root_path.rename(root_path.with_name(new_dir_name))


def main():
    print("=" * 50)
    print("  New STS2 Mod Setup")
    print("=" * 50)

    mod_name = prompt("\nMod name (PascalCase, e.g. MyAwesomeMod)")
    if not re.match(r"^[A-Za-z][A-Za-z0-9_]*$", mod_name):
        print(
            "Error: mod name must start with a letter and contain only letters, numbers, or underscores."
        )
        sys.exit(1)

    author = prompt("Author name", default="Author")

    target_input = prompt("Path where to create the mod", default=DEFAULT_TARGET_DIR)
    target_dir = Path(target_input).expanduser().resolve()
    if target_dir.exists() and not target_dir.is_dir():
        print(f"\nError: {target_dir} is not a folder.")
        sys.exit(1)

    template_folder = "ModTemplate"
    source_name = template_folder

    publicize_value = "true"
    nullable_value = "enable"

    destination = target_dir / to_kebab_case(mod_name)
    if destination.exists():
        print(f"\nError: {destination} already exists.")
        sys.exit(1)
    target_dir.mkdir(parents=True, exist_ok=True)

    print("\nCloning template...")
    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = Path(temp_dir) / "template"
        clone_result = subprocess.run(
            ["git", "clone", "--depth=1", "--branch", REPO_BRANCH, REPO_URL, str(clone_dir)],
            capture_output=True,
            text=True,
        )
        if clone_result.returncode != 0:
            print("Git clone failed:")
            print(clone_result.stderr)
            sys.exit(1)

        source_dir = clone_dir / "content" / template_folder
        shutil.copytree(
            source_dir,
            destination,
            ignore=shutil.ignore_patterns(
                ".git", ".godot", ".template.config", "README.md", "*.py"
            ),
        )

    sts2_exe = find_sts2_exe()
    if sts2_exe:
        sts2_exe_path = str(sts2_exe)
        sts2_dir_path = str(sts2_exe.parent)
    else:
        sts2_exe_path = r"C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.exe"
        sts2_dir_path = (
            r"C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2"
        )
        print(
            "  Warning: STS2 not found automatically. Edit the 'Launch STS2' run config in Rider with your game path."
        )

    replacements = {
        source_name: mod_name,
        "{ModAuthor}": author,
        "{PublicizeSts}": publicize_value,
        "{NullableChecks}": nullable_value,
        "{Sts2ExePath}": sts2_exe_path,
        "{Sts2DirPath}": sts2_dir_path,
    }

    print("Applying replacements...")
    apply_replacements(destination, replacements, source_name, mod_name)

    lib_dir = destination / "lib"
    lib_dir.mkdir(exist_ok=True)

    kebab_name = to_kebab_case(mod_name)
    idea_pascal = destination / ".idea" / f".idea.{mod_name}.dir"
    idea_kebab = destination / ".idea" / f".idea.{kebab_name}.dir"
    if idea_pascal.exists() and not idea_kebab.exists():
        idea_pascal.rename(idea_kebab)

    print("Initialising git repository...")
    subprocess.run(["git", "init"], cwd=destination, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=destination, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit from mod template"],
        cwd=destination,
        capture_output=True,
    )

    exclude_file = destination / ".git" / "info" / "exclude"
    exclude_content = exclude_file.read_text(encoding="utf-8")
    if ".claude" not in exclude_content:
        exclude_file.write_text(exclude_content + "\n.claude\n", encoding="utf-8")

    print("\nDone! Your mod is ready at:")
    print(f"  {destination}")

    missing = " and ".join(REQUIRED_DLLS)
    print(f"WARNING! Missing DLLs. Copy {missing} into {lib_dir}")

    input("Press Enter to close...")


if __name__ == "__main__":
    main()
