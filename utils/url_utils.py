"""
URL Utility Functions
URL 처리 관련 유틸리티 함수들
"""
import re
from urllib.parse import urlparse, urlunparse, parse_qs


def ensure_scheme(url: str) -> str:
    """URL에 스킴이 없으면 https:// 추가"""
    url = url.strip()
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return "https://" + url
    return url


def normalize_home(url: str) -> str:
    """URL을 홈페이지 주소로 정규화 (경로, 쿼리, 프래그먼트 제거)"""
    u = ensure_scheme(url)
    p = urlparse(u)
    return urlunparse((p.scheme, p.netloc, "", "", "", ""))


def strip_query_fragment(url: str) -> str:
    """쿼리 스트링과 프래그먼트를 제거하여 깨끗한 경로만 반환"""
    u = ensure_scheme(url)
    p = urlparse(u)
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))


def is_homepage(url: str) -> bool:
    """
    URL이 홈페이지/인덱스 페이지인지 판단
    '없는 상품 → 홈으로 리다이렉트'를 감지하기 위해 사용
    """
    p = urlparse(ensure_scheme(url))
    path = (p.path or "").lower().strip()

    # 기본 홈 경로
    if path in ["", "/"]:
        return True

    # 흔한 홈/인덱스 경로들
    home_like_paths = {
        "/index.html", "/index.htm", "/index.php", "/index.asp", "/index.aspx",
        "/default.asp", "/default.aspx",
        "/main", "/main/", "/main/index.html", "/main/index.htm", "/main/index.php",
    }
    if path in home_like_paths:
        return True

    return False


def normalize_for_compare(url: str) -> str:
    """
    URL 비교용 정규화
    - 쿼리/프래그먼트 제거
    - 호스트/스킴 소문자 변환
    - trailing slash 제거
    """
    p = urlparse(ensure_scheme(url))
    path = (p.path or "").rstrip("/")
    return f"{p.scheme.lower()}://{p.netloc.lower()}{path}"


def extract_domain_from_url(url: str) -> str:
    """URL에서 도메인만 추출 (파일명 생성용)"""
    p = urlparse(ensure_scheme(url))
    domain = p.netloc.replace("www.", "").replace(":", "_").replace("/", "_")
    return domain


def extract_query_param(url: str, param_name: str) -> str | None:
    """URL에서 특정 쿼리 파라미터 값을 추출"""
    p = urlparse(ensure_scheme(url))
    qs = parse_qs(p.query)
    if param_name in qs and qs[param_name]:
        return qs[param_name][0]
    return None
