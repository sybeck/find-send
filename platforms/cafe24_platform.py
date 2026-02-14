"""
Cafe24 Platform Implementation
카페24 플랫폼 구현
"""
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

from platforms.base_platform import BasePlatform
from utils.url_utils import ensure_scheme, strip_query_fragment


class Cafe24Platform(BasePlatform):
    """
    카페24 플랫폼
    
    지원 패턴:
    - /surl/p/{id}
    - /product/.../{{id}}/category/...
    - /product/detail.html?product_no={id}
    
    중요: 모든 카페24 URL은 스캔 시 /surl/p/{id} 패턴을 사용
    """
    
    @property
    def name(self) -> str:
        return "cafe24"
    
    def detect(self, url: str) -> bool:
        """카페24 URL 패턴 감지"""
        raw = ensure_scheme(url)
        clean = strip_query_fragment(raw)
        
        parsed_clean = urlparse(clean)
        parsed_raw = urlparse(raw)
        
        path = parsed_clean.path or ""
        query = parsed_raw.query or ""
        
        # 패턴 A: /surl/p/{id}
        if "/surl/p/" in path and re.search(r"/surl/p/\d+", path):
            return True
        
        # 패턴 B: /product/.../{{id}}/category/...
        if path.startswith("/product/") and re.search(r"/product/.+/\d+/category/", path):
            return True
        
        # 패턴 C: /product/detail.html?product_no={id}
        if path.rstrip("/").lower().endswith("/product/detail.html"):
            if re.search(r"(?:^|&)product_no=\d+(?:&|$)", query, re.IGNORECASE):
                return True
        
        return False
    
    def get_scan_template(self, url: str) -> str:
        """카페24는 항상 /surl/p/{id} 패턴으로 스캔"""
        base_url = self._extract_base_url(url)
        return f"{base_url}/surl/p/{{id}}"
    
    def extract_product_id(self, url: str) -> Optional[int]:
        """URL에서 제품 ID 추출"""
        raw = ensure_scheme(url)
        clean = strip_query_fragment(raw)
        
        p_clean = urlparse(clean)
        p_raw = urlparse(raw)
        
        path = p_clean.path or ""
        query = p_raw.query or ""
        
        # 패턴 A: /surl/p/{id}
        m = re.search(r"/surl/p/(\d+)", path)
        if m:
            return int(m.group(1))
        
        # 패턴 B: /product/.../{{id}}/category/...
        m = re.search(r"/product/.+/(\d+)/category/", path)
        if m:
            return int(m.group(1))
        
        # 패턴 C: /product/detail.html?product_no={id}
        if path.rstrip("/").lower().endswith("/product/detail.html"):
            qs = parse_qs(query)
            if "product_no" in qs and qs["product_no"]:
                v = qs["product_no"][0]
                if v.isdigit():
                    return int(v)
        
        return None
