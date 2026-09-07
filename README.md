# Rotaract Club of Galgotias Educational Institutions - Media Repository

Welcome to the official media asset repository for the **Rotaract Club of Galgotias Educational Institutions (RaC-GEI)** ([rotaractgalgotias.org](https://rotaractgalgotias.org)).

This repository serves as the central storage and management hub for tenure-wise media files, including:
- **Board of Directors** photos
- **Council Members** photos
- **Event Thumbnails & Posters**
- **Miscellaneous Brand & Graphic Assets**

---

## 📁 Repository Directory Structure

Media files are organized by tenure folders to maintain a clean history across rotary years:

```text
media/
├── 2026-27/
│   ├── Board of Directors/
│   │   ├── FIRSTNAME_LASTNAME.jpg
│   ├── Council Members/
│   │   ├── FIRSTNAME_LASTNAME.jpg
│   ├── Events/
│   │   ├── EVENT_NAME_THUMBNAIL.jpg
│   └── Misc/
├── tools/
│   ├── scan_images.py
│   ├── confirm_and_process.py
│   ├── log.txt
│   └── plan.json
├── README.md
└── requirements.txt
```

---

## 🏷️ Naming Conventions & Best Practices

To ensure reliable web rendering and avoid broken image links, adhere strictly to these naming guidelines:

1. **Use Standard Format**: All images **MUST** use `.jpg` extension (all lowercase).
2. **Clean File Names**:
   - For Members/Directors: `FIRSTNAME_LASTNAME.jpg` (e.g., `VIJAY_SHARMA.jpg`)
   - For Events: `EVENT_NAME_THUMBNAIL.jpg` (e.g., `BLOOD_DONATION_2026.jpg`)
3. **No Special Characters or Spaces**: Avoid spaces, quotes, emojis, or symbols (`#`, `@`, `$`, `%`, `&`, `?`). Use underscores (`_`) or hyphens (`-`).
4. **No Raw Camera Names**: Never upload default camera outputs like `IMG_9823.HEIC` or `DCIM_001.PNG`.

---

## 🔗 Direct Git Raw URL Usage for Website Admin Panel

You can use images stored in this repository directly on the official website or admin CMS panels without uploading files twice.

### How to Get the Raw Image URL:
1. Navigate to the image file on GitHub (e.g., `2026-27/Board of Directors/VIJAY.jpg`).
2. Append `?raw=true` to the browser URL, or right-click the **Raw** button and copy the address.

**URL Format:**
```text
https://github.com/<Organization>/<Repository>/raw/main/2026-27/Board%20of%20Directors/VIJAY.jpg
```
or
```text
https://github.com/<Organization>/<Repository>/blob/main/2026-27/Board%20of%20Directors/VIJAY.jpg?raw=true
```

> **Tip**: Paste this raw URL directly into the image URL input field in the website admin panel.

---

## ⚠️ Important Upload Warnings

> [!CAUTION]
> **DO NOT upload arbitrary or raw camera files!**
> - **No Alien Formats**: `.heic`, `.heif`, `.avif`, `.raw`, `.tiff`, `.bmp` files must be processed before committing.
> - **No Uncompressed Ultra-High Resolution**: Images directly from iPhones or cameras can be 10MB+ with resolutions over 4000px. Uploading uncompressed images degrades website loading performance and consumes excess bandwith.
> - **Always Run the Automated Tools** (detailed below) before pushing new images to GitHub!

---

## ⚙️ Technical Tools & Automation Scripts

We provide automated Python scripts in `./tools` to maintain optimal image formats, resolutions, and quality across the entire repository.

### Rules Applied by Tools:
1. **Format Standardization**: Converts non-standard formats (`.heic`, `.png`, `.webp`, `.bmp`, `.tiff`, `.jpeg`) to web-optimized `.jpg`.
2. **Smart Resolution Scaling**:
   - Condition: `min(height, width) > 1000px`
   - If the smaller dimension exceeds 1000px, it is scaled down to **1000px**, while the larger dimension is scaled proportionally to **preserve the exact aspect ratio**.

---

### 🚀 How to Set Up & Run the Tools

#### 1. Install Requirements
Ensure Python 3.9+ is installed, then run:
```bash
pip install -r requirements.txt
```

#### 2. Step 1: Scan Repository & Generate Log
Run the scanner script to scan the repository and preview planned changes:
```bash
python tools/scan_images.py
```
- This creates/overwrites `./tools/log.txt` from start listing all files scanned, target paths, format changes, and target dimensions.

#### 3. Step 2: Confirm and Execute Operations
After reviewing `./tools/log.txt`, execute the processing script:
```bash
python tools/confirm_and_process.py
```
- The script will display a summary and prompt for `[y/N]` confirmation before applying transformations.
- To run non-interactively in automated pipelines, use:
  ```bash
  python tools/confirm_and_process.py --yes
  ```

---

## 🤝 Support & Maintenance

For questions or updates regarding media management, contact the **RaC-GEI Tech & Media Team** or visit [rotaractgalgotias.org](https://rotaractgalgotias.org).
