"""
Module for work with `requires_python`, `Requires-Dist` syntax

PipIOS

(c) tankalxat34 - 2023
"""

import re
try:
    import Constants
except ModuleNotFoundError:
    from . import Constants


def mapStrip(s: str):
    return s.strip()


def findSign(s: str):
    """
    Return `str` with sign in requirement

    `>`, `<`, `>=`, `<=`, `==`, `!=`, `~=`
    """
    return "".join(re.findall(r"([>|<|=|~|!])", s))


def filterVersions(requirement: str, ver_list: list):
    """
    Return `list` with suitable versions by requirement
    """
    result = []

    sign = findSign(requirement)
    ver = requirement.replace(sign, "")

    version1 = Version(ver)
    for v in ver_list:
        if Version(v).compare(sign, ver):
            result.append(v)
    return result


def is_correct_python(release):
    result = []

    requirements = release["requires_python"]

    # print(release)
    # print(requirements)

    if not requirements:
        return True

    my_v = Version(Constants.USER.PYTHON)
    for v in requirements.split(","):
        sign = findSign(v)
        v_for_compare = v.replace(sign, "")
        # print("   ", sign, v_for_compare)
        result.append(my_v.compare(sign, v_for_compare))
    
    return result[0] if len(set(result)) == 1 else False



class Multiclass:
    """Class with ability to set and get attributes. Could be use as parent class"""

    def __init__(self) -> None:
        pass

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __str__(self):
        return f"{self.__dict__}"



class Version:
    def __init__(self, version: str = "0.1.0"):
        self.version = version

        try:
            self.releaselevel = re.findall(r"[a-z]+\d+", version)[0]
        except IndexError:
            self.releaselevel = ""

        self.raw = version.replace(self.releaselevel, "")

    @property
    def major(self):
        return int(self.raw.split(".")[0])
    
    @property
    def minor(self):
        try:
            return int(self.raw.split(".")[1])
        except ValueError:
            return (self.raw.split(".")[1])
        except IndexError:
            return 0

    @property
    def micro(self):
        try:
            return int(self.raw.split(".")[2])
        except ValueError:
            return (self.raw.split(".")[2])
        except IndexError:
            return 0
    
    def compare(self, sign: str, version: str):
        cases = {
            ">":  lambda version: self > Version(version),
            ">=": lambda version: self >= Version(version),
            "<":  lambda version: self < Version(version),
            "<=": lambda version: self <= Version(version),
            "!=": lambda version: self != Version(version),
            "==": lambda version: self == Version(version)
        }
        return cases[sign](version)
    
    def __ne__(self, __x): 
        """!="""
        return not self.__eq__(__x)

    def __eq__(self, __x): 
        """=="""
        lst = [self.major - __x.major] + [0] * 2
        try:
            lst[1] = self.minor - __x.minor
        except TypeError:
            pass
            
        try:
            lst[2] = self.micro - __x.micro
        except TypeError:
            pass
        return True if len(set(lst)) == 1 and lst[0] == 0 and (self.releaselevel == __x.releaselevel) else False

    def __lt__(self, __x): 
        """<"""
        lst = [self.major - __x.major] + [0] * 2
        try:
            lst[1] = self.minor - __x.minor
        except TypeError:
            pass
            
        try:
            lst[2] = self.micro - __x.micro
        except TypeError:
            pass
        return True if lst[1] < 0 or (lst[1] == 0 and lst[2] < 0) else False

    def __le__(self, __x): 
        """<="""
        return self.__lt__(__x) or self.__eq__(__x)

    def __gt__(self, __x): 
        """>"""
        lst = [self.major - __x.major] + [0] * 2
        try:
            lst[1] = self.minor - __x.minor
        except TypeError:
            pass
            
        try:
            lst[2] = self.micro - __x.micro
        except TypeError:
            pass
        return True if lst[1] > 0 or (lst[1] == 0 and lst[2] > 0) else False

    def __ge__(self, __x): 
        """>="""
        return self.__gt__(__x) or self.__eq__(__x)
    
    def __str__(self) -> str:
        return f"Version(version='{self.version}', releaselevel='{self.releaselevel}', raw='{self.raw}', major={self.major}, minor={self.minor}, micro={self.micro})"




