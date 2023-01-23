"""
This module implement package in `site-packages`

PipIOS

(c) tankalxat34 - 2023
"""

import re
import urllib3
import json
import pathlib
import string
import sys
import shutil
import os

try:
    import Constants
except ModuleNotFoundError:
    from . import Constants

try:
    import App
except ModuleNotFoundError:
    from . import App

try:
    import RequiresParser
except ModuleNotFoundError:
    from . import RequiresParser

try:
    import Exceptions
except ModuleNotFoundError:
    from . import Exceptions


class InstalledPackage(App.Multiclass):
    def __init__(
        self,
        name: str,
        # _site_packages: pathlib = pathlib.Path("site-packages").absolute(), 
        _site_packages: pathlib = Constants.USER.PATH, 
        _detailed_log: bool = False
        ):
        self.name = name.lower()
        self.name_replaced = self.name.replace("-", "_")
        self._site_packages = _site_packages
        self._detailed_log = _detailed_log
        
        self.py_files = list()
        self.other_files = list()
        self._package_files = list()

        for file in self._site_packages.iterdir():
            if self.name_replaced in file.name.lower():
                self._package_files.append(file)
                if file.is_dir():
                    if re.findall(f"{self.name_replaced}\-\d.*\.dist-info", file.name.lower()):
                        self.dist_info = file
                        self.metadata_path = file / "METADATA"

                    if f"{self.name_replaced}.egg-info" in file.name.lower():
                        self.egg_info = file
                        self.pkg_info_path = file / "PKG-INFO"

                    if self.name_replaced == file.name.lower():
                        self.main_dir = file
                
                elif file.is_file():
                    if file.suffix == ".py":
                        self.py_files.append(file)
                    else:
                        self.other_files.append(file)
        
        if not self._package_files:
            raise Exceptions.SitePackages.PackageNotFoundError(self.name)

        try:
            self.metadata = App.Metadata(self.metadata_path)
        except AttributeError:
            self.metadata = App.Metadata(self.pkg_info_path)
        
        self.version = self.metadata.version
        self.summary = self.metadata.summary
    
    def __str__(self):
        return f"PipIOS.InstalledPackage({self.__dict__})"

    def uninstall(self):
        """Deleting this package from your device"""
        print("Found existing installation:", self.name, self.metadata.version)
        print("Uninstalling", f"{self.name}-{self.metadata.version}:")
        for file in self._package_files:
            print(" ", str(file).lower())
            shutil.rmtree(str(file))
        print("Successfully uninstalled", f"{self.name}-{self.metadata.version}")
        return True
        

if __name__ == "__main__":
    # pack = InstalledPackage("pandas", pathlib.Path("site-packages").absolute())
    pack = InstalledPackage("pandas", pathlib.Path("site-packages").absolute())
    print(RequiresParser.Requirements(pack.metadata.requires_dist))
    # print(pack.metadata)
    # print(pack.version)
    # print(pack.summary)
