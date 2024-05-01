import datetime
import gradio as gr
from modules import script_callbacks, errors
from readme_browser.main import getTabUI, cacheAll
from readme_browser.options import needUseOnUICallback, needCacheOnStartup
from readme_browser.tools import enoughtTimeLeftForCache


def onUITabs():
    tab = getTabUI()
    return [(tab, "Readme files", "readme_files")]


def addTabInExtensionsTab(component, **kwargs):
    try:
        if kwargs.get('elem_id', "") != 'extensions_backup_top_row':
            return
        tabs = component.parent.parent

        with tabs:
            with gr.Tab("Readme files", elem_id="readme_files_tab"):
                getTabUI()

    except Exception as e:
        errors.report(f"Can't add Readme files tab", exc_info=True)


if needUseOnUICallback():
    script_callbacks.on_ui_tabs(onUITabs)
else:
    script_callbacks.on_after_component(addTabInExtensionsTab)


if needCacheOnStartup():
    if enoughtTimeLeftForCache():
        script_callbacks.on_app_started(cacheAll)
        
