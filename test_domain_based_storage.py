"""
테스트: 도메인 기반 파일 로드 및 스캔 스킵 기능
"""
from services.storage_service import StorageService
from utils.url_utils import extract_domain_from_url, normalize_home

# 테스트 URL들 (같은 도메인)
url1 = "https://brainology.kr/surl/p/1"
url2 = "https://brainology.kr/product/%EB%B8%8C%EB%A0%88%EC%9D%B8%EC%98%A4%EB%A1%9C%EC%A7%80-%ED%82%A4%EC%A6%88-%EC%98%A4%EB%A9%94%EA%B0%803-%EC%B8%84%EC%96%B4%EB%B8%94-980-30%EC%9D%BC%EB%B6%84/42/category/1/display/3/"

print("="*70)
print("🧪 도메인 기반 파일 로드 테스트")
print("="*70)

# 1. 도메인 추출 테스트
print("\n[테스트 1] 도메인 추출")
domain1 = extract_domain_from_url(url1)
domain2 = extract_domain_from_url(url2)
base1 = normalize_home(url1)
base2 = normalize_home(url2)

print(f"URL 1: {url1}")
print(f"  → 도메인: {domain1}")
print(f"  → 베이스 URL: {base1}")

print(f"\nURL 2: {url2}")
print(f"  → 도메인: {domain2}")
print(f"  → 베이스 URL: {base2}")

print(f"\n✅ 도메인 일치: {domain1 == domain2}")
print(f"✅ 베이스 URL 일치: {base1 == base2}")

# 2. 더미 파일 생성 및 로드 테스트
print("\n[테스트 2] 더미 파일 생성 및 로드")
storage = StorageService()

# 더미 데이터 생성
dummy_products = [
    ("테스트 제품 1", "https://brainology.kr/product/1"),
    ("테스트 제품 2", "https://brainology.kr/product/2"),
    ("테스트 제품 3", "https://brainology.kr/product/3"),
]

print(f"더미 데이터 저장 중... ({len(dummy_products)}개 제품)")
saved_file = storage.save_results(base1, dummy_products, append=False)
print(f"✅ 저장 완료: {saved_file.name}")

# 3. URL1로 로드 시도
print("\n[테스트 3] URL1로 기존 파일 로드")
products1, urls1 = storage.load_existing_results(base1)
print(f"✅ 로드된 제품 수: {len(products1)}개")

# 4. URL2로 로드 시도 (같은 도메인이므로 같은 파일을 찾아야 함)
print("\n[테스트 4] URL2로 기존 파일 로드 (같은 도메인)")
products2, urls2 = storage.load_existing_results(base2)
print(f"✅ 로드된 제품 수: {len(products2)}개")

# 5. 결과 비교
print("\n[테스트 5] 결과 비교")
print(f"products1 == products2: {products1 == products2}")
print(f"urls1 == urls2: {urls1 == urls2}")

if products1 == products2 and urls1 == urls2:
    print("\n🎉 ✅ 테스트 성공!")
    print("같은 도메인의 서로 다른 URL이 동일한 파일을 참조합니다.")
else:
    print("\n❌ 테스트 실패!")
    print("결과가 일치하지 않습니다.")

# 6. 저장된 제품 목록 출력
print("\n[저장된 제품 목록]")
for idx, (name, url) in enumerate(products1, 1):
    print(f"{idx}. {name}")
    print(f"   {url}")

print("\n" + "="*70)
print("테스트 완료!")
print("="*70)
