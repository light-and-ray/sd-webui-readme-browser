import re, datetime, os
from modules.gitpython_hack import Repo
from readme_browser.options import EXT_ROOT_DIRECTORY

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
        siteName = 'GitHub page'

    return f"[Open {siteName}]({url})↗"


lastCacheAllDatetimeFile = os.path.join(EXT_ROOT_DIRECTORY, 'lastCacheAllDatetime')

def saveLastCacheAllDatetime():
    with open(lastCacheAllDatetimeFile, 'w') as f:
        f.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)"))

def readLastCacheAllDatetime() -> datetime.datetime:
    dt = None
    if os.path.exists(lastCacheAllDatetimeFile):
        with open(lastCacheAllDatetimeFile, 'r') as f:
            dt = datetime.datetime.strptime(f.readline().removesuffix('\n'), "%d-%b-%Y (%H:%M:%S.%f)")
    return dt
