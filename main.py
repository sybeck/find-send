"""
Main Entry Point
슬랙 웹훅으로부터 URL을 받아 제품 스캔을 시작하는 메인 프로그램
"""
import sys
from typing import Optional

from config import settings
from platforms.cafe24_platform import Cafe24Platform
from platforms.imweb_platform import ImwebPlatform
from platforms.base_platform import BasePlatform
from services.slack_service import SlackService
from services.scanner_service import ScannerService
from services.storage_service import StorageService
from utils.url_utils import normalize_home


# 플랫폼 등록
PLATFORMS = [
    Cafe24Platform(),
    ImwebPlatform(),
    # 새로운 플랫폼을 여기에 추가
]


def detect_platform(url: str) -> Optional[BasePlatform]:
    """
    URL에서 플랫폼 감지
    
    Args:
        url: 제품 URL
        
    Returns:
        Optional[BasePlatform]: 감지된 플랫폼, 없으면 None
    """
    for platform in PLATFORMS:
        if platform.detect(url):
            return platform
    return None


def process_product_url(
    product_url: str,
    slack_channel: Optional[str] = None,
    slack_thread_ts: Optional[str] = None
):
    """
    제품 URL 처리 메인 로직
    
    Args:
        product_url: 제품 URL
        slack_channel: Slack 채널 ID (스레드 메시지용)
        slack_thread_ts: Slack 스레드 타임스탬프 (스레드 메시지용)
    """
    # 서비스 초기화
    slack_service = SlackService()
    storage_service = StorageService()
    scanner_service = ScannerService(slack_service, storage_service)
    
    # Slack 스레드 컨텍스트 설정
    if slack_channel and slack_thread_ts:
        slack_service.set_thread_context(slack_channel, slack_thread_ts)
    
    print("="*70)
    print("🚀 인플루언서 DM 자동화 프로그램")
    print("="*70)
    print(f"\n입력 URL: {product_url}\n")
    
    try:
        # 1. 플랫폼 감지
        slack_service.notify_step("🔍 플랫폼 감지 중...")
        platform = detect_platform(product_url)
        
        if not platform:
            error_msg = f"지원하지 않는 플랫폼입니다.\n입력 URL: {product_url}"
            print(f"\n[ERROR] {error_msg}\n")
            slack_service.notify_error(error_msg)
            return
        
        print(f"[✓] 플랫폼: {platform.name}")
        
        # 2. 제품 ID 추출
        slack_service.notify_step("🔢 제품 ID 추출 중...")
        product_id = platform.extract_product_id(product_url)
        
        if product_id is None:
            error_msg = f"제품 ID를 추출할 수 없습니다.\n입력 URL: {product_url}"
            print(f"\n[ERROR] {error_msg}\n")
            slack_service.notify_error(error_msg)
            return
        
        print(f"[✓] 제품 ID: {product_id}")
        
        # 3. 스캔 템플릿 생성
        template_url = platform.get_scan_template(product_url)
        base_url = normalize_home(product_url)
        
        print(f"[✓] 스캔 템플릿: {template_url}")
        print(f"[✓] 베이스 URL: {base_url}\n")
        
        # 4. 스캔 시작 알림
        slack_service.notify_start(product_url, platform.name)
        
        # 5. 스캔 실행
        print(f"{'='*70}")
        print("제품 페이지 스캔 시작")
        print(f"{'='*70}\n")
        
        found_products = scanner_service.scan(
            template_url=template_url,
            base_url=base_url,
            input_product_id=product_id
        )
        
        # 6. 결과 출력
        print(f"\n{'='*70}")
        print("📦 스캔 결과 요약")
        print(f"{'='*70}\n")
        
        if not found_products:
            msg = "찾은 제품이 없습니다."
            print(msg)
            slack_service.notify_scan_complete(0, "없음")
            return
        
        # 제품 목록 출력
        for idx, (name, url) in enumerate(found_products, 1):
            print(f"{idx}. {name}")
            print(f"   {url}\n")
        
        print(f"총 발견 제품 수: {len(found_products)}")
        
        # 7. 최종 저장 (파일 경로 확인용)
        filepath = storage_service._find_existing_file(base_url)
        if filepath:
            slack_service.notify_scan_complete(len(found_products), filepath.name)
        
        print(f"\n{'='*70}")
        print("✨ 스캔 완료!")
        print(f"{'='*70}\n")
        
        # TODO: 4번 단계 - 인플루언서 찾기 및 DM 발송은 여기서 이어집니다
        
    except Exception as e:
        error_msg = f"스캔 중 오류 발생: {str(e)}"
        print(f"\n[ERROR] {error_msg}\n")
        slack_service.notify_error(error_msg)
        raise


def main():
    """
    메인 함수
    
    사용법:
    1. 직접 실행: python main.py
    2. Slack 웹훅: process_product_url() 함수를 호출
    """
    if len(sys.argv) > 1:
        # 커맨드 라인 인자로 URL 받기
        product_url = sys.argv[1]
    else:
        # 대화형 입력
        print("="*70)
        print("제품 URL을 입력하세요")
        print("="*70)
        print("\n지원 플랫폼:")
        print("• 카페24: /surl/p/{id}, /product/.../id}/category/..., /product/detail.html?product_no={id}")
        print("• 아임웹: /Product/?idx={id}")
        print("\n예시:")
        print("• https://brainology.kr/surl/p/10")
        print("• https://www.realcumin.kr/Product/?idx=72")
        print()
        
        product_url = input("> ").strip()
        
        if not product_url:
            print("\n[ERROR] URL을 입력해주세요.")
            return
    
    # URL 처리 (Slack 없이 로컬 실행)
    process_product_url(product_url)


if __name__ == "__main__":
    main()
