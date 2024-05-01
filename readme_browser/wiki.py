import os
import urllib.parse
from git import Repo
from modules import util
from readme_browser.options import DEFAULT_WIKI_LOCATION
from readme_browser.tools import JS_PREFIX


def makeDummySidebar(dirPath: str) -> str:
    sidebar = ''
    for file in util.listfiles(dirPath):
        file = os.path.basename(file)
        if not file.endswith('.md'): continue
        if file.startswith('_'): continue
        name = file.removesuffix('.md')
        sidebar += f"[{name}](/{urllib.parse.quote(name)})\n"
    return sidebar


def isWikiURL(url: str, extName: str):
    url = url.lower()

    if extName.startswith('wiki - '):
        tmp = extName.split(' - ')
        repoName = tmp[1] + '/' + tmp[2]
        isValidWiki = repoName in url
    else:
        isValidWiki = extName in url

    return 'github.com' in url and ('/wiki/' in url or url.endswith('/wiki')) and isValidWiki


def getLocalWikiURL(url: str) -> str:
    url = url.lower()
    if url.endswith('/'):
        url = url[:-1]
    if '#' in url:
        url = url.removesuffix('#' + url.split('#')[-1])
    if url.endswith('/wiki'):
        url += '/'
    tmp = url.split('/wiki/')
    repoURL = f'{tmp[0]}.wiki.git'
    repoName = tmp[0].split('/')[-2] + " - " + tmp[0].split('/')[-1]
    repoPath = tmp[1]

    dirPath = os.path.join(DEFAULT_WIKI_LOCATION, repoName)
    try:
        if not os.path.exists(dirPath):
            Repo.clone_from(repoURL, dirPath)
        else:
            repo = Repo(dirPath)
            repo.git.fetch(all=True)
            repo.git.reset('origin', hard=True)
    except Exception as e:
        # print(f"Cannot clone wiki {repoURL}:", e)
        pass

    link = f"{JS_PREFIX}readme_browser_openWiki('{repoName}', '{repoPath}')"
    return link


def getwikiFilePath(repoName, fileName):
    dirPath = os.path.join(DEFAULT_WIKI_LOCATION, repoName)
    if not fileName:
        fileName = 'Home.md'
    else:
        fileName += '.md'

    for file in util.listfiles(dirPath):
        file = os.path.basename(file)
        if file.lower() == fileName:
            fileName = file
            break

    return os.path.join(dirPath, fileName)

