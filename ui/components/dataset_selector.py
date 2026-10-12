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
    """Generate refined botanical Sage & Porcelain Cream catalog cards for discovered videos."""
    if not videos:
        return """
        <div style="padding: 20px; border: 1.5px dashed #DCD4C4; border-radius: 14px; background: #FAF8F2; color: #526356; text-align: center; font-family: 'Plus Jakarta Sans', sans-serif;">
            <div style="font-size: 14px; font-weight: 600; color: #2E5339; margin-bottom: 4px;">No Media Streams Initialized</div>
            <div style="font-size: 13px;">Click <strong>'🌿 Load Video Dataset'</strong> above to index the local video repository.</div>
        </div>
        """

    cards_html = []
    for vid in videos:
        thumb_url = f"/file={vid['thumbnail_path']}" if vid.get("thumbnail_path") and os.path.exists(vid['thumbnail_path']) else ""
        thumb_markup = (
            f'<img src="{thumb_url}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 12px 12px 0 0; border-bottom: 1px solid #EAE4D6;" alt="{vid["title"]}"/>'
            if thumb_url
            else '<div style="height: 100px; background: #E1EDE3; display: flex; align-items: center; justify-content: center; color: #2E5339; font-family: \'Plus Jakarta Sans\', sans-serif; font-size: 12px; font-weight: 600;">Feed Preview</div>'
        )

        card = f"""
        <div style="flex: 1 1 260px; max-width: 340px; background: #FFFFFF; border: 1px solid #DCD4C4; border-radius: 14px; overflow: hidden; box-shadow: 0 8px 24px -6px rgba(35, 55, 42, 0.08); transition: transform 0.2s, box-shadow 0.2s;">
            {thumb_markup}
            <div style="padding: 14px 16px;">
                <div style="font-family: 'Playfair Display', Georgia, serif; font-size: 17px; font-weight: 700; color: #182C1E; margin-bottom: 6px;">{vid['title']}</div>
                <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; background: #EDF4EE; color: #2E5339; padding: 3px 8px; border-radius: 6px; border: 1px solid #D5E4D8;">⏱ {vid['formatted_duration']} ({vid['duration_seconds']}s)</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; background: #FAF8F2; color: #526356; padding: 3px 8px; border-radius: 6px; border: 1px solid #DCD4C4;">📐 {vid['resolution']}</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; background: #FAF8F2; color: #526356; padding: 3px 8px; border-radius: 6px; border: 1px solid #DCD4C4;">💾 {vid['size_mb']} MB</span>
                </div>
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 11px; color: #7E8F82; font-weight: 500;">File: {vid['filename']}</div>
            </div>
        </div>
        """
        cards_html.append(card)

    joined_cards = "".join(cards_html)
    return f"""
    <div style="margin-top: 14px; margin-bottom: 14px;">
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: #2E5339; margin-bottom: 10px;">
            ✦ Discovered Traffic Video Feeds ({len(videos)})
        </div>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
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
            "⚠️ No videos found in dataset directory.",
        )

    # Format choices as (label, file_path)
    choices = [
        (f"{v['title']}  ·  {v['formatted_duration']} ({v['duration_seconds']}s)  ·  {v['resolution']}  ·  {v['fps']} FPS", v["path"])
        for v in videos
    ]
    default_val = choices[0][1] if choices else None
    catalog_html = render_dataset_catalog_html(videos)
    status_msg = f"[Loaded] {len(videos)} video datasets indexed successfully. Select an option below to load stream."

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
