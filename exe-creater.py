import os
import sys
import subprocess

def package_executable(script_name):
    # Check if the provided script exists
    if not os.path.isfile(script_name):
        print(f"Error: {script_name} does not exist.")
        return
    
    command = [
    'pyinstaller',
    '--onefile',
    '--windowed',
    '--distpath', '.',
    '--exclude-module', 'numpy',  # If you're sure you don't need numpy (not common)
    script_name
    ]


    # Run the PyInstaller command
    print(f"Packaging {script_name} into an executable...")
    try:
        subprocess.run(command, check=True)
        print("Packaging complete. Check the current directory for the executable.")
    except subprocess.CalledProcessError as e:
        print(f"Error during packaging: {e}")
        sys.exit(1)

if __name__ == "__main__":
    script_to_package = 'worldBankUI.py'  # Specify the main script
    package_executable(script_to_package)
