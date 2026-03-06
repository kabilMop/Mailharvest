# ─────────────────────────────────────────────
# auth.py — Login / logout / user checking
# ─────────────────────────────────────────────

import threading
from datetime import datetime

import streamlit as st

from config import USERS
from sheets import log_activity, update_user_summary


def check_login(username: str, password: str):
    """Returns display name if credentials are valid, else None."""
    u = USERS.get(username.strip().lower())
    if u and u[1] == password:
        return u[0]
    return None


def render_login():
    """Renders the login screen. Stops app if not authenticated."""
    st.markdown("""
    <div style="max-width:380px;margin:8vh auto 0;padding:2.5rem 2rem;
         background:var(--surface);border:1px solid var(--border);border-radius:10px;">
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:1.5rem;
           letter-spacing:-0.03em;margin-bottom:0.2rem;">
           Mailharvest<span style="color:var(--text-muted);font-weight:400;">.</span></div>
      <div style="font-family:'DM Sans',sans-serif;font-size:0.78rem;color:var(--text-muted);
           letter-spacing:0.06em;text-transform:uppercase;margin-bottom:1.5rem;">
           Sign in to continue</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username  = st.text_input("Username", placeholder="your username")
        password  = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                display_name = check_login(username, password)
                if display_name:
                    uname = username.strip().lower()
                    st.session_state["authenticated"] = True
                    st.session_state["username"]      = uname
                    st.session_state["display_name"]  = display_name
                    st.session_state["login_time"]    = datetime.now()
                    # Log login event silently in background
                    threading.Thread(
                        target=log_activity,
                        args=(uname, display_name, "LOGIN", "Successful login"),
                        daemon=True
                    ).start()
                    threading.Thread(
                        target=update_user_summary,
                        args=(uname, display_name),
                        daemon=True
                    ).start()
                    st.rerun()
                else:
                    # Log failed attempt
                    threading.Thread(
                        target=log_activity,
                        args=(username.strip().lower(), "Unknown",
                              "LOGIN FAILED", f"Wrong password for: {username.strip()}"),
                        daemon=True
                    ).start()
                    st.error("Invalid username or password.")


def render_header():
    """Renders the top header with username and sign out button."""
    col_logo, col_user = st.columns([8, 2])
    with col_logo:
        st.markdown("""
        <div class="wordmark">Mailharvest<span>.</span></div>
        <div class="tagline">Email extraction tool &mdash; powered by requests &amp; bs4</div>
        """, unsafe_allow_html=True)
    with col_user:
        st.markdown(f"""
        <div style="text-align:right;padding-top:0.4rem;">
          <div style="font-family:'DM Mono',monospace;font-size:0.72rem;
               color:var(--text-muted);letter-spacing:0.04em;">signed in as</div>
          <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.9rem;
               color:var(--text-primary);">{st.session_state.display_name}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True):
            uname   = st.session_state.get("username", "")
            dname   = st.session_state.get("display_name", "")
            login_t = st.session_state.get("login_time")
            duration = ""
            if login_t:
                secs = int((datetime.now() - login_t).total_seconds())
                mins, secs = divmod(secs, 60)
                duration = f"Session duration: {mins}m {secs}s"
            threading.Thread(
                target=log_activity,
                args=(uname, dname, "LOGOUT", duration),
                daemon=True
            ).start()
            for k in ["authenticated","username","display_name",
                      "results","logs","running","done","login_time"]:
                st.session_state.pop(k, None)
            st.rerun()
