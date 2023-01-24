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

try:
    import Package
except ModuleNotFoundError:
    from . import Package


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
        _requires_python: RequiresParser.Version = RequiresParser.Version(Constants.USER.PYTHON),
        _detailed_log: bool = False
        ):
        """
        Get access to information on `pypi.org` about package
        """
        self.name = name.strip()
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
            raise Exceptions.PyPi.PackageOrVersionDoesNotExistsOnPyPi(self.name, self._version)

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
                    RequiresParser.is_correct_python(release):
                # self._requires_python.compare(sing, release["requires_python"].replace(sing, "")):
                # self._requires_python.compare_with(release["requires_python"]):
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

    def _identifyRealDir(self, readed_iobytes):
        """
        Return string dirname to unpack tar.gz archives
        """
        for i in range(len(readed_iobytes)):
            if self._release_objects[i].packagetype == Constants.PACKAGETYPE.WHEEL:
                with zipfile.ZipFile(readed_iobytes[i], 'r') as archive:
                    for file in archive.namelist():
                        if ".dist-info" not in str(file):
                            # print(str(file))
                            try:
                                return str(file).split("/")[-2]
                            except IndexError:
                                return str(file)
        return f"{self.name}-{self._version}"

    def _move_files_from_unpacked_targz(self, dir_to_unpack):
        """Move all folders from the unpacked `.tar.gz` folder with replacement"""
        # if dir_to_unpack == "__default":
        #     unpacked_targz = pathlib.Path(self._site_packages / f"{self.name}-{self._version}")
        # else:
        unpacked_targz = pathlib.Path(self._site_packages / dir_to_unpack)
        
        try:
            try:
                unpacked_targz.unlink()
            except Exception:
                unpacked_targz.rmdir()
        except Exception:
            pass
            

        if not unpacked_targz.exists():
            unpacked_targz.mkdir()

        for directory in unpacked_targz.iterdir():
            shutil.move(str(directory.absolute()), str(self._site_packages))

        unpacked_targz.rmdir()
    
    def _setup_requirements(self):
        if "requires_dist" in self.info.keys() and self.info["requires_dist"]:
            installed_packages_list = []

            r = RequiresParser.Requirements(metadata_requires_dist=self.info["requires_dist"])
            for name in r:
                name_replaced = name.replace("-", "_")
                # print(name_replaced)

                try:
                    installed_pack = Package.InstalledPackage(name_replaced)
                    print("Requirement already satisfied:", f"{name}-{installed_pack.version}", "in", self._site_packages)
                except Exceptions.SitePackages.PackageNotFoundError:

                    for section in r[name]:
                        local_section = section

                        if "python_version" in section["options"].keys() and \
                            RequiresParser.Version(Constants.USER.PYTHON).compare(section["options"]["python_version"]["sign"], section["options"]["python_version"]["value"]):
                            local_section = section
                            break

                    ver = RequiresParser.Version(local_section["version"])
                    sign = local_section["sign"]
                    
                    version_for_installing = ver

                    local_pack = PyPi(name_replaced, version_for_installing.version, self._site_packages)
                    local_pack.setup()

                    installed_packages_list.append({"name": local_pack.name, "version": version_for_installing, "sign": sign})
            
            return installed_packages_list
        return []
    
    def setup(self):
        """Setup package to site-packages on your device"""
        print(f"Collecting {self.name}" + f"=={self._version}")
        readed_iobytes = self._read_iobytes_archive()
        for i in range(len(readed_iobytes)):
            if self._release_objects[i].packagetype == Constants.PACKAGETYPE.SDIST:
                print("  Downloading", self._release_objects[i].whl_tar.basename, end=" ")
                print("(", *App.calculate_bytes_size(readed_iobytes[i]), ")", sep="")
                self._unpack_as_targz(readed_iobytes[i])
                self._move_files_from_unpacked_targz(self._identifyRealDir(readed_iobytes))
                # print("  Success!")
        
        for i in range(len(readed_iobytes)):
            if self._release_objects[i].packagetype == Constants.PACKAGETYPE.WHEEL:
                print("  Downloading", self._release_objects[i].whl_tar.basename, end=" ")
                print("(", *App.calculate_bytes_size(readed_iobytes[i]), ")", sep="")
                self._unpack_as_zip(readed_iobytes[i])
                # print("  Success!")
        
        installed_requirements = self._setup_requirements()

        if not installed_requirements:
            # print("Installing collected packages:", end=" ")
            for p in installed_requirements:
                print(p["name"], sep=" ", end="")
            # print("\n", "Successfully installed!")
            for p in installed_requirements:
                print(f"{p['name']}-{p['version'].version}", sep=" ", end="")
        else:
            print("Successfully installed", f"{self.name}-{self._version}")
        return True


if __name__ == "__main__":
    # pack = PyPi(name = "pandas", version="1.5.2", _site_packages = pathlib.Path("site-packages").absolute())
    # pack = PyPi(name = "python-dateutil", _site_packages = pathlib.Path("site-packages").absolute())
    pack = PyPi(name = "hypothesis", _site_packages = pathlib.Path("site-packages").absolute())
    print(pack.setup(), file="log.log")
    # print(pack.all_versions())
    # print(pack.info)

    # print(pack._setup_requirements())

    # print(pack._release_objects)
    # for e in pack._release_objects:
    #     print(e.filename)
    # print(pack._site_packages)
    # print(pack._release_objects)
    # print(pack._read_iobytes_archive())
    # print(pack._move_files_from_unpacked_targz())
        # print(e)
