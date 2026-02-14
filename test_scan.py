"""
테스트 스크립트: 카페24 URL로 간단한 스캔 테스트
"""
from main import process_product_url

# 테스트 URL (카페24 예시)
test_url = "https://brainology.kr/surl/p/10"

print("="*70)
print("🧪 테스트 실행: 플랫폼 감지 및 스캔 로직 검증")
print("="*70)
print(f"\n테스트 URL: {test_url}\n")

try:
    # 실제 스캔은 하지 않고 플랫폼 감지만 테스트
    from platforms.cafe24_platform import Cafe24Platform
    from platforms.imweb_platform import ImwebPlatform
    
    platform_cafe24 = Cafe24Platform()
    platform_imweb = ImwebPlatform()
    
    # 테스트 1: 카페24 감지
    print("테스트 1: 카페24 URL 감지")
    is_cafe24 = platform_cafe24.detect(test_url)
    print(f"  결과: {'✅ 성공' if is_cafe24 else '❌ 실패'}")
    
    if is_cafe24:
        # 테스트 2: 제품 ID 추출
        print("\n테스트 2: 제품 ID 추출")
        product_id = platform_cafe24.extract_product_id(test_url)
        print(f"  추출된 ID: {product_id}")
        print(f"  결과: {'✅ 성공' if product_id == 10 else '❌ 실패'}")
        
        # 테스트 3: 스캔 템플릿 생성
        print("\n테스트 3: 스캔 템플릿 생성")
        template = platform_cafe24.get_scan_template(test_url)
        print(f"  템플릿: {template}")
        expected = "https://brainology.kr/surl/p/{id}"
        print(f"  결과: {'✅ 성공' if template == expected else '❌ 실패'}")
    
    # 테스트 4: 아임웹 감지 (False여야 함)
    print("\n테스트 4: 아임웹 감지 (False 예상)")
    is_imweb = platform_imweb.detect(test_url)
    print(f"  결과: {'✅ 성공 (정상적으로 False)' if not is_imweb else '❌ 실패'}")
    
    print("\n" + "="*70)
    print("✨ 모든 테스트 완료!")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ 테스트 중 오류 발생: {e}")
    import traceback
    traceback.print_exc()

