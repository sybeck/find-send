"""
Slack Service
Slack 웹훅 수신 및 메시지 전송 서비스
"""
import json
import requests
from typing import Optional

from config import settings


class SlackService:
    """
    Slack 통신 서비스
    
    - 웹훅을 통한 메시지 수신
    - 스레드를 통한 진행 상황 알림
    """
    
    # Slack 웹훅 URL
    WEBHOOK_URL = settings.SLACK_WEBHOOK_URL
    
    # Slack Bot Token (스레드 메시지용)
    BOT_TOKEN = settings.SLACK_BOT_TOKEN
    
    def __init__(self):
        self.current_thread_ts: Optional[str] = None
        self.current_channel: Optional[str] = None
    
    def set_thread_context(self, channel: str, thread_ts: str):
        """
        스레드 컨텍스트 설정
        모든 후속 메시지는 이 스레드에 전송됨
        
        Args:
            channel: Slack 채널 ID
            thread_ts: 스레드 타임스탬프 (부모 메시지의 ts)
        """
        self.current_channel = channel
        self.current_thread_ts = thread_ts
        print(f"[SLACK] 스레드 컨텍스트 설정: channel={channel}, thread_ts={thread_ts}")
    
    def send_message(self, text: str, thread: bool = True) -> bool:
        """
        Slack 메시지 전송
        
        Args:
            text: 전송할 메시지
            thread: True면 스레드로 전송, False면 새 메시지로 전송
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.BOT_TOKEN or not self.current_channel:
            print(f"[SLACK] Bot token 또는 채널이 설정되지 않음. 메시지 출력만 함: {text}")
            return False
        
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": self.current_channel,
            "text": text
        }
        
        # 스레드로 전송할 경우
        if thread and self.current_thread_ts:
            payload["thread_ts"] = self.current_thread_ts
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            result = response.json()
            
            if result.get("ok"):
                print(f"[SLACK] 메시지 전송 성공")
                return True
            else:
                print(f"[SLACK] 메시지 전송 실패: {result.get('error', 'Unknown error')}")
                return False
        
        except Exception as e:
            print(f"[SLACK] 메시지 전송 중 오류: {e}")
            return False
    
    def send_webhook_message(self, text: str) -> bool:
        """
        Webhook을 통한 메시지 전송 (스레드 없음)
        
        Args:
            text: 전송할 메시지
            
        Returns:
            bool: 전송 성공 여부
        """
        if not self.WEBHOOK_URL:
            print(f"[SLACK] Webhook URL이 설정되지 않음. 메시지 출력만 함: {text}")
            return False
        
        payload = {"text": text}
        
        try:
            response = requests.post(
                self.WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[SLACK] Webhook 메시지 전송 성공")
                return True
            else:
                print(f"[SLACK] Webhook 메시지 전송 실패: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"[SLACK] Webhook 메시지 전송 중 오류: {e}")
            return False
    
    def notify_start(self, url: str, platform_name: str):
        """스캔 시작 알림"""
        msg = f"🚀 *제품 스캔 시작*\n• URL: {url}\n• 플랫폼: {platform_name}"
        print(f"\n{msg}\n")
        self.send_message(msg)
    
    def notify_progress(self, current_id: int, found_count: int):
        """진행 상황 알림 (주기적으로 호출)"""
        msg = f"⏳ 스캔 중... (현재 ID: {current_id}, 발견: {found_count}개)"
        print(msg)
        # 너무 자주 보내지 않도록 필요시 조절
        # self.send_message(msg)
    
    def notify_product_found(self, product_name: str, product_url: str):
        """제품 발견 알림"""
        msg = f"✅ *제품 발견*\n• 이름: {product_name}\n• URL: {product_url}"
        print(msg)
        self.send_message(msg)
    
    def notify_scan_complete(self, total_found: int, file_path: str):
        """스캔 완료 알림"""
        msg = f"✨ *스캔 완료*\n• 총 발견: {total_found}개\n• 저장 파일: {file_path}"
        print(f"\n{msg}\n")
        self.send_message(msg)
    
    def notify_error(self, error_message: str):
        """에러 알림"""
        msg = f"❌ *오류 발생*\n{error_message}"
        print(f"\n{msg}\n")
        self.send_message(msg)
    
    def notify_step(self, step: str):
        """단계별 진행 알림"""
        msg = f"📍 {step}"
        print(msg)
        self.send_message(msg)
