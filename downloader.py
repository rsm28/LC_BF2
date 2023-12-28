import os
import shutil
import requests
import zipfile
import time
import subprocess

MOD_DOWNLOAD_PATH = "mod_downloads"

def clear_mod_downloads():
    print("Clearing everything from " + MOD_DOWNLOAD_PATH + "...")
    # Check if MOD_DOWNLOAD_PATH exists
    if os.path.exists(MOD_DOWNLOAD_PATH):
        for root, dirs, files in os.walk(MOD_DOWNLOAD_PATH):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
    else:
        print("MOD_DOWNLOAD_PATH does not exist, skipping")

def clear_old_bepinex():
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

def download_mod(author, mod, version):
    if mod == "LC_API":
        version = "2.2.0"
    print(f"Downloading {mod} version {version} from author {author}...")
    
    webrequest_url = f"https://thunderstore.io/package/download/{author}/{mod}/{version}/"
    print(webrequest_url)
    
    response = requests.get(webrequest_url)
    download_path = f"{MOD_DOWNLOAD_PATH}/{mod}_{version}.zip"
    with open(download_path, 'wb') as f:
        f.write(response.content)

    print(f"Extracting {mod} version {version}...")
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(f"{MOD_DOWNLOAD_PATH}/")
    clear_mod_downloads()
    
def process_modpack(modpack):
    authors = []
    mods = []
    versions = []
    with open("modpacks/modpack.txt", "r") as file:
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

def download_and_setup_bepinex():
    print("Downloading and extracting BepInExPack...")
    # Step 1: Download BepInExPack
    response = requests.get('https://thunderstore.io/package/download/BepInEx/BepInExPack/5.4.2100/')
    download_path = "BepInExPack_5.4.2100.zip"
    with open(download_path, 'wb') as f:
        f.write(response.content)

    # Step 2: Extract the zip file directly to the root directory
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(".")

    print("Launching LC to install BepInEx...")
    # Step 4: Launch and close Lethal Company.exe
    process = subprocess.Popen(["Lethal Company.exe"])
    time.sleep(5)
    process.terminate()
    
    if os.path.isfile("BepInExPack_5.4.2100.zip"):
        os.remove("BepInExPack_5.4.2100.zip")

def extract():
    # THE BIG BOY FUNCTION THAT DEALS WITH ALL SHIT MOD AUTHORS
    # 1. if a folder called "BepInEx" exists, we merge it, going from MOD_DOWNLOAD_PATH, and merging it with the one in the root folder (in essence, MOD_DOWNLOAD_PATH\BepInEx merges with <root directory>\BepInEx)
    # 2. if "BepInEx" does NOT exist, we do one of the following:
        # 2a. if "plugins" exists, merge it with <root directory>\BepInEx\plugins
        # 2b. if "config" exists, do the same as 2a, but for config
        # 2c. if "patchers" exists, do the same as 2a, but for patchers
        # 2d. if NO folders exist, we do these two things:
            #2da. move all .dll folders into <root directory>\BepInEx\plugins
    root_dir = os.getcwd()
    bepinex_dir = os.path.join(root_dir, "BepInEx")
    mod_download_path = os.path.join(root_dir, MOD_DOWNLOAD_PATH)

    # Check if BepInEx folder exists in mod downloads
    if os.path.isdir(os.path.join(mod_download_path, "BepInEx")):
        # Merge it with the one in the root directory
        shutil.copytree(os.path.join(mod_download_path, "BepInEx"), bepinex_dir, dirs_exist_ok=True)
    else:
        # Check for plugins, config, patchers folders
        for folder in ["plugins", "config", "patchers"]:
            if os.path.isdir(os.path.join(mod_download_path, folder)):
                # Merge them with the corresponding folders in the root directory
                shutil.copytree(os.path.join(mod_download_path, folder), os.path.join(bepinex_dir, folder), dirs_exist_ok=True)

        # If no folders exist, move all .dll files into BepInEx/plugins
        if not any(os.path.isdir(os.path.join(mod_download_path, folder)) for folder in os.listdir(mod_download_path)):
            for file in os.listdir(mod_download_path):
                if file.endswith(".dll"):
                    shutil.move(os.path.join(mod_download_path, file), os.path.join(bepinex_dir, "plugins"))
   
    

if not os.path.exists(MOD_DOWNLOAD_PATH):
    os.makedirs(MOD_DOWNLOAD_PATH)
if not os.path.exists("modpacks"):
    os.makedirs("modpacks")

if __name__ == "__main__":
    clear_old_bepinex()
    clear_mod_downloads()
    download_and_setup_bepinex()
    process_modpack("modpack.txt")

