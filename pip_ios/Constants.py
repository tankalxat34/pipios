"""
Constants for PipIOS
"""

import pathlib
import sys

UNDEFINED = -100

class StringUI(object):
    UNDERTAB = "\n\t"
    ASCII_LOWERCASE = "abcdefghijklmnopqrstuvwxyz"

class URL(object):
    PYPI_JSON = "https://pypi.org/pypi/{name}/json"
    PYPI_VERSION_JSON = "https://pypi.org/pypi/{name}/{version}/json"

class USER(object):
    PYTHON = f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"
    PATH = pathlib.Path(sys.path[4])
    for p in sys.path:
        if "site-packages" in p.lower():
            PATH = pathlib.Path(p).absolute()
            break

class PACKAGETYPE(object):
    WHEEL = "bdist_wheel"
    SDIST = "sdist"
    
class PLATFORM(object):
    ANY                 = "any"
    WIN32               = "win32"
    WIN_AMD64           = "win_amd64"
    MACOSX              = "darwin"
    MACOSX_11_0_ARM64   = "macosx_11_0_arm64"
    MACOSX_10_9         = "macosx_10_9_x86_64"
    IOS                 = "ios"
    MANYLINUX_X86_64    = "manylinux_2_17_x86_64.manylinux2014_x86_64"
    MANYLINUX_ARCH64    = "manylinux_2_17_aarch64.manylinux2014_aarch64"

    # Local names of OS that do not using in *.whl filenames
    CYGWIN  = "cygwin"
    MSYS    = "msys"
    LINUX   = "linux"
    LINUX2  = "linux2"

class SIZE(object):
    BYTES  = 1
    KB = 1024
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024
    