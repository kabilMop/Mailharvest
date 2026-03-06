# ─────────────────────────────────────────────
# config.py — All settings and constants
# Edit this file to change app behaviour
# ─────────────────────────────────────────────

# ── Scraper settings ──────────────────────────
REQUEST_TIMEOUT  = 18    # seconds before giving up on a page
PER_DOMAIN_DELAY = 1     # seconds between requests to same domain
MAX_DEPTH1_PAGES = 30    # max pages to scan per site

# ── Users — add/remove/change passwords here ──
# Format: "username": ("Display Name", "password")
USERS = {
    "sangeetha":    ("Sangeetha",    "sangeetha@#123"),
    "kabil":        ("Kabil",        "kabil@#123"),
    "subashree":    ("Subashree",    "subashree@#123"),
    "sakthimari":   ("Sakthi Mari",  "sakthimari@#123"),
    "mariselvi":    ("Mari Selvi",   "mariselvi@#123"),
    "rajeswari":    ("Rajeswari",    "rajeswari@#123"),
    "ajantha":      ("Ajantha",      "ajantha@#123"),
    "muthulakshmi": ("Muthu Lakshmi","muthulakshmi@#123"),
    "abitha":       ("Abitha",       "abitha@#123"),
    "kumaresan":    ("Kumaresan",     "kumaresan@#123"),
}

# ── Google Sheet ───────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1AVWugxVRbDti-PBTWF59oI_eTpbpdIOW3V0IuRcL0_s/edit?gid=0#gid=0"
GSHEET_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Sheet tab names
EMAILS_SHEET   = "Email Results"
ACTIVITY_SHEET = "Activity Log"
SUMMARY_SHEET  = "User Summary"

# Sheet column headers
EMAILS_HEADERS   = ["Date","Time","Username","Display Name","Source URL","Email","Status","Found At","Navigation","Domain Match"]
ACTIVITY_HEADERS = ["Date","Time","Username","Display Name","Event","Details"]
SUMMARY_HEADERS  = ["Username","Display Name","Total Logins","Last Seen (Date & Time)","Total Extractions","Total Emails Collected"]

# ── URL crawling ───────────────────────────────
PRIORITY_KEYWORDS = [
    "contact","contact-us","contacto","contato","kontakt","contatti",
    "nous-contacter","get-in-touch","about","about-us","company","profile",
    "corporate","who-we-are","legal","terms","privacy","privacy-policy",
    "impressum","imprint","support","help","press","media","news",
    "investor","office","offices","address","directions","map"
]
SKIP_PATH_KEYWORDS = [
    "team","our-team","staff","employees","leadership","people","person"
]

# ── Email filtering ────────────────────────────
INVALID_LOCAL_PART_TIER = [
    "admin","administrator","career","careers","ceo","chairman",
    "companysecretary","hr","humanresource","humanresources","jobs",
    "personal","president","secretary","webadministrator",
    "webmaster","wizard"
]
INVALID_LOCAL_PART_HARVEST = [
    "career","careers","ceo","chairman",
    "companysecretary","jobs",
    "personal","president","secretary","webadministrator",
    "webmaster","wizard"
]
INVALID_LOCAL_PART_WORDS = INVALID_LOCAL_PART_TIER

INVALID_DOMAINS = [
    "gmail.com","yahoo.com","ymail.com","aol.com","hotmail.com",
    "msn.com","comcast.net","rediffmail.com","163.com","126.com"
]
BLACKLISTED_EXT = {
    '.jpg','.jpeg','.png','.gif','.svg','.webp','.pdf','.doc','.docx',
    '.xls','.xlsx','.zip','.rar','.7z','.mp4','.mp3','.avi','.mkv',
    '.exe','.dmg','.iso','.apk','.csv'
}
AVOID_DOMAINS = (
    'facebook.com','fb.com','instagram.com','linkedin.com','twitter.com',
    'x.com','youtube.com','t.me','pinterest.com','threads.net',
    'snapchat.com','whatsapp.com','discord.com','reddit.com',
    'telegram.org','medium.com','google.com','googletagmanager.com',
    'google-analytics.com','doubleclick.net','bing.com','yandex.ru',
    'cloudflare.com','gravatar.com','paypal.com','shopify.com',
    'wordpress.com','blogger.com','tumblr.com','vimeo.com','tiktok.com',
    'weebly.com','wix.com','zoom.us','dropbox.com','slack.com'
)

# ── Network ────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
]
CLOUDFLARE_STRINGS = [
    "checking your browser before accessing","cf-browser-verification",
    "cf-chl-bypass","attention required! | cloudflare",
    "/cdn-cgi/l/chk_captcha","ddos protection by cloudflare",
    "please enable javascript to view the site",
    "checking if the site connection is secure",
]