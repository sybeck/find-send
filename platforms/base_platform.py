"""
Base Platform Class
모든 플랫폼이 상속받아야 하는 기본 클래스
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import re
from urllib.parse import urlparse


class BasePlatform(ABC):
    """
    플랫폼 기본 클래스
    
    새로운 플랫폼을 추가하려면:
    1. 이 클래스를 상속
    2. detect(), get_scan_template(), extract_product_id() 메서드 구현
    3. config/settings.py의 PLATFORMS 리스트에 추가
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """플랫폼 이름 (예: 'cafe24', 'imweb')"""
        pass
    
    @abstractmethod
    def detect(self, url: str) -> bool:
        """
        주어진 URL이 이 플랫폼에 속하는지 감지
        
        Args:
            url: 감지할 URL
            
        Returns:
            bool: 이 플랫폼이면 True
        """
        pass
    
    @abstractmethod
    def get_scan_template(self, url: str) -> str:
        """
        스캔에 사용할 URL 템플릿 반환
        
        Args:
            url: 원본 제품 URL
            
        Returns:
            str: {id}를 포함한 템플릿 URL (예: "https://example.com/product/{id}")
        """
        pass
    
    @abstractmethod
    def extract_product_id(self, url: str) -> Optional[int]:
        """
        URL에서 제품 ID 추출
        
        Args:
            url: 제품 URL
            
        Returns:
            Optional[int]: 추출된 제품 ID, 실패 시 None
        """
        pass
    
    def _extract_base_url(self, url: str) -> str:
        """URL에서 베이스 URL 추출 (스킴 + 호스트)"""
        from utils.url_utils import ensure_scheme
        u = ensure_scheme(url)
        p = urlparse(u)
        return f"{p.scheme}://{p.netloc}"
