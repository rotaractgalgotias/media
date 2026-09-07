#!/usr/bin/env python3
"""
confirm_and_process.py
----------------------
Execution script to process image conversions and resizes based on scan results.
Reads `./tools/plan.json` and `./tools/log.txt`, asks for user confirmation,
and applies the image transformations safely.
"""

import os
import sys
import json
from pathlib import Path

# Register pillow_heif if available
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

from PIL import Image, ImageOps


def get_repo_root() -> Path:
    tools_dir = Path(__file__).resolve().parent
    return tools_dir.parent


def process_image(record: dict) -> bool:
    """Processes a single image record safely."""
    full_path = Path(record["full_path"])
    target_path = Path(record["target_full_path"])
    target_size = tuple(record["target_size"])
    needs_resize = record["needs_resize"]
    
    if not full_path.exists():
        print(f"[!] Source file missing: {full_path}")
        return False

    temp_target_path = target_path.with_name(f".tmp_{target_path.name}")

    try:
        with Image.open(full_path) as img:
            # Auto-orient based on EXIF tag before any resize/conversion
            img = ImageOps.exif_transpose(img)

            # Handle alpha channel when converting to JPEG
            if img.mode in ("RGBA", "LA", "P"):
                # Composite over solid white background
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1])
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # Perform high quality resize if required
            if needs_resize:
                # Use Image.Resampling.LANCZOS if available, fallback to Image.LANCZOS
                resample = getattr(Image.Resampling, "LANCZOS", Image.LANCZOS)
                img = img.resize(target_size, resample=resample)

            # Ensure parent target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as standard JPEG
            img.save(temp_target_path, "JPEG", quality=92, optimize=True)

        # Replace target file cleanly
        if temp_target_path.exists():
            if target_path.exists() and target_path != full_path:
                target_path.unlink()
            
            temp_target_path.replace(target_path)

            # If extension changed (e.g. .heic -> .jpg, .png -> .jpg), delete old original file
            if full_path != target_path and full_path.exists():
                full_path.unlink()

        return True

    except Exception as e:
        print(f"[!] Error processing {full_path.name}: {e}")
        if temp_target_path.exists():
            try:
                temp_target_path.unlink()
            except Exception:
                pass
        return False


def main():
    repo_root = get_repo_root()
    tools_dir = repo_root / "tools"
    plan_file = tools_dir / "plan.json"
    log_file = tools_dir / "log.txt"

    if not plan_file.exists() or not log_file.exists():
        print("[!] No scan plan found. Please run 'python tools/scan_images.py' first.")
        sys.exit(1)

    with open(plan_file, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    records_to_process = [r for r in plan_data.get("records", []) if r.get("action_needed")]

    print("=" * 80)
    print("IMAGE CONVERSION & RESIZE - EXECUTION CONFIRMATION")
    print("=" * 80)
    print(f"Scan Timestamp  : {plan_data.get('timestamp')}")
    print(f"Repository Root : {repo_root}")
    print(f"Total Scanned   : {plan_data.get('total_scanned')}")
    print(f"Total Actions   : {len(records_to_process)}")
    print(f"  - Conversions : {plan_data.get('convert_count')}")
    print(f"  - Resizes     : {plan_data.get('resize_count')}")
    print("=" * 80)

    if not records_to_process:
        print("[+] No actions required! All images are standard .jpg and <= 1000px on min dimension.")
        sys.exit(0)

    # Check for non-interactive flag --yes / -y
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv

    if not auto_confirm:
        confirm = input("\nProceed with processing the above files? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("[-] Operation cancelled by user.")
            sys.exit(0)

    print("\n[*] Processing files...")
    success_count = 0
    fail_count = 0

    for idx, r in enumerate(records_to_process, start=1):
        rel_path = r['rel_path']
        print(f"[{idx}/{len(records_to_process)}] Processing: {rel_path} ...", end=" ")
        
        ok = process_image(r)
        if ok:
            print("OK")
            success_count += 1
        else:
            print("FAILED")
            fail_count += 1

    print("\n" + "=" * 80)
    print(f"[+] Execution completed!")
    print(f"    Successfully Processed : {success_count}")
    print(f"    Failed                 : {fail_count}")
    print("=" * 80)

    # Run scan again to refresh log.txt and plan.json
    print("\n[*] Refreshing scan log...")
    try:
        from scan_images import scan_repository
        scan_repository()
    except Exception as e:
        print(f"[!] Refreshing scan log failed: {e}")


if __name__ == "__main__":
    main()
