import os
from dataclasses import dataclass
import gradio as gr
from modules import extensions, util, paths_internal
from readme_browser.tools import getURLsFromFile, isLocalURL, isAnchor, isMarkdown

JS_PREFIX = 'readme_browser_javascript_'


def renderMarkdownFile(filePath: str, extDir: str):
    with open(filePath) as f:
        file = f.read()

    for url in getURLsFromFile(file):
        originalURL = url
        replacementUrl = None
        if JS_PREFIX in originalURL:
            file = file.replace(originalURL, "***")
            continue

        if 'github.com' in url and '/blob/' in url:
            url = url.split('/blob/')[-1]
            url = url.removeprefix(url.split('/')[0])

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

        if replacementUrl is not None:
            file = file.replace(originalURL, replacementUrl)

    return file


def selectExtension(extName: str):
    if extName == "None":
        return "", ""
    data = readmeFilesByExtName[extName]
    file = renderMarkdownFile(data.filePath, data.extPath)
    return file, data.extPath


@dataclass
class ReadmeFileData:
    filePath: str
    extPath: str


readmeFilesByExtName: dict[str, ReadmeFileData] = {}

def initReadmeFiles():
    global readmeFilesByExtName
    webuiPath = paths_internal.data_path
    webuiName = os.path.basename(webuiPath)
    files = util.listfiles(webuiPath)
    for file in files:
        if os.path.basename(file).lower() == 'readme.md':
            readmeFilesByExtName[webuiName] = ReadmeFileData(file, webuiPath)
            break

    for ext in extensions.extensions:
        # if not ext.enabled: continue
        files = util.listfiles(ext.path)
        for file in files:
            if os.path.basename(file).lower() == 'readme.md':
                readmeFilesByExtName[ext.name] = ReadmeFileData(file, ext.path)
                break


def openSubFile(filePath: str, extPath: str):
    file = renderMarkdownFile(filePath, extPath)
    return file


markdownFile = gr.Markdown("", elem_classes=['readme-browser-file'], elem_id='readme_browser_file')

def getTabUI():
    initReadmeFiles()

    with gr.Blocks() as tab:
        dummy_component = gr.Textbox("", visible=False)
        extPath = gr.Textbox("", visible=False)

        with gr.Row():
            selectedExtension = gr.Dropdown(
                label="Extension",
                value="None",
                choices=["None"] + list(readmeFilesByExtName.keys())
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
