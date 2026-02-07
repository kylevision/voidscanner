# 👁️ TWITCH VOID SCANNER v3.2
**A Digital Telescope for the Darkest Corners of Live Streaming**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B.svg)
![Twitch API](https://img.shields.io/badge/API-Twitch_Helix-9146FF.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

> **Mission:** Twitch's algorithm is designed to show you what is popular. The Void Scanner is designed to show you what is ignored. It recursively pages through the API to find streams with 0 viewers, and forgotten categories.
---

## ⚡ Features

### 1. 📉 Deep Drill (The Trench)
Bypasses the "Wall of Popularity." Most tools only show the top 100 streams. The Deep Drill digs through up to **100 pages** (10,000 streams) to find the absolute bottom of a category.
* **Target:** Find streams with 0-5 viewers in huge categories like *Minecraft* or *Just Chatting*.
* **Filters:** Language Lock (en, es, ru, etc.), Viewer Range (e.g., 0-0 or 1-3).
* **Mosaic Mode:** View a wall of 50 thumbnails at once for rapid visual scanning.

### 2. 🕵️ Dragnet (Sentinel)
Twitch does not allow global searches for stream titles (e.g., you can't search for "IMG_001"). The Dragnet solves this by manually downloading the top 500 streams from high-probability categories (*Just Chatting*, *Travel*, *Art*) and filtering them locally.
* **Keywords:** Detects raw filenames like `IMG_`, `DSC_`, `MVI_` or terms like `Security`, `Testing`, `WIP`.
* **Use Case:** Finding people streaming raw camera feeds or forgotten OBS tests.

### 3. 📹 CCTV Grid
Transforms your screen into a security guard's monitor bank.
* **Function:** Loads 4 random "Void Streams" (0-2 viewers) from your chosen category.
* **Experience:** Watch multiple windows into the unknown simultaneously.

### 4. 👴 Time Capsule Detection
Automatically checks the **Account Age** of found streamers.
* **Why?** Finding a 10-year-old account streaming to 0 viewers is a rare "Time Capsule" event.

---

## 🛠️ Installation

### Prerequisites
* Python 3.8+
* A [Twitch Developer Account](https://dev.twitch.tv/console) (Free) to get a Client ID & Secret.

### 1. Clone the Repository
```bash
git clone [https://github.com/kylevision/twitch-void-scanner.git](https://github.com/kylevision/twitch-void-scanner.git)
cd twitch-void-scanner
```

### 2. Install Dependencies
```Bash
pip install -r requirements.txt
```

###3. Run the Scanner
```Bash
streamlit run twitch.py
```

🔑 Setup & Usage
Launch the App: Open the URL provided in your terminal (usually http://localhost:8501).

Authenticate:

Open the Sidebar (left).

Enter your Twitch Client ID and Client Secret.

Wait for the green "ONLINE" indicator.

Start Scanning:

Select a mode (Deep Drill, Dragnet, or CCTV) from the tabs.

Enter a category or keyword.

Set your Viewer Range (recommended: 0-5 for the void, 5-20 for small communities).

Hit Start.

🧠 Pro Tips for Hunters
The "True Void": Set the viewer slider to 0 - 0. This finds streams that are truly broadcasting to nobody.

Keyword Hunting: In "Dragnet" mode, try these terms:

DSC / IMG / MVI (Raw camera uploads)

Testing / Test (OBS tests)

Security / Cam (IP Cameras)

Sleeping (Sleep streams)

Work / Study (Focus streams)

The "Mosaic" Technique: In Deep Drill, switch View Mode to MOSAIC. You can scan 50 thumbnails in seconds to spot dark rooms, weird lighting, or glitched feeds faster than reading titles.

⚠️ Disclaimer
This tool is for educational and research purposes (Digital Archaeology).

Respect the privacy of streamers. Just because they have 0 viewers doesn't mean they want to be harassed.


[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/kylevision)

Do not use this tool to brigade or troll small channels.

API Limits: This tool respects Twitch's rate limits, but aggressive usage (scanning 100 pages every second) may result in a temporary API cooldown.

License: MIT
