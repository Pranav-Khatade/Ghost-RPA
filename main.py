import asyncio
import os
from playwright.async_api import async_playwright
from vision import plan_action, verify_state_change
from engine.debug import annotate_viewport_debug  # Import the Pillow debug helper

async def run_universal_ghost_rpa(target_url: str, goal: str, max_steps: int = 8):
    os.makedirs("data/screenshots", exist_ok=True)
    before_path = os.path.abspath("data/screenshots/current_frame.png")
    after_path = os.path.abspath("data/screenshots/next_frame.png")

    action_history = []
    
    async with async_playwright() as p:
        print(f"\n[GhostRPA] Starting Universal Engine...")
        print(f"[Target URL] : {target_url}")
        print(f"[Goal]       : {goal}\n")

        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 720})
        page = await context.new_page()

        await page.goto(target_url)
        await asyncio.sleep(2)  # Wait for initial page load

        step = 1
        completed = False

        while step <= max_steps and not completed:
            print(f"\n--- [Step {step}/{max_steps}] ---")
            
            # 1. Capture Viewport State
            await page.screenshot(path=before_path)

            # 2. Query Local VLM Planner
            plan = plan_action(before_path, goal, action_history)
            
            thought = plan.get("thought", "No thought provided.")
            action = plan.get("action", "wait")
            coords = plan.get("coordinates", {"x": 640, "y": 360})
            text_to_type = plan.get("text_to_type", "")
            completed = plan.get("is_goal_complete", False)

            print(f"[GhostRPA Reasoning] : {thought}")
            print(f"[Action Planned]    : {action.upper()} at ({coords['x']}, {coords['y']})")

            if completed or action == "finish":
                print("\n[GhostRPA] Goal accomplished successfully!")
                break

            # 3. Render Debug Visual Overlay (Crosshairs/Targets)
            if "x" in coords and "y" in coords:
                debug_output_path = os.path.abspath(f"data/screenshots/debug_step_{step}.png")
                annotate_viewport_debug(
                    input_image_path=before_path,
                    output_image_path=debug_output_path,
                    click_coords={"x": coords["x"], "y": coords["y"]},
                    label=f"{action.upper()}"
                )

            # 4. Execute Browser Actions
            if action in ["click", "type"]:
                await page.mouse.move(coords["x"], coords["y"])
                await page.mouse.click(coords["x"], coords["y"])
                action_desc = f"Clicked at ({coords['x']}, {coords['y']})"

                if action == "type" or text_to_type:
                    await asyncio.sleep(0.5)
                    await page.keyboard.type(text_to_type, delay=50)
                    await page.keyboard.press("Enter")
                    action_desc += f" and typed '{text_to_type}'"

                action_history.append(action_desc)

            elif action == "scroll_down":
                await page.mouse.wheel(0, 500)
                action_history.append("Scrolled down page")

            elif action == "scroll_up":
                await page.mouse.wheel(0, -500)
                action_history.append("Scrolled up page")

            elif action == "wait":
                await asyncio.sleep(2)
                action_history.append("Waited for UI rendering")

            # 5. Self-Healing State Verification
            await asyncio.sleep(2.5)
            await page.screenshot(path=after_path)
            
            state_changed = verify_state_change(before_path, after_path, action_history[-1])
            if not state_changed:
                print("[Self-Healing] No visual change detected. Clearing focus/modals...")
                await page.keyboard.press("Escape")

            step += 1

        print(f"\n[GhostRPA] Final URL reached: {page.url}")
        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    URL = "https://news.ycombinator.com"
    GOAL = "Click on the search box at the bottom and type 'AI Agent'"

    asyncio.run(run_universal_ghost_rpa(URL, GOAL))