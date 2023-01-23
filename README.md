# PipIOS
**PipIOS** - is a simple tool for managing Python packages in IOS application [Pythonista](http://omz-software.com/pythonista/).

<img src="https://github.com/tankalxat34/pipios/raw/content/IMG_5265.PNG" alt="image1" width=250px>

# Install

Create new file and paste there this code:

```py
import urllib.request; open("pipios.py", "w", encoding="UTF-8").write(urllib.request.urlopen("https://bit.ly/3R4y9gk").read().decode("utf-8"))
```

# Commands
Commands for work with tool
- `install`     Install or update the requested package from PyPi on your IOS device (shortly as `i`);
- `update`      Update the requested package from PyPi on your IOS device to the last version (shortly as `u`);
- `info`        Show you information about the requested package (shortly as `p`);
- `version`     Print version of the requested package (shortly as `v`);
- `delete`      Delete the requested package (shortly as `d`);
- `list`        Show you all packages that installed on your device (shortly as `l`);
- `count`       Show count of installed packages;
- `releases`    Show list of versions for the requested package;
- `help`        Show this message;
- `exit`        Exit from tool;

Paramethers for work with commands
- `~version`    Install the package of the specified version;

Flags for work with commands
- `-i`          Ignore any conflicts with Python versions;
