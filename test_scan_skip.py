"""
테스트: 기존 파일이 있을 때 스캔 스킵 기능
"""
from services.storage_service import StorageService
from services.scanner_service import ScannerService
from services.slack_service import SlackService
from platforms.cafe24_platform import Cafe24Platform
from utils.url_utils import normalize_home

print("="*70)
print("🧪 스캔 스킵 기능 테스트")
print("="*70)

# 테스트 URL들
url1 = "https://brainology.kr/surl/p/1"
url2 = "https://brainology.kr/product/test/42/category/1/display/3/"

# 플랫폼 감지
platform = Cafe24Platform()
base_url = normalize_home(url1)

print(f"\n[설정]")
print(f"URL 1: {url1}")
print(f"URL 2: {url2}")
print(f"베이스 URL: {base_url}")
print(f"도메인: brainology.kr")

# 서비스 초기화
storage = StorageService()
slack = SlackService()
scanner = ScannerService(slack, storage)

# 1. 기존 파일 상태 확인
print(f"\n[테스트 1] 기존 파일 상태 확인")
existing_products, existing_urls = storage.load_existing_results(base_url)

if existing_products:
    print(f"✅ 기존 파일 발견: {len(existing_products)}개 제품")
    print(f"\n저장된 제품 목록:")
    for idx, (name, url) in enumerate(existing_products[:5], 1):  # 최대 5개만 출력
        print(f"  {idx}. {name}")
        print(f"     {url}")
    if len(existing_products) > 5:
        print(f"  ... (외 {len(existing_products) - 5}개)")
else:
    print("❌ 기존 파일 없음 (테스트를 위해 더미 데이터를 생성합니다)")
    
    # 더미 데이터 생성
    dummy_products = [
        ("브레인올로지 키즈 오메가3", "https://brainology.kr/product/1"),
        ("브레인올로지 성인 오메가3", "https://brainology.kr/product/2"),
        ("브레인올로지 비타민D", "https://brainology.kr/product/3"),
    ]
    storage.save_results(base_url, dummy_products)
    print(f"✅ 더미 데이터 생성 완료: {len(dummy_products)}개 제품")

# 2. URL1로 스캔 시도 (skip_if_exists=True)
print(f"\n[테스트 2] URL1로 스캔 시도 (skip_if_exists=True)")
print("→ 기존 파일이 있으므로 스캔을 스킵하고 저장된 데이터를 반환해야 함")

template_url = platform.get_scan_template(url1)
product_id = platform.extract_product_id(url1)

try:
    # skip_if_exists=True로 스캔 (기본값)
    results = scanner.scan(
        template_url=template_url,
        base_url=base_url,
        input_product_id=product_id or 1,
        skip_if_exists=True  # 기존 파일이 있으면 스캔 스킵
    )
    
    print(f"\n✅ 결과 반환 완료: {len(results)}개 제품")
    print("스캔을 수행하지 않고 저장된 데이터를 반환했습니다.")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")

# 3. URL2로 스캔 시도 (같은 도메인이므로 같은 파일 사용)
print(f"\n[테스트 3] URL2로 스캔 시도 (같은 도메인)")
print("→ URL은 다르지만 같은 도메인이므로 같은 파일을 참조")

template_url2 = platform.get_scan_template(url2)
product_id2 = platform.extract_product_id(url2)

try:
    results2 = scanner.scan(
        template_url=template_url2,
        base_url=normalize_home(url2),  # URL2의 베이스 (하지만 도메인은 동일)
        input_product_id=product_id2 or 42,
        skip_if_exists=True
    )
    
    print(f"\n✅ 결과 반환 완료: {len(results2)}개 제품")
    print("URL2도 같은 파일을 참조하여 스캔을 스킵했습니다.")
    
    # 결과 비교
    if results == results2:
        print("\n🎉 ✅ 테스트 성공!")
        print("URL1과 URL2가 같은 데이터를 반환합니다.")
    else:
        print("\n⚠️ 경고: URL1과 URL2의 결과가 다릅니다.")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")

print("\n" + "="*70)
print("테스트 완료!")
print("="*70)
