# Influencer DM Automation

Slack에서 제품 URL을 입력하면 자동으로 제품 페이지를 스캔하고, 인플루언서를 찾아 인스타그램 DM을 보내는 자동화 프로그램입니다.

## 🚀 기능

1. **Slack 웹훅 통합**: Slack에서 URL 감지 시 자동 실행
2. **멀티 플랫폼 지원**: 카페24, 아임웹 (확장 가능한 구조)
3. **스마트 스캔**: ID 기반 제품 페이지 탐색
4. **자동 저장**: 스캔 결과를 파일에 저장하여 재시작 시 이어서 진행
5. **실시간 알림**: 각 단계별 진행 상황을 Slack 스레드로 전송

## 📦 설치

```bash
# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

## ⚙️ 환경 변수 설정

`.env` 파일에 다음 정보를 입력하세요:

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLEEP_SECONDS=1.0
CONSECUTIVE_MISSES_THRESHOLD=100
CONSECUTIVE_HITS_THRESHOLD=200
REQUEST_TIMEOUT_SECONDS=10
DATA_DIR=data
```

## 🎯 사용 방법

### 직접 실행
```bash
python main.py
```

### Slack에서 사용
Slack 채널에 제품 URL을 포함한 메시지를 전송하면 자동으로 실행됩니다.

## 📁 프로젝트 구조

```
├── main.py                    # 메인 진입점
├── config/
│   └── settings.py           # 설정 관리
├── services/
│   ├── slack_service.py      # Slack 통신
│   ├── scanner_service.py    # 제품 스캔
│   └── storage_service.py    # 파일 저장/로드
├── platforms/
│   ├── base_platform.py      # 플랫폼 기본 클래스
│   ├── cafe24_platform.py    # 카페24
│   └── imweb_platform.py     # 아임웹
├── utils/
│   ├── url_utils.py          # URL 처리
│   └── html_parser.py        # HTML 파싱
└── data/                     # 스캔 결과 저장
```

## 🔧 지원 플랫폼

- **카페24**
  - `/surl/p/{id}`
  - `/product/.../id}/category/...`
  - `/product/detail.html?product_no={id}`
  
- **아임웹**
  - `/Product/?idx={id}`

## 📝 데이터 저장

스캔 결과는 `data/` 디렉토리에 다음 형식으로 저장됩니다:
- 파일명: `{도메인}_{타임스탬프}.txt`
- 형식: 각 라인에 "제품명 | 제품URL"

## 🔄 재시작 처리

프로그램이 중단되어도 같은 URL로 다시 요청하면 저장된 파일을 확인하고 이어서 진행합니다.

## 📮 Slack 알림

모든 진행 상황은 최초 메시지의 스레드로 전송됩니다:
- 스캔 시작 알림
- 제품 발견 알림
- 단계별 진행 상황
- 완료/에러 알림

## 🛠️ 개발

새로운 플랫폼을 추가하려면:
1. `platforms/` 디렉토리에 새 파일 생성
2. `BasePlatform` 클래스 상속
3. 필수 메서드 구현: `detect()`, `get_scan_template()`
4. `config/settings.py`의 `PLATFORMS` 리스트에 추가
