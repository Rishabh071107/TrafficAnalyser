import os
import gradio as gr

def get_classic_gradio_theme() -> gr.Theme:
    """Returns the authentic classic Gradio theme with subtle emerald sage & stone accents."""
    return gr.themes.Default(
        primary_hue=gr.themes.colors.emerald,
        secondary_hue=gr.themes.colors.stone,
        neutral_hue=gr.themes.colors.stone,
    )


def load_custom_css() -> str:
    """Reads minimal CSS helper rules for side navbar and metric badges."""
    css_path = os.path.join(os.path.dirname(__file__), "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
