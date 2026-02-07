"""
TWITCH VOID SCANNER v4.0 — GLOBAL HUNTER
Feature: "Global Keyword Search" - Crawls the Top 100 Categories to find 
a specific word in stream titles across the entire platform.
"""
import streamlit as st
import pandas as pd
import requests
import datetime
import time
import random

# ═══════════════════════════════════════════════════════════════════════
# CONFIG & STYLE
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="VOID SCANNER v4.0", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp {
        background-color: #050505;
        color: #b19dd8;
        font-family: 'JetBrains Mono', monospace;
    }
    
    h1, h2, h3 { color: #9147ff !important; text-transform: uppercase; letter-spacing: -1px; }
    
    .status-terminal {
        background: #111;
        color: #00ff41;
        font-family: monospace;
        padding: 10px;
        border: 1px solid #333;
        margin-bottom: 20px;
        height: 150px;
        overflow-y: auto;
    }
    
    .uptime-badge { color: #ff4f4f; font-weight: bold; }
    .cat-badge { background: #333; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }
    
    /* Input Styling */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0f0f13;
        color: #fff;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# API LOGIC
# ═══════════════════════════════════════════════════════════════════════

def get_app_token(client_id, client_secret):
    try:
        url = "https://id.twitch.tv/oauth2/token"
        params = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}
        r = requests.post(url, params=params)
        return r.json().get("access_token")
    except: return None

def headers(token, client_id):
    return {"Client-ID": client_id, "Authorization": f"Bearer {token}"}

def search_game_id(query, token, client_id):
    url = "https://api.twitch.tv/helix/search/categories"
    r = requests.get(url, headers=headers(token, client_id), params={"query": query})
    if r.status_code == 200:
        data = r.json().get("data", [])
        if data: return data[0]["id"], data[0]["name"], data[0]["box_art_url"]
    return None, None, None

def calculate_uptime(started_at):
    if not started_at: return "0h 0m", 0.0
    start = datetime.datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ")
    now = datetime.datetime.utcnow()
    diff = now - start
    hours = diff.total_seconds() / 3600
    return f"{int(hours)}h {int((hours*60)%60)}m", hours

def deep_drill(game_id, token, client_id, min_v, max_v, status_box, language=None, max_results=50):
    """Standard Deep Drill for single category."""
    url = "https://api.twitch.tv/helix/streams"
    cursor = None
    matches = []
    pages = 0
    total = 0
    
    while len(matches) < max_results and pages < 50:
        pages += 1
        params = {"first": 100, "game_id": game_id}
        if cursor: params["after"] = cursor
        if language and language != "All": params["language"] = language
        
        try:
            r = requests.get(url, headers=headers(token, client_id), params=params)
            data = r.json()
            streams = data.get("data", [])
        except: break
            
        if not streams: break
        total += len(streams)
        
        if status_box:
             status_box.markdown(f"SCANNING PAGE {pages}... TOTAL SCANNED: {total} | FOUND: {len(matches)}")

        for s in streams:
            vc = s['viewer_count']
            if vc > max_v: continue
            if min_v <= vc <= max_v:
                s['uptime_str'], s['uptime_hours'] = calculate_uptime(s['started_at'])
                matches.append(s)
            if vc < min_v: break 
        
        cursor = data.get("pagination", {}).get("cursor")
        if not cursor: break
        
    return matches

def global_keyword_hunt(keyword, token, client_id, min_v, max_v, language=None, depth=50, status_box=None):
    """
    THE CRAWLER:
    1. Fetches Top N Categories on Twitch.
    2. Scans the stream titles in ALL of them.
    """
    # Step 1: Get Top Games
    if status_box: status_box.markdown(f"📡 FETCHING TOP {depth} CATEGORIES...")
    
    url_games = "https://api.twitch.tv/helix/games/top"
    all_games = []
    cursor = None
    
    # Fetch enough games to fill depth
    while len(all_games) < depth:
        params = {"first": 100}
        if cursor: params["after"] = cursor
        r = requests.get(url_games, headers=headers(token, client_id), params=params)
        data = r.json()
        games = data.get("data", [])
        if not games: break
        all_games.extend(games)
        cursor = data.get("pagination", {}).get("cursor")
        if not cursor: break
    
    # Trim to requested depth
    targets = all_games[:depth]
    
    # Step 2: Scan Each Game
    matches = []
    url_streams = "https://api.twitch.tv/helix/streams"
    
    total_checked = 0
    
    for i, game in enumerate(targets):
        gid = game['id']
        gname = game['name']
        
        if status_box:
             status_box.markdown(f"""
             ```bash
             > TARGETING: {gname} [{i+1}/{depth}]
             > TOTAL STREAMS CHECKED: {total_checked}
             > HITS FOUND: {len(matches)}
             ```
             """)
        
        # We scan 1 page (100 streams) per top category. 
        # Most "keyword" streams will be in the top 100 of their category.
        params = {"first": 100, "game_id": gid}
        if language and language != "All": params["language"] = language
        
        try:
            r = requests.get(url_streams, headers=headers(token, client_id), params=params)
            streams = r.json().get("data", [])
        except: continue
        
        total_checked += len(streams)
        
        for s in streams:
            # TITLE MATCH CHECK
            if keyword.lower() in s['title'].lower():
                # Viewer Range Check
                if min_v <= s['viewer_count'] <= max_v:
                    s['uptime_str'], s['uptime_hours'] = calculate_uptime(s['started_at'])
                    matches.append(s)
        
        # Rate limit niceness
        time.sleep(0.05)

    return matches

# ═══════════════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════════════

def main():
    st.title("VOID SCANNER v4.0 // GLOBAL HUNTER")
    
    with st.sidebar:
        st.header("🔑 KEYS")
        c_id = st.text_input("CLIENT ID", type="password")
        c_secret = st.text_input("CLIENT SECRET", type="password")
        if c_id and c_secret:
            if "token" not in st.session_state:
                t = get_app_token(c_id, c_secret)
                if t: st.session_state.token = t; st.session_state.cid = c_id; st.success("ONLINE")

    if "token" not in st.session_state:
        st.info("ENTER KEYS TO START"); return

    # TABS
    tab_global, tab_drill, tab_cctv = st.tabs(["🌍 GLOBAL TITLE SEARCH", "📉 DEEP DRILL", "📹 CCTV"])

    # ─── TAB 1: GLOBAL HUNTER ───
    with tab_global:
        st.markdown("### 🌍 SEARCH ENTIRE SITE BY TITLE")
        st.caption("Crawls the Top 100 Categories to find a keyword in ANY stream title.")
        
        c_kw, c_lang = st.columns([3, 1])
        with c_kw: keyword = st.text_input("TITLE KEYWORD", placeholder="e.g. Fart, Pizza, Secret, Test")
        with c_lang: lang_global = st.selectbox("LANGUAGE", ["All", "en", "es", "fr", "de", "ru", "ja", "ko"], index=1, key="l_glob")
        
        c_range, c_depth = st.columns([1, 1])
        with c_range: v_global = st.slider("VIEWERS", 0, 1000, (0, 100), key="v_glob", help="Broad range recommended for global search.")
        with c_depth: depth_scan = st.slider("SCAN DEPTH (Categories)", 10, 100, 50, help="How many game categories to scan? 100 covers 95% of Twitch.")
        
        if st.button("INITIATE GLOBAL CRAWL", use_container_width=True):
            if keyword:
                box = st.empty()
                results = global_keyword_hunt(
                    keyword, st.session_state.token, st.session_state.cid, 
                    v_global[0], v_global[1], lang_global, depth_scan, box
                )
                
                box.success(f"CRAWL COMPLETE. Found {len(results)} streams with '{keyword}' in title.")
                
                if results:
                    # Sort by viewers (Ascending = Void First)
                    results.sort(key=lambda x: x['viewer_count'])
                    
                    for s in results:
                        with st.container():
                            c_img, c_txt = st.columns([1,3])
                            with c_img: st.image(s['thumbnail_url'].replace("{width}","320").replace("{height}","180"))
                            with c_txt:
                                st.markdown(f"**[{s['user_name']}](https://twitch.tv/{s['user_name']})**")
                                st.markdown(f"👁️ {s['viewer_count']} | <span class='cat-badge'>{s['game_name']}</span>", unsafe_allow_html=True)
                                st.markdown(f"Title: **{s['title']}**") # Highlight title
                                st.markdown(f"<span class='uptime-badge'>⏱️ {s['uptime_str']}</span>", unsafe_allow_html=True)
                            st.markdown("---")

    # ─── TAB 2: DEEP DRILL ───
    with tab_drill:
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1: game_q = st.text_input("CATEGORY", value="Just Chatting")
        with c2: lang_drill = st.selectbox("LANGUAGE", ["All", "en", "es", "fr", "de", "ru", "ja", "ko"], index=1)
        with c3: v_range = st.slider("VIEWERS", 0, 50, (0, 5), key="d_slider")
        with c4: view_mode = st.selectbox("VIEW MODE", ["LIST", "MOSAIC"])
        
        if st.button("START DRILL", use_container_width=True):
            gid, gname, _ = search_game_id(game_q, st.session_state.token, st.session_state.cid)
            if gid:
                st.success(f"DRILLING: {gname} ({lang_drill})")
                box = st.empty()
                res = deep_drill(gid, st.session_state.token, st.session_state.cid, v_range[0], v_range[1], box, language=lang_drill)
                
                if not res: st.warning("No matches found.")
                else:
                    res.sort(key=lambda x: x['uptime_hours'], reverse=True)
                    if view_mode == "LIST":
                        for s in res:
                            with st.container():
                                c_img, c_txt = st.columns([1,3])
                                with c_img: st.image(s['thumbnail_url'].replace("{width}","320").replace("{height}","180"))
                                with c_txt:
                                    st.markdown(f"**[{s['user_name']}](https://twitch.tv/{s['user_name']})**")
                                    st.markdown(f"👁️ {s['viewer_count']} | <span class='uptime-badge'>⏱️ {s['uptime_str']}</span>", unsafe_allow_html=True)
                                    st.text(s['title'])
                    elif view_mode == "MOSAIC":
                        cols = st.columns(4)
                        for idx, s in enumerate(res):
                            with cols[idx % 4]:
                                st.image(s['thumbnail_url'].replace("{width}","320").replace("{height}","180"), use_container_width=True)
                                st.caption(f"{s['user_name']} ({s['viewer_count']}v)")
                                st.markdown(f"[Watch](https://twitch.tv/{s['user_name']})")

    # ─── TAB 3: CCTV ───
    with tab_cctv:
        c_cat, c_lang = st.columns([3, 1])
        with c_cat: cctv_cat = st.text_input("CATEGORY", value="Minecraft", key="cctv_q")
        with c_lang: lang_cctv = st.selectbox("LANGUAGE", ["All", "en", "es", "fr", "de", "ru", "ja", "ko"], index=1, key="l_cctv")
        
        if st.button("ACTIVATE CAMERAS"):
            gid, _, _ = search_game_id(cctv_cat, st.session_state.token, st.session_state.cid)
            if gid:
                res = deep_drill(gid, st.session_state.token, st.session_state.cid, 0, 5, None, language=lang_cctv, max_results=20)
                if len(res) < 4: st.warning("Not enough void streams.")
                else:
                    targets = random.sample(res, 4)
                    c1, c2 = st.columns(2)
                    c3, c4 = st.columns(2)
                    grid = [c1, c2, c3, c4]
                    for i, t in enumerate(targets):
                        with grid[i]:
                            st.markdown(f"**CAM {i+1}: {t['user_name']}**")
                            st.markdown(f'<iframe src="https://player.twitch.tv/?channel={t["user_name"]}&parent=localhost&muted=true" height="300" width="100%" allowfullscreen></iframe>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
