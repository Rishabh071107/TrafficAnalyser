import os
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts

# Refined Alpine Sage Palette
sage = colors.Color(
    c50="#F1F6F2",
    c100="#E1EDE3",
    c200="#C4DCC8",
    c300="#A3C7AA",
    c400="#7FAFA9",
    c500="#547B61",
    c600="#2E5339",  # Botanical Deep Sage
    c700="#24422D",
    c800="#1B3222",
    c900="#132418",
    c950="#0B150E",
    name="sage",
)

# Refined Porcelain Cream Palette
cream = colors.Color(
    c50="#FFFFFF",
    c100="#FAF8F3",
    c200="#F5F1E6",
    c300="#ECE4D3",
    c400="#DFD4BE",
    c500="#CDC0A4",
    c600="#B3A486",
    c700="#948569",
    c800="#6E624C",
    c900="#494132",
    c950="#2B261D",
    name="cream",
)


def get_sage_cream_theme() -> gr.Theme:
    """Returns the refined Alpine Sage and Porcelain Cream theme for Gradio."""
    theme = Base(
        primary_hue=sage,
        secondary_hue=cream,
        neutral_hue=cream,
        font=(
            fonts.GoogleFont("Plus Jakarta Sans"),
            "system-ui",
            "-apple-system",
            "sans-serif",
        ),
        font_mono=(
            fonts.GoogleFont("JetBrains Mono"),
            "Consolas",
            "monospace",
        ),
    ).set(
        # Cream Backgrounds
        body_background_fill="#F7F4EC",
        body_background_fill_dark="#142117",
        block_background_fill="#FFFFFF",
        block_background_fill_dark="#1C2E21",
        block_border_color="#DCD4C4",
        block_border_color_dark="#2F4433",
        block_border_width="1px",
        block_radius="16px",
        block_shadow="0 10px 28px -6px rgba(35, 55, 42, 0.06)",
        # Sage Primary Buttons
        button_primary_background_fill="#2E5339",
        button_primary_background_fill_hover="#23422C",
        button_primary_text_color="#FAF7F0",
        button_primary_border_color="#23422C",
        button_secondary_background_fill="#FFFFFF",
        button_secondary_background_fill_hover="#F5EFE3",
        button_secondary_text_color="#182C1E",
        button_secondary_border_color="#DCD4C4",
        # Typography & Text
        body_text_color="#152219",
        body_text_color_subdued="#526356",
        # Input Styling
        input_background_fill="#FFFFFF",
        input_border_color="#DCD4C4",
        input_border_color_focus="#2E5339",
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
