import os
import sys
import json
import pandas as pd
from typing import Dict, Any, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def format_congestion_badge(status: str) -> str:
    """Format HTML badge with glowing indicators based on traffic congestion state."""
    status_lower = status.lower()
    if "free" in status_lower:
        badge_class = "status-free-flow"
        dot_color = "#1F6B3B"
    elif "moderate" in status_lower:
        badge_class = "status-moderate"
        dot_color = "#A36B15"
    else:
        badge_class = "status-heavy"
        dot_color = "#B54222"

    return f"""
    <span class="{badge_class}">
        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{dot_color}; margin-right:6px; box-shadow: 0 0 6px {dot_color}88;"></span>
        {status.upper()}
    </span>
    """


def render_analytics_dashboard_html(data: Dict[str, Any]) -> str:
    """Render executive Sage Green & Porcelain Cream telemetry dashboard cards."""
    if not data or data.get("status") != "completed":
        return """
        <div style="background: #FFFFFF; border: 1.5px dashed #DCD4C4; border-radius: 14px; padding: 28px; text-align: center; color: #526356; font-family: 'Plus Jakarta Sans', sans-serif; box-shadow: 0 4px 16px -4px rgba(35, 55, 42, 0.04);">
            <div style="font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; color: #2E5339; margin-bottom: 6px;">Telemetry Awaiting Stream Execution</div>
            <div style="font-size: 13px;">Select a video feed above and click <strong>'⚡ Execute Traffic Analysis'</strong> to calibrate vehicle tracks and live density.</div>
        </div>
        """

    counts = data.get("counts", {})
    speed = data.get("speed_metrics", {})
    congestion = data.get("congestion", {})
    classes = data.get("classes_detected", {})

    total_counted = counts.get("total", 0)
    in_count = counts.get("inbound", 0)
    out_count = counts.get("outbound", 0)

    avg_spd = speed.get("average_kmh", 0.0)
    max_spd = speed.get("max_kmh", 0.0)
    congestion_status = congestion.get("status", "Free Flow")
    fps = data.get("average_fps", 0.0)
    frames_proc = data.get("total_frames_processed", 0)
    elapsed = data.get("total_elapsed_seconds", 0.0)
    unique_vehicles = data.get("total_unique_vehicles", total_counted)

    congestion_badge = format_congestion_badge(congestion_status)

    # Class breakdown badges
    class_pills = []
    for cls_name, count in classes.items():
        class_pills.append(
            f'<div style="background:#FAF8F3; border:1px solid #DCD4C4; padding:5px 12px; border-radius:8px; font-family:\'Plus Jakarta Sans\', sans-serif; font-size:12px; color:#182C1E;">'
            f'<strong style="font-family:\'JetBrains Mono\', monospace; color:#2E5339; font-size:13px;">{count}</strong> {cls_name.title()}'
            f'</div>'
        )
    class_markup = "".join(class_pills) if class_pills else '<span style="font-size:12px; color:#7E8F82;">Standard Multi-Class Vehicles</span>'

    html = f"""
    <div style="margin-top: 10px;">
        <!-- Top Metrics Grid -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; margin-bottom: 16px;">
            <!-- Total Counted -->
            <div class="metric-tile">
                <div class="metric-tile-label">Line Crossings</div>
                <div class="metric-tile-value">{total_counted}</div>
                <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:11px; color:#526356; margin-top:6px;">
                    In: <strong style="color:#1F6B3B;">{in_count}</strong> &nbsp;·&nbsp; Out: <strong style="color:#B54222;">{out_count}</strong>
                </div>
            </div>

            <!-- Unique Vehicles -->
            <div class="metric-tile">
                <div class="metric-tile-label">Tracked Targets</div>
                <div class="metric-tile-value">{unique_vehicles}</div>
                <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:11px; color:#526356; margin-top:6px;">
                    Persistent Object IDs
                </div>
            </div>

            <!-- Mean Velocity -->
            <div class="metric-tile">
                <div class="metric-tile-label">Mean Velocity</div>
                <div class="metric-tile-value">{avg_spd}<span class="metric-tile-unit">km/h</span></div>
                <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:11px; color:#526356; margin-top:6px;">
                    Peak: <strong style="color:#2E5339;">{max_spd} km/h</strong>
                </div>
            </div>

            <!-- Congestion State -->
            <div class="metric-tile">
                <div class="metric-tile-label">Flow Density</div>
                <div style="margin-top: 6px;">{congestion_badge}</div>
                <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:11px; color:#526356; margin-top:8px;">
                    Peak concurrency: {congestion.get('peak_density', 0)}
                </div>
            </div>

            <!-- Processing Telemetry -->
            <div class="metric-tile">
                <div class="metric-tile-label">Inference Engine</div>
                <div class="metric-tile-value">{fps}<span class="metric-tile-unit">fps</span></div>
                <div style="font-family:'Plus Jakarta Sans', sans-serif; font-size:11px; color:#526356; margin-top:6px;">
                    {frames_proc} frames in {elapsed}s
                </div>
            </div>
        </div>

        <!-- Vehicle Classification Strip -->
        <div style="background: #FFFFFF; border: 1px solid #DCD4C4; border-radius: 12px; padding: 14px 18px; margin-bottom: 14px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; box-shadow: 0 4px 14px -4px rgba(35, 55, 42, 0.05);">
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #2E5339;">
                ✦ Detected Vehicle Classification:
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                {class_markup}
            </div>
        </div>
    </div>
    """
    return html


def export_analysis_csv(data: Dict[str, Any]) -> str:
    """Exports the latest analysis report to a CSV file and returns its path."""
    if not data or data.get("status") != "completed":
        return None

    job_id = data.get("job_id", "report")
    csv_path = os.path.join(REPORTS_DIR, f"traffic_analysis_{job_id}.csv")

    flat_records = [
        {"Metric": "Video Source", "Value": data.get("video_source", "")},
        {"Metric": "Output Video", "Value": data.get("output_video", "")},
        {"Metric": "Total Frames Processed", "Value": data.get("total_frames_processed", 0)},
        {"Metric": "Elapsed Time (seconds)", "Value": data.get("total_elapsed_seconds", 0)},
        {"Metric": "Average Processing FPS", "Value": data.get("average_fps", 0)},
        {"Metric": "Total Unique Vehicles", "Value": data.get("total_unique_vehicles", 0)},
        {"Metric": "Inbound Vehicles", "Value": data.get("counts", {}).get("inbound", 0)},
        {"Metric": "Outbound Vehicles", "Value": data.get("counts", {}).get("outbound", 0)},
        {"Metric": "Total Crossings", "Value": data.get("counts", {}).get("total", 0)},
        {"Metric": "Average Speed (km/h)", "Value": data.get("speed_metrics", {}).get("average_kmh", 0)},
        {"Metric": "Peak Speed (km/h)", "Value": data.get("speed_metrics", {}).get("max_kmh", 0)},
        {"Metric": "Dominant Congestion", "Value": data.get("congestion", {}).get("status", "")},
    ]

    df = pd.DataFrame(flat_records)
    df.to_csv(csv_path, index=False)
    return csv_path
