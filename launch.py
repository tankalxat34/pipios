"""
PipIOS - simple tool for managing Python packages in IOS application Pythonista

Commands for work with tool
    install     Install or update the requested package from PyPi on your IOS device (shortly as `i`)
    update      Update the requested package from PyPi on your IOS device to the last version (shortly as `u`)
    info        Show you information about the requested package (shortly as `p`)
    version     Print version of the requested package (shortly as `v`)
    delete      Delete the requested package (shortly as `d`)
    list        Show you all packages that installed on your device (shortly as `l`)
    count       Show count of installed packages
    releases    Show list of versions for the requested package
    help        Show this message
    exit        Exit from tool

Paramethers for work with commands
    ~version    Install the package of the specified version

Flags for work with commands
    -i          Ignore any conflicts with Python versions
    -d          Delete package with depencies
    -v          Show versions of installed packages

(c) tankalxat34 - 2022
https://github.com/tankalxat34/pipios
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


if sys.platform == "ios":
    # Pythonista
    PATH_TO_INSTALL = sys.path[1]
else:
    raise ValueError("You're platform is not IOS!")

print(PATH_TO_INSTALL)


class Command:
    def __init__(self, command):
        """Class for parsing command in PipIOS terminal"""
        self.command = command.split()

        self.flags = list()
        self.params = dict()
        self.names = list()

        for word in self.command[1:]:
            if word[0] == "~":
                self.params[word[1:].split("=")[0].strip()] = word[1:].split("=")[1].strip()
            elif word[0] == "-":
                self.flags.append(word[1])
            else:
                self.names.append(word)

    def get_flags(self):
        """Return list of flags from command"""
        return self.flags
    
    def get_params(self):
        """Return dictionary with key:value pairs"""
        return self.params
    
    def get_names(self):
        """Return list of names from command"""
        return self.names



class PackagesDir:
    def __init__(self, command: Command, path: str = PATH_TO_INSTALL) -> None:
        self.path = path
        self.command = command
        print(self.command.get_flags())
    
    def list(self):
        result = list()
        for element in os.listdir(self.path):
            if ".dist-info" not in element:
                if ".py" in element:
                    package = element[:-3]
                else:
                    package = element

                if "v" in self.command.get_flags():
                    package += f" {Package('', package)._installedVersion()}"

                result.append(package.lower())
        result.sort()
        return result
    
    def count(self):
        return len(self.list())


class Package:
    def __init__(self, command: Command, path_to_install: str = PATH_TO_INSTALL):
        """Class for package-object"""
        self.command = command
        self.name = self.command.get_names()[0]
        self.path_to_install = path_to_install

        try:
            self.response = urllib.request.urlopen(PYPI_JSON % self.name)
            for e in self.response:
                self.info = json.loads(e)
                break
        except urllib.error.HTTPError:
            raise NameError("This package does not existing on PyPi or package does not existing on your device!")
    
    def _installedVersion(self):
        for folder in os.listdir(self.path_to_install):
            if self.name in folder and ".dist-info" in folder:
                return folder.split("-")[1][:-5]
        return "This package doesnt have any version!"
    
    def _parseMetadata(self):
        path_to_package = self.path_to_install + "/" + self.name
        with open(path_to_package +  "-" + self._installedVersion() + ".dist-info/METADATA", encoding="UTF-8") as file:
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
            result = ""
            for key in mtd.keys():
                result += f"{key}: {mtd[key]}\n"
            return result
        except Exception as e:
            return "Package does not have any information about itself or package is not defined!"

    def get_pypi(self):
        return self.info

    def releases(self):
        result = []
        for release in self.info["releases"].keys():
            result.append(release)
        return result

    def correctPythonVersion(self):
        try:
            package_python_versions = list(re.findall("\d{0,2}\.{1,}\d{0,2}\.{0,}\d{0,2}", self.info["urls"][0]["requires_python"]))
            if sys.version_info >= tuple(map(int, package_python_versions[0].split("."))):
                return True
            else:
                return False
        except TypeError:
            return True
    
    def update(self, showMessage: bool = False):
        old_version = self._installedVersion()
        if self.is_installed():
            self.install()
            new_version = self._installedVersion()
            if showMessage:
                if old_version != new_version:
                    return (f"The \"{self.name}\" package has been updated: {old_version} -> {new_version}")
                else:
                    return (f"The \"{self.name}\" package does not updated because you are using the last version of this package!")
        else:
            return (f"The \"{self.name}\" package does not existing!")

    def is_installed(self):
        return self.name in " ".join(os.listdir(self.path_to_install))
    
    def delete(self, showMessage: bool = False):
        counterFiles = 0
        for file in os.listdir(self.path_to_install):
            if self.name.lower() == file.lower() or f"{self.name.lower()}-{self._installedVersion()}.dist-info" == file.lower():
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
        self.delete(True)
        if "i" in self.command.get_flags():
            print("Ignore Python version enabled!")
        if not self.correctPythonVersion() and not "i" in self.command.get_flags():
            raise ValueError("Invalid Python version to install this package!")

        if "version" in self.command.get_params().keys():
            print("Installing user version", self.info['releases'][self.command.get_params()['version']][0]['filename'])
            whl_archive = BytesIO(urllib.request.urlopen(self.info["releases"][self.command.get_params()["version"]][0]["url"]).read())
        else:
            print("Installing", self.info['urls'][0]['filename'])
            whl_archive = BytesIO(urllib.request.urlopen(self.info["urls"][0]["url"]).read())

        with zipfile.ZipFile(file=whl_archive, mode="r") as archive:
            for file in archive.namelist():
                archive.extract(file, self.path_to_install)

        if showMessage:
            if "version" in self.command.get_params().keys():
                return f"Package '{self.info['info']['name']}' v{self.command.get_params()['version']} successfully installed!"
            return f"Package '{self.info['info']['name']}' v{self.info['info']['version']} successfully installed!"
        else:
            return True
        


COMMANDS = {
    "pipios":   lambda c: print("Hello from PipIOS! Please type 'i <package_name>' or 'help' to get more information!"),
    "help":     lambda c: print(__doc__),
    "exit":     lambda c: sys.exit(),
    "i":        lambda c: print(Package(Command(c)).install(True)),
    "install":  lambda c: print(Package(Command(c)).install(True)),
    "u":        lambda c: print(Package(Command(c)).update(True)),
    "update":   lambda c: print(Package(Command(c)).update(True)),
    "d":        lambda c: print(Package(Command(c)).delete(True)),
    "delete":   lambda c: print(Package(Command(c)).delete(True)),
    "v":        lambda c: print(Package(Command(c))._installedVersion()),
    "version":  lambda c: print(Package(Command(c))._installedVersion()),
    "p":        lambda c: print(Package(Command(c)).showInfo()),
    "info":     lambda c: print(Package(Command(c)).showInfo()),
    "list":     lambda c: print("\n".join(PackagesDir(Command(c)).list())),
    "count":    lambda c: print(PackagesDir(Command(c)).count()),
    "releases": lambda c: print("\n".join(Package(Command(c)).releases()))
}

command = "pipios"
COMMANDS[command.split()[0]](command)

while command != "exit":
    try:
        command = str(input(">>>"))
        try:
            COMMANDS[command.split()[0]](command)
        except KeyError:
            print("Invalid command. Type help to get more information!")

        print("")
    except Exception as e:
        print(e, e.with_traceback)
