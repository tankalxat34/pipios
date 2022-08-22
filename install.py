import urllib.request
with open("pipios.py", "w", encoding="UTF-8") as file:
    file.write(urllib.request.urlopen("https://raw.githubusercontent.com/tankalxat34/pipios/main/launch.py").read().decode("utf-8"))