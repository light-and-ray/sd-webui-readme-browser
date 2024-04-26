import os
from dataclasses import dataclass
from modules import extensions, util, paths_internal
from readme_browser.options import needHideDisabledExtensions


@dataclass
class ReadmeFileData:
    filePath: str
    extPath: str


readmeFilesByExtName: dict[str, ReadmeFileData] = {}

def initReadmeFiles():
    global readmeFilesByExtName
    readmeFilesByExtName = {}

    webuiPath = paths_internal.data_path
    webuiName = os.path.basename(webuiPath)
    files = util.listfiles(webuiPath)
    for file in files:
        if os.path.basename(file).lower() == 'readme.md':
            readmeFilesByExtName[webuiName] = ReadmeFileData(file, webuiPath)
            break

    for ext in extensions.extensions:
        if needHideDisabledExtensions() and not ext.enabled: continue
        files = util.listfiles(ext.path)
        for file in files:
            if os.path.basename(file).lower() == 'readme.md':
                readmeFilesByExtName[ext.name] = ReadmeFileData(file, ext.path)
                break

