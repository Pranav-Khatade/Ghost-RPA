import sys
import asyncio
import time
import os
import glob

# Force Windows Proactor Event Loop Policy to support subprocesses on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="GhostRPA Studio", description="Autonomous Local-First Web Automation Engine")

os.makedirs("data/screenshots", exist_ok=True)

try:
    app.mount("/screenshots", StaticFiles(directory="data/screenshots"), name="screenshots")
except Exception:
    pass

run_status = {
    "is_running": False,
    "current_goal": "",
    "current_url": "",
    "logs": []
}

class RunRequest(BaseModel):
    url: str
    goal: str

def log_message(msg: str):
    print(msg)
    run_status["logs"].append(msg)
    if len(run_status["logs"]) > 100:
        run_status["logs"].pop(0)

def execute_rpa_task(target_url: str, goal: str):
    from vision import plan_action, verify_state_change
    from engine.debug import annotate_viewport_debug
    from playwright.sync_api import sync_playwright
    import traceback

    run_status["is_running"] = True
    run_status["current_goal"] = goal
    run_status["current_url"] = target_url
    run_status["logs"] = []

    log_message("[GhostRPA Studio] Background task started (Sync-Bridge Mode)...")
    
    before_path = os.path.abspath("data/screenshots/current_frame.png")
    after_path = os.path.abspath("data/screenshots/next_frame.png")

    try:
        with sync_playwright() as p:
            log_message("[GhostRPA] Launching Chromium (Sync Mode)...")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1280, "height": 720})
            page = context.new_page()

            log_message(f"[GhostRPA] Navigating to: {target_url}")
            page.goto(target_url)
            time.sleep(2)

            step = 1
            completed = False
            max_steps = 8
            action_history = []

            while step <= max_steps and not completed and run_status["is_running"]:
                log_message(f"\n--- [Step {step}/{max_steps}] ---")
                
                page.screenshot(path=before_path)
                log_message("[GhostRPA] Consulting local VLM for visual planning...")
                plan = plan_action(before_path, goal, action_history)
                
                thought = plan.get("thought", "No thought provided.")
                action = plan.get("action", "wait")
                coords = plan.get("coordinates", {"x": 640, "y": 360})
                text_to_type = plan.get("text_to_type", "")
                completed = plan.get("is_goal_complete", False)

                log_message(f"[Reasoning] : {thought}")
                log_message(f"[Action]    : {action.upper()} at ({coords['x']}, {coords['y']})")

                if completed or action == "finish":
                    log_message("[GhostRPA] Goal accomplished successfully!")
                    break

                if "x" in coords and "y" in coords:
                    debug_output_path = os.path.abspath(f"data/screenshots/debug_step_{step}.png")
                    annotate_viewport_debug(
                        input_image_path=before_path,
                        output_image_path=debug_output_path,
                        click_coords={"x": coords["x"], "y": coords["y"]},
                        label=f"{action.upper()}"
                    )
                    log_message(f"[Debug] Saved overlay frame: debug_step_{step}.png")

                if action in ["click", "type"]:
                    page.mouse.move(coords["x"], coords["y"])
                    page.mouse.click(coords["x"], coords["y"])
                    action_desc = f"Clicked at ({coords['x']}, {coords['y']})"

                    if action == "type" or text_to_type:
                        time.sleep(0.5)
                        log_message(f"[GhostRPA] Typing text: '{text_to_type}'")
                        page.keyboard.type(text_to_type, delay=50)
                        page.keyboard.press("Enter")
                        action_desc += f" and typed '{text_to_type}'"

                    action_history.append(action_desc)

                elif action == "scroll_down":
                    page.mouse.wheel(0, 500)
                    action_history.append("Scrolled down page")

                elif action == "scroll_up":
                    page.mouse.wheel(0, -500)
                    action_history.append("Scrolled up page")

                elif action == "wait":
                    time.sleep(2)
                    action_history.append("Waited for UI rendering")

                time.sleep(2.5)
                page.screenshot(path=after_path)
                
                state_changed = verify_state_change(before_path, after_path, action_history[-1])
                if not state_changed:
                    log_message("[Self-Healing] No visual change detected. Clearing focus/modals with Escape...")
                    page.keyboard.press("Escape")

                step += 1

            log_message(f"\n[GhostRPA] Final URL reached: {page.url}")
            time.sleep(2)
            browser.close()

    except Exception as e:
        log_message(f"[GhostRPA Error] {str(e)}\n{traceback.format_exc()}")
    finally:
        run_status["is_running"] = False
        log_message("[GhostRPA Studio] Execution session ended.")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GhostRPA Studio - Autonomous Web Agent</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-main: #090d16;
                --bg-card: #111827;
                --border-color: #1f2937;
                --accent-green: #10b981;
                --accent-green-hover: #059669;
                --text-main: #f3f4f6;
                --text-muted: #9ca3af;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: 'Inter', sans-serif;
                background-color: var(--bg-main);
                color: var(--text-main);
                min-height: 100vh;
                padding: 2rem 1rem;
            }
            .container { max-width: 1300px; margin: 0 auto; }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 1px solid var(--border-color);
                padding-bottom: 1.5rem;
                margin-bottom: 2rem;
            }
            h1 { font-size: 1.85rem; font-weight: 700; color: var(--accent-green); display: flex; align-items: center; gap: 0.5rem; }
            .subtitle { font-size: 0.875rem; color: var(--text-muted); margin-top: 0.25rem; }
            
            .badge {
                display: inline-flex;
                align-items: center;
                padding: 0.35rem 0.85rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
                border: 1px solid var(--border-color);
            }
            .badge.idle { background: #1e293b; color: #94a3b8; }
            .badge.active { background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.4); }
            .dot { width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
            .badge.idle .dot { background: #64748b; }
            .badge.active .dot { background: var(--accent-green); animation: pulse 1.5s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

            .grid-layout { display: grid; grid-template-columns: 380px 1fr; gap: 2rem; }
            @media(max-width: 1024px) { .grid-layout { grid-template-columns: 1fr; } }

            .card {
                background-color: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 1rem;
                padding: 1.5rem;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            }
            .card h2 { font-size: 1.1rem; font-weight: 600; color: #34d399; margin-bottom: 1.25rem; }
            
            .form-group { margin-bottom: 1.25rem; }
            label { display: block; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 0.5rem; font-weight: 600; }
            input[type="text"], textarea {
                width: 100%;
                background: #030712;
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                padding: 0.75rem 1rem;
                color: var(--text-main);
                font-size: 0.875rem;
                font-family: inherit;
                outline: none;
                transition: border-color 0.2s;
            }
            input[type="text"]:focus, textarea:focus { border-color: var(--accent-green); }
            textarea { resize: vertical; min-height: 90px; }

            button.btn {
                width: 100%;
                background-color: var(--accent-green);
                color: #030712;
                font-weight: 600;
                padding: 0.75rem;
                border: none;
                border-radius: 0.5rem;
                cursor: pointer;
                font-size: 0.875rem;
                transition: background-color 0.2s, opacity 0.2s;
            }
            button.btn:hover:not(:disabled) { background-color: var(--accent-green-hover); }
            button.btn:disabled { opacity: 0.5; cursor: not-allowed; }

            .status-box { margin-top: 1.5rem; border-top: 1px solid var(--border-color); padding-top: 1.25rem; }
            .status-box p { font-size: 0.8rem; color: var(--text-muted); }
            .status-box span { color: var(--text-main); font-weight: 500; }

            .right-column { display: flex; flex-direction: column; gap: 2rem; }
            
            .console-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
            .console-header h2 { margin-bottom: 0; }
            .text-btn { background: none; border: none; color: var(--text-muted); font-size: 0.75rem; cursor: pointer; }
            .text-btn:hover { color: var(--accent-green); }

            .terminal {
                background-color: #030712;
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                padding: 1rem;
                height: 280px;
                overflow-y: auto;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                color: #34d399;
                line-height: 1.5;
            }
            .terminal .empty { color: #4b5563; font-style: italic; }

            .gallery-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 1rem;
            }
            .gallery-item {
                background: #030712;
                border: 1px solid var(--border-color);
                border-radius: 0.5rem;
                overflow: hidden;
            }
            .gallery-item img {
                width: 100%;
                height: 110px;
                object-fit: cover;
                display: block;
                transition: opacity 0.2s;
            }
            .gallery-item img:hover { opacity: 0.75; }
            .gallery-caption {
                padding: 0.5rem;
                text-align: center;
                font-size: 0.7rem;
                color: var(--text-muted);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .empty-gallery {
                grid-column: 1 / -1;
                text-align: center;
                padding: 2rem;
                color: #4b5563;
                font-size: 0.8rem;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div>
                    <h1>GhostRPA Studio</h1>
                    <div class="subtitle">Autonomous Local-First Web Automation & Vision Agent</div>
                </div>
                <div>
                    <div id="statusBadge" class="badge idle">
                        <span class="dot"></span><span id="badgeText">Idle</span>
                    </div>
                </div>
            </header>

            <div class="grid-layout">
                <div class="card">
                    <h2>Run Configuration</h2>
                    <form id="rpxForm">
                        <div class="form-group">
                            <label for="urlInput">Target URL</label>
                            <input type="text" id="urlInput" value="https://news.ycombinator.com" required>
                        </div>
                        <div class="form-group">
                            <label for="goalInput">Natural Language Goal</label>
                            <textarea id="goalInput" required>Click on search box and type AI Agent</textarea>
                        </div>
                        <button type="submit" id="submitBtn" class="btn">Launch Agent Run</button>
                    </form>

                    <div class="status-box">
                        <p>Current Goal: <span id="currentGoalDisplay">None</span></p>
                    </div>
                </div>

                <div class="right-column">
                    <div class="card">
                        <div class="console-header">
                            <h2>Execution Stream</h2>
                            <button class="text-btn" onclick="fetchStatus()">Refresh Stream</button>
                        </div>
                        <div id="terminal" class="terminal">
                            <div class="empty">No activity logs yet. Launch a run to begin.</div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="console-header">
                            <h2>Visual Debug Frames (Crosshairs)</h2>
                            <button class="text-btn" onclick="fetchScreenshots()">Refresh Gallery</button>
                        </div>
                        <div id="gallery" class="gallery-grid">
                            <div class="empty-gallery">No debug frames captured yet.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let isRunning = false;

            document.getElementById('rpxForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const url = document.getElementById('urlInput').value;
                const goal = document.getElementById('goalInput').value;
                
                try {
                    const res = await fetch('/api/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url, goal })
                    });
                    const data = await res.json();
                    if(res.ok) {
                        isRunning = true;
                        updateUIState();
                        fetchStatus();
                    } else {
                        alert(data.detail || 'Error starting run');
                    }
                } catch (err) {
                    console.error(err);
                }
            });

            async function fetchStatus() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    
                    isRunning = data.is_running;
                    document.getElementById('currentGoalDisplay').innerText = data.current_goal || 'None';
                    
                    const terminal = document.getElementById('terminal');
                    if(data.logs && data.logs.length > 0) {
                        terminal.innerHTML = data.logs.map(log => `<div>${escapeHtml(log)}</div>`).join('');
                        terminal.scrollTop = terminal.scrollHeight;
                    } else {
                        terminal.innerHTML = '<div class="empty">No activity logs yet. Launch a run to begin.</div>';
                    }
                    
                    updateUIState();
                } catch (err) {
                    console.error(err);
                }
            }

            async function fetchScreenshots() {
                try {
                    const res = await fetch('/api/screenshots');
                    const data = await res.json();
                    
                    const gallery = document.getElementById('gallery');
                    if(data.screenshots && data.screenshots.length > 0) {
                        gallery.innerHTML = data.screenshots.map(img => `
                            <div class="gallery-item">
                                <a href="/screenshots/${img}" target="_blank">
                                    <img src="/screenshots/${img}?t=${Date.now()}" alt="${img}">
                                </a>
                                <div class="gallery-caption">${img}</div>
                            </div>
                        `).join('');
                    } else {
                        gallery.innerHTML = '<div class="empty-gallery">No debug frames captured yet.</div>';
                    }
                } catch (err) {
                    console.error(err);
                }
            }

            function updateUIState() {
                const badge = document.getElementById('statusBadge');
                const badgeText = document.getElementById('badgeText');
                const btn = document.getElementById('submitBtn');

                if(isRunning) {
                    badge.className = 'badge active';
                    badgeText.innerText = 'Agent Active';
                    btn.innerText = 'Execution in Progress...';
                    btn.disabled = true;
                } else {
                    badge.className = 'badge idle';
                    badgeText.innerText = 'Idle';
                    btn.innerText = 'Launch Agent Run';
                    btn.disabled = false;
                }
            }

            function escapeHtml(text) {
                const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
                return text.replace(/[&<>"']/g, m => map[m]);
            }

            setInterval(() => {
                fetchStatus();
            }, 2000);

            fetchStatus();
            fetchScreenshots();
        </script>
    </body>
    </html>
    """

@app.post("/api/run")
async def trigger_run(payload: RunRequest, background_tasks: BackgroundTasks):
    if run_status["is_running"]:
        raise HTTPException(status_code=400, detail="An automation task is already running.")
    background_tasks.add_task(execute_rpa_task, payload.url, payload.goal)
    return {"status": "started", "url": payload.url, "goal": payload.goal}

@app.get("/api/status")
async def get_status():
    return run_status

@app.get("/api/screenshots")
async def list_screenshots():
    files = sorted(glob.glob("data/screenshots/*.png"))
    filenames = [os.path.basename(f) for f in files]
    return {"screenshots": filenames}