import os
from pathlib import Path
import gradio as gr
from modules import shared

def needUseOnUICallback():
    res : str = shared.opts.data.get("readme_browser_tab_location", "Extensions -> Readme files")
    return res == "Readme files"


def needHideDisabledExtensions():
    res : bool = shared.opts.data.get("readme_browser_hide_disabled_extensions", False)
    return res

def needCache():
    res : bool = shared.opts.data.get("readme_browser_need_cache", True)
    return res

def needCacheOnStartup():
    if not needCache():
        return False
    res : bool = shared.opts.data.get("readme_browser_need_cache_on_startup", False)
    return res

EXT_ROOT_DIRECTORY = str(Path(__file__).parent.parent.absolute())
DEFAULT_CACHE_LOCATION = os.path.join(EXT_ROOT_DIRECTORY, 'cache')

def getCacheLocation():
    res : str = shared.opts.data.get("readme_browser_cache_location", "")
    if res == "":
        res = DEFAULT_CACHE_LOCATION
    return res


DEFAULT_WIKI_LOCATION = os.path.join(EXT_ROOT_DIRECTORY, 'wiki')


section = ("readme_browser", "Readme browser")
options = {
    "readme_browser_tab_location": shared.OptionInfo(
        "Extensions -> Readme files",
        "Tab location",
        gr.Radio,
        {
            'choices' : ["Extensions -> Readme files", "Readme files"],
        },
        section=section,
    ).needs_reload_ui(),

    "readme_browser_hide_disabled_extensions": shared.OptionInfo(
        False,
        "Hide disabled extensions",
        gr.Checkbox,
        section=section,
    ).needs_reload_ui(),

    "readme_browser_need_cache": shared.OptionInfo(
        True,
        "Need cache some external-hosted media",
        gr.Checkbox,
        section=section,
    ).info('github user content and repo assets, imgur'),

    "readme_browser_need_cache_on_startup": shared.OptionInfo(
        False,
        "Cache these media and wikis for all extensions on the webui startup if last cache was made >= 24 hours ago",
        gr.Checkbox,
        section=section,
    ).needs_reload_ui(),

    "readme_browser_cache_location": shared.OptionInfo(
        "",
        "Cache location",
        gr.Textbox,
        {
            "placeholder": "Leave empty to use default 'sd-webui-readme-browser/cache' location",
        },
        section=section,
    ).needs_reload_ui(),
}
shared.options_templates.update(shared.options_section(section, options))
