@echo off
echo Checking for required Python dependencies...
IF EXIST requirements.txt (
    echo Installing dependencies from requirements.txt...
    python -m pip install -r requirements.txt
    IF %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to install dependencies. Please check your Python and pip installation.
        pause
        exit /b %ERRORLEVEL%
    )
    echo Dependencies installed successfully.
) ELSE (
    echo Error: requirements.txt not found. Please ensure it exists in the same directory as this script.
    pause
    exit /b 1
)

echo Running downloader.py...
IF EXIST downloader.py (
    python downloader.py
    IF %ERRORLEVEL% NEQ 0 (
        echo Error: downloader.py encountered an error.
        pause
        exit /b %ERRORLEVEL%
    )
) ELSE (
    echo Error: downloader.py not found. Attempting to download...
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rsm28/LC_BF2/main/downloader.py' -OutFile 'downloader.py'"
    IF EXIST downloader.py (
        echo Successfully downloaded downloader.py. Running the script...
        python downloader.py
    ) ELSE (
        echo Failed to download downloader.py. Please check your internet connectivity or the URL and try again.
        pause
        exit /b 1
    )
)
pause
