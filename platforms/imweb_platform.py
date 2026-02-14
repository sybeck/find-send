"""
Imweb Platform Implementation
아임웹 플랫폼 구현
"""
import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

from platforms.base_platform import BasePlatform
from utils.url_utils import ensure_scheme, strip_query_fragment, extract_query_param


class ImwebPlatform(BasePlatform):
    """
    아임웹 플랫폼
    
    지원 패턴:
    - /Product/?idx={id}
    """
    
    @property
    def name(self) -> str:
        return "imweb"
    
    def detect(self, url: str) -> bool:
        """아임웹 URL 패턴 감지"""
        raw = ensure_scheme(url)
        clean = strip_query_fragment(raw)
        
        parsed_raw = urlparse(raw)
        path = parsed_raw.path or ""
        query = parsed_raw.query or ""
        
        # /Product/?idx={id}
        if path.rstrip("/").lower().endswith("/product"):
            if re.search(r"(?:^|&)idx=\d+(?:&|$)", query, re.IGNORECASE):
                return True
        
        return False
    
    def get_scan_template(self, url: str) -> str:
        """아임웹 스캔 템플릿"""
        base_url = self._extract_base_url(url)
        return f"{base_url}/Product/?idx={{id}}"
    
    def extract_product_id(self, url: str) -> Optional[int]:
        """URL에서 제품 ID (idx) 추출"""
        idx = extract_query_param(url, "idx")
        if idx and idx.isdigit():
            return int(idx)
        return None
