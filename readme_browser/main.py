import os, time
import urllib.parse
from pathlib import Path
from threading import Thread
import gradio as gr
from readme_browser.tools import (getURLsFromFile, isLocalURL, isAnchor, isMarkdown,
    makeOpenRepoLink, JS_PREFIX, replaceURLInFile, saveLastCacheDatetime, hasAllowedExt,
    makeAllMarkdownFilesList, SPECIAL_EXTENSION_NAMES, enoughTimeLeftForCache, makeFileIndex,
    addJumpAnchors,
)

from readme_browser.options import needCache
from readme_browser.cache import cache
from readme_browser import readme_files
from readme_browser.wiki import isWikiURL, getLocalWikiURL, makeDummySidebar, getWikiFilePath


def renderMarkdownFile(filePath: str, extDir: str, extName: str):
    isWiki = extName.startswith('wiki - ')

    with open(filePath, mode='r', encoding="utf-8-sig") as f:
        file = f.read()

    if isWiki:
        footerPath = os.path.join(os.path.dirname(filePath), '_Footer.md')
        if os.path.exists(footerPath):
            with open(footerPath, mode='r', encoding="utf-8-sig") as f:
                file += '\n\n' + f.read()

    file = addJumpAnchors(file)
    file += makeFileIndex(file)

    if isWiki:
        sidebarPath = os.path.join(os.path.dirname(filePath), '_Sidebar.md')
        if os.path.exists(sidebarPath):
            with open(sidebarPath, mode='r', encoding="utf-8-sig") as f:
                sidebar = f.read()
        else:
            sidebar = makeDummySidebar(os.path.dirname(filePath))

        file += '\n\n-----------\nSidebar\n-------------\n\n' + sidebar
    else:
        allMarkdownFilesList = makeAllMarkdownFilesList(extDir)
        if allMarkdownFilesList:
            file += '\n\n-----------\nAll markdown files\n-------------\n\n' + allMarkdownFilesList


    for url in getURLsFromFile(file):
        originalURL = url
        replacementUrl = None
        if JS_PREFIX in originalURL:
            file = file.replace(originalURL, "***")
            continue

        if 'github.com' in url and '/blob/' in url:
            url = url.split('/blob/')[-1]
            url = url.removeprefix(url.split('/')[0])
            if '?' in url:
                url = url.removesuffix('?' + url.split('?')[-1])

        if isLocalURL(url):
            if isAnchor(url): continue
            if '#' in url:
                url = url.removesuffix('#' + url.split('#')[-1])
            if isWiki and not hasAllowedExt(url):
                url += '.md'

            if url[0] == '/':
                urlFullPath = os.path.join(extDir, url[1:])
            else:
                urlFullPath = os.path.join(os.path.dirname(filePath), url)

            if os.path.exists(urlFullPath):
                if isMarkdown(url):
                    replacementUrl = f"{JS_PREFIX}readme_browser_openSubFile('{urlFullPath}')"
                else:
                    replacementUrl = f'file={urlFullPath}'

        elif isWikiURL(url, extName):
            replacementUrl = getLocalWikiURL(url)

        if replacementUrl is None and needCache() and not isLocalURL(originalURL):
            cachedFile = cache(originalURL, extName)
            if cachedFile:
                replacementUrl = f'file={cachedFile}'

        if replacementUrl is not None:
            replacementUrl = urllib.parse.quote(replacementUrl)
            file = replaceURLInFile(file, originalURL, replacementUrl)

    if enoughTimeLeftForCache(extName):
        saveLastCacheDatetime(extName)
    return file


def selectExtension(extName: str):
    if extName not in readme_files.readmeFilesByExtName.keys():
        return "", "", "", ""
    data = readme_files.readmeFilesByExtName[extName]
    file = renderMarkdownFile(data.filePath, data.extPath, extName)
    openRepo = makeOpenRepoLink(data.extPath)
    return file, data.extPath, extName, openRepo


def openSubFile(filePath: str, extPath: str, extName: str):
    file = renderMarkdownFile(filePath, extPath, extName)
    return file


def openWiki(wikiName, filePath):
    filePath = getWikiFilePath(wikiName, filePath)
    dirPath = os.path.dirname(filePath)
    file = renderMarkdownFile(filePath, dirPath, f'wiki - {wikiName}')
    openRepo = makeOpenRepoLink(dirPath)
    return file, filePath, wikiName, openRepo



markdownFile = gr.Markdown("", elem_classes=['readme-browser-file'], elem_id='readme_browser_file')
openRepo = gr.Markdown("", elem_classes=['readme-browser-open-repo'], elem_id='readme_browser_open_repo')

def getTabUI():
    readme_files.initReadmeFiles()

    with gr.Blocks() as tab:
        dummy_component = gr.Textbox("", visible=False)
        extPath = gr.Textbox("", visible=False)
        extName = gr.Textbox("", visible=False)

        with gr.Row():
            selectedExtension = gr.Dropdown(
                label="Extension",
                value="",
                choices=[""] + list(readme_files.readmeFilesByExtName.keys())
            )
            selectButton = gr.Button('Select')
            selectButton.click(
                fn=selectExtension,
                inputs=[selectedExtension],
                outputs=[markdownFile, extPath, extName, openRepo],
            ).then(
                fn=None,
                _js='readme_browser_afterRender',
            )

        with gr.Row():
            markdownFile.render()

        with gr.Row():
            openRepo.render()

        openSubFileButton = gr.Button("", visible=False, elem_id="readme_browser_openSubFileButton")
        openSubFileButton.click(
            fn=openSubFile,
            _js="readme_browser_openSubFile_",
            inputs=[dummy_component, extPath, extName],
            outputs=[markdownFile]
        ).then(
            fn=None,
            _js='readme_browser_afterRender',
        )

        openWikiButton = gr.Button("", visible=False, elem_id="readme_browser_openWikiButton")
        openWikiButton.click(
            fn=openWiki,
            _js="readme_browser_openWiki_",
            inputs=[dummy_component, dummy_component],
            outputs=[markdownFile, extPath, extName, openRepo]
        ).then(
            fn=None,
            _js='readme_browser_afterRender',
        )

    return tab


def cacheAll(demo, app):
    def func():
        for extName, data in readme_files.readmeFilesByExtName.items():
            if not enoughTimeLeftForCache(extName):
                continue
            if extName in SPECIAL_EXTENSION_NAMES:
                continue
            try:
                for mdFile in Path(data.extPath).rglob('*.md'):
                    _ = renderMarkdownFile(mdFile, data.extPath, extName)
            except Exception as e:
                print(f'Error on creating cache on startup, data.extPath = {data.extPath}')
                print(e)
        time.sleep(60)

    Thread(target=func).start()
