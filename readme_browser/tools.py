import re, datetime, os
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from modules.gitpython_hack import Repo
from modules import errors, paths_internal
from readme_browser.options import EXT_ROOT_DIRECTORY, getCacheLocation

JS_PREFIX = 'readme_browser_javascript_'


@dataclass
class Anchor:
    name: str
    id: str
    depth: int


def makeFileIndex(file: str) -> str:
    anchors: list[Anchor] = []
    anchorsIDs: dict[str, int] = {}
    hs: list[str] = re.findall(r'^#{1,6} +.+', file, re.MULTILINE)
    validChars = set('abcdefghijklmnopqrstuvwxyz0123456789-_')

    for h in hs:
        depth = len(h.split(' ')[0])
        anchorName = h.lstrip('#').strip().removesuffix(':')
        anchor = anchorName.lower().replace(' ', '-')
        tmp = anchor
        for char in set(anchor):
            if char not in validChars:
                tmp = tmp.replace(char, '')
        anchor = tmp
        if anchor in anchorsIDs:
            num = anchorsIDs[anchor]
            anchorsIDs[anchor] += 1
            anchor += f'-{num}'
        else:
            anchorsIDs[anchor] = 1

        anchors.append(Anchor(anchorName, anchor, depth))

    if len(anchors) <= 4:
        return ""

    minDepth = min(x.depth for x in anchors)
    for i in range(len(anchors)):
        anchors[i].depth = anchors[i].depth - minDepth

    result = '\n\n-----------------------\n\n<details>\n<summary>File index</summary>\n\n'
    for anchor in anchors:
        filler = ''
        if anchor.depth > 0:
            filler = '&nbsp;&nbsp;&nbsp;&nbsp;' * anchor.depth
        result += f'{filler}[{anchor.name}](#{anchor.id})\\\n'
    result = result[:-2]
    result += '\n\n</details>\n\n'

    return result


def addJumpAnchors(file: str) -> str:
    if file.count('\n') <= 30:
        topInvisible = '<a id="readme_browser_top_anchor"></a>'
        return f'{topInvisible}\n\n{file}\n'
    
    top = '<a id="readme_browser_top_anchor" href="#readme_browser_bottom_anchor">Go to the bottom ↓</a>'
    bottom = '<a id="readme_browser_bottom_anchor" href="#">Go to the top ↑</a>'

    return f'{top}\n\n{file}\n\n{bottom}\n'


def getURLsFromFile(file: str) -> list[str]:
    urls = set()

    MDLinks = re.findall(r'\[.*?\]\((.+?)\)', file)
    for link in MDLinks:
        urls.add(link)

    srcLinks = re.findall(r'src="(.+?)"', file)
    for link in srcLinks:
        urls.add(link)

    hrefLinks = re.findall(r'href="(.+?)"', file)
    for link in hrefLinks:
        urls.add(link)
    
    httpsLinks = re.findall(r'(^|\s)(https://.+?)($|\s)', file, re.MULTILINE)
    for link in httpsLinks:
        link = link[1].removesuffix('.')
        urls.add(link)

    return urls


def replaceURLInFile(file: str, oldUrl: str, newUrl: str) -> str:
    foundIdx = file.find(oldUrl)
    while foundIdx != -1:
        try:
            needReplaceLeft = False
            if file[foundIdx-len('href="'):foundIdx] == 'href="':
                needReplaceLeft = True
            elif file[foundIdx-len('src="'):foundIdx] == 'src="':
                needReplaceLeft = True
            elif file[foundIdx-len(']('):foundIdx] == '](':
                needReplaceLeft = True
            elif oldUrl.lower().startswith('https://'):
                needReplaceLeft = True
                newUrl = f'[{newUrl}]({newUrl})'
            
            needReplaceRight = False
            if file[foundIdx+len(oldUrl)] in ')]}>"\' \\\n.,':
                needReplaceRight = True

            if needReplaceLeft and needReplaceRight:
                file = file[0:foundIdx] + newUrl + file[foundIdx+len(oldUrl):]

        except IndexError:
            pass

        foundIdx = file.find(oldUrl, foundIdx+1)
    
    return file


def isLocalURL(url: str):
    return not ('://' in url or url.startswith('//'))

def isAnchor(url: str):
    return url.startswith('#')

def isMarkdown(url: str):
    if '#' in url:
        url = url.removesuffix('#' + url.split('#')[-1])
    return url.endswith('.md')


def makeOpenRepoLink(extPath: str):
    url: str = None
    try:
        url = next(Repo(extPath).remote().urls, None)
    except Exception:
        pass
    if not url:
        return ""

    siteName = 'repository'
    if 'github.com' in url.lower():
        if url.endswith('.wiki.git'):
            siteName = 'wiki on GitHub'
            url = url.removesuffix('.wiki.git') + '/wiki'
        else:
            siteName = 'GitHub page'

    return f"[Open {siteName}]({url})↗"


def saveLastCacheDatetime(extName: str):
    file = os.path.join(getCacheLocation(), extName, 'lastCacheDatetime')
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, 'w') as f:
        f.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))


def readLastCacheDatetime(extName: str) -> datetime.datetime:
    dt = None
    file = os.path.join(getCacheLocation(), extName, 'lastCacheDatetime')
    if os.path.exists(file):
        with open(file, 'r') as f:
            dt = datetime.datetime.strptime(f.readline().removesuffix('\n'), "%d-%b-%Y (%H:%M:%S.%f)")
    return dt


def enoughtTimeLeftForCache(extName: str) -> bool:
    last = None
    try:
        last = readLastCacheDatetime(extName)
    except Exception as e:
        errors.report(f"Can't readLastCacheAllDatetime {e}", exc_info=True)

    return not last or datetime.datetime.now() - last >= datetime.timedelta(hours=72)



def hasAllowedExt(url: str):
    url = url.lower()
    ALLOWED_EXTENSIONS = ['.jpeg', '.jpg', '.png', '.webp', '.gif', '.mp4', '.webm']
    return any(url.endswith(x) for x in ALLOWED_EXTENSIONS)


SPECIAL_EXTENSION_NAMES = [os.path.basename(EXT_ROOT_DIRECTORY), os.path.basename(paths_internal.data_path)]


def makeAllMarkdownFilesList(extPath: str) -> str:
    if os.path.basename(extPath) in SPECIAL_EXTENSION_NAMES:
        return None

    allMarkdownFilesList = ''
    number = 0

    for filePath in Path(extPath).rglob('*.md'):
        fileName = os.path.basename(filePath)
        if not fileName.endswith('.md'): continue
        if fileName.startswith('_'): continue
        if fileName.startswith('.'): continue
        fullFileName = os.path.relpath(filePath, extPath)
        if fullFileName.startswith('.'): continue
        if fullFileName.startswith('venv'): continue
        allMarkdownFilesList += f"[{fullFileName}](/{urllib.parse.quote(fullFileName)})\n"
        number += 1

    if number <= 1:
        return None

    return allMarkdownFilesList
