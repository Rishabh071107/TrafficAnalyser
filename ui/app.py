import os
import sys
import glob
import socket
import gradio as gr
from typing import Tuple, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ui.theme import get_classic_gradio_theme, load_custom_css
from ui.components.dataset_selector import fetch_dataset_options
from ui.components.analytics_view import render_analytics_dashboard_html, export_analysis_csv
from src.api_client import TrafficApiClient

api_client = TrafficApiClient()


def find_free_port(start_port: int = 7860, max_tries: int = 20) -> int:
    """Find the first available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def find_cached_output_for_video(video_path: str) -> Optional[str]:
    """Finds existing processed output video for a given input file if present."""
    if not video_path:
        return None
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    out_dir = os.path.join(PROJECT_ROOT, "outputs", "tracking")
    if not os.path.exists(out_dir):
        return None

    candidates = [
        os.path.join(out_dir, f"analyzed_{base_name}.mp4"),
        os.path.join(out_dir, f"output_{base_name}.mp4"),
    ]
    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 0:
            return c

    matches = glob.glob(os.path.join(out_dir, f"analyzed_*_{base_name}.mp4"))
    if matches:
        return sorted(matches, key=os.path.getmtime, reverse=True)[0]

    return None


def handle_video_selection(selected_video_path: str) -> Tuple[Optional[str], Optional[str], str]:
    """When a dataset option is selected, updates input preview and loads output video if available."""
    if not selected_video_path or not os.path.exists(selected_video_path):
        return None, None, "Select a valid video from the dataset."

    cached_output = find_cached_output_for_video(selected_video_path)
    status_text = (
        f"Selected: {os.path.basename(selected_video_path)} · Cached output loaded"
        if cached_output
        else f"Selected: {os.path.basename(selected_video_path)} · Ready for analysis"
    )

    return selected_video_path, cached_output, status_text


def execute_analysis(
    selected_video_path: str,
    conf_thresh: float,
    imgsz: int,
    frame_stride: int,
    line_y: float,
    max_frames: int,
    progress=gr.Progress(track_tqdm=True),
) -> Tuple[Optional[str], str, Optional[str], str]:
    """Runs the traffic analysis pipeline and renders the output video + metrics."""
    if not selected_video_path or not os.path.exists(selected_video_path):
        return (
            None,
            render_analytics_dashboard_html({}),
            None,
            "⚠️ Please load and select a video dataset first.",
        )

    def ui_progress_callback(frame_idx, total_frames, fps, interim):
        if total_frames > 0:
            progress((frame_idx, total_frames), desc=f"Processing frame {frame_idx}/{total_frames} ({fps} FPS)")

    try:
        max_f = int(max_frames) if max_frames > 0 else None
        result = api_client.run_analysis(
            video_path=selected_video_path,
            conf_thresh=conf_thresh,
            imgsz=int(imgsz),
            frame_stride=int(frame_stride),
            line_y=line_y,
            max_frames=max_f,
            progress_callback=ui_progress_callback,
        )

        out_video = result.get("output_video")
        dashboard_html = render_analytics_dashboard_html(result)
        csv_path = export_analysis_csv(result)

        status_msg = f"✓ Analysis complete: {result.get('total_frames_processed', 0)} frames processed at {result.get('average_fps', 0)} FPS."
        return out_video, dashboard_html, csv_path, status_msg

    except Exception as e:
        return (
            None,
            f"<div style='color:#B85D38; padding: 12px; background: #FFF0F0; border-radius: 8px;'>Error executing analysis: {str(e)}</div>",
            None,
            f"⚠️ Error: {str(e)}",
        )


def build_app() -> gr.Blocks:
    """Constructs the Gradio application with Classic theme and Side Navbar."""
    with gr.Blocks(title="Traffic Monitoring & Analysis System") as demo:
        # Side Navbar (Left navigation drawer)
        with gr.Sidebar(label="Traffic Analyser Navigation", open=True, width=360):
            gr.Markdown("## 🚦 Traffic Analyser")
            gr.Markdown("*Real-Time Vehicle Tracking & Density Monitoring*")

            gr.Markdown("---")
            gr.Markdown("### 1. Dataset Repository")
            btn_load_dataset = gr.Button("🌿 Load Video Dataset", variant="primary")
            status_label = gr.Markdown("*Click 'Load Video Dataset' to index media.*")

            dataset_selector = gr.Radio(
                label="Available Video Feeds",
                choices=[],
                value=None,
                visible=False,
                interactive=True,
            )

            dataset_catalog = gr.HTML("", visible=True)

            gr.Markdown("---")
            gr.Markdown("### 2. Inference Calibration")
            conf_slider = gr.Slider(
                minimum=0.1,
                maximum=0.9,
                value=0.25,
                step=0.05,
                label="Confidence Threshold",
            )
            stride_slider = gr.Slider(
                minimum=1,
                maximum=5,
                value=1,
                step=1,
                label="Frame Stride (1 = Full Coverage)",
            )
            line_y_slider = gr.Slider(
                minimum=0.2,
                maximum=0.8,
                value=0.5,
                step=0.05,
                label="Counting Line Y-Ratio",
            )
            imgsz_dropdown = gr.Dropdown(
                choices=[320, 640],
                value=640,
                label="Inference Resolution (px)",
            )
            max_frames_slider = gr.Slider(
                minimum=0,
                maximum=1000,
                value=0,
                step=50,
                label="Max Frames (0 = Full Video)",
                info="0 analyzes the full video duration without truncation.",
            )

            gr.Markdown("---")
            btn_analyze = gr.Button("⚡ Execute Traffic Analysis", variant="primary", size="lg")

            gr.Markdown("---")
            gr.Markdown(
                "<small><strong>Backend:</strong> Flask REST API (5000)<br>"
                "<strong>Engine:</strong> YOLO11 + ByteTrack Tracker</small>"
            )

        # Main Area (Right Content)
        gr.Markdown("# 🛰️ Live Traffic Observatory & Vision Analytics")
        gr.Markdown(
            "End-to-end traffic monitoring, multi-object tracking, speed estimation, virtual line counting, and congestion density metrics."
        )

        # Dual Video Displays
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📹 Source Input Stream")
                input_video = gr.Video(label="Input Video Preview", interactive=False)

            with gr.Column(scale=1):
                gr.Markdown("### ✨ Annotated Output Stream")
                output_video = gr.Video(label="Analyzed Output (Overlays & Tracks)", interactive=False)

        # Telemetry & Dashboard
        gr.Markdown("### 📊 Real-Time Telemetry & Traffic Flow Analytics")
        analytics_display = gr.HTML(render_analytics_dashboard_html({}))

        # Export report file
        csv_download = gr.File(label="Download Traffic Analysis Report (CSV)", visible=True)

        # Event Bindings
        # 1. Load Dataset Button -> fetch options & catalog
        btn_load_dataset.click(
            fn=fetch_dataset_options,
            inputs=[],
            outputs=[dataset_selector, dataset_catalog, status_label],
        )

        # 2. Select Video Option -> preview input video and load cached output video if present
        dataset_selector.change(
            fn=handle_video_selection,
            inputs=[dataset_selector],
            outputs=[input_video, output_video, status_label],
        )

        # 3. Execute Analysis Button -> run pipeline, update output video, analytics dashboard and CSV
        btn_analyze.click(
            fn=execute_analysis,
            inputs=[
                dataset_selector,
                conf_slider,
                imgsz_dropdown,
                stride_slider,
                line_y_slider,
                max_frames_slider,
            ],
            outputs=[output_video, analytics_display, csv_download, status_label],
        )

    return demo


def launch_app():
    """Build and launch the Gradio app with port fallback."""
    app = build_app()
    theme = get_classic_gradio_theme()
    custom_css = load_custom_css()

    target_port = find_free_port(7860)
    print(f"[Gradio UI] Launching on port {target_port} ...")

    app.launch(
        server_name="127.0.0.1",
        server_port=target_port,
        theme=theme,
        css=custom_css,
    )


if __name__ == "__main__":
    launch_app()
