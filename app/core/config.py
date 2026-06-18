import os
from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str) -> str:
    value = os.getenv(name, "")
    if isinstance(value, str):
        return value.strip().strip('"\'')
    return ""


SUPABASE_URL = _get_env("SUPABASE_URL")
SUPABASE_ANON_KEY = _get_env("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = _get_env("SUPABASE_SERVICE_ROLE_KEY")

APP_ENV = _get_env("APP_ENV") or "development"
