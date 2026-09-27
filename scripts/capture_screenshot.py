"""
Captures full-rendered screenshots of the Streamlit dashboard using Chrome CDP.
"""

import asyncio
import json
import base64
import subprocess
import time
import urllib.request
import shutil
from pathlib import Path


async def capture(port=9222, target_url="http://localhost:8501"):
    base_dir = Path(__file__).resolve().parent.parent
    profile_dir = base_dir / "assets" / "chrome_profile_cdp"
    profile_dir.mkdir(parents=True, exist_ok=True)
    chrome_proc = None

    try:
        cmd = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--headless=new",
            "--disable-gpu",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir.resolve()}",
            "--window-size=1440,1100",
            target_url
        ]
        chrome_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        version_url = f"http://localhost:{port}/json/version"
        connected = False
        for _ in range(30):
            try:
                with urllib.request.urlopen(version_url, timeout=1) as resp:
                    if resp.status == 200:
                        connected = True
                        break
            except Exception:
                time.sleep(0.5)

        if not connected:
            raise RuntimeError("Could not connect to Chrome DevTools Protocol")

        list_url = f"http://localhost:{port}/json/list"
        with urllib.request.urlopen(list_url) as resp:
            targets = json.loads(resp.read().decode())

        page_target = next((t for t in targets if t.get("type") == "page"), targets[0])
        ws_url = page_target["webSocketDebuggerUrl"]

        import websockets

        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            await ws.recv()

            # Wait 6 seconds for initial render
            await asyncio.sleep(6)

            # Capture primary visual (Header, KPIs, Academics)
            await ws.send(json.dumps({
                "id": 2,
                "method": "Page.captureScreenshot",
                "params": {"format": "png"}
            }))

            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 2 and "result" in msg:
                    img_bytes = base64.b64decode(msg["result"]["data"])
                    p1 = base_dir / "assets" / "dashboard_preview.png"
                    p1.write_bytes(img_bytes)
                    print(f"Captured: {p1} ({len(img_bytes)} bytes)")
                    break

            # Scroll down to capture Pattern Breaks & Insights
            await ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {"expression": "window.scrollTo(0, 950);"}
            }))
            await asyncio.sleep(1.5)

            await ws.send(json.dumps({
                "id": 4,
                "method": "Page.captureScreenshot",
                "params": {"format": "png"}
            }))

            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 4 and "result" in msg:
                    img_bytes2 = base64.b64decode(msg["result"]["data"])
                    p2 = base_dir / "assets" / "pattern_breaks_preview.png"
                    p2.write_bytes(img_bytes2)
                    print(f"Captured: {p2} ({len(img_bytes2)} bytes)")
                    break

    finally:
        if chrome_proc:
            chrome_proc.terminate()
            try:
                chrome_proc.wait(timeout=3)
            except Exception:
                chrome_proc.kill()
        if profile_dir.exists():
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == '__main__':
    asyncio.run(capture())
