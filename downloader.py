import os
import shutil
import requests
import zipfile
import time
import subprocess

MOD_DOWNLOAD_PATH = "mod_downloads"

def clear_mod_downloads():
    """
    Clears all files and directories within the MOD_DOWNLOAD_PATH.
    """
    print("Clearing everything from " + MOD_DOWNLOAD_PATH + "...")
    if os.path.exists(MOD_DOWNLOAD_PATH):
        for root, dirs, files in os.walk(MOD_DOWNLOAD_PATH):
            for f in files:
                os.unlink(os.path.join(root, f))
                print(f"Deleted file: {f}")
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
                print(f"Deleted directory: {d}")
        print("Mod downloads cleared.")
    else:
        print("MOD_DOWNLOAD_PATH does not exist, skipping")

def clear_old_bepinex():
    """
    Removes specific BepInEx files and directories from the root directory.
    """
    print("Clearing old BepInEx files...")
    files = ["doorstop_config.ini", "winhttp.dll"]
    directories = ["BepInEx"]

    for file in files:
        if os.path.isfile(file):
            os.remove(file)
            print(f"Successfully removed the file {file}")
    for directory in directories:
        if os.path.isdir(directory):
            shutil.rmtree(directory)
            print(f"Successfully removed the directory {directory}")
    print("Old BepInEx files cleared.")

