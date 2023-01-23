"""
Exceptions for PipIOS application

PipIOS

(c) tankalxat34
"""

class PyPi:
    class PackageOrVersionDoesNotExistsOnPyPi(Exception):
        def __init__(self, name):
            super().__init__(f"Package '{name}' does not exists on pypi.org!")

class SitePackages:
    class PackageNotFoundError(Exception):
        def __init__(self, name):
            super().__init__(f"Package '{name}' is not installed!")
    
    class MetadataFileNotFound(Exception):
        def __init__(self, name):
            super().__init__(f"METADATA file is not found in '{name}'")

    class RequirementsNotFound(Exception):
        def __init__(self, name):
            super().__init__(f"Requirements not found for package '{name}'")
    
class User:
    class InvalidPythonVersion(Exception):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)