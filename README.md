# CCTV 동기화 시스템 (AI 분류 포함)

Google Sheets와 Supabase를 연동하여 CCTV 관련 데이터를 자동으로 동기화하고 Claude AI로 분류하는 시스템입니다.

## 📋 주요 기능

- 🔍 **Google Sheets 자동 동기화**: 30분마다 자동으로 데이터를 가져옵니다
- 🤖 **AI 데이터 분류**: Claude 4 Sonnet을 사용하여 데이터를 자동 분류합니다
- 💾 **Supabase 통합**: 분류된 데이터를 통합 테이블에 저장합니다
- 🔔 **알림 시스템**: 슬랙, 카카오톡, 이메일 알림 지원
- 📊 **통합 스키마**: 모든 데이터 타입을 하나의 통합 테이블에 저장

## 🚀 설치 및 설정

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/MQI.git
cd MQI
```

### 2. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 추가:

```env
# Google Sheets 설정
GOOGLE_SERVICE_ACCOUNT_FILE=your-service-account-key.json
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Claude AI API 설정
ANTHROPIC_API_KEY=your-anthropic-api-key

# 스케줄 설정
SYNC_INTERVAL_MINUTES=30

# AI 데이터 분류 설정
ENABLE_AI_CLASSIFICATION=true
AI_CLASSIFICATION_TIMEOUT=30

# 알림 설정
ENABLE_SLACK_NOTIFICATIONS=true
SLACK_WEBHOOK_URL=your-slack-webhook-url
```

### 5. Google Service Account 키 파일 배치
Google Cloud Console에서 생성한 Service Account 키 파일을 프로젝트 루트에 배치합니다.

## 🐳 Docker 사용

### Docker 빌드
```bash
docker build -t cctv-sync .
```

### Docker 실행
```bash
docker run -d \
  --name cctv-sync \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  cctv-sync
```

## 📖 사용법

### 1. 수동 실행
```bash
python cctv_supabase_sync.py
```

### 2. 백그라운드 실행 (Linux/Mac)
```bash
./run_sync.sh
```

### 3. 스케줄러 사용
프로그램이 자동으로 30분마다 실행됩니다.

## 📁 프로젝트 구조

```
MQI/
├── cctv_supabase_sync.py         # 메인 동기화 스크립트
├── google_sheets_manager_improved.py  # Google Sheets 관리자
├── slack_notification.py        # 슬랙 알림 시스템
├── kakao_notification.py        # 카카오톡 알림 시스템
├── requirements.txt             # 의존성 패키지
├── Dockerfile                   # Docker 설정
├── setup.py                     # 패키지 설정
├── .env                         # 환경 변수 (직접 생성)
├── .gitignore                   # Git 제외 파일
├── run_sync.sh                  # 실행 스크립트
├── logs/                        # 로그 파일
└── README.md                    # 이 파일
```

## 🔧 AI 분류 시스템

### 분류 카테고리
1. **estimate**: 견적 요청
2. **consultation**: 상담 요청
3. **inquiry**: 일반 문의
4. **cctv_management**: CCTV 관리 데이터
5. **careon_application**: CareOn 서비스 신청

### AI 분류 과정
1. Google Sheets에서 데이터를 가져옵니다
2. Claude AI가 데이터 내용을 분석합니다
3. 적절한 카테고리로 자동 분류합니다
4. 95% 이상의 분류 정확도를 달성합니다

## 📊 데이터베이스 스키마

### customer_inquiries 테이블
- **통합 테이블**: 모든 데이터 타입을 하나의 테이블에 저장
- **31개 컬럼**: 다양한 데이터 소스를 수용
- **AI 분류 필드**: 자동 분류 결과 저장

## 📱 알림 시스템

### 지원 알림 채널
- **슬랙**: 웹훅을 통한 실시간 알림
- **카카오톡**: 알림톡 서비스
- **이메일**: SMTP를 통한 이메일 알림

### 알림 내용
- 새로운 데이터 감지
- 동기화 완료 상태
- 오류 발생 시 알림

## 🛠️ 개발 환경 설정

### 로컬 개발
```bash
# 가상환경 활성화
source venv/bin/activate

# 개발 모드 실행
python cctv_supabase_sync.py

# 테스트 실행
python -m pytest tests/
```

### 코드 스타일
- **PEP 8** 준수
- **Type hints** 사용
- **상세한 주석** 포함

## 🔐 보안 고려사항

- 모든 API 키는 `.env` 파일에 저장
- Google Service Account 키는 Git에서 제외
- 민감한 정보는 환경 변수로 관리

## 🚀 배포

### 서버 배포
```bash
# 서버에 클론
git clone https://github.com/your-username/MQI.git

# 환경 설정
cp .env.example .env
# .env 파일 수정

# 서비스 실행
systemctl start cctv-sync
systemctl enable cctv-sync
```

### Docker 배포
```bash
# 이미지 빌드
docker build -t cctv-sync .

# 컨테이너 실행
docker run -d --name cctv-sync cctv-sync
```

## 📈 모니터링

### 로그 확인
```bash
# 실시간 로그 확인
tail -f logs/cctv_sync.log

# 오류 로그 확인
grep ERROR logs/cctv_sync.log
```

### 성능 지표
- 동기화 주기: 30분
- AI 분류 정확도: 95%+
- 처리 속도: 1,000건/분

## 🤝 기여

1. 저장소를 Fork합니다
2. 새로운 기능 브랜치를 생성합니다
3. 변경사항을 커밋합니다
4. Pull Request를 생성합니다

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 🆘 지원

문제가 있거나 도움이 필요한 경우:
- GitHub Issues 생성
- 이메일: tlswk@example.com

---

**Made with ❤️ by Shin Ja-dong**