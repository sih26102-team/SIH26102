import urllib.request
import zipfile
import os
import sys

NODE_URL = "https://nodejs.org/dist/v20.11.1/node-v20.11.1-win-x64.zip"
ZIP_FILE = "node-portable.zip"
EXTRACT_DIR = "node_portable"

print("Downloading portable Node.js (this bypasses your system installation)...")
try:
    urllib.request.urlretrieve(NODE_URL, ZIP_FILE)
    print("Download complete. Extracting...")
    
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
        
    os.remove(ZIP_FILE)
    print("Extraction complete.")
    
    # Create the launcher script
    bat_content = f"""@echo off
echo ====================================================
echo Starting CivicShield Frontend using Portable Node.js
echo ====================================================

:: Set PATH to use the portable node ONLY for this script
set PATH=%~dp0{EXTRACT_DIR}\\node-v20.11.1-win-x64;%PATH%

:: Verify Node works
echo Verifying Node.js...
node -v
npm -v

cd frontend-dashboard

echo.
echo Installing dependencies (this may take a minute the first time)...
call npm install

echo.
echo Starting Vite development server...
call npm run dev
pause
"""
    with open("start_frontend.bat", "w") as f:
        f.write(bat_content)
        
    print("\nSUCCESS! I have downloaded a standalone, portable version of Node.js.")
    print("You do not need to install NPM on your laptop anymore.")
    print("Just double-click 'start_frontend.bat' in this folder to run the React app!")
    
except Exception as e:
    print(f"Error: {e}")
