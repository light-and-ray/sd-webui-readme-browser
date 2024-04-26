import gradio as gr
from modules import shared

def needUseOnUICallback():
    res : str = shared.opts.data.get("readme_browser_tab_location", "Extensions -> Readme files")
    return res == "Readme files"


def needHideDisabledExtensions():
    res : bool = shared.opts.data.get("readme_browser_hide_disabled_extensions", False)
    return res


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
}
shared.options_templates.update(shared.options_section(section, options))
