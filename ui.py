# ─────────────────────────────────────────────
# ui.py — UI rendering helpers
# Table, badges, stats cards, log viewer
# ─────────────────────────────────────────────

import streamlit as st


def df_badge_html(label):
    """Coloured badge for Domain Match column."""
    styles = {
        'Exact':     ('var(--badge-exact-bg)',   'var(--badge-exact-fg)'),
        'Partial':   ('var(--badge-partial-bg)', 'var(--badge-partial-fg)'),
        'Not Match': ('var(--badge-nomatch-bg)', 'var(--badge-nomatch-fg)'),
        '-':         ('var(--badge-neutral-bg)', 'var(--badge-neutral-fg)'),
    }
    bg, fg = styles.get(label, styles['-'])
    return (f'<span style="background:{bg};color:{fg};padding:2px 10px;'
            f'border-radius:4px;font-size:0.72rem;font-weight:600;'
            f'letter-spacing:0.04em;text-transform:uppercase;">{label}</span>')


def status_dot_html(status):
    """Coloured dot + label for Status column."""
    colors = {
        'Valid':     'var(--dot-valid)',
        'Invalid':   'var(--dot-invalid)',
        'Blocked':   'var(--dot-blocked)',
        'Not Found': 'var(--dot-notfound)',
    }
    c = colors.get(status, '#aaa')
    return (f'<span style="display:inline-block;width:8px;height:8px;'
            f'border-radius:50%;background:{c};margin-right:6px;'
            f'vertical-align:middle;"></span>{status}')


def render_table(results):
    """Render the full results table with stats cards below."""
    rows_html = ""
    for r in results:
        status_cls = r['status'].lower().replace(' ', '-')
        url_td     = f'<a href="{r["url"]}" target="_blank" class="tbl-link">{r["url"]}</a>'
        loc_td     = f'<a href="{r["location"]}" target="_blank" class="tbl-link">{r["location"]}</a>'
        email_td   = (f'<span class="email-cell">{r["email"]}</span>'
                      if r['email'] else '<span class="email-empty">—</span>')
        status_td  = status_dot_html(r['status'])
        df_td      = df_badge_html(r['domain_filter'])
        nav_td     = r['navigation']

        rows_html += f"""
        <tr class="row-{status_cls}">
          <td>{url_td}</td>
          <td>{email_td}</td>
          <td>{status_td}</td>
          <td>{loc_td}</td>
          <td class="nav-cell">{nav_td}</td>
          <td>{df_td}</td>
        </tr>"""

    st.markdown(f"""
    <div class="table-wrap">
    <table class="results-table">
      <thead>
        <tr>
          <th>Source URL</th>
          <th>Email Address</th>
          <th>Status</th>
          <th>Found At</th>
          <th>Navigation Path</th>
          <th>Domain Match</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    # Stats cards
    total   = len([r for r in results if r['email']])
    valid   = sum(1 for r in results if r['status'] == 'Valid')
    invalid = sum(1 for r in results if r['status'] == 'Invalid')
    blocked = sum(1 for r in results if r['status'] == 'Blocked')
    nf      = sum(1 for r in results if r['status'] == 'Not Found')

    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{total}</div>
        <div class="stat-label">Emails Found</div>
      </div>
      <div class="stat-card stat-valid">
        <div class="stat-value">{valid}</div>
        <div class="stat-label">Valid</div>
      </div>
      <div class="stat-card stat-invalid">
        <div class="stat-value">{invalid}</div>
        <div class="stat-label">Invalid</div>
      </div>
      <div class="stat-card stat-blocked">
        <div class="stat-value">{blocked}</div>
        <div class="stat-label">Blocked</div>
      </div>
      <div class="stat-card stat-notfound">
        <div class="stat-value">{nf}</div>
        <div class="stat-label">Not Found</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_log_box(lines, placeholder=None):
    """Render the terminal-style live log box."""
    body = '\n'.join(lines[-80:])
    html = f"""
    <div class="log-container">
      <div class="log-header">
        <div class="log-dot"></div>
        <div class="log-title">extraction.log</div>
      </div>
      <div class="log-body">{body}</div>
    </div>
    """
    if placeholder:
        placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)
