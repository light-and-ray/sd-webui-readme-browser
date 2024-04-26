import os
from pathlib import Path
from threading import Thread
import gradio as gr
from readme_browser.tools import getURLsFromFile, isLocalURL, isAnchor, isMarkdown
from readme_browser.options import needCache
from readme_browser.cache import cache
from readme_browser import readme_files


JS_PREFIX = 'readme_browser_javascript_'

def renderMarkdownFile(filePath: str, extDir: str):
    with open(filePath) as f:
        file = f.read()
    extName = os.path.basename(extDir)

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

            if url[0] == '/':
                urlFullPath = os.path.join(extDir, url[1:])
            else:
                urlFullPath = os.path.join(os.path.dirname(filePath), url)

            if os.path.exists(urlFullPath):
                if isMarkdown(url):
                    replacementUrl = f"{JS_PREFIX}readme_browser_openSubFile('{urlFullPath}')"
                else:
                    replacementUrl = f'file={urlFullPath}'

        if replacementUrl is None and needCache():
            cachedFile = cache(originalURL, extName)
            if cachedFile:
                replacementUrl = f'file={cachedFile}'

        if replacementUrl is not None:
            file = file.replace(originalURL, replacementUrl)

    return file


def selectExtension(extName: str):
    if extName not in readme_files.readmeFilesByExtName.keys():
        return "", ""
    data = readme_files.readmeFilesByExtName[extName]
    file = renderMarkdownFile(data.filePath, data.extPath)
    return file, data.extPath


def openSubFile(filePath: str, extPath: str):
    file = renderMarkdownFile(filePath, extPath)
    return file




markdownFile = gr.Markdown("", elem_classes=['readme-browser-file'], elem_id='readme_browser_file')

def getTabUI():
    readme_files.initReadmeFiles()

    with gr.Blocks() as tab:
        dummy_component = gr.Textbox("", visible=False)
        extPath = gr.Textbox("", visible=False)

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
                outputs=[markdownFile, extPath],
            ).then(
            fn=None,
            _js='readme_browser_convertUrls',
            )
        with gr.Row():
            markdownFile.render()

        openSubFileButton = gr.Button("", visible=False, elem_id="readme_browser_openSubFileButton")
        openSubFileButton.click(
            fn=openSubFile,
            _js="readme_browser_openSubFile_",
            inputs=[dummy_component, extPath],
            outputs=[markdownFile]
        ).then(
            fn=None,
            _js='readme_browser_convertUrls',
        )

    return tab


def cacheAll(demo, app):
    def func():
        isFirst = True
        for _, data in readme_files.readmeFilesByExtName.items():
            if isFirst:
                isFirst = False
                continue
            try:
                for mdFile in Path(data.extPath).rglob('*.md'):
                    _ = renderMarkdownFile(mdFile, data.extPath)
            except Exception as e:
                print(f'Error on creating cache on startup, data.extPath = {data.extPath}')
                print(e)
    Thread(target=func).start()
