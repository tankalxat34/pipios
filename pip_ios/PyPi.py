"""
This module implement package on PyPi

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

from io import BytesIO
import zipfile
import tarfile

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


class Release(App.Multiclass):
    def __init__(self, dictionary_pypi: dict):
        self.dictionary_pypi = dictionary_pypi

        for k in self.dictionary_pypi.keys():
            self.__setattr__(k, self.dictionary_pypi[k])
        


class PyPi(App.Multiclass):
    def __init__(
        self, 
        name: str, 
        version: str = None, 
        # _site_packages: pathlib = pathlib.Path("site-packages").absolute(), 
        _site_packages: pathlib = Constants.USER.PATH,
        _requires_python: RequiresParser.Version = App.USER_PYTHON_VERSION,
        _detailed_log: bool = False
        ):
        """
        Get access to information on `pypi.org` about package
        """
        self.name = name
        self._version = version
        self._site_packages = _site_packages
        self._requires_python = _requires_python
        self._detailed_log = _detailed_log


        self.pm = urllib3.PoolManager()
        
        self._request_url = Constants.URL.PYPI_JSON.format(name=name)
        if self._version:
            self._request_url = Constants.URL.PYPI_VERSION_JSON.format(name=self.name, version=self._version)

        self._pypi = self.pm.request("GET", self._request_url)
        self._resp = json.loads(self._pypi.data)

        if "message" in self._resp.keys() and self._resp["message"].lower() == "not found":
            raise Exceptions.PyPi.PackageOrVersionDoesNotExistsOnPyPi(self.name)

        # determine attributes & reinitialisation of _version attribute for quick access
        self._version = self._resp["info"]["version"]
        
        for k in self._resp["info"].keys():
            self.__setattr__(k, self._resp["info"][k])

        for k in self._resp.keys():
            self.__setattr__(k, self._resp[k])
        
        self.whl_platform = Constants.PLATFORM.ANY
        
        if sys.platform in [Constants.PLATFORM.WIN32, Constants.PLATFORM.CYGWIN, Constants.PLATFORM.WIN_AMD64]:
            self.whl_platform = Constants.PLATFORM.WIN32
        
        elif sys.platform in [Constants.PLATFORM.IOS, Constants.PLATFORM.MACOSX, Constants.PLATFORM.MACOSX_10_9, Constants.PLATFORM.MACOSX_11_0_ARM64]:
            self.whl_platform = Constants.PLATFORM.MACOSX_10_9

        elif sys.platform in [Constants.PLATFORM.LINUX, Constants.PLATFORM.LINUX2, Constants.PLATFORM.MANYLINUX_ARCH64, Constants.PLATFORM.MANYLINUX_X86_64]:
            self.whl_platform = Constants.PLATFORM.MANYLINUX_X86_64
        
        # determine attributes for download package
        self._release_objects = self._find_url_files()
        self.package_obj = None
    
    def version_before_specified(self, version):
        """Returns the version released before the specified"""
        index = self.all_versions().index(version)
        return self.all_versions()[index - 1]

    def is_version_exising(self, version: str):
        """Return True if specified version is existing"""
        return version in self.all_versions()

    def all_versions(self):
        """Return list with all versions of package"""
        return list(self.releases.keys())

    def __str__(self):
        return f"PipIOS.PyPi({self.__dict__})"

    def _find_targz_url(self):
        """Return release with url to `.tar.gz` file by specified version"""
        release = self.urls[-1]
        release["whl_tar"] = App.TarGzFile(release["url"])
        return Release(release)

    def _find_url_files(self):
        """Return list with string URLs to files by specified version"""
        result = []
        RELEASES = self.urls
        for release in RELEASES:
            release["whl_tar"] = App.WheelFile(release["url"])

            if (release["whl_tar"].platform in [self.whl_platform, Constants.PLATFORM.ANY]) and \
                (release["packagetype"] == Constants.PACKAGETYPE.WHEEL) and \
                self._requires_python.compare_with(release["requires_python"]):
                    # RequiresParser.Version("3.10.0").compare_with(release["requires_python"]):
                result.append(Release(release))

        result.append(self._find_targz_url())
        
        return result[-2:]

    def _read_iobytes_archive(self):
        """Return `BytesIO` of archive"""
        result = []
        for release in self._release_objects:
            iobytes_file = BytesIO(self.pm.request("GET", release.url).data)
            result.append(iobytes_file)
        return result

    def _unpack_as_zip(self, iobytes: BytesIO):
        """Unpack archive that represented as wheel (`*.zip`)"""
        with zipfile.ZipFile(iobytes, 'r') as archive:
            for file in archive.namelist():
                archive.extract(file, self._site_packages)
    
    def _unpack_as_targz(self, iobytes: BytesIO):
        """Unpack archive that represented as `*.tar.gz`"""
        tar = tarfile.open(fileobj=iobytes)
        for member in tar.getmembers():
            try:
                if self.name.lower() in f"{str(member.name).lower().split('/')[1]}":
                    tar.extract(member, self._site_packages)
                else:
                    if self._detailed_log:
                        print("    Ignored file:", member.path)
            except Exception:
                pass
        tar.close()

    def _move_files_from_unpacked_targz(self):
        """Move all folders from the unpacked .tar.gz folder with replacement"""
        unpacked_targz = pathlib.Path(self._site_packages / f"{self.name}-{self._version}")
        for directory in unpacked_targz.iterdir():
            shutil.move(str(directory.absolute()), str(self._site_packages))
        unpacked_targz.rmdir()
    
    def setup(self):
        """Setup package to site-packages on your device"""
        print(f"Collecting {self.name}" + f"=={self._version}")
        readed_iobytes = self._read_iobytes_archive()
        for i in range(len(readed_iobytes)):
            if self._release_objects[i].packagetype == Constants.PACKAGETYPE.SDIST:
                print("  Downloading", self._release_objects[i].whl_tar.basename, end=" ")
                print("(", *App.calculate_bytes_size(readed_iobytes[i]), ")", sep="")
                self._unpack_as_targz(readed_iobytes[i])
                self._move_files_from_unpacked_targz()
                # print("  Success!")
        
        for i in range(len(readed_iobytes)):
            if self._release_objects[i].packagetype == Constants.PACKAGETYPE.WHEEL:
                print("  Downloading", self._release_objects[i].whl_tar.basename, end=" ")
                print("(", *App.calculate_bytes_size(readed_iobytes[i]), ")", sep="")
                self._unpack_as_zip(readed_iobytes[i])
                # print("  Success!")
        return True


if __name__ == "__main__":
    pack = PyPi(name = "numpy", _site_packages = pathlib.Path("site-packages").absolute())
    # print(pack.setup())
    print(pack.all_versions())
    # print(pack._site_packages)
    # print(pack._release_objects)
    # print(pack._read_iobytes_archive())
    # print(pack._move_files_from_unpacked_targz())
        # print(e)
