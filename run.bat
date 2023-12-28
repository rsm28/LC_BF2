@echo off
IF EXIST downloader.py (
    echo downloader.py exists, running the script...
    python downloader.py
) ELSE (
    echo downloader.py not found, attempting to download...
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rsm28/LC_BF2/main/downloader.py' -OutFile 'downloader.py'"
    IF EXIST downloader.py (
        echo Successfully downloaded downloader.py, running the script...
        python downloader.py
    ) ELSE (
        echo Failed to download downloader.py. Please check your internet connectivity or the URL and try again.
    )
)
pause