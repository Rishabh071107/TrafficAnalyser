import os
import sys
from typing import List, Dict, Any, Tuple
import gradio as gr

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.api_client import TrafficApiClient

api_client = TrafficApiClient()


def render_dataset_catalog_html(videos: List[Dict[str, Any]]) -> str:
    """Generate artisanal Sage Green and Cream HTML cards for discovered dataset videos."""
    if not videos:
        return """
        <div style="padding: 16px; border: 1px dashed #DFD7C7; border-radius: 12px; background: #FAF7F0; color: #57655A; text-align: center; font-family: 'Space Grotesk', sans-serif;">
            No videos detected in dataset directory. Click <strong>'Load Video Dataset'</strong> to discover media.
        </div>
        """

    cards_html = []
    for vid in videos:
        thumb_url = f"/file={vid['thumbnail_path']}" if vid.get("thumbnail_path") and os.path.exists(vid['thumbnail_path']) else ""
        thumb_markup = (
            f'<img src="{thumb_url}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 8px 8px 0 0; border-bottom: 1px solid #DFD7C7;" alt="{vid["title"]}"/>'
            if thumb_url
            else '<div style="height: 90px; background: #E4EBE5; display: flex; align-items: center; justify-content: center; color: #4A6B56; font-family: \'Space Grotesk\', sans-serif; font-size: 12px;">Video Stream</div>'
        )

        card = f"""
        <div style="flex: 1 1 240px; max-width: 320px; background: #FCFBF7; border: 1px solid #DFD7C7; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px -2px rgba(47, 62, 50, 0.08); transition: transform 0.2s;">
            {thumb_markup}
            <div style="padding: 12px 14px;">
                <div style="font-family: 'Fraunces', serif; font-size: 15px; font-weight: 600; color: #1E2B21; margin-bottom: 4px;">{vid['title']}</div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; background: #EEF2EE; color: #4A6B56; padding: 2px 6px; border-radius: 4px; border: 1px solid #D6E0D8;">⏱ {vid['formatted_duration']}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; background: #FAF7F0; color: #57655A; padding: 2px 6px; border-radius: 4px; border: 1px solid #DFD7C7;">📐 {vid['resolution']}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 10px; background: #FAF7F0; color: #57655A; padding: 2px 6px; border-radius: 4px; border: 1px solid #DFD7C7;">💾 {vid['size_mb']} MB</span>
                </div>
                <div style="font-family: 'Space Grotesk', sans-serif; font-size: 11px; color: #6E8879;">{vid['filename']}</div>
            </div>
        </div>
        """
        cards_html.append(card)

    joined_cards = "".join(cards_html)
    return f"""
    <div style="margin-top: 14px; margin-bottom: 14px;">
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #4A6B56; margin-bottom: 8px;">
            ✦ Discovered Dataset Streams ({len(videos)})
        </div>
        <div style="display: flex; gap: 14px; flex-wrap: wrap;">
            {joined_cards}
        </div>
    </div>
    """


def fetch_dataset_options() -> Tuple[gr.Radio, str, str]:
    """Triggered when user clicks 'Load Video Dataset'. Returns updated radio choices, catalog HTML, and status."""
    videos = api_client.load_dataset_videos()
    if not videos:
        return (
            gr.Radio(choices=[], value=None, visible=True),
            render_dataset_catalog_html([]),
            "⚠️ No videos found in datasets directory.",
        )

    # Format choices as (label, file_path)
    choices = [
        (f"{v['title']}  [{v['formatted_duration']} | {v['resolution']} | {v['fps']} fps]", v["path"])
        for v in videos
    ]
    default_val = choices[0][1] if choices else None
    catalog_html = render_dataset_catalog_html(videos)
    status_msg = f"[Loaded] {len(videos)} video datasets indexed successfully."

    return (
        gr.Radio(choices=choices, value=default_val, visible=True),
        catalog_html,
        status_msg,
    )


def on_dataset_video_selected(selected_video_path: str) -> str:
    """When a video option is selected, returns the video path to preview in the video component."""
    if not selected_video_path or not os.path.exists(selected_video_path):
        return None
    return selected_video_path
