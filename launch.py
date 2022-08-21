"""
Launch the pipios console

/private/var/mobile/Containers/Shared/AppGroup/CODE-CODE-CODE/Pythonista3/Documents/site-packages-3
"""

import pathlib
import os
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
            print("Installing", response["filename"], end=" ")
            # fileForInstall = urllib.request.urlretrieve(response["url"], response["filename"])
            print("Completed!")

            with zipfile.ZipFile(response["filename"], mode="r") as archive:
                for file in archive.namelist():
                    if file.split("/")[0] == pypi_response["info"]["name"]:
                        archive.extract(file)
                    else:
                        break
    else:
        print(f"Package \"{package}\" does not existing on PyPi!")


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
    "exit": lambda: quit(),
    "package": lambda c: print(c),
    "install": lambda c: _installPackage(c.split()[1])
}

# command = "install uploadgrampyapi"
# command = "install vk_api"
command = "install requests"
COMMANDS[command.split(" ")[0]](command)

# command = "pipios"
# COMMANDS[command]()

# while command != "exit":
#     try:
#         command = str(input(">>>"))
#     except TypeError:
#         pass
#     try:
#         COMMANDS[command.split()[0]](command)
#     except KeyError:
#         command = str(input("Invalid command. Type help to get more information...\n>>>"))