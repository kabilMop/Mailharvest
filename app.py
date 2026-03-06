# ─────────────────────────────────────────────
# app.py — Main entry point
# Run with: streamlit run app.py
#
# Project structure:
#   app.py         ← you are here (UI flow)
#   config.py      ← all settings & users
#   auth.py        ← login / logout
#   sheets.py      ← Google Sheets logging
#   scraper.py     ← website crawling
#   email_utils.py ← email finding & cleaning
#   network.py     ← HTTP fetching
#   ui.py          ← table, badges, log box
# ─────────────────────────────────────────────

import threading

import streamlit as st

# ── Page config — MUST be first Streamlit call ─
st.set_page_config(
    page_title="Mailharvest",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>@</text></svg>",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:#f7f7f5;--surface:#ffffff;--surface2:#f0f0ec;--border:#e2e2dc;
  --border-strong:#c8c8c0;--text-primary:#1a1a18;--text-secondary:#5a5a56;
  --text-muted:#9a9a94;--accent:#1a1a18;--accent-fg:#ffffff;--accent-hover:#3a3a38;
  --log-bg:#1c1c1a;--log-fg:#a8a89e;--log-border:#2e2e2c;
  --dot-valid:#2d7a4f;--dot-invalid:#c0392b;--dot-blocked:#c07a2b;--dot-notfound:#7a7a74;
  --badge-exact-bg:#d4edda;--badge-exact-fg:#1a5c35;
  --badge-partial-bg:#fff3cd;--badge-partial-fg:#7a5c00;
  --badge-nomatch-bg:#fde8e8;--badge-nomatch-fg:#8b1a1a;
  --badge-neutral-bg:#ebebeb;--badge-neutral-fg:#5a5a56;
  --row-valid-bg:#f0faf4;--row-invalid-bg:#fdf4f4;
  --row-blocked-bg:#fdf6f0;--row-notfound-bg:#f7f7f5;
  --th-bg:#1a1a18;--th-fg:#ffffff;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#141412;--surface:#1e1e1c;--surface2:#252523;--border:#2e2e2c;
    --border-strong:#3e3e3c;--text-primary:#e8e8e4;--text-secondary:#a8a8a2;
    --text-muted:#686864;--accent:#e8e8e4;--accent-fg:#141412;--accent-hover:#c8c8c4;
    --log-bg:#0e0e0c;--log-fg:#7a7a74;--log-border:#1e1e1c;
    --dot-valid:#4aad72;--dot-invalid:#e05c4a;--dot-blocked:#e0944a;--dot-notfound:#5a5a56;
    --badge-exact-bg:#1a3d28;--badge-exact-fg:#6dd99a;
    --badge-partial-bg:#3d3010;--badge-partial-fg:#e0c060;
    --badge-nomatch-bg:#3d1a1a;--badge-nomatch-fg:#e08080;
    --badge-neutral-bg:#2a2a28;--badge-neutral-fg:#8a8a84;
    --row-valid-bg:#131f18;--row-invalid-bg:#1f1313;
    --row-blocked-bg:#1f1a13;--row-notfound-bg:#1a1a18;
    --th-bg:#252523;--th-fg:#a8a8a2;
  }
}
[data-theme="dark"] {
  --bg:#141412 !important;--surface:#1e1e1c !important;--surface2:#252523 !important;
  --border:#2e2e2c !important;--border-strong:#3e3e3c !important;
  --text-primary:#e8e8e4 !important;--text-secondary:#a8a8a2 !important;
  --text-muted:#686864 !important;--accent:#e8e8e4 !important;
  --accent-fg:#141412 !important;--accent-hover:#c8c8c4 !important;
  --log-bg:#0e0e0c !important;--log-fg:#7a7a74 !important;--log-border:#1e1e1c !important;
  --dot-valid:#4aad72 !important;--dot-invalid:#e05c4a !important;
  --dot-blocked:#e0944a !important;--dot-notfound:#5a5a56 !important;
  --badge-exact-bg:#1a3d28 !important;--badge-exact-fg:#6dd99a !important;
  --badge-partial-bg:#3d3010 !important;--badge-partial-fg:#e0c060 !important;
  --badge-nomatch-bg:#3d1a1a !important;--badge-nomatch-fg:#e08080 !important;
  --badge-neutral-bg:#2a2a28 !important;--badge-neutral-fg:#8a8a84 !important;
  --row-valid-bg:#131f18 !important;--row-invalid-bg:#1f1313 !important;
  --row-blocked-bg:#1f1a13 !important;--row-notfound-bg:#1a1a18 !important;
  --th-bg:#252523 !important;--th-fg:#a8a8a2 !important;
}
* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; color: var(--text-primary) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 4rem !important; max-width: 1300px !important; }
.wordmark { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.75rem; letter-spacing: -0.03em; color: var(--text-primary); margin-bottom: 0; line-height: 1; }
.wordmark span { color: var(--text-muted); font-weight: 400; }
.tagline { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; margin-top: 4px; margin-bottom: 2rem; }
.section-divider { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
textarea { font-family: 'DM Mono', monospace !important; font-size: 0.82rem !important; background: var(--surface) !important; color: var(--text-primary) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; }
textarea:focus { border-color: var(--border-strong) !important; box-shadow: none !important; }
.stButton > button { font-family: 'Syne', sans-serif !important; font-weight: 600 !important; font-size: 0.82rem !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; border-radius: 5px !important; border: 1px solid var(--border-strong) !important; background: var(--surface) !important; color: var(--text-primary) !important; padding: 0.45rem 1.2rem !important; transition: all 0.15s ease !important; }
.stButton > button:hover { background: var(--surface2) !important; border-color: var(--text-muted) !important; }
.stButton > button[kind="primary"] { background: var(--accent) !important; color: var(--accent-fg) !important; border-color: var(--accent) !important; }
.stButton > button[kind="primary"]:hover { background: var(--accent-hover) !important; border-color: var(--accent-hover) !important; }
.section-label { font-family: 'Syne', sans-serif; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem; }
.log-container { background: var(--log-bg); border: 1px solid var(--log-border); border-radius: 6px; padding: 0; overflow: hidden; }
.log-header { display: flex; align-items: center; gap: 8px; padding: 8px 14px; border-bottom: 1px solid var(--log-border); background: var(--log-bg); }
.log-dot { width: 8px; height: 8px; border-radius: 50%; background: #e05c4a; box-shadow: 14px 0 0 #e0944a, 28px 0 0 #4aad72; }
.log-title { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: var(--log-fg); margin-left: 36px; }
.log-body { font-family: 'DM Mono', monospace; font-size: 0.74rem; color: var(--log-fg); padding: 12px 14px; height: 200px; overflow-y: auto; white-space: pre-wrap; line-height: 1.7; }
.results-heading { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem; color: var(--text-primary); letter-spacing: -0.01em; margin: 1.5rem 0 0.75rem; }
.table-wrap { overflow-x: auto; border: 1px solid var(--border); border-radius: 6px; margin-bottom: 1.5rem; }
.results-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
.results-table thead tr { background: var(--th-bg); }
.results-table th { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--th-fg); padding: 10px 14px; text-align: left; white-space: nowrap; }
.results-table td { padding: 9px 14px; border-bottom: 1px solid var(--border); color: var(--text-primary); vertical-align: middle; }
.results-table tr:last-child td { border-bottom: none; }
.row-valid td { background: var(--row-valid-bg); }
.row-invalid td { background: var(--row-invalid-bg); }
.row-blocked td { background: var(--row-blocked-bg); }
.row-not-found td { background: var(--row-notfound-bg); }
.results-table tr:hover td { filter: brightness(0.97); }
.tbl-link { color: var(--text-secondary) !important; text-decoration: none !important; font-family: 'DM Mono', monospace; font-size: 0.74rem; word-break: break-all; }
.tbl-link:hover { color: var(--text-primary) !important; text-decoration: underline !important; }
.email-cell { font-family: 'DM Mono', monospace; font-size: 0.78rem; font-weight: 500; color: var(--text-primary); }
.email-empty { color: var(--text-muted); }
.nav-cell { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: var(--text-secondary); }
.stats-row { display: flex; gap: 12px; margin-top: 1rem; flex-wrap: wrap; }
.stat-card { flex: 1; min-width: 100px; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px 18px; text-align: center; }
.stat-value { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; color: var(--text-primary); line-height: 1; }
.stat-label { font-size: 0.68rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); margin-top: 4px; }
.stat-valid .stat-value { color: var(--dot-valid); }
.stat-invalid .stat-value { color: var(--dot-invalid); }
.stat-blocked .stat-value { color: var(--dot-blocked); }
.stat-notfound .stat-value { color: var(--dot-notfound); }
.streamlit-expanderHeader { font-family: 'Syne', sans-serif !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; color: var(--text-muted) !important; }
div[data-testid="stRadio"] > label { font-family: 'Syne', sans-serif !important; font-size: 0.68rem !important; font-weight: 700 !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; color: var(--text-muted) !important; }
div[data-testid="stRadio"] > div { display: flex !important; gap: 8px !important; flex-direction: row !important; }
div[data-testid="stRadio"] > div label { font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important; font-weight: 500 !important; color: var(--text-secondary) !important; background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 4px !important; padding: 5px 14px !important; cursor: pointer !important; transition: background 0.15s, color 0.15s, border-color 0.15s !important; letter-spacing: 0.02em !important; text-transform: none !important; }
div[data-testid="stRadio"] > div label:has(input:checked) { background: #1a1a18 !important; color: #ffffff !important; border-color: #1a1a18 !important; }
@media (prefers-color-scheme: dark) { div[data-testid="stRadio"] > div label:has(input:checked) { background: #e8e8e4 !important; color: #141412 !important; border-color: #e8e8e4 !important; } }
[data-theme="dark"] div[data-testid="stRadio"] > div label:has(input:checked) { background: #e8e8e4 !important; color: #141412 !important; border-color: #e8e8e4 !important; }
div[data-testid="stRadio"] > div label:hover { border-color: var(--border-strong) !important; color: var(--text-primary) !important; }
div[data-testid="stRadio"] > div input { display: none !important; }
.config-hint { font-family: 'DM Mono', monospace; font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; margin-bottom: 1rem; }
.status-running { display: inline-flex; align-items: center; gap: 8px; font-family: 'DM Mono', monospace; font-size: 0.78rem; color: var(--text-secondary); background: var(--surface2); border: 1px solid var(--border); border-radius: 4px; padding: 5px 12px; margin-bottom: 1rem; }
.pulse { width: 7px; height: 7px; border-radius: 50%; background: var(--dot-valid); animation: pulse 1.4s infinite; flex-shrink: 0; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

# ── Local module imports ───────────────────────
from auth    import render_login, render_header
from config  import INVALID_LOCAL_PART_TIER, INVALID_LOCAL_PART_HARVEST
from network import create_session
from scraper import extract_site
from sheets  import append_email_results
from ui      import render_table, render_log_box

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if 'results'       not in st.session_state: st.session_state.results       = []
if 'logs'          not in st.session_state: st.session_state.logs          = []
if 'running'       not in st.session_state: st.session_state.running       = False
if 'done'          not in st.session_state: st.session_state.done          = False
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'username'      not in st.session_state: st.session_state.username      = ""
if 'display_name'  not in st.session_state: st.session_state.display_name  = ""
if 'login_time'    not in st.session_state: st.session_state.login_time    = None

# ─────────────────────────────────────────────
# AUTH GATE — stops app if not logged in
# ─────────────────────────────────────────────
if not st.session_state.authenticated:
    render_login()
    st.stop()

# ─────────────────────────────────────────────
# HEADER + SIGN OUT
# ─────────────────────────────────────────────
render_header()
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EXTRACTION MODE
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Extraction Mode</div>', unsafe_allow_html=True)

config_mode = st.radio(
    "Extraction Mode",
    options=["Tier", "Harvest"],
    horizontal=True,
    label_visibility="collapsed",
    disabled=st.session_state.running
)
HINTS = {
    "Tier":    "Strict — filters admin, hr, pr and role-based addresses",
    "Harvest": "Relaxed — allows admin, hr, pr through; filters only job/exec titles",
}
st.markdown(f'<div class="config-hint">{HINTS[config_mode]}</div>', unsafe_allow_html=True)

active_invalid_words = (
    INVALID_LOCAL_PART_TIER if config_mode == "Tier" else INVALID_LOCAL_PART_HARVEST
)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# URL INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Target URLs</div>', unsafe_allow_html=True)

url_input = st.text_area(
    "Enter URLs",
    placeholder="https://example.com\nhttps://another-site.com",
    height=120,
    label_visibility="collapsed",
    disabled=st.session_state.running
)

col1, col2 = st.columns([5, 1])
with col1:
    extract_btn = st.button("Run Extraction", type="primary",
                            use_container_width=True, disabled=st.session_state.running)
with col2:
    clear_btn = st.button("Clear", use_container_width=True,
                          disabled=st.session_state.running)

if clear_btn:
    st.session_state.results = []
    st.session_state.logs    = []
    st.session_state.done    = False
    st.rerun()

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# EXTRACTION
# ─────────────────────────────────────────────
if extract_btn:
    urls = [u.strip() for u in url_input.strip().splitlines() if u.strip()]
    if not urls:
        st.warning("Enter at least one URL to proceed.")
    else:
        st.session_state.results = []
        st.session_state.logs    = []
        st.session_state.running = True
        st.session_state.done    = False

        session = create_session()
        logs    = []

        st.markdown(
            '<div class="status-running"><div class="pulse"></div>Extraction in progress...</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="section-label">Live Log</div>', unsafe_allow_html=True)
        log_placeholder  = st.empty()
        result_placeholder = st.empty()
        all_results      = []

        def log_fn(msg):
            logs.append(msg)
            st.session_state.logs = logs

        def yield_fn():
            render_log_box(logs, log_placeholder)

        for i, url in enumerate(urls):
            url = url.strip()
            if not url:
                continue
            log_fn(f"{'─'*48}")
            log_fn(f"[{i+1}/{len(urls)}] {url}")
            yield_fn()

            try:
                rows = extract_site(url, session, log_fn, yield_fn, active_invalid_words)
                all_results.extend(rows)
            except Exception as e:
                log_fn(f"  [ERROR] {e}")
                yield_fn()
                all_results.append({
                    'url': url, 'email': '', 'status': 'Blocked',
                    'location': url, 'navigation': 'Home', 'domain_filter': '-'
                })

            with result_placeholder.container():
                if all_results:
                    st.markdown('<div class="results-heading">Results &mdash; live preview</div>',
                                unsafe_allow_html=True)
                    render_table(all_results)

        log_fn(f"{'─'*48}")
        log_fn(f"Complete. {len([r for r in all_results if r['email']])} email(s) collected.")
        yield_fn()

        # Silent background logging — invisible to user
        threading.Thread(
            target=append_email_results,
            args=(all_results, st.session_state.username,
                  st.session_state.display_name, config_mode),
            daemon=True
        ).start()

        st.session_state.results = all_results
        st.session_state.running = False
        st.session_state.done    = True
        st.rerun()

# ─────────────────────────────────────────────
# RESULTS (after page rerun)
# ─────────────────────────────────────────────
if st.session_state.done and st.session_state.results:
    if st.session_state.logs:
        with st.expander("View extraction log"):
            render_log_box(st.session_state.logs)

    st.markdown('<div class="results-heading">Extraction Results</div>', unsafe_allow_html=True)
    render_table(st.session_state.results)
