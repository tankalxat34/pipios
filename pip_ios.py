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
    path        Show path to packages directory
    size        Get size of the package in KB
    exit        Exit from tool

Paramethers for work with commands
    ~version    Install the package of the specified version

Flags for work with commands
    -i          Ignore any conflicts with Python versions
    -f          Get full information about package

(c) tankalxat34 - 2023
https://github.com/tankalxat34/pipios
"""

import pathlib
import sys

import pip_ios.App


# Init constants
PATH = pathlib.Path()
CWD = PATH.cwd()
INDEX_SYSPATH = 5


if sys.platform == "ios":
    INDEX_SYSPATH = 1
elif sys.platform == "win32" or sys.platform == "cygwin":
    if "-t" in sys.argv:
        sys.path.append(CWD / "site-packages")
        INDEX_SYSPATH = -1

SITE_PACKAGES = pathlib.Path(sys.path[INDEX_SYSPATH])

if __name__ == "__main__":
    pack = pip_ios.App.Package("pandas", SITE_PACKAGES)
    print(pack.metadata.path)