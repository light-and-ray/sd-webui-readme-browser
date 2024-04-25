import gradio as gr
from modules import script_callbacks
from readme_browser.main import getTabUI

# def onUITabs():
#     tab = getTabUI()
#     return [(tab, "Readme files", "readme_files")]

# script_callbacks.on_ui_tabs(onUITabs)

def addTabInExtensionsTab(component, **kwargs):
    if kwargs.get('elem_id', "") != 'extensions_backup_top_row':
        return
    tabs = component.parent.parent

    with tabs:
        with gr.Tab("Readme files", elem_id="readme_files_tab"):
            getTabUI()


script_callbacks.on_after_component(addTabInExtensionsTab)
