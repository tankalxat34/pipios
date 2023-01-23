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


class Requirements(Multiclass):
    def __init__(self, metadata_requires_dist: list):
        """Parsing `metadata.requires_dist` list"""

        # self.case_conditions = {
        #     ">":    lambda a, b: a > b,
        #     ">=":   lambda a, b: a >= b,
        #     "<":    lambda a, b: a < b,
        #     "<=":   lambda a, b: a <= b,
        #     "==":   lambda a, b: a == b,
        #     "===":  lambda a, b: a == b,
        #     "!=":   lambda a, b: a != b,
        # }
        self.case_conditions = {
            ">":    lambda a, b: a > b,
            ">=":   lambda a, b: a >= b,
            "<":    lambda a, b: a < b,
            "<=":   lambda a, b: a <= b,
            "==":   lambda a, b: a == b,
            "===":  lambda a, b: a == b,
            "!=":   lambda a, b: a != b,
        }

        for req in metadata_requires_dist:
            if ";" in req:
                part1, part2 = req.split(";")
            else:
                part1, part2 = req, ""

            name, version = part1.split()[0], part1.split()[1][1:-1]
            sign = "".join(re.findall(r"([>|<|=|~|!])", version))
            version = version.replace(sign, "")
            try:
                self[name].append({"sign": sign, "version": version, "options": dict()})
            except Exception:
                self[name] = list()
                self[name].append({"sign": sign, "version": version, "options": dict()})

            if part2:
                part2 = part2.strip().replace("'", '"').split(",")
                for p in part2:
                    sign2 = "".join(re.findall(r"([>|<|=|~|!])", p))
                    name2, value2 = p.split(sign2)
                    self[name][-1]["options"][name2.strip()] = {"value": value2.strip().replace('"', ""), "sign": sign2}
    
    def select_versions_from(self, all_releases: list, version_requirement: str = ">=1.0.0"):
        """
        Selects a suitable version from the passed version list 
        according to the specified condition in the 
        "requirements" syntax

        Return `list`
        """
        result = []
        for v in all_releases:
            if self.is_true_version(v, version_requirement):
                result.append(v)
        return result
    
    def is_true_version(self, 
            version: str, 
            version_requirement: str):
        """
        Return `True` if this version is true for version requirement
        
        Arg `version` without `*`-symbol
        """
        sign = "".join(re.findall(r"([>|<|=|~|!])", version_requirement))
        
        v1 = version
        v2 = version_requirement.replace(sign, "")

        if v2[-1] == "0":
            v1 += ".0" * (version_requirement.count(".") - version.count("."))
        
        if v1[-1] == "0":
            v2 += ".0" * (version.count(".") - version_requirement.count("."))

        if sign in ["==", "===", "!="]:
            try:
                return self.case_conditions[sign](v1, re.findall(v2, v1)[0])
            except IndexError:
                return False

        elif sign == "~=":
            v2_splitted = v2.split(".")
            cond1 = f">={v2}"

            cut_right_index = -1
            if v2_splitted[-1][0] in Constants.StringUI.ASCII_LOWERCASE:
                cut_right_index = -2

            cond2 = f"=={'.'.join(v2_splitted[0:cut_right_index])}.*"
            return self.is_true_version(version, cond1) and self.is_true_version(version, cond2)
            
        else:
            
            def less_zero(*args):
                for arg in args:
                    print(arg)
                    if arg <= 0:
                        pass
                    else:
                        return False
                return True
            
            def more_zero(*args):
                print(args)
                for arg in args:
                    if arg >= 0:
                        return False
                return True


            result = []

            m1 = v1.split(".")
            m2 = v2.split(".")

            for i in range(len(m1)):
                """
                1.24.0 < 1.23.2 < [False, False, True] → False
                1.23.1 < 1.23.2 < [False, False, True] → True
                """
                if not re.findall(r"[a-z]{1,}", v1):
                    result.append(int(m2[i]) - int(m1[i]))
                else:
                    result.append(Constants.UNDEFINED)

            if sign == "<":
                answer = less_zero(*result) and Constants.UNDEFINED not in result

            elif sign == ">":
                answer = more_zero(*result) and Constants.UNDEFINED not in result
            else:
                answer = self.is_true_version(v1, f"=={v2}") or self.is_true_version(v1, f"{sign[0]}{v2}")
            print(v1, v2, result, answer, sep=f" {sign} ")
            return answer
        
    def is_true_version_for_requirements(self, 
            version: str = "3.10.5", 
            version_requirements: str = ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"):
        """
        Return `True` if specified version is truth for requirements list
        """
        result = []
        
        for v2 in version_requirements.split(","):
            result.append(self.is_true_version(version, v2))
        return result

        



if __name__ == "__main__":
    ALL_RELEASES = ['0.1', '0.10.0', '0.10.1', '0.11.0', '0.12.0', '0.13.0', '0.13.1', '0.14.0', '0.14.1', '0.15.0', '0.15.1', '0.15.2', '0.16.0', '0.16.1', '0.16.2', '0.17.0', '0.17.1', '0.18.0', '0.18.1', '0.19.0', '0.19.1', '0.19.2', '0.2', '0.20.0', '0.20.1', '0.20.2', '0.20.3', '0.21.0', '0.21.1', '0.22.0', '0.23.0', '0.23.1', '0.23.2', '0.23.3', '0.23.4', '0.24.0', '0.24.1', '0.24.2', '0.25.0', '0.25.1', '0.25.2', '0.25.3', '0.3.0', '0.4.0', '0.4.1', '0.4.2', '0.4.3', '0.5.0', '0.6.0', '0.6.1', '0.7.0', '0.7.1', '0.7.2', '0.7.3', '0.8.0', '0.8.1', '0.9.0', '0.9.1', '1.0.0', '1.0.1', '1.0.2', '1.0.3', '1.0.4', '1.0.5', '1.1.0', '1.1.1', '1.1.2', 
    '1.1.3', '1.1.4', '1.1.5', '1.2.0', '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.2.5', '1.3.0', '1.3.1', '1.3.2', '1.3.3', '1.3.4', '1.3.5', '1.4.0', '1.4.0rc0', '1.4.1', '1.4.2', '1.4.3', '1.4.4', '1.5.0', '1.5.0rc0', '1.5.1', '1.5.2', '1.5.3'] 

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
            'python-dateutil (>=2.8.1)', 
            'pytz (>=2020.1)', 
            'numpy (>=1.20.3) ; python_version < "3.10"', 
            'numpy (>=1.21.0) ; python_version >= "3.10"',
            'numpy (>=1.23.2) ; python_version >= "3.11"', 
            "hypothesis (>=5.5.3) ; extra == 'test'", 
            "pytest (>=6.0) ; extra == 'test'", 
            "pytest-xdist (>=1.31) ; extra == 'test'"
        ])

    """
    1.24.0 < 1.23.2 < [False, False, True] → False
    1.23.1 < 1.23.2 < [False, False, True] → True
    """

    # print(r.select_versions_from(NUMPY_ALL_RELEASES, ">1.23.2"))
    # print(r.select_versions_from(ALL_RELEASES, ">1.3.5"))
    # print(r.select_versions_from(ALL_RELEASES, "<0.13.1"))
    # print(r.select_versions_from(NUMPY_ALL_RELEASES, "~=1.23.0"))
    print(r.is_true_version("1.24.0", "<1.23.2"))
    print(r.is_true_version("1.23.1", "<1.23.2"))
    print(r.is_true_version("1.22.3", "<1.23.2"))

    # print(r.is_true_version("2.3", "~=2.2")) # True
    # print(r.is_true_version("2.10", "~=2.2")) # True
    # print(r.is_true_version("2.0", "~=2.2")) # True
    # print(r.is_true_version("3.1", "~=2.2")) # False
    
    # print(r.is_true_version("2.5", "~=2.2"))
    # print(r.is_true_version("1.4.5", "~=1.4.5"))

    # print(r.is_true_version("3.1", "~=2.2.post3"))
    # print(r.is_true_version("3.1", "~=1.4.5a4"))

    # print(r.is_true_version("3.1", "~=2.2.0"))
    # print(r.is_true_version("3.1", "~=1.4.5.0"))

    # print(r.is_true_version_for_requirements("3.10.5", version_requirements=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*"))
