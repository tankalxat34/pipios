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


def _installPackage(package: str):
    response = _getPyPiPackageInfo(package)["urls"][1]
    if response != "__invalid_package_name__":
        print("Connecting to", response["filename"])

        # checking python version
        package_python_versions = list(re.findall("\d{0,2}\.{1,}\d{0,2}\.{0,}\d{0,2}", response["requires_python"]))
        if sys.version_info >= tuple(map(int, package_python_versions[0].split("."))):
            print("The Python version is suitable")
        else:
            print("The Python version is not suitable!")


def _getPyPiPackageInfo(package: str):
    """Getting info in JSON format"""
    try:
        response = urllib.request.urlopen(PYPI_JSON % package)
        for e in response:
            return json.loads(e)
    except urllib.error.HTTPError:
        print(f"Package \"{package}\" does not existing on PyPi!")
        return "__invalid_package_name__"


COMMANDS = {
    "pipios": lambda: print("PIPIOS - this is a tool for Pythonista for full managing your installed Python-packages. Type help to get more information.", sys.platform),
    "exit": lambda: quit(),
    "package": lambda c: print(c),
    "install": lambda c: _installPackage(c.split()[1])
}

command = "pipios"
COMMANDS[command]()

while command != "exit":
    try:
        command = str(input(">>>"))
    except TypeError:
        pass
    try:
        COMMANDS[command.split()[0]](command)
    except KeyError:
        command = str(input("Invalid command. Type help to get more information...\n>>>"))