def download_mod(author, mod, version):
    """
    Downloads and extracts a mod from a given author and version.

    :param author: The author of the mod.
    :param mod: The name of the mod.
    :param version: The version of the mod.
    """
    print(f"Preparing to download {mod} version {version} from author {author}...")
    if mod == "LC_API":
        version = "2.2.0"
        print(f"Version override: Downloading {mod} version {version} instead.")

    webrequest_url = f"https://thunderstore.io/package/download/{author}/{mod}/{version}/"
    print(f"Downloading from URL: {webrequest_url}")

    response = requests.get(webrequest_url)
    download_path = f"{MOD_DOWNLOAD_PATH}/{mod}_{version}.zip"
    with open(download_path, 'wb') as f:
        f.write(response.content)
    print(f"Download complete: {mod}_{version}.zip")

    print(f"Extracting {mod} version {version}...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(f"{MOD_DOWNLOAD_PATH}/")
    print(f"Extraction complete: {mod} version {version}")
    extract()
    clear_mod_downloads()

def process_modpack(modpack):
    """
    Processes a modpack by downloading and extracting each mod listed in the modpack file.

    :param modpack: The name of the modpack file without the extension.
    """
    print(f"Processing modpack: {modpack}")
    authors = []
    mods = []
    versions = []
    with open(f"modpacks/{modpack}.txt", "r") as file:
        for line in file:
            author, mod, version = line.strip().split("-")
            authors.append(author)
            mods.append(mod)
            versions.append(version)
    if len(authors) != len(mods) or len(mods) != len(versions):
        print("Error: The number of authors, mods, and versions do not match.")
        return
    for i in range(len(authors)):
        download_mod(authors[i], mods[i], versions[i])
    print(f"Modpack {modpack} processed successfully.")

def download_and_setup_bepinex():
    """
    Downloads and sets up BepInEx by downloading the BepInExPack, extracting it, and moving its contents to the root directory.
    """
    print("Downloading and extracting BepInExPack...")
    response = requests.get('https://thunderstore.io/package/download/BepInEx/BepInExPack/5.4.2100/')
    download_path = "BepInExPack_5.4.2100.zip"
    with open(download_path, 'wb') as f:
        f.write(response.content)
    print("BepInExPack downloaded.")

    print("Extracting BepInExPack...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(".")
    print("BepInExPack extracted.")

    time.sleep(5)
    # Move files and directories of BepInExPack to root directory
    bepinex_pack_dir = "BepInExPack"
    if os.path.exists(bepinex_pack_dir):
        for item in os.listdir(bepinex_pack_dir):
            item_path = os.path.join(bepinex_pack_dir, item)
            shutil.move(item_path, ".")
        os.rmdir(bepinex_pack_dir)  # Remove the now-empty BepInExPack directory
        print("Moved BepInExPack contents to the root directory.")

    print("Launching LC to install BepInEx...")
    process = subprocess.Popen(["Lethal Company.exe"])
    time.sleep(10)
    process.terminate()
    print("LC launched and terminated to install BepInEx.")

    if os.path.isfile(download_path):
        os.remove(download_path)
        print(f"Cleanup: Removed {download_path}")

def fetch_modpacks():
    """
    Fetches the list of modpacks from a GitHub repository and allows the user to select and download one.
    """
    print("Fetching list of modpacks from GitHub...")
    user = 'rsm28'
    repo = 'LC_BF2'
    response = requests.get(f"https://api.github.com/repos/{user}/{repo}/contents/modpacks")
    response.raise_for_status()

    modpacks = [item['name'].replace('.txt', '') for item in response.json()]
    print("Available modpacks:")
    for i, modpack in enumerate(modpacks, start=1):
        print(f"{i}) {modpack}")

    modpack = input("Enter the EXACT NAME of the modpack you want to install: ")
    if modpack in modpacks:
        print(f"Downloading {modpack}...")
        modpack_url = f"https://raw.githubusercontent.com/{user}/{repo}/main/modpacks/{modpack}.txt"
        response = requests.get(modpack_url)
        response.raise_for_status()

        with open(f"./modpacks/{modpack}.txt", 'w') as f:
            f.write(response.text)
        print(f"{modpack} downloaded successfully.")
    else:
        print(f"Modpack '{modpack}' does not exist. Exiting...")
        exit(1)

    process_modpack(modpack)

def config_download():
    """
    Downloads and applies custom configuration files from a GitHub repository.
    """
    print("Downloading and applying custom config files...")
    config_temp_dir = f"{MOD_DOWNLOAD_PATH}/config-temp"
    bepinex_config_dir = "BepInEx/config"

    # Create temporary directory for downloading and extracting configs
    if not os.path.exists(config_temp_dir):
        os.makedirs(config_temp_dir)

    # Download the zip file from the GitHub repository
    config_zip_url = 'https://github.com/rsm28/LC_BF2/archive/refs/heads/main.zip'
    config_zip_path = os.path.join(config_temp_dir, 'main.zip')
    print("Downloading config files...")
    response = requests.get(config_zip_url)
    with open(config_zip_path, 'wb') as f:
        f.write(response.content)

    # Extract the zip file
    print("Extracting config files...")
    with zipfile.ZipFile(config_zip_path, 'r') as zip_ref:
        zip_ref.extractall(config_temp_dir)

    # Copy the config files to the BepInEx config directory
    source_config_dir = os.path.join(config_temp_dir, 'LC_BF2-main', 'config')
    if os.path.exists(source_config_dir):
        print("Copying config files to BepInEx config directory...")
        shutil.copytree(source_config_dir, bepinex_config_dir, dirs_exist_ok=True)

    # Remove the temporary directory
    shutil.rmtree(config_temp_dir)
    print("Custom config files applied successfully.")

def extract():
    # THE BIG BOY FUNCTION THAT DEALS WITH ALL SHIT MOD AUTHORS
    # 1. if a folder called "BepInEx" exists, we merge it, going from MOD_DOWNLOAD_PATH, and merging it with the one in the root folder (in essence, MOD_DOWNLOAD_PATH\BepInEx merges with <root directory>\BepInEx)
    # 2. if "BepInEx" does NOT exist, we do one of the following:
        # 2a. if "plugins" exists, merge it with <root directory>\BepInEx\plugins
        # 2b. if "config" exists, do the same as 2a, but for config
        # 2c. if "patchers" exists, do the same as 2a, but for patchers
        # 2d. if NO folders exist, we do these two things:
            #2da. move all .dll folders into <root directory>\BepInEx\plugins
    time.sleep(3)
    print("---------- extract ----------")
    root_dir = os.getcwd()
    bepinex_dir = os.path.join(root_dir, "BepInEx")
    mod_download_path = os.path.join(root_dir, MOD_DOWNLOAD_PATH)

    # Check if BepInEx folder exists in mod downloads
    if os.path.isdir(os.path.join(mod_download_path, "BepInEx")):
        # Merge it with the one in the root directory
        shutil.copytree(os.path.join(mod_download_path, "BepInEx"), bepinex_dir, dirs_exist_ok=True)
    else:
        # Check for internal BepInEx folders
        for folder in ["plugins", "config", "patchers", "core", "cache", "Lang", "Bundles"]:
            if os.path.isdir(os.path.join(mod_download_path, folder)):
                # Merge them with the corresponding folders in the root directory
                shutil.copytree(os.path.join(mod_download_path, folder), os.path.join(bepinex_dir, folder), dirs_exist_ok=True)

        # If no folders exist, move all .dll files into BepInEx/plugins
        if not any(os.path.isdir(os.path.join(mod_download_path, folder)) for folder in os.listdir(mod_download_path)):
            for file in os.listdir(mod_download_path):
                if file.endswith(".dll"):
                    shutil.move(os.path.join(mod_download_path, file), os.path.join(bepinex_dir, "plugins"))
                    print(f"Moved {file} to {os.path.join(bepinex_dir, 'plugins')}")
                # exceptions/edge cases:
                # NEEDYCATS
                if file == "names.txt":
                    shutil.move(os.path.join(mod_download_path, file), os.path.join(bepinex_dir, "plugins"))
    


if not os.path.exists(MOD_DOWNLOAD_PATH):
    os.makedirs(MOD_DOWNLOAD_PATH)
if not os.path.exists("modpacks"):
    os.makedirs("modpacks")

if __name__ == "__main__":
    print("---------- CLEARING OLD BEPINEX FILES ----------")
    clear_old_bepinex()
    print("---------- CLEARING MOD DOWNLOADS ----------")
    clear_mod_downloads()
    print("---------- DOWNLOADING AND SETTING UP BEPINEX ----------")
    download_and_setup_bepinex()
    print("---------- STARTING DOWNLOADS... ----------")
    fetch_modpacks()
    print("---------- DOWNLOADING CONFIGS ----------")
    config_download()
    print("---------------------------")
    print("All done! Launch LC to play.")
