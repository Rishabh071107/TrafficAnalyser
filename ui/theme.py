import os
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts

# Bespoke Sage Green Color Palette
sage = colors.Color(
    c50="#F3F6F4",
    c100="#E4EBE5",
    c200="#C9D7CC",
    c300="#AEC3B3",
    c400="#8FA996",
    c500="#6E8879",
    c600="#4A6B56",  # Primary Sage Green
    c700="#3E5A48",
    c800="#2F4437",
    c900="#1E2B21",
    c950="#131B15",
    name="sage",
)

# Bespoke Warm Cream Color Palette
cream = colors.Color(
    c50="#FFFFFF",
    c100="#FAF7F0",
    c200="#F4EFE6",
    c300="#EAE3D4",
    c400="#DFD7C4",
    c500="#D1C6B0",
    c600="#B8AB91",
    c700="#968970",
    c800="#6B614E",
    c900="#453E32",
    c950="#2B271F",
    name="cream",
)


def get_sage_cream_theme() -> gr.Theme:
    """Returns the custom Gradio theme configured in Sage Green and Warm Cream with editorial fonts."""
    theme = Base(
        primary_hue=sage,
        secondary_hue=cream,
        neutral_hue=cream,
        font=(
            fonts.GoogleFont("Outfit"),
            "ui-sans-serif",
            "system-ui",
            "sans-serif",
        ),
        font_mono=(
            fonts.GoogleFont("JetBrains Mono"),
            "ui-monospace",
            "Consolas",
            "monospace",
        ),
    ).set(
        # Cream Backgrounds
        body_background_fill="#F4EFE6",
        body_background_fill_dark="#1C281F",
        block_background_fill="#FCFBF7",
        block_background_fill_dark="#243328",
        block_border_color="#DFD7C7",
        block_border_color_dark="#3A4D3E",
        block_border_width="1px",
        block_radius="14px",
        block_shadow="0 6px 18px -4px rgba(47, 62, 50, 0.08)",
        # Sage Primary Buttons
        button_primary_background_fill="#4A6B56",
        button_primary_background_fill_hover="#3E5A48",
        button_primary_text_color="#FAF7F0",
        button_primary_border_color="#3E5A48",
        button_secondary_background_fill="#FAF7F0",
        button_secondary_background_fill_hover="#F0E9DC",
        button_secondary_text_color="#2F3E32",
        button_secondary_border_color="#DFD7C7",
        # Typography & Text
        body_text_color="#1E2B21",
        body_text_color_subdued="#57655A",
        # Input Styling
        input_background_fill="#FAF7F0",
        input_border_color="#DFD7C7",
        input_border_color_focus="#4A6B56",
        input_radius="10px",
    )
    return theme


def load_custom_css() -> str:
    """Reads the custom CSS stylesheet containing typography rules and bespoke classes."""
    css_path = os.path.join(os.path.dirname(__file__), "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
