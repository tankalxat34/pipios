"""
Launch the pipios console

/private/var/mobile/Containers/Shared/AppGroup/CODE-CODE-CODE/Pythonista3/Documents/site-packages-3
"""

import pathlib
import os
from io import BytesIO
import shutil
import zipfile
import urllib
import urllib.request
import json
import sys
import re

__version__ = "0.1.0"
__author__ = "tankalxat34 <tankalxat34@gmail.com>"


PYPI_JSON = "https://pypi.org/pypi/%s/json"


def _checkPythonVersion(response: str):
    try:
        package_python_versions = list(re.findall("\d{0,2}\.{1,}\d{0,2}\.{0,}\d{0,2}", response["requires_python"]))
        if sys.version_info >= tuple(map(int, package_python_versions[0].split("."))):
            return True
        else:
            return False
    except TypeError:
        return None


def _installPackage(package: str):
    pypi_response = _getPyPiPackageInfo(package)
    if pypi_response != "__invalid_package_name__":
        response = pypi_response["urls"][0]
        print("Connecting to", response["filename"])

        python_version = _checkPythonVersion(response)
        if python_version:
            print("The Python version is suitable for installing this package")
        elif python_version == False:
            print("The Python version is not suitable for installing this package")
        else:
            print("Python version does not appear for installing")

        if python_version in [True, None]:
            print("Installing", response["filename"])            
            whl_archive = BytesIO(urllib.request.urlopen(response["url"]).read())

            with zipfile.ZipFile(file=whl_archive, mode="r") as archive:
                for file in archive.namelist():
                    if "/" in file:
                        if file.split("/")[0] == package:
                            archive.extract(file)
                        else:
                            break
                    else:
                        archive.extract(file)
            print(f"The \"{package}\" package was installed successfully!")
    else:
        print(f"Package \"{package}\" does not existing on PyPi!")


def _deletePackage(package: str):
    try:
        shutil.rmtree(package)
        print(f"The \"{package}\" package was removed successfully!")
    except FileNotFoundError:
        print(f"The \"{package}\" package does not existing!")


def _getPyPiPackageInfo(package: str):
    """Getting info in JSON format"""
    try:
        response = urllib.request.urlopen(PYPI_JSON % package)
        for e in response:
            return json.loads(e)
    except urllib.error.HTTPError:
        return "__invalid_package_name__"


COMMANDS = {
    "pipios": lambda: print("PIPIOS - this is a tool for Pythonista for full managing your installed Python-packages. Type help to get more information.", sys.platform),
    "exit": lambda: sys.exit(),
    "package": lambda c: print(c),
    "install": lambda c: _installPackage(c.split()[1]),
    "i": lambda c: _installPackage(c.split()[1]),
    "d": lambda c: _deletePackage(c.split()[1])
}

# command = "install uploadgrampyapi"
# command = "install vk_api"
# command = "install requests"
command = "pipios"
# command = "pipios"
COMMANDS[command]()

while command != "exit":

    command = str(input(">>>"))

    try:
        COMMANDS[command.split()[0]](command)
    except KeyError:
        # command = str(input("Invalid command. Type help to get more information...\n>>>"))
        print("Invalid command. Type help to get more information!")
    
    print("")