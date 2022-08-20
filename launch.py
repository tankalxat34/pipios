"""
Launch the pipios console
"""

import pathlib
import os
import zipfile
import urllib
import urllib.request
import json


PYPI_JSON = "https://pypi.org/pypi/%s/json"


def _getPyPiPackageInfo(package="pygitconnect"):
    """Getting info in JSON format"""
    response = urllib.request.urlopen(PYPI_JSON % package)
    for e in response:
        return json.loads(e)


print(_getPyPiPackageInfo("uploadgrampyapi")["info"]["author"])

