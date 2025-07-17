# Google Sheets to Supabase 자동 동기화 시스템

Google Sheets의 CCTV 문의 데이터를 Supabase 데이터베이스와 자동으로 동기화하고, 신규 데이터가 추가될 때 슬랙으로 알림을 발송하는 시스템입니다.

## 🚀 주요 기능

- **자동 동기화**: 30분마다 Google Sheets 데이터를 Supabase와 동기화
- **모든 문의 유형 지원**: 
  - 견적 의뢰
  - 상담 문의
  - 문의 사항
  - CCTV 관리
  - 케어온 신청
- **델타 동기화**: 신규 데이터만 추가하여 중복 방지
- **실시간 알림**: 새로운 문의 접수 시 슬랙으로 즉시 알림
- **날짜 기반 시트 선택**: 오늘 날짜와 매칭되는 시트를 자동으로 선택
- **Google API 재시도 로직**: 503 오류 시 지수 백오프로 재시도
- **엑셀 파일 보관**: 다운로드한 모든 파일을 날짜별 폴더에 저장

## 📋 필수 요구사항

- Python 3.8 이상
- Google Cloud 서비스 계정
- Supabase 프로젝트
- 슬랙 Webhook URL

## 🛠️ 설치 방법

1. **프로젝트 클론**
```bash
git clone [repository-url]
cd MQI
```

2. **Python 가상 환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**
   - `.env` 파일을 생성하고 다음 내용을 설정:
```env
# Google Sheets 설정
GOOGLE_SERVICE_ACCOUNT_FILE=your-service-account-key.json
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 슬랙 알림 설정
ENABLE_SLACK_NOTIFICATIONS=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# 기타 설정
SYNC_INTERVAL_MINUTES=30
SAVE_ALL_SHEETS=true
```

5. **Google 서비스 계정 키 파일 추가**
   - Google Cloud Console에서 서비스 계정 키 JSON 파일 다운로드
   - 프로젝트 루트에 저장

## 🚀 실행 방법

**기본 실행**
```bash
python -m src.main
```

**백그라운드 실행 (Linux/Mac)**
```bash
nohup python -m src.main > sync.log 2>&1 &
```

**systemd 서비스로 등록 (권장)**
1. 서비스 파일 생성:
```bash
sudo nano /etc/systemd/system/cctv-sync.service
```

2. 서비스 파일 내용:
```ini
[Unit]
Description=CCTV Google Sheets to Supabase Sync
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/MQI
Environment="PATH=/home/ubuntu/MQI/venv/bin"
ExecStart=/home/ubuntu/MQI/venv/bin/python -m src.main
Restart=always

[Install]
WantedBy=multi-user.target
```

3. 서비스 시작:
```bash
sudo systemctl start cctv-sync
sudo systemctl enable cctv-sync
```

## 📊 데이터 구조

### customer_inquiries 테이블
- `name`: 이름
- `phone`: 연락처
- `inquiry_type`: 문의 유형 (견적 의뢰, 상담 문의, 문의 사항, CCTV 관리, 케어온 신청)
- `sheet_name`: 원본 시트 이름
- 각 문의 유형별 추가 필드

### 뷰 구조
- `estimates`: 견적 의뢰만 필터링
- `consultations`: 상담 문의만 필터링
- `inquiries`: 문의 사항만 필터링
- `cctv_management`: CCTV 관리만 필터링
- `careon_applications`: 케어온 신청만 필터링

## 🔔 슬랙 알림 형식

```
🔔 *새로운 문의가 3건 접수되었습니다!*
📅 시간: 2025-01-16 14:30:00

*【케어온 신청】* - 2건
  1. 홍길동 (010-1234-5678) | 설치장소: 서울시 강남구
  2. 김철수 (010-9876-5432) | 설치장소: 경기도 성남시

*【견적 의뢰】* - 1건
  1. 이영희 (010-5555-6666) | 회사: ABC기업

📊 [Supabase 대시보드 바로가기](https://supabase.com/dashboard/...)
```

## 📁 프로젝트 구조

```
MQI/
├── src/
│   ├── __init__.py
│   ├── main.py                    # 메인 실행 파일
│   ├── google_sheets_manager.py   # Google Sheets 관리
│   ├── supabase_manager.py        # Supabase DB 관리
│   └── notification/
│       ├── __init__.py
│       ├── notification_manager.py # 알림 통합 관리
│       └── slack_notification.py   # 슬랙 알림
├── downloads/                      # 다운로드된 엑셀 파일 저장
├── logs/                          # 로그 파일
├── .env                           # 환경 변수
├── requirements.txt               # Python 의존성
└── README.md
```

## 🔍 로그 확인

```bash
# 실시간 로그 확인
tail -f logs/sync.log

# systemd 서비스 로그
sudo journalctl -u cctv-sync -f
```

## ⚠️ 주의사항

- 서비스 계정에 Google Sheets 읽기 권한 필요
- Supabase Service Role Key는 보안에 주의
- 슬랙 Webhook URL은 외부에 노출되지 않도록 주의
- 다운로드된 엑셀 파일은 자동으로 삭제되지 않으므로 주기적으로 정리 필요

## 🛠️ 문제 해결

### Google API 503 오류
- 자동으로 재시도됩니다 (최대 5회, 지수 백오프)

### Supabase 연결 오류
- Service Role Key 확인
- Supabase URL 확인

### 슬랙 알림 미발송
- Webhook URL 확인
- `ENABLE_SLACK_NOTIFICATIONS=true` 설정 확인

## 📝 라이센스

이 프로젝트는 MIT 라이센스를 따릅니다.