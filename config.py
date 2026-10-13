import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://dcore-dashboard.onrender.com")
