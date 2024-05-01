import re
from modules.gitpython_hack import Repo


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

    return urls


def isLocalURL(url: str):
    return '://' not in url

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
