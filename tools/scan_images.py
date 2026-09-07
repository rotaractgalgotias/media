#!/usr/bin/env python3
"""
scan_images.py
--------------
Scans the media repository for images:
1. Converts non-standard/alien image formats (.heic, .heif, .avif, .png, .webp, .bmp, .tiff, .jpeg) to standard .jpg.
2. Checks image dimensions:
   If min(width, height) > 1000:
     Reduces min dimension to 1000px and scales max dimension to maintain aspect ratio.
3. Overwrites `./tools/log.txt` with a human-readable list of all scanned files and planned actions.
4. Saves `./tools/plan.json` for precise execution by `confirm_and_process.py`.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Try to register pillow_heif if available
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_SUPPORT = True
except ImportError:
    HEIF_SUPPORT = False

from PIL import Image, ImageOps

# Supported image extensions (lowercase)
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".heic", ".heif", ".avif", ".png", 
    ".webp", ".bmp", ".tiff", ".tif", ".gif"
}

# Directories to skip during scan
SKIP_DIRS = {".git", ".idea", ".vscode", "tools", "__pycache__", "node_modules", "venv", ".venv", "env"}


def get_repo_root() -> Path:
    """Returns the repository root directory (parent directory of tools/)."""
    tools_dir = Path(__file__).resolve().parent
    return tools_dir.parent


def calculate_target_dimensions(width: int, height: int):
    """
    Calculates target dimensions based on rule:
    If min(height, width) > 1000:
      reduce min dimension to 1000px and scale other dimension proportionally.
    Returns (target_width, target_height, needs_resize).
    """
    min_dim = min(width, height)
    if min_dim > 1000:
        scale = 1000.0 / min_dim
        new_width = round(width * scale)
        new_height = round(height * scale)
        return new_width, new_height, True
    return width, height, False


def scan_repository():
    repo_root = get_repo_root()
    tools_dir = repo_root / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    log_file = tools_dir / "log.txt"
    plan_file = tools_dir / "plan.json"

    print(f"[*] Scanning repository root: {repo_root}")
    if not HEIF_SUPPORT:
        print("[!] Note: pillow_heif is not loaded. HEIC/HEIF files might fail opening unless pillow-heif is installed.")

    image_files = []
    for root, dirs, files in os.walk(repo_root):
        # Modify dirs in-place to skip unwanted directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        
        for file in files:
            ext = Path(file).suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                image_files.append(Path(root) / file)

    image_files.sort()

    scanned_records = []
    actions_count = 0
    convert_count = 0
    resize_count = 0

    for file_path in image_files:
        rel_path = file_path.relative_to(repo_root)
        ext = file_path.suffix.lower()
        
        try:
            with Image.open(file_path) as img:
                # Apply EXIF rotation if present so dimensions accurately reflect actual image orientation
                img = ImageOps.exif_transpose(img)
                width, height = img.size
                format_name = (img.format or ext.strip(".")).upper()
        except Exception as e:
            scanned_records.append({
                "rel_path": str(rel_path),
                "full_path": str(file_path),
                "error": f"Failed to open image: {e}",
                "action_needed": False
            })
            continue

        # Check format conversion rule
        # Standard target format is .jpg
        needs_convert = (ext != ".jpg")
        target_ext = ".jpg"
        target_path = file_path.with_suffix(target_ext)
        target_rel_path = target_path.relative_to(repo_root)

        # Check dimension rule
        new_width, new_height, needs_resize = calculate_target_dimensions(width, height)

        action_needed = needs_convert or needs_resize

        if action_needed:
            actions_count += 1
            if needs_convert:
                convert_count += 1
            if needs_resize:
                resize_count += 1

        record = {
            "rel_path": str(rel_path),
            "full_path": str(file_path),
            "target_rel_path": str(target_rel_path),
            "target_full_path": str(target_path),
            "original_format": format_name,
            "original_ext": ext,
            "target_ext": target_ext,
            "original_size": (width, height),
            "target_size": (new_width, new_height),
            "needs_convert": needs_convert,
            "needs_resize": needs_resize,
            "action_needed": action_needed
        }
        scanned_records.append(record)

    # Generate log.txt output
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines = []
    log_lines.append("=" * 80)
    log_lines.append("MEDIA REPOSITORY IMAGE SCAN & CONVERSION LOG")
    log_lines.append(f"Generated at: {timestamp}")
    log_lines.append(f"Repository Root: {repo_root}")
    log_lines.append(f"Total Image Files Scanned: {len(scanned_records)}")
    log_lines.append(f"Total Files Requiring Action: {actions_count}")
    log_lines.append(f"  - Format Conversions (-> .jpg): {convert_count}")
    log_lines.append(f"  - Dimension Resizes (min dim > 1000px): {resize_count}")
    log_lines.append("=" * 80)
    log_lines.append("")

    log_lines.append("SUMMARY OF PLANNED ACTIONS:")
    log_lines.append("-" * 80)

    item_idx = 1
    for r in scanned_records:
        if r.get("error"):
            log_lines.append(f"[{item_idx:03d}] ERROR: {r['rel_path']}")
            log_lines.append(f"      Reason: {r['error']}")
            log_lines.append("")
            item_idx += 1
            continue

        if not r["action_needed"]:
            log_lines.append(f"[{item_idx:03d}] NO CHANGE: {r['rel_path']}")
            log_lines.append(f"      Format: {r['original_ext'].upper()} | Size: {r['original_size'][0]}x{r['original_size'][1]}")
            log_lines.append("")
        else:
            reasons = []
            if r["needs_convert"]:
                reasons.append(f"Format Convert ({r['original_ext']} -> {r['target_ext']})")
            if r["needs_resize"]:
                reasons.append(f"Resize ({r['original_size'][0]}x{r['original_size'][1]} -> {r['target_size'][0]}x{r['target_size'][1]})")

            log_lines.append(f"[{item_idx:03d}] ACTION REQUIRED: {r['rel_path']}")
            log_lines.append(f"      Target Path : {r['target_rel_path']}")
            log_lines.append(f"      Original    : {r['original_ext'].upper()} | {r['original_size'][0]}x{r['original_size'][1]} px")
            log_lines.append(f"      Target      : {r['target_ext'].upper()} | {r['target_size'][0]}x{r['target_size'][1]} px")
            log_lines.append(f"      Actions     : {', '.join(reasons)}")
            log_lines.append("")

        item_idx += 1

    # Overwrite tools/log.txt from start (mode 'w')
    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    # Write plan.json for confirm script
    plan_data = {
        "timestamp": timestamp,
        "repo_root": str(repo_root),
        "total_scanned": len(scanned_records),
        "actions_count": actions_count,
        "convert_count": convert_count,
        "resize_count": resize_count,
        "records": scanned_records
    }
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2)

    print(f"[+] Scan completed.")
    print(f"    Total Scanned: {len(scanned_records)}")
    print(f"    Actions Planned: {actions_count}")
    print(f"[+] Written log file : {log_file}")
    print(f"[+] Written plan file: {plan_file}")


if __name__ == "__main__":
    scan_repository()
