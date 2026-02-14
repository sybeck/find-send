"""
Configuration Settings
모든 설정 값을 관리하는 중앙 파일
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===== Base Paths =====
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")

# ===== Slack Configuration =====
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")

# ===== Scanning Configuration =====
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "1.0"))
CONSECUTIVE_MISSES_THRESHOLD = int(os.getenv("CONSECUTIVE_MISSES_THRESHOLD", "100"))
CONSECUTIVE_HITS_THRESHOLD = int(os.getenv("CONSECUTIVE_HITS_THRESHOLD", "200"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))

# ===== HTTP Configuration =====
USER_AGENT = "Mozilla/5.0 (compatible; InfluencerDMBot/1.0)"

# ===== Detection Keywords =====
NOT_FOUND_KEYWORDS = [
    "페이지를 찾을 수", "찾을 수 없습니다", "존재하지",
    "삭제된", "판매중지", "상품이 없습니다",
    "없는 상품", "not found", "404"
]

# ===== Platform Registration =====
# 새로운 플랫폼을 추가할 때 이 리스트에 클래스를 추가하세요
PLATFORMS = []  # Will be populated by platform modules

# ===== Data Directory Setup =====
DATA_DIR.mkdir(parents=True, exist_ok=True)
