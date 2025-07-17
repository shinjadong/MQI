# Google Sheets to Supabase Sync System

구글 시트의 데이터를 Supabase 데이터베이스와 효율적으로 동기화하는 파이썬 기반 시스템입니다.

## 📋 핵심 기능

- **델타 동기화 (Delta Sync)**: 구글 시트에서 새로 추가된 데이터만 식별하여 Supabase에 동기화합니다. 이를 통해 불필요한 데이터 중복 및 리소스 낭비를 방지합니다.
- **주기적 실행**: 30분 간격으로 자동으로 동기화 작업을 수행합니다.
- **알림 기능**: 새로운 데이터가 추가될 때마다 슬랙(Slack)으로 실시간 알림을 보냅니다. (설정 필요)
- **데이터 유효성 검사**: 데이터베이스에 추가하기 전, 필수 데이터(`name`, `phone`)의 누락 여부를 확인하여 데이터 무결성을 유지합니다.
- **간편한 설정**: `install.sh` 스크립트를 통해 가상환경 설정 및 필요 패키지를 한 번에 설치할 수 있습니다.
- **로그 관리**: `logs/` 디렉토리에 실행 로그를 기록하여 작업 내역 및 오류를 쉽게 추적할 수 있습니다.

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/MQI.git
cd MQI
```

### 2. 설치 및 설정
프로젝트에 필요한 가상환경과 패키지를 설치합니다.
```bash
./install.sh
```
*스크립트 실행 권한이 없는 경우 `chmod +x install.sh` 명령어를 먼저 실행해주세요.*

### 3. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고, Supabase 및 Google Sheets API 접근을 위한 정보를 입력합니다.
```env
# Supabase 설정
SUPABASE_URL="YOUR_SUPABASE_URL"
SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
SUPABASE_SERVICE_ROLE_KEY="YOUR_SUPABASE_SERVICE_ROLE_KEY"

# Google Sheets API 설정
GOOGLE_SERVICE_ACCOUNT_FILE="your-google-service-account-file.json"
GOOGLE_SHEETS_URL="YOUR_GOOGLE_SHEETS_URL"

# 알림 설정 (선택 사항)
SLACK_WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL"
```
- `GOOGLE_SERVICE_ACCOUNT_FILE`: Google Cloud에서 발급받은 JSON 키 파일의 이름을 입력합니다. 이 파일은 프로젝트 루트 디렉토리에 위치해야 합니다.

### 4. 실행
동기화 스크립트를 실행합니다. 스크립트는 설정된 주기에 따라 백그라운드에서 계속 실행됩니다.
```bash
python main.py
```
실행을 중단하려면 `Ctrl+C`를 누르세요.

## 📁 프로젝트 구조

```
MQI/
├── src/                      # 소스 코드 디렉토리
│   ├── __init__.py
│   ├── main.py               # 메인 실행 스크립트
│   ├── sync_logic.py         # 데이터 동기화 핵심 로직
│   ├── google_sheets_manager.py # Google Sheets 연동 관리
│   ├── supabase_manager.py   # Supabase DB 연동 관리
│   └── notification/         # 알림 관련 모듈
│       ├── __init__.py
│       ├── notification_manager.py
│       └── slack_notification.py
├── logs/                     # 로그 파일 저장 디렉토리
├── .env                      # 환경 변수 파일 (직접 생성)
├── requirements.txt          # 파이썬 의존성 패키지 목록
├── install.sh                # 설치 스크립트
├── .gitignore
└── README.md                 # 프로젝트 설명 파일
```

## 🔧 주요 설정 값

- **동기화 주기**: `main.py` 파일 내의 `SCHEDULE_MINUTES` 변수 값을 수정하여 동기화 주기를 변경할 수 있습니다. (기본값: 30분)
- **대상 시트**: `google_sheets_manager.py` 파일 내에서 동기화할 구글 시트의 특정 시트 이름(`SHEET_NAME`)을 지정할 수 있습니다.

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

---

**Made with ❤️ by Shin Ja-dong**