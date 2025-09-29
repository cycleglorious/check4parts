import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BM_PARTS_TOKEN = os.getenv("BM_PARTS_TOKEN")
ASG_TOKEN = os.getenv("ASG_TOKEN")
OMEGA_KEY = os.getenv("OMEGA_KEY")
UNIQTRADE_EMAIL = os.getenv("UNIQTRADE_EMAIL")
UNIQTRADE_PASSWORD = os.getenv("UNIQTRADE_PASSWORD")
UNIQTRADE_FINGERPRINT = os.getenv("UNIQTRADE_FINGERPRINT")