class Requirements(Multiclass):
    def __init__(self, metadata_requires_dist: list):
        """Parsing `metadata.requires_dist` list"""

        for req in metadata_requires_dist:
            if ";" in req:
                part1, part2 = req.split(";")
            else:
                part1, part2 = req, ""

            print("    ", "parsing:", req)
            try:
                name, version = part1.split()[0], part1.split()[1][1:-1]
            except Exception:
                name, version = part1, ""
            if version.count(",") == 0:
                sign = findSign(version)
            else:
                # print(version.split(",")[1])
                sign = findSign(version.split(",")[1])
                version = version.split(",")[1]

            version = version.replace(sign, "")
            name = name.strip()
            print("       ", "version:", version)


            try:
                self[name].append({"sign": sign, "version": version, "options": dict()})
            except Exception:
                self[name] = list()
                self[name].append({"sign": sign, "version": version, "options": dict()})

            if part2:
                part2 = part2.strip().replace("'", '"').split(",")
                for p in part2:
                    try:
                        sign2 = "".join(re.findall(r"([>|<|=|~|!])", p))
                        name2, value2 = p.split(sign2)
                        self[name][-1]["options"][name2.strip()] = {"value": value2.strip().replace('"', ""), "sign": sign2}
                    except Exception:
                        pass

    def __iter__(self):
        return iter(self.__dict__.keys())




