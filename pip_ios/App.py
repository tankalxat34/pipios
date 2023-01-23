"""
Initialisation classes for PyPi-packages

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
    import RequiresParser
except ModuleNotFoundError:
    from . import RequiresParser

try:
    import Exceptions
except ModuleNotFoundError:
    from . import Exceptions

USER_PYTHON_VERSION = RequiresParser.Version(Constants.USER.PYTHON)

def calculate_bytes_size(iobytes: BytesIO):
    """Return `tuple` with rounded float number at first and humanized string at second"""
    size = sys.getsizeof(iobytes)
    if size / Constants.SIZE.BYTES <= Constants.SIZE.BYTES:
        return (round(size / Constants.SIZE.BYTES, 1), " BYTES")
    if size / Constants.SIZE.KB <= Constants.SIZE.KB:
        return (round(size / Constants.SIZE.KB, 1), " KB")
    if size / Constants.SIZE.MB <= Constants.SIZE.MB:
        return (round(size / Constants.SIZE.MB, 1), " MB")
    if size / Constants.SIZE.GB <= Constants.SIZE.GB:
        return (round(size / Constants.SIZE.GB, 1), " GB")

class Multiclass:
    """Class with ability to set and get attributes. Could be use as parent class"""
    def __init__(self) -> None:
        pass
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)


class Metadata(Multiclass):
    def __init__(self, path_or_dict):
        try:
            self.path = path_or_dict.absolute()
            self._parse()
        except Exception:
            for k in path_or_dict.keys():
                self.__setattr__(k, path_or_dict[k])

    def _parse(self):
        try:
            with open(self.path, "r", encoding="UTF-8") as file:
                content = file.readlines()
        except TypeError:
            raise Exceptions.SitePackages.MetadataFileNotFound(self.path)
        
        for line in content:
            if line[0] in string.ascii_uppercase:
                splitted_line = line.split(":")

                # key = splitted_line[0]
                key = splitted_line[0].lower().replace("-", "_")
                value = ":".join(splitted_line[1:]).strip()

                if key in self.__dict__.keys():
                    try:
                        self[key].append(value)
                    except Exception:
                        self.__setattr__(key, [self[key], value])
                else:
                    self.__setattr__(key, value)
            else:
                break

    def __str__(self):
        return f"MetadataFile({self.__dict__})"


class WheelFile(Multiclass):
    def __init__(self, filename: str = "https://example.com/file/None.whl"):
        f = filename[:-4].split("/")[-1].split("-")
        self.filename   = filename
        self.basename   = filename.split("/")[-1]
        self.name       = f[0]
        self.version    = f[1]
        self.platform   = f[-1]
        self.suffix = filename.split(".")[-1]
        try:
            self.python   = [re.findall(r"\d+", f[2])[0], re.findall(r"\d+", f[3])[0]]
            # self.python   = [f[2], f[3]]
        except Exception:
            self.python = [None, None]
            
    def __str__(self):
        return f"WheelFile({self.__dict__})"


class TarGzFile(WheelFile):
    def __init__(self, filename: str = "https://example.com/numpy-1.24.1.tar.gz"):
        super().__init__(filename)
        self.version = self.version[:-3]
        self.subsuffix = self.basename.split(".")[-2]
        self.platform = None


class PyPi(Multiclass):
    def __init__(self, name: str):
        self.name = name
        self.pm = urllib3.PoolManager()
        self._pypi = self.pm.request("GET", Constants.URL.PYPI_JSON.format(self.name))
        self._resp = json.loads(self._pypi.data)

        if "message" in self._resp.keys() and self._resp["message"].lower() == "not found":
            raise Exceptions.PyPi.PackageDoesNotExistsOnPyPi(self.name)
        
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

    def version_before_specified(self, version):
        """Returns the version released before the specified"""
        index = self.package_versions().index(version)
        return self.package_versions()[index - 1]

    def is_version_exising(self, version: str):
        return version in self.package_versions()

    def package_versions(self):
        """Return list with all versions of package"""
        return list(self.releases.keys())

    def is_available_by_python_ver(self):
        """Return True if this package available to download for this Python version"""
        # print(f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",self.info["requires_python"])
        return USER_PYTHON_VERSION.compare_with(self.info["requires_python"])

    def _getDownloadUrls(self, version=None):
        RELEASES = self.urls
        result = []
        for platform in [self.whl_platform, Constants.PLATFORM.ANY]:
            if version and version in self.releases.keys():
                RELEASES = self.releases[version]

            # Uncomment this lines for download .tar.gz files
            if RELEASES[-1]["url"] not in result:
                result.append(TarGzFile(RELEASES[-1]["url"]))

            for release in RELEASES:
                whl = WheelFile(release["url"])
                if whl.suffix == "whl" and whl.platform == platform and USER_PYTHON_VERSION.compare_with(release["requires_python"]):
                    result.append(whl)
                    return set(result)
                    
    def _setup_as_targz(self, path_to_install: pathlib, fileobj: BytesIO, whl):
        tar = tarfile.open(fileobj=fileobj)
        for member in tar.getmembers():
            try:
                if self.name.lower() in f"{str(member.name).lower().split('/')[1]}":
                    tar.extract(member, path_to_install)
            except Exception:
                print("    Ignored file:", member.path)
        tar.close()

    def _setup_as_zip(self, path_to_install: pathlib, fileobj: BytesIO, whl):
        with zipfile.ZipFile(file=fileobj, mode="r") as archive:
            for file in archive.namelist():
                archive.extract(file, path_to_install)
                # if self.name.lower() in f"{file.lower()}":
                    # print("    Ignored file:", file.lower())
                # if self.name.lower() in f"{file.lower()}":
                #     archive.extract(file, path_to_install)
                # else:
                #     print("    Ignored file:", file.lower())
    
    def _move_from_targz_to_packagefolder(self, path_to_install: pathlib, version=None):
        """Function moving files from targz folder"""
        setup_v = self.info['version']
        if version:
            setup_v = version
        shutil.move(str(path_to_install / pathlib.Path(f"{self.name}-{setup_v}")), f"{path_to_install}")
        try:
            shutil.move(str(path_to_install / pathlib.Path(f"{self.name}-{setup_v}.egg-info")), f"{path_to_install}")
        except FileNotFoundError:
            pass

    def calculate_bytes_size(self, iobytes: BytesIO):
        size = sys.getsizeof(iobytes)
        if size / Constants.SIZE.BYTES <= Constants.SIZE.BYTES:
            return (round(size / Constants.SIZE.BYTES, 1), "BYTES")
        if size / Constants.SIZE.KB <= Constants.SIZE.KB:
            return (round(size / Constants.SIZE.KB, 1), "KB")
        if size / Constants.SIZE.MB <= Constants.SIZE.MB:
            return (round(size / Constants.SIZE.MB, 1), "MB")
        if size / Constants.SIZE.GB <= Constants.SIZE.GB:
            return (round(size / Constants.SIZE.GB, 1), "GB")

    def setup(self, path_to_install: pathlib, version=None):
        found_urls_list = self._getDownloadUrls(version)
        for whl in found_urls_list:
            print(f"Collecting {whl.name}\n  Downloading", whl.basename, end=" ")
            iobytes_file = BytesIO(self.pm.request("GET", whl.filename).data)

            print("(", *self.calculate_bytes_size(iobytes_file), ")", sep="")

            if whl.suffix == "gz":
                self._setup_as_targz(path_to_install, iobytes_file, whl)
            elif whl.suffix in ["whl", "zip"]:
                self._setup_as_zip(path_to_install, iobytes_file, whl)
            
        self._move_from_targz_to_packagefolder(path_to_install, version)

        print(f"Installed {self.name.lower()}-{whl.version}\n")

        self.package = Package(self.name).setupTheDependencies()

    def get(self):
        """Return data from pypi"""
        return self._resp


class Package(Multiclass):
    def __init__(self, name: str, default_path: pathlib = pathlib.Path("site-packages"), **kwargs):
        self.name = name.lower()
        self.name_replaced = self.name.replace("-", "_")
        self.default_path = default_path.absolute()

        if not self.is_installed():
            raise Exceptions.SitePackages.PackageNotFoundError(self.name)

        self.dist_info = None
        self.package_folder = None
        self.py_files = list()
        self.other_files = list()
        self.metadata_filepath = None

        for file in self.default_path.iterdir():            
            if self.name_replaced in file.name.lower():
                if file.is_dir():
                    if re.findall(f"{self.name_replaced}\-\d.*\.dist-info", file.name.lower()):
                        self["dist_info"] = file
                        self["metadata_filepath"] = file / "METADATA"
                        self.metadata_filepath = file / "METADATA"
                    if self.name_replaced == file.name:
                        self["package_folder"] = self.name_replaced
                elif file.is_file():
                    if file.suffix == ".py":
                        self["py_files"].append(file)
                    else:
                        self["other_files"].append(file)

        self.metadata = Metadata(self.__dict__["metadata_filepath"])

    @property
    def pypi(self):
        """
        Get `PipIOS.App.PyPi` object with parsed JSON-response from PyPi
        """
        return PyPi(self.name)

    def is_installed(self):
        """Return `True` if this package is installed on your device"""
        for file in self.default_path.iterdir():
            expression = re.findall(f"{self.name_replaced}\-\d.*\.dist-info", file.name.lower()) or self.name_replaced == file.name.lower()
            if expression:
                return True
        return False

    def remove(self):
        """Return True if package successfuly removed"""
        print("Uninstalling", self.name.lower()+"-"+self.metadata.Version)

        for file in self.default_path.iterdir():
            if self.name.lower() == file.name.lower() or f"{self.name.lower()}-{self.metadata.Version}.dist-info" == file.name.lower() or f"{self.name.lower()}." in file.name.lower():
                print("  Remove", file.name.lower())
                try:
                    shutil.rmtree(f"{file.absolute()}")
                except Exception:
                    os.remove(f"{file.absolute()}")
        
        return f"Successfully uninstalled {self.name}-{self.metadata.Version}"
    
    def setupTheDependencies(self):
        """
        Setup all dependencies from METADATA.
        
        !! Only after installing the self.name package !!
        """
        # RequiresParser.Version(USER_PYTHON_VERSION).compare_with(req["optional"]["python_version"])
        # print(local_pack.metadata["Requires-Dist"])

        if "Requires-Dist" not in self.metadata.__dict__.keys():
            raise Exceptions.SitePackages.RequirementsNotFound(self.metadata["Name"])

        requirements = RequiresParser.RequiresDist(self.metadata).requirements
        r_dict = requirements.__dict__
        installed_packages = []
        for r in (r_dict):
            print(f"Collecting: {r}{requirements[r]['version']}")
            try:
                local_pack = Package(r)
                print("Requirement already satisfied:", f"{local_pack.name}-{local_pack.metadata.Version}", "in",  f"{local_pack.default_path}".lower())
            except Exceptions.SitePackages.PackageNotFoundError:
                # print(r, requirements[r])
                installed_packages.append(r)
                local_pypi = PyPi(r)
                # if RequiresParser.Version(local_pypi.info["version"]).compare_with(requirements[r]["version"]) and local_pypi.is_available_by_python_ver():
                if local_pypi.is_available_by_python_ver():

                    version_for_setup = local_pypi.version

                    if requirements[r]['version'][:2] in ["==", "<=", "~="]:
                        version_for_setup = requirements[r]['version'][2:]
                    elif requirements[r]['version'][:1] == "<":
                        version_for_setup = local_pypi.version_before_specified(requirements[r]['version'][1:])
                    else:
                        if RequiresParser.Version(local_pypi.info["version"]).compare_with(requirements[r]["version"]):
                            version_for_setup = local_pypi.version
                    
                    print(f"  Searching {r}-{version_for_setup}")
                    local_pypi.setup(self.default_path, version=version_for_setup)

                else:
                    print(f"  PipIOS.Error: YOUR PYTHON VERSION ({USER_PYTHON_VERSION.parsed['str_version'][0]}) IS NOT SUITABLE TO SETUP THIS REQUIREMENT (Requires Python {local_pypi.info['requires_python']})" + "\n")

        print("Successfully installed requirements:", f"{', '.join(installed_packages)}")
        return True

    def __str__(self):
        return f"PipIOS.Package({self.__dict__})"


if __name__ == "__main__":

    INSTALL_PATH = pathlib.Path("site-packages").absolute()
    PACKAGE = "uploadgram"
    # PACKAGE = "pytz"
    # PACKAGE = "uploadgrampyapi"
    
    # print(TarGzFile("numpy-1.24.1.tar.gz"))

    # 'https://files.pythonhosted.org/packages/44/d3/e9df2f568692647fe5c3b02506610829d004a00b3ba5c7fd92d382f8d511/pandas-1.5.2-cp39-cp39-win32.whl'

    pypi = PyPi(PACKAGE)
    print(pypi.setup(INSTALL_PATH))
    # print(pypi.package_versions())

    # import time
    # time.sleep(2)

    # test_pack = Package(PACKAGE)
    # test_pack.setupTheDependencies()
    # print(test_pack.is_installed())
    # print(pack.metadata)
    # print(pack.default_path)
    # pack.remove()
    # print(pack.metadata["Requires-Python"])
    # print(RequiresParser.RequiresDist(pack.metadata).get())
    # print(pack.remove())
    # print(pack.metadata)
    # print(RequiresDist(pack.metadata).get())
    # pack.setupTheDependencies()
