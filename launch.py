"""
PipIOS - simple tool for managing Python packages in IOS application Pythonista

Commands for work with tool
    install     Can install the requested package from PyPi on your IOS device (shortly as `i`)
    info        Can show you information about the requested package (shortly as `p`)
    version     Print version of the requested package (shortly as `v`)
    delete      Can delete the requested package (shortly as `d`)
    list        Can show you all packages that installed on your device (shortly as `l`)
    help        Show this message
    exit        Exit from tool

Paramethers for work with commands
    --version   Install the package of the specified version

Flags for work with commands
    -i          Ignore any conflicts with Python versions   

(c) tankalxat34 - 2022
https://github.com/tankalxat34/pipios
"""

import pathlib
import os
from io import BytesIO
import shutil
from tkinter import COMMAND
import zipfile
import urllib
import urllib.request
import json
import sys
import re

__version__ = "0.1.0"
__author__ = "tankalxat34 <tankalxat34@gmail.com>"


PYPI_JSON = "https://pypi.org/pypi/%s/json"

if True:
    PATH_TO_INSTALL = os.getcwd() + "/test"
else:
    if sys.platform == "ios":
        # Pythonista
        PATH_TO_INSTALL = sys.path[1]
    else:
        PATH_TO_INSTALL = sys.path[3]

print(PATH_TO_INSTALL)


class Package:
    def __init__(self, name: str, path_to_install: str = PATH_TO_INSTALL):
        """Class for package-object"""
        self.name = name
        self.path_to_install = path_to_install

        try:
            self.response = urllib.request.urlopen(PYPI_JSON % name)
            for e in self.response:
                self.info = json.loads(e)
                break
        except urllib.error.HTTPError:
            raise NameError("This package does not existing on PyPi or package does not existing on your device!")
    
    def _installedVersion(self):
        for folder in os.listdir(self.path_to_install):
            if self.name in folder and ".dist-info" in folder:
                return re.findall("\d{1,}\.\d{1,}\.\d{1,}", folder)[0]
        return "This package doesnt have any version!"
    
    def _parseMetadata(self):
        path_to_package = self.path_to_install + "/" + self.name
        with open(path_to_package +  "-" + self._installedVersion() + ".dist-info/METADATA") as file:
            content = file.readlines()
        
        dct = dict()

        for line in content:
            key = line.split(":")[0].lower()
            if line != "\n":
                value = "".join(line.split(":")[1:])
                try:
                    dct[key] += value
                except KeyError:
                    dct[key] = value
            else:
                break
        
        dct["path_to_package"] = path_to_package
        
        for key in dct.keys():
            dct[key] = dct[key].strip()
        
        return dct
    
    def showInfo(self):
        try:
            mtd = self._parseMetadata()
            return f"""NAME: {mtd["name"]} v{mtd["version"]}
AUTHOR: {mtd["author"]} 
    EMAIL: {mtd["author-email"]}
DESCRIPTION: {mtd["summary"]}
HOME-PAGE: {mtd["home-page"]}
PATH: {mtd["path_to_package"]}"""
        except Exception:
            return "Package does not have any information about itself or package is not defined!"

    def get_pypi(self):
        return self.info

    def correctPythonVersion(self):
        try:
            package_python_versions = list(re.findall("\d{0,2}\.{1,}\d{0,2}\.{0,}\d{0,2}", self.info["urls"][0]["requires_python"]))
            if sys.version_info >= tuple(map(int, package_python_versions[0].split("."))):
                return True
            else:
                return False
        except TypeError:
            return True

    def is_installed(self):
        return self.name in os.listdir(self.path_to_install)
    
    def delete(self, showMessage: bool = False):
        counterFiles = 0
        for file in os.listdir(self.path_to_install):
            if self.name in file or self.name.lower() in file.lower():
                try:
                    # trying remove as dir
                    shutil.rmtree(self.path_to_install + "/" + file)
                except Exception:
                    os.remove(self.path_to_install + "/" + file)
                counterFiles += 1
        if showMessage:
            if counterFiles:
                return (f"The \"{self.name}\" package was removed successfully!")
            else:
                return (f"The \"{self.name}\" package does not existing!")
    
    def install(self, showMessage: bool = False):
        if self.correctPythonVersion():
            print("Installing", self.info['urls'][0]['filename'])
            whl_archive = BytesIO(urllib.request.urlopen(self.info["urls"][0]["url"]).read())

            with zipfile.ZipFile(file=whl_archive, mode="r") as archive:
                for file in archive.namelist():
                    archive.extract(file, self.path_to_install)

            if showMessage:
                return f"Package '{self.info['info']['name']}' v{self.info['info']['version']} successfully installed!"
            else:
                return True
        else:
            raise ValueError("Invalid Python version to install this package!")


COMMANDS = {
    "pipios":   lambda c: print("Hello from PipIOS! Please type 'i <package_name>' or 'help' to get more information!"),
    "help":     lambda c: print(__doc__),
    "exit":     lambda c: sys.exit(),
    "i":        lambda c: print(Package(c.split()[1]).install(True)),
    "install":  lambda c: print(Package(c.split()[1]).install(True)),
    "d":        lambda c: print(Package(c.split()[1]).delete(True)),
    "delete":   lambda c: print(Package(c.split()[1]).delete(True)),
    "v":        lambda c: print(Package(c.split()[1])._installedVersion()),
    "version":  lambda c: print(Package(c.split()[1])._installedVersion()),
    "p":        lambda c: print(Package(c.split()[1]).showInfo()),
    "info":     lambda c: print(Package(c.split()[1]).showInfo()),
}

# command = "install uploadgrampyapi"
# command = "install vk_api"
# command = "install requests"
command = "pipios"
# command = "pipios"
COMMANDS[command.split()[0]](command)

# p = Package("qwerty")
# print(p.showInfo())

while command != "exit":
    try:
        command = str(input(">>>"))
        try:
            COMMANDS[command.split()[0]](command)
        except KeyError:
            print("Invalid command. Type help to get more information!")

        print("")
    except Exception as e:
        print(e)
