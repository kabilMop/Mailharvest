# ─────────────────────────────────────────────
# sheets.py — Google Sheets integration
# All sheet writes happen silently in background
# ─────────────────────────────────────────────

import threading
from datetime import datetime, timezone, timedelta

# Indian Standard Time (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

import streamlit as st

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except Exception:
    GSPREAD_AVAILABLE = False

from config import (
    SHEET_URL, GSHEET_SCOPES,
    EMAILS_SHEET, ACTIVITY_SHEET, SUMMARY_SHEET,
    EMAILS_HEADERS, ACTIVITY_HEADERS, SUMMARY_HEADERS,
)

_sheet_lock = threading.Lock()


def _get_workbook():
    """Connect to Google Sheets workbook."""
    try:
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=GSHEET_SCOPES)
    except Exception:
        creds = Credentials.from_service_account_file(
            "service_account.json", scopes=GSHEET_SCOPES)
    return gspread.authorize(creds).open_by_url(SHEET_URL)


def _get_or_create_sheet(wb, title, headers):
    """Get sheet tab by name, create it with headers if it doesn't exist."""
    try:
        ws = wb.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = wb.add_worksheet(title=title, rows=1000, cols=len(headers))
        ws.append_row(headers, value_input_option="RAW")
    if not ws.row_values(1):
        ws.append_row(headers, value_input_option="RAW")
    return ws


def log_activity(username, display_name, event, details=""):
    """
    Write one row to the Activity Log sheet.
    Called on: LOGIN, LOGOUT, LOGIN FAILED, EXTRACTION
    """
    if not GSPREAD_AVAILABLE:
        return
    now = datetime.now(IST)
    try:
        with _sheet_lock:
            wb = _get_workbook()
            ws = _get_or_create_sheet(wb, ACTIVITY_SHEET, ACTIVITY_HEADERS)
            ws.append_row(
                [now.strftime("%d-%m-%Y"), now.strftime("%I:%M:%S %p"),
                 username, display_name, event, details],
                value_input_option="RAW"
            )
    except Exception:
        pass


def update_user_summary(username, display_name, emails_found=0, extraction_done=False):
    """
    Update the User Summary sheet.
    One row per user — updates totals in place.
    """
    if not GSPREAD_AVAILABLE:
        return
    today = datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")
    try:
        with _sheet_lock:
            wb       = _get_workbook()
            ws       = _get_or_create_sheet(wb, SUMMARY_SHEET, SUMMARY_HEADERS)
            all_vals = ws.get_all_values()

            user_row_idx = None
            for i, row in enumerate(all_vals[1:], start=2):
                if row and row[0].lower() == username.lower():
                    user_row_idx = i
                    break

            if user_row_idx:
                row = all_vals[user_row_idx - 1]
                total_logins      = int(row[2]) if len(row) > 2 and row[2].isdigit() else 0
                total_extractions = int(row[4]) if len(row) > 4 and row[4].isdigit() else 0
                total_emails      = int(row[5]) if len(row) > 5 and row[5].isdigit() else 0
                total_logins      += 1
                total_extractions += 1 if extraction_done else 0
                total_emails      += emails_found
                ws.update(f"A{user_row_idx}:F{user_row_idx}", [[
                    username, display_name, total_logins,
                    today, total_extractions, total_emails
                ]])
            else:
                ws.append_row([
                    username, display_name, 1, today,
                    1 if extraction_done else 0,
                    emails_found
                ], value_input_option="RAW")
    except Exception:
        pass


def append_email_results(results, username, display_name, mode=""):
    """
    Write extracted emails to Email Results sheet.
    Also logs the extraction event and updates user summary.
    Runs completely silently — user never sees this.
    """
    if not GSPREAD_AVAILABLE:
        return

    now      = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%I:%M:%S %p")

    email_rows  = [r for r in results if r.get("email")]
    email_count = len(email_rows)

    # 1. Write emails to Email Results sheet
    if email_rows:
        rows = [
            [date_str, time_str, username, display_name,
             r["url"], r["email"], r["status"],
             r["location"], r["navigation"], r["domain_filter"]]
            for r in email_rows
        ]
        try:
            with _sheet_lock:
                wb = _get_workbook()
                ws = _get_or_create_sheet(wb, EMAILS_SHEET, EMAILS_HEADERS)
                ws.append_rows(rows, value_input_option="RAW")
        except Exception:
            pass

    # 2. Log extraction event to Activity Log
    urls_tried = len(set(r["url"] for r in results))
    log_activity(
        username, display_name, "EXTRACTION",
        f"URLs: {urls_tried} | Emails Found: {email_count} | Mode: {mode}"
    )

    # 3. Update User Summary totals
    update_user_summary(
        username, display_name,
        emails_found=email_count,
        extraction_done=True
    )
