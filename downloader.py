import os
import shutil
import requests
import zipfile

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
        print(authors)
        print(mods)
        print(versions)
    if len(authors) != len(mods) or len(mods) != len(versions):
        print("Error: The number of authors, mods, and versions do not match.")
        return
    for i in range(len(authors)):
        download_mod(authors[i], mods[i], versions[i])

if not os.path.exists(MOD_DOWNLOAD_PATH):
    os.makedirs(MOD_DOWNLOAD_PATH)
if not os.path.exists("modpacks"):
    os.makedirs("modpacks")

if __name__ == "__main__":
    clear_old_bepinex()
    clear_mod_downloads()
    process_modpack("modpack.txt")

