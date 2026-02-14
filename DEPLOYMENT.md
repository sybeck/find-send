# 배포 가이드

## 🚀 배포 완료!

인플루언서 DM 자동화 프로그램이 GitHub에 배포되었습니다.

### 📦 저장소 정보
- **Repository**: https://github.com/sybeck/stocks-alert
- **Branch**: `main` (프로덕션), `genspark_ai_developer` (개발)
- **Latest Commit**: feat: 인플루언서 DM 자동화 프로그램 초기 구조 및 제품 스캔 기능 구현

---

## 🎯 구현된 기능 (1-3단계)

### ✅ 1단계: Slack 웹훅 통합
- Slack에서 URL 감지 시 자동 실행
- 스레드 기반 진행 상황 알림

### ✅ 2단계: 멀티 플랫폼 스캔
- **카페24 지원**:
  - `/surl/p/{id}`
  - `/product/.../{{id}}/category/...`
  - `/product/detail.html?product_no={id}`
- **아임웹 지원**:
  - `/Product/?idx={id}`
- 확장 가능한 플랫폼 구조

### ✅ 3단계: 결과 저장 및 재시작
- 실시간 파일 저장 (`data/{도메인}_{타임스탬프}.txt`)
- **도메인 기반 캐싱**: 같은 도메인의 모든 URL은 동일한 결과 공유
  - 예: `brainology.kr/surl/p/1`과 `brainology.kr/product/.../42/...`은 같은 파일 사용
- 기존 파일이 있으면 스캔 스킵하고 저장된 데이터 사용
- 중복 제품 자동 필터링

### 🔧 개선 사항
- **업그레이드된 제품명 추출**: BeautifulSoup4 활용
  - og:title 메타 태그 우선
  - 제품명 클래스/ID 감지
  - h1 태그 파싱
  - title 태그에서 사이트명 자동 제거

---

## 📋 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/sybeck/stocks-alert.git
cd stocks-alert
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 실제 Slack 정보 입력
```

`.env` 파일 예시:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLEEP_SECONDS=1.0
CONSECUTIVE_MISSES_THRESHOLD=100
CONSECUTIVE_HITS_THRESHOLD=200
REQUEST_TIMEOUT_SECONDS=10
DATA_DIR=data
```

### 4. 실행
```bash
# 대화형 실행
python main.py

# 커맨드 라인 인자로 실행
python main.py "https://brainology.kr/surl/p/10"
```

---

## 🧪 테스트 실행

플랫폼 감지 및 기본 로직 테스트:
```bash
python test_scan.py
```

예상 결과:
```
✅ 테스트 1: 카페24 URL 감지 - 성공
✅ 테스트 2: 제품 ID 추출 - 성공
✅ 테스트 3: 스캔 템플릿 생성 - 성공
✅ 테스트 4: 아임웹 감지 - 성공
```

---

## 📁 프로젝트 구조

```
/home/user/webapp/
├── .env                          # 환경 변수 (git 제외)
├── .env.example                  # 환경 변수 예시
├── .gitignore                    # Git 무시 파일
├── requirements.txt              # Python 의존성
├── README.md                     # 프로젝트 설명서
├── DEPLOYMENT.md                 # 배포 가이드 (이 파일)
├── main.py                       # 메인 진입점
├── test_scan.py                  # 테스트 스크립트
├── config/
│   └── settings.py              # 설정 관리
├── services/
│   ├── slack_service.py         # Slack 통신
│   ├── scanner_service.py       # 제품 스캔
│   └── storage_service.py       # 파일 저장/로드
├── platforms/
│   ├── base_platform.py         # 플랫폼 기본 클래스
│   ├── cafe24_platform.py       # 카페24 구현
│   └── imweb_platform.py        # 아임웹 구현
├── utils/
│   ├── url_utils.py             # URL 처리
│   └── html_parser.py           # HTML 파싱
└── data/                        # 스캔 결과 저장 디렉토리
```

---

## 🔄 다음 단계 (TODO)

### 4단계: 인플루언서 닉네임 추출
- [ ] 제품명에서 인플루언서 닉네임 추출 로직 구현
- [ ] 하이브리드 방식 (규칙 기반 + LLM 폴백)
- [ ] 브랜드별 패턴 학습 기능

### 5단계: 인스타그램 계정 검색
- [ ] 구글 검색 API 통합
- [ ] 인스타그램 URL 필터링
- [ ] 계정 유효성 검증

### 6단계: 인스타그램 DM 발송
- [ ] 인스타그램 API 통합
- [ ] DM 메시지 템플릿
- [ ] 발송 결과 추적

---

## 🛠️ 개발 가이드

### 새로운 플랫폼 추가 방법

1. `platforms/` 디렉토리에 새 파일 생성 (예: `new_platform.py`)

2. `BasePlatform` 클래스 상속:
```python
from platforms.base_platform import BasePlatform

class NewPlatform(BasePlatform):
    @property
    def name(self) -> str:
        return "new_platform"
    
    def detect(self, url: str) -> bool:
        # URL 감지 로직
        pass
    
    def get_scan_template(self, url: str) -> str:
        # 스캔 템플릿 반환
        pass
    
    def extract_product_id(self, url: str) -> Optional[int]:
        # 제품 ID 추출
        pass
```

3. `main.py`의 `PLATFORMS` 리스트에 추가:
```python
PLATFORMS = [
    Cafe24Platform(),
    ImwebPlatform(),
    NewPlatform(),  # 새 플랫폼 추가
]
```

---

## 📞 지원

문제가 발생하거나 질문이 있으시면 GitHub Issues를 통해 문의해주세요.

---

**배포일**: 2026-02-14
**버전**: 1.0.0 (Phase 1-3 완료)
