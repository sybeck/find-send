"""
Scanner Service
제품 페이지 스캔 서비스
"""
import time
import requests
from typing import List, Tuple, Optional, Set

from config import settings
from utils.html_parser import extract_product_name, looks_not_found
from services.slack_service import SlackService
from services.storage_service import StorageService


class ScannerService:
    """
    제품 페이지 스캔 서비스
    
    주요 기능:
    - ID 증가 방식으로 제품 페이지 탐색
    - 실시간 파일 저장
    - Slack 진행 상황 알림
    """
    
    # Configuration from settings
    SLEEP_SECONDS = settings.SLEEP_SECONDS
    CONSECUTIVE_MISSES_THRESHOLD = settings.CONSECUTIVE_MISSES_THRESHOLD
    CONSECUTIVE_HITS_THRESHOLD = settings.CONSECUTIVE_HITS_THRESHOLD
    REQUEST_TIMEOUT_SECONDS = settings.REQUEST_TIMEOUT_SECONDS
    NOT_FOUND_KEYWORDS = settings.NOT_FOUND_KEYWORDS
    USER_AGENT = settings.USER_AGENT
    
    def __init__(
        self,
        slack_service: Optional[SlackService] = None,
        storage_service: Optional[StorageService] = None
    ):
        self.slack = slack_service or SlackService()
        self.storage = storage_service or StorageService()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
    
    def _check_url(self, url: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        URL 체크
        
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                (발견 여부, 제품명, 최종 URL)
        """
        try:
            response = self.session.get(
                url,
                allow_redirects=True,
                timeout=self.REQUEST_TIMEOUT_SECONDS
            )
            
            # Not Found 판단
            if looks_not_found(
                response.status_code,
                url,
                response.url,
                response.text or "",
                self.NOT_FOUND_KEYWORDS
            ):
                return False, None, None
            
            # 제품 발견
            final_url = response.url
            product_name = extract_product_name(response.text or "")
            
            return True, product_name, final_url
        
        except requests.RequestException as e:
            print(f"  -> ERROR: {e}")
            return False, None, None
    
    def scan_pass(
        self,
        template_url: str,
        base_url: str,
        start_id: int,
        found_products: List[Tuple[str, str]],
        found_urls: Set[str],
        allow_extra_retry: bool = False,
        progress_interval: int = 50
    ) -> Tuple[List[Tuple[str, str]], Set[str]]:
        """
        한 번의 스캔 패스
        
        Args:
            template_url: {id}를 포함한 템플릿 URL
            base_url: 베이스 URL (저장용)
            start_id: 시작 ID
            found_products: 기존 발견 제품 리스트
            found_urls: 기존 발견 URL 세트
            allow_extra_retry: 아무것도 못 찾았을 때 추가 재시도 허용
            progress_interval: 진행 상황 알림 간격
            
        Returns:
            Tuple[List[Tuple[str, str]], Set[str]]: (제품 리스트, URL 세트)
        """
        product_id = start_id
        consecutive_misses = 0
        consecutive_hits = 0
        extra_retry_used = False
        
        initial_count = len(found_products)
        
        while True:
            url = template_url.format(id=product_id)
            print(f"[CHECK #{product_id}] {url}")
            
            # URL 체크
            is_found, product_name, final_url = self._check_url(url)
            
            if not is_found:
                # Not Found
                consecutive_misses += 1
                consecutive_hits = 0
                print(f"  -> NOT FOUND ({consecutive_misses}/{self.CONSECUTIVE_MISSES_THRESHOLD})")
            
            else:
                # Found
                consecutive_misses = 0
                consecutive_hits += 1
                
                # 중복 체크 및 저장
                if final_url not in found_urls:
                    found_products.append((product_name, final_url))
                    found_urls.add(final_url)
                    
                    # 실시간 파일 저장
                    try:
                        self.storage.append_product(base_url, product_name, final_url)
                    except Exception as e:
                        print(f"[STORAGE ERROR] {e}")
                    
                    # Slack 알림
                    self.slack.notify_product_found(product_name, final_url)
                    
                    print(f"  ✅ FOUND: {product_name}")
                    print(f"     URL: {final_url}")
                else:
                    print(f"  ✅ FOUND (중복): {product_name}")
                
                print(f"     (연속 Hit: {consecutive_hits}/{self.CONSECUTIVE_HITS_THRESHOLD})")
                
                # 비정상 감지: 너무 많은 연속 Hit
                if consecutive_hits >= self.CONSECUTIVE_HITS_THRESHOLD:
                    error_msg = (
                        f"비정상 감지: 연속 {self.CONSECUTIVE_HITS_THRESHOLD}개가 'FOUND'로 판정되었습니다. "
                        f"NOT FOUND 판정 로직을 확인해주세요."
                    )
                    self.slack.notify_error(error_msg)
                    raise RuntimeError(error_msg)
            
            # 중단 조건 체크
            if consecutive_misses >= self.CONSECUTIVE_MISSES_THRESHOLD:
                # 추가 재시도 조건
                if allow_extra_retry and len(found_products) == initial_count and not extra_retry_used:
                    msg = f"[INFO] 제품을 찾지 못해 추가 {self.CONSECUTIVE_MISSES_THRESHOLD}회 스캔을 진행합니다."
                    print(f"\n{msg}\n")
                    self.slack.notify_step(msg)
                    consecutive_misses = 0
                    extra_retry_used = True
                else:
                    break
            
            # 진행 상황 주기적 알림
            if product_id % progress_interval == 0:
                self.slack.notify_progress(product_id, len(found_products))
            
            product_id += 1
            time.sleep(self.SLEEP_SECONDS)
        
        return found_products, found_urls
    
    def scan(
        self,
        template_url: str,
        base_url: str,
        input_product_id: int,
        skip_if_exists: bool = True
    ) -> List[Tuple[str, str]]:
        """
        전체 스캔 프로세스
        
        1. 기존 저장 파일 확인 및 로드
        2. 기존 파일이 있고 skip_if_exists=True면 스캔 스킵하고 기존 데이터 반환
        3. 1차 스캔 (start=1)
        4. 조건부 2차 스캔 (start=입력 제품 ID)
        
        Args:
            template_url: {id}를 포함한 템플릿 URL
            base_url: 베이스 URL
            input_product_id: 입력받은 제품 ID
            skip_if_exists: True면 기존 파일이 있을 때 스캔 스킵
            
        Returns:
            List[Tuple[str, str]]: [(제품명, URL), ...] 리스트
        """
        # 기존 결과 로드
        self.slack.notify_step("📂 기존 스캔 결과 확인 중...")
        found_products, found_urls = self.storage.load_existing_results(base_url)
        
        if found_products:
            if skip_if_exists:
                # 기존 파일이 있으면 스캔 스킵
                msg = (
                    f"✅ 기존 스캔 결과 발견!\n"
                    f"• 도메인: {base_url}\n"
                    f"• 저장된 제품 수: {len(found_products)}개\n"
                    f"• 새로운 스캔을 하지 않고 저장된 데이터를 사용합니다."
                )
                print(f"\n[INFO] {msg}\n")
                self.slack.notify_step(msg)
                
                # 저장된 데이터 반환 (스캔 스킵)
                return found_products
            else:
                msg = f"기존 파일에서 {len(found_products)}개 제품을 불러왔습니다. 이어서 스캔합니다."
                print(f"\n[INFO] {msg}\n")
                self.slack.notify_step(msg)
        
        # 1차 스캔
        self.slack.notify_step("🔍 1차 스캔 시작 (ID=1부터)")
        print(f"\n{'='*60}")
        print("[1차 스캔] start=1")
        print(f"{'='*60}\n")
        
        found_products, found_urls = self.scan_pass(
            template_url=template_url,
            base_url=base_url,
            start_id=1,
            found_products=found_products,
            found_urls=found_urls,
            allow_extra_retry=True
        )
        
        # 2차 스캔 조건 체크
        threshold = input_product_id * 0.01
        
        if len(found_products) < threshold:
            msg = (
                f"🔄 2차 스캔 시작\n"
                f"• 발견 개수({len(found_products)}) < 입력 ID × 0.01 ({threshold:.2f})\n"
                f"• ID={input_product_id}부터 스캔"
            )
            print(f"\n{'='*60}")
            print(f"[2차 스캔 트리거]")
            print(f"발견: {len(found_products)}, 임계값: {threshold:.2f}")
            print(f"start={input_product_id}부터 스캔 시작")
            print(f"{'='*60}\n")
            self.slack.notify_step(msg)
            
            found_products, found_urls = self.scan_pass(
                template_url=template_url,
                base_url=base_url,
                start_id=input_product_id,
                found_products=found_products,
                found_urls=found_urls,
                allow_extra_retry=False
            )
        else:
            msg = "✓ 2차 스캔 조건 미충족 (스킵)"
            print(f"\n[INFO] {msg}\n")
            self.slack.notify_step(msg)
        
        return found_products
