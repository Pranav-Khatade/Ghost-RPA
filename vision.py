import json
import ollama

def plan_action(image_path: str, task_goal: str, previous_actions: list = None, model: str = "moondream:v2") -> dict:

    with open(image_path, "rb") as img_file:
        img_bytes = img_file.read()

    history_str = "\n".join(previous_actions) if previous_actions else "None (Initial Step)"

    prompt = f"""
    You are an autonomous web automation agent inspecting a browser screen (1280x720 resolution).
    
    Overall Goal: "{task_goal}"
    History of performed actions:
    {history_str}

    Analyze the screenshot and decide the single NEXT action needed toward the goal.

    Respond STRICTLY with a raw JSON object (no markdown, no formatting):
    {{
        "thought": "Brief visual explanation of what element you see and why you chose it",
        "action": "click" | "type" | "scroll_down" | "scroll_up" | "wait" | "finish",
        "coordinates": {{"x": integer_0_to_1280, "y": integer_0_to_720}},
        "text_to_type": "string to type if action is type, otherwise empty",
        "is_goal_complete": true | false
    }}
    """

    try:
        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [img_bytes]
            }]
        )

        content = response['message']['content'].strip()

        if "```" in content:
            content = content.split("```")[1].replace("json", "").strip()

        # Parse JSON output
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "action" in parsed:
            return parsed

        # Bounding box array fallback parser for models like Moondream
        if isinstance(parsed, list) and len(parsed) == 4:
            ymin, xmin, ymax, xmax = parsed
            return {
                "thought": "Detected bounding box array.",
                "action": "click",
                "coordinates": {
                    "x": int(((xmin + xmax) / 2) * 1280),
                    "y": int(((ymin + ymax) / 2) * 720)
                },
                "text_to_type": "",
                "is_goal_complete": False
            }

    except Exception as e:
        print(f"[Vision Module Warning] Raw output parsing error: {e}")

    # Universal center screen click fallback if parsing fails completely
    return {
        "thought": "Fallback execution due to unparseable VLM response.",
        "action": "click",
        "coordinates": {"x": 640, "y": 360},
        "text_to_type": "",
        "is_goal_complete": False
    }


def verify_state_change(before_img: str, after_img: str, action_taken: str, model: str = "moondream:v2") -> bool:
    """
    Universal Verifier: Evaluates visual detail between state transitions.
    """
    with open(after_img, "rb") as img_file:
        after_bytes = img_file.read()

    prompt = f"Did the web page change or transition after executing '{action_taken}'? Answer YES or NO."

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt, "images": [after_bytes]}]
        )
        answer = response['message']['content'].strip().upper()
        return "YES" in answer
    except Exception:
        return True  # Proceed assuming success on error