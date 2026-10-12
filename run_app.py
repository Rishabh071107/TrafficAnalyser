import os
import sys
import time
import argparse
import threading
import requests

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from deployment.api.flask_app import run_flask_server
from ui.app import build_app, find_free_port
from ui.theme import get_classic_gradio_theme, load_custom_css


def wait_for_flask(url="http://127.0.0.1:5000/api/health", timeout=10.0):
    """Wait until Flask server is responding."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.3)
    return False


def main():
    parser = argparse.ArgumentParser(description="Veloce Traffic Analyser - UI & Backend Runner")
    parser.add_argument(
        "--mode",
        choices=["all", "gradio", "flask"],
        default="all",
        help="Run mode: 'all' (Flask + Gradio), 'gradio' (frontend only), or 'flask' (backend only)",
    )
    parser.add_argument("--flask-port", type=int, default=5000, help="Port for Flask REST backend")
    parser.add_argument("--gradio-port", type=int, default=7860, help="Port for Gradio UI frontend")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface to bind to")
    parser.add_argument("--share", action="store_true", help="Generate public Gradio share link")

    args = parser.parse_args()

    print("=" * 70)
    print("🌿 VELOCE TRAFFIC INTELLIGENCE OBSERVATORY")
    print(f"   Theme: Sage Green & Cream Aesthetic | Fonts: Fraunces / Space Grotesk")
    print(f"   Execution Mode: {args.mode.upper()}")
    print("=" * 70)

    if args.mode in ["all", "flask"]:
        flask_thread = threading.Thread(
            target=run_flask_server,
            kwargs={"host": args.host, "port": args.flask_port, "debug": False},
            daemon=True,
        )
        flask_thread.start()
        print(f"[Runner] Starting Flask Backend on http://{args.host}:{args.flask_port} ...")

        if wait_for_flask(f"http://{args.host}:{args.flask_port}/api/health"):
            print(f"✓ Flask REST Backend verified active and healthy.")
        else:
            print(f"⚠️ Flask initialization timeout; continuing with local fallback bridge.")

    if args.mode in ["all", "gradio"]:
        actual_port = find_free_port(args.gradio_port)
        print(f"[Runner] Initializing Classic Gradio Frontend on http://{args.host}:{actual_port} ...")
        gradio_app = build_app()
        gradio_app.launch(
            server_name=args.host,
            server_port=actual_port,
            share=args.share,
            theme=get_classic_gradio_theme(),
            css=load_custom_css(),
        )
    elif args.mode == "flask":
        print("[Runner] Flask backend running in standalone mode. Press Ctrl+C to terminate.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Flask service.")


if __name__ == "__main__":
    main()
