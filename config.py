import os
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY")

# Fail-fast: Báo lỗi ngay lúc khởi động server nếu thiếu key quan trọng
if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Cảnh báo: Thiếu TELEGRAM_BOT_TOKEN hoặc OPENAI_API_KEY trong file .env!")