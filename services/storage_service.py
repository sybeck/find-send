"""
Storage Service
스캔 결과를 파일에 저장하고 불러오는 서비스
"""
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional

from config import settings
from utils.url_utils import extract_domain_from_url


class StorageService:
    """
    파일 저장/로드 서비스
    
    파일 형식: {domain}_{timestamp}.txt
    각 라인: 제품명 | 제품URL
    """
    
    def __init__(self, data_dir: Path = settings.DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, base_url: str) -> str:
        """파일명 생성: {domain}_{timestamp}.txt"""
        domain = extract_domain_from_url(base_url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{domain}_{timestamp}.txt"
    
    def _find_existing_file(self, base_url: str) -> Optional[Path]:
        """
        같은 도메인의 기존 파일 찾기
        가장 최근 파일을 반환
        """
        domain = extract_domain_from_url(base_url)
        pattern = f"{domain}_*.txt"
        
        matching_files = sorted(
            self.data_dir.glob(pattern),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        return matching_files[0] if matching_files else None
    
    def load_existing_results(self, base_url: str) -> Tuple[List[Tuple[str, str]], set]:
        """
        기존 스캔 결과 로드 (도메인 기반)
        
        같은 도메인의 가장 최근 파일을 찾아 로드합니다.
        예: brainology.kr 도메인의 모든 URL은 같은 파일을 공유
        
        Returns:
            Tuple[List[Tuple[str, str]], set]: (제품 리스트, URL 세트)
        """
        existing_file = self._find_existing_file(base_url)
        
        if not existing_file or not existing_file.exists():
            domain = extract_domain_from_url(base_url)
            print(f"[STORAGE] '{domain}' 도메인의 기존 파일이 없습니다. 새로 스캔을 시작합니다.")
            return [], set()
        
        products = []
        urls = set()
        domain = extract_domain_from_url(base_url)
        
        try:
            with open(existing_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # "제품명 | URL" 형식으로 파싱
                    if ' | ' in line:
                        parts = line.split(' | ', 1)
                        if len(parts) == 2:
                            name, url = parts
                            products.append((name.strip(), url.strip()))
                            urls.add(url.strip())
            
            print(f"[STORAGE] ✅ '{domain}' 도메인의 기존 파일 발견!")
            print(f"[STORAGE] 파일명: {existing_file.name}")
            print(f"[STORAGE] 로드된 제품 수: {len(products)}개")
            return products, urls
        
        except Exception as e:
            print(f"[STORAGE] 파일 로드 중 오류: {e}")
            return [], set()
    
    def save_results(
        self, 
        base_url: str, 
        products: List[Tuple[str, str]], 
        append: bool = False
    ) -> Path:
        """
        스캔 결과 저장
        
        Args:
            base_url: 베이스 URL
            products: [(제품명, URL), ...] 리스트
            append: True면 기존 파일에 추가, False면 새 파일 생성
            
        Returns:
            Path: 저장된 파일 경로
        """
        if append:
            filepath = self._find_existing_file(base_url)
            if not filepath:
                filepath = self.data_dir / self._generate_filename(base_url)
            mode = 'a'
        else:
            filepath = self.data_dir / self._generate_filename(base_url)
            mode = 'w'
        
        try:
            with open(filepath, mode, encoding='utf-8') as f:
                # 새 파일이면 헤더 추가
                if mode == 'w':
                    f.write(f"# Product Scan Results\n")
                    f.write(f"# Base URL: {base_url}\n")
                    f.write(f"# Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"# Format: ProductName | ProductURL\n")
                    f.write(f"#\n")
                
                # 제품 데이터 저장
                for name, url in products:
                    f.write(f"{name} | {url}\n")
            
            print(f"[STORAGE] {len(products)}개 제품 저장 완료: {filepath.name}")
            return filepath
        
        except Exception as e:
            print(f"[STORAGE] 파일 저장 중 오류: {e}")
            raise
    
    def append_product(self, base_url: str, product_name: str, product_url: str):
        """
        단일 제품을 기존 파일에 추가
        실시간 저장용
        """
        self.save_results(base_url, [(product_name, product_url)], append=True)
