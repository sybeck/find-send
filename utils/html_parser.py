"""
HTML Parser Utility
HTML 파싱 및 제품명 추출 유틸리티
"""
import re
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """텍스트 정리: 연속 공백 제거 및 trim"""
    return re.sub(r"\s+", " ", text).strip()


def extract_product_name(html: str) -> str:
    """
    HTML에서 제품명 추출 (업그레이드된 버전)
    
    우선순위:
    1. og:title 메타 태그
    2. product_name 클래스/id
    3. h1 태그 (제품 상세 페이지에서 주로 사용)
    4. title 태그 (마지막 수단)
    """
    if not html:
        return "(제품명 추출 실패)"
    
    try:
        soup = BeautifulSoup(html, 'lxml')
        
        # 1. og:title 메타 태그 (가장 신뢰도 높음)
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = clean_text(og_title["content"])
            if title and len(title) > 0:
                return title
        
        # 2. 제품명 관련 클래스/ID 찾기
        product_name_selectors = [
            # 카페24 일반적인 패턴
            ".product_name",
            "#product_name",
            ".prod_name",
            ".prdName",
            ".product-name",
            ".product_title",
            ".productName",
            # 아임웹 일반적인 패턴
            ".product-title",
            ".prod-title",
            # 일반적인 패턴
            "[itemprop='name']",
            ".detail_product_name",
            ".product-detail-title",
        ]
        
        for selector in product_name_selectors:
            try:
                element = soup.select_one(selector)
                if element:
                    title = clean_text(element.get_text())
                    if title and len(title) > 0:
                        return title
            except:
                continue
        
        # 3. h1 태그 찾기 (제품 페이지에서 주로 제품명이 h1)
        h1_tags = soup.find_all("h1")
        for h1 in h1_tags:
            title = clean_text(h1.get_text())
            # h1이 너무 짧거나 너무 길지 않은지 확인
            if title and 2 <= len(title) <= 200:
                return title
        
        # 4. title 태그 (마지막 수단)
        title_tag = soup.find("title")
        if title_tag:
            title = clean_text(title_tag.get_text())
            # title에서 사이트명 제거 시도 (일반적으로 " | ", " - " 등으로 구분됨)
            for sep in [" | ", " - ", " :: ", " > "]:
                if sep in title:
                    parts = title.split(sep)
                    # 가장 긴 부분을 제품명으로 간주
                    title = max(parts, key=len).strip()
                    break
            
            if title and len(title) > 0:
                return title
        
        return "(제품명 추출 실패)"
    
    except Exception as e:
        return f"(제품명 추출 오류: {str(e)})"


def looks_not_found(status_code: int, requested_url: str, final_url: str, html: str, not_found_keywords: list[str]) -> bool:
    """
    페이지가 404/Not Found 상태인지 판단
    
    Args:
        status_code: HTTP 상태 코드
        requested_url: 요청한 URL
        final_url: 리다이렉트 후 최종 URL
        html: HTML 내용
        not_found_keywords: Not Found 판단 키워드 리스트
    """
    from utils.url_utils import normalize_for_compare, is_homepage
    
    # HTTP 상태 코드가 200이 아니면 Not Found
    if status_code != 200:
        return True
    
    # 없는 상품이면 홈/인덱스로 리다이렉트되는 케이스
    req = normalize_for_compare(requested_url)
    fin = normalize_for_compare(final_url)
    if req != fin and is_homepage(final_url):
        return True
    
    # HTML 내용에서 Not Found 키워드 검색
    sample = (html[:20000] or "").lower()
    for kw in not_found_keywords:
        if kw in sample:
            return True
    
    # HTML이 너무 짧으면 Not Found로 간주
    if len(sample.strip()) < 200:
        return True
    
    return False