if __name__ == "__main__":
    ALL_RELEASES = [
        '0.1', '0.10.0', '0.10.1', '0.11.0', 
        '0.12.0', '0.13.0', '0.13.1', '0.14.0', 
        '0.14.1', '0.15.0', '0.15.1', '0.15.2', 
        '0.16.0', '0.16.1', '0.16.2', '0.17.0', 
        '0.17.1', '0.18.0', '0.18.1', '0.19.0', 
        '0.19.1', '0.19.2', '0.2', '0.20.0', 
        '0.20.1', '0.20.2', '0.20.3', '0.21.0', 
        '0.21.1', '0.22.0', '0.23.0', '0.23.1', 
        '0.23.2', '0.23.3', '0.23.4', '0.24.0', 
        '0.24.1', '0.24.2', '0.25.0', '0.25.1', 
        '0.25.2', '0.25.3', '0.3.0', '0.4.0', 
        '0.4.1', '0.4.2', '0.4.3', '0.5.0', 
        '0.6.0', '0.6.1', '0.7.0', '0.7.1', 
        '0.7.2', '0.7.3', '0.8.0', '0.8.1', 
        '0.9.0', '0.9.1', '1.0.0', '1.0.1', 
        '1.0.2', '1.0.3', '1.0.4', '1.0.5', 
        '1.1.0', '1.1.1', '1.1.2', '1.1.3', 
        '1.1.4', '1.1.5', '1.2.0', '1.2.1', 
        '1.2.2', '1.2.3', '1.2.4', '1.2.5', 
        '1.3.0', '1.3.1', '1.3.2', '1.3.3', 
        '1.3.4', '1.3.5', '1.4.0', '1.4.0rc0', 
        '1.4.1', '1.4.2', '1.4.3', '1.4.4', 
        '1.5.0', '1.5.0rc0', '1.5.1', '1.5.2', 
        '1.5.3'
    ]

    NUMPY_ALL_RELEASES = [
        '0.9.6', '0.9.8', '1.0', '1.0.3', '1.0.4', 
        '1.0b1', '1.0b4', '1.0b5', '1.0rc1', '1.0rc2', 
        '1.0rc3', '1.1.1', '1.10.0', '1.10.1', '1.10.2', 
        '1.10.3', 
        '1.10.4', '1.11.0', '1.11.1', '1.11.2', '1.11.3', 
        '1.12.0', '1.12.1', '1.13.0', '1.13.1', '1.13.3', 
        '1.14.0', '1.14.1', '1.14.2', '1.14.3', '1.14.4', 
        '1.14.5', '1.14.6', '1.15.0', '1.15.1', '1.15.2', 
        '1.15.3', '1.15.4', '1.16.0', '1.16.1', '1.16.2', 
        '1.16.3', '1.16.4', '1.16.5', '1.16.6', '1.17.0', 
        '1.17.1', '1.17.2', '1.17.3', '1.17.4', '1.17.5', 
        '1.18.0', '1.18.1', '1.18.2', '1.18.3', '1.18.4', 
        '1.18.5', '1.19.0', '1.19.1', '1.19.2', '1.19.3', 
        '1.19.4', '1.19.5', '1.2.0', '1.2.1', '1.20.0', 
        '1.20.1', '1.20.2', '1.20.3', '1.21.0', '1.21.1', 
        '1.21.2', '1.21.3', '1.21.4', '1.21.5', '1.21.6', 
        '1.22.0', '1.22.1', '1.22.2', '1.22.3', '1.22.4', 
        '1.23.0', '1.23.0rc1', '1.23.0rc2', '1.23.0rc3', 
        '1.23.1', '1.23.2', '1.23.3', '1.23.4', '1.23.5', 
        '1.24.0', '1.24.0rc1', '1.24.0rc2', '1.24.1', 
        '1.3.0', '1.4.0', '1.4.1', '1.5.0', '1.5.1', 
        '1.6.0', '1.6.1', '1.6.2', '1.7.0', '1.7.1', 
        '1.7.2', '1.8.0', '1.8.1', '1.8.2', '1.9.0', 
        '1.9.1', '1.9.2', '1.9.3'
        ]

    r = Requirements([
            "attrs (>=19.2.0)",
            "sortedcontainers (<3.0.0,>=2.1.0)",
            "exceptiongroup (>=1.0.0) ; python_version < \"3.11\"",
            "black (>=19.10b0) ; extra == 'all'",
            "click (>=7.0) ; extra == 'all'",
            "django (>=3.2) ; extra == 'all'",
            "dpcontracts (>=0.4) ; extra == 'all'",
            "lark (>=0.10.1) ; extra == 'all'",
            "libcst (>=0.3.16) ; extra == 'all'",
            "numpy (>=1.9.0) ; extra == 'all'",
            "pandas (>=1.0) ; extra == 'all'",
            "pytest (>=4.6) ; extra == 'all'",
            "python-dateutil (>=1.4) ; extra == 'all'",
            "pytz (>=2014.1) ; extra == 'all'",
            "redis (>=3.0.0) ; extra == 'all'",
            "rich (>=9.0.0) ; extra == 'all'",
            "importlib-metadata (>=3.6) ; (python_version < \"3.8\") and extra == 'all'",
            "backports.zoneinfo (>=0.2.1) ; (python_version < \"3.9\") and extra == 'all'",
            "tzdata (>=2022.7) ; (sys_platform == \"win32\") and extra == 'all'",
            "click (>=7.0) ; extra == 'cli'",
            "black (>=19.10b0) ; extra == 'cli'",
            "rich (>=9.0.0) ; extra == 'cli'",
            "libcst (>=0.3.16) ; extra == 'codemods'",
            "python-dateutil (>=1.4) ; extra == 'dateutil'",
            "django (>=3.2) ; extra == 'django'",
            "dpcontracts (>=0.4) ; extra == 'dpcontracts'",
            "black (>=19.10b0) ; extra == 'ghostwriter'",
            "lark (>=0.10.1) ; extra == 'lark'",
            "numpy (>=1.9.0) ; extra == 'numpy'",
            "pandas (>=1.0) ; extra == 'pandas'",
            "pytest (>=4.6) ; extra == 'pytest'",
            "pytz (>=2014.1) ; extra == 'pytz'",
            "redis (>=3.0.0) ; extra == 'redis'",
            "backports.zoneinfo (>=0.2.1) ; (python_version < \"3.9\") and extra == 'zoneinfo'",
            "tzdata (>=2022.7) ; (sys_platform == \"win32\") and extra == 'zoneinfo'"
        ])

    print(r["sortedcontainers"])

    # for name in r:
    #     name_replaced = name.replace("-", "_")
    #     print(name_replaced)
    #     for section in r[name]:
    #         local_section = section

    #         if "python_version" in section["options"].keys() and \
    #             Version(Constants.USER.PYTHON).compare(section["options"]["python_version"]["sign"], section["options"]["python_version"]["value"]):
    #             local_section = section
    #             break

    #     ver = Version(local_section["version"])
    #     sign = local_section["sign"]

    #     print("   ",ver, sign)
        

    # v1 = Version("3.0.*")
    # print(v1)

    # my_v = Version("3.0.5")
    # print(my_v == v1)

    # print(is_correct_python({"requires_python": "!=3.0.*,!=3.1.*,!=3.2.*,>=2.7"}))

    # print(filterVersions(">=1.10.3", NUMPY_ALL_RELEASES))

    # result = []

    # version1 = Version("1.10.3")
    # for v in NUMPY_ALL_RELEASES:
    #     if Version(v) >= version1:
    #         result.append(v)
    # print(*result, sep="\n")
    # print(len(result))
