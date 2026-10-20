import os
from PIL import Image, ImageDraw, ImageFont

def annotate_viewport_debug(
    input_image_path: str,
    output_image_path: str,
    click_coords: dict = None,
    bbox: list = None,
    label: str = "Target Action",
    color: str = "#00FF00"  # Bright green indicator
) -> str:
    """
    Overlays a crosshair target, bounding box, and label tag on a viewport screenshot.
    
    :param input_image_path: Path to the raw captured screenshot.
    :param output_image_path: Path to save the annotated debug screenshot.
    :param click_coords: Dict with {"x": int, "y": int} center target.
    :param bbox: Optional list [ymin, xmin, ymax, xmax] normalized (0.0 to 1.0).
    :param label: Action description string to display next to the target.
    :param color: Hex color for the overlay stroke (default: Neon Green).
    """
    if not os.path.exists(input_image_path):
        print(f"[Debug Warning] Image path not found: {input_image_path}")
        return ""

    # Load image and initialize drawing canvas
    image = Image.open(input_image_path).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    width, height = image.size

    # 1. Draw Bounding Box if normalized [ymin, xmin, ymax, xmax] array is provided
    if bbox and len(bbox) == 4:
        ymin, xmin, ymax, xmax = bbox
        x1 = int(xmin * width)
        y1 = int(ymin * height)
        x2 = int(xmax * width)
        y2 = int(ymax * height)

        # Draw thick rectangular bounding frame
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

    # 2. Draw Target Crosshair and Click Point
    if click_coords and "x" in click_coords and "y" in click_coords:
        cx, cy = click_coords["x"], click_coords["y"]
        radius = 18

        # Draw outer focus ring and inner solid dot
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=3)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill="red", outline="white", width=1)

        # Draw crosshair lines extenders
        line_length = 28
        draw.line([(cx - line_length, cy), (cx + line_length, cy)], fill=color, width=2)
        draw.line([(cx, cy - line_length), (cx, cy + line_length)], fill=color, width=2)

        # 3. Draw Label Tag
        tag_text = f" {label} ({cx}, {cy}) "
        
        # Load default font or fallback
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except OSError:
            font = ImageFont.load_default()

        # Get text dimensions for background banner
        bbox_text = draw.textbbox((cx + 25, cy - 25), tag_text, font=font)
        
        # Draw text background box
        draw.rectangle(
            [bbox_text[0] - 4, bbox_text[1] - 2, bbox_text[2] + 4, bbox_text[3] + 2],
            fill=(0, 0, 0, 200),
            outline=color,
            width=1
        )
        
        # Draw text string
        draw.text((cx + 25, cy - 25), tag_text, fill="white", font=font)

    # Composite translucent overlay with original screenshot
    annotated = Image.alpha_composite(image, overlay)
    annotated = annotated.convert("RGB")
    
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    annotated.save(output_image_path)
    print(f"[GhostRPA Debug] Annotated frame saved to: {output_image_path}")
    return output_image_path