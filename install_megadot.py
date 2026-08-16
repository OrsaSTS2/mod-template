import io
import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
import winreg
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MEGADOT_FOLDER = ".megadot"
MEGADOT_EXECUTABLE_PATTERN = "MegaDot_*_console.exe"
MEGADOT_VARIABLE = "MEGADOT"
MEGADOT_URL ="https://megadot.megacrit.com/4.5.1-m.14/megadot-4.5.1-m.14-windows-x86_64-llvm-editor-csharp.zip"


def download_bytes(url):
    request = urllib.request.Request(url, headers={"User-Agent": "sts2-setup"})
    with urllib.request.urlopen(request) as response:
        data = response.read()

    return data


def extract_zip_into(data, folder_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            archive.extractall(temp_path)

        entries = list(temp_path.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            source_root = entries[0]
        else:
            source_root = temp_path

        folder_path.mkdir(parents=True, exist_ok=True)
        for item in source_root.iterdir():
            shutil.move(str(item), str(folder_path / item.name))


def install_megadot():
    folder_path = BASE_DIR / MEGADOT_FOLDER

    if folder_path.exists():
        shutil.rmtree(folder_path)

    print(f"  Downloading Megadot in {MEGADOT_FOLDER}...")
    data = download_bytes(MEGADOT_URL)
    extract_zip_into(data, folder_path)
    print(f"  {MEGADOT_FOLDER}: installed.")


def find_megadot_executable():
    megadot_folder = BASE_DIR / MEGADOT_FOLDER
    matches = sorted(megadot_folder.glob(MEGADOT_EXECUTABLE_PATTERN))
    if not matches:
        executable = None
        return executable

    executable = matches[0]
    return executable


def read_user_variable(name):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
    except OSError:
        value = None

    return value


def set_megadot_variable():
    executable = find_megadot_executable()
    if executable is None:
        print(f"  {MEGADOT_VARIABLE}: megadot executable not found, skipped.")
        return

    wanted_value = str(executable)
    current_value = read_user_variable(MEGADOT_VARIABLE)
    if current_value == wanted_value:
        print(f"  {MEGADOT_VARIABLE}: already points at {wanted_value}.")
        return

    result = subprocess.run(
        ["setx", MEGADOT_VARIABLE, wanted_value],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  {MEGADOT_VARIABLE}: failed to set ({result.stderr.strip()}).")
        return

    os.environ[MEGADOT_VARIABLE] = wanted_value
    print(f"  {MEGADOT_VARIABLE}: set to {wanted_value}")
    print("  Restart your shell, Rider, or Explorer for it to be visible.")


def main():
    print("Installing MegaDot...")
    try:
        install_megadot()
    except Exception as error:
        print(f"  {MEGADOT_FOLDER}: failed ({error}).")

    print("Setting environment variables...")
    try:
        set_megadot_variable()
    except Exception as error:
        print(f"  {MEGADOT_VARIABLE}: failed ({error}).")

    print("MegaDot installation complete.")


if __name__ == "__main__":
    main()
