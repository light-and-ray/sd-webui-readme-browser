import re, datetime, os
import urllib.parse
from pathlib import Path
from modules.gitpython_hack import Repo
from modules import errors, paths_internal
from readme_browser.options import EXT_ROOT_DIRECTORY, getCacheLocation

JS_PREFIX = 'readme_browser_javascript_'

def getURLsFromFile(file: str) -> list[str]:
    urls = set()

    MDLinks = re.findall(r'\[.*?\]\(.+?\)', file)
    for link in MDLinks:
        tmp: str = link.replace(r'\(', '')
        tmp = tmp.split('(')[-1]
        url = tmp.removesuffix(')')
        urls.add(url)

    srcLinks = re.findall(r'src=".+?"', file)
    for link in srcLinks:
        url = link.split('"')[-2]
        urls.add(url)

    hrefLinks = re.findall(r'href=".+?"', file)
    for link in hrefLinks:
        url = link.split('"')[-2]
        urls.add(url)
    
    httpsLinks = re.findall(r'[\n\r\s]+?https://.+?[\n\r\s]+?', file)
    for link in httpsLinks:
        link = link[1:-1].removesuffix('.')
        urls.add(link)

    return urls


def replaceURLInFile(file: str, oldUrl: str, newUrl: str) -> str:
    foundIdx = file.find(oldUrl)
    while foundIdx != -1:
        try:
            needReplace = False
            if file[foundIdx-len('href="'):foundIdx] == 'href="':
                needReplace = True
            elif file[foundIdx-len('src="'):foundIdx] == 'src="':
                needReplace = True
            elif file[foundIdx-len(']('):foundIdx] == '](':
                needReplace = True
            elif oldUrl.lower().startswith('https://'):
                needReplace = True
                newUrl = f'[{newUrl}]({newUrl})'

            if needReplace:
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
