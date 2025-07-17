# CCTV Google Sheets to Supabase 자동 동기화 시스템

Google Sheets에서 CCTV 관리 데이터를 30분마다 자동으로 다운로드하여 Supabase 데이터베이스에 저장하는 시스템입니다.

## 🎯 주요 기능

- ⏰ **자동 동기화**: 30분마다 Google Sheets 데이터를 Supabase에 자동 저장
- 📊 **다중 시트 지원**: 여러 시트를 동시에 처리
- 🔄 **실시간 로그**: 동기화 상태 및 오류 로그 기록
- 🛡️ **에러 처리**: 네트워크 오류 및 데이터 오류 자동 복구
- 📱 **모니터링**: 동기화 상태 추적 및 알림

## 📋 데이터 구조

### 1. CCTV 관리 데이터 (cctv_management)
```sql
- id: 고유 ID
- sheet_name: 시트명
- no: 번호
- entry_date: 인입날짜
- inquiry_source: 문의
- channel: 채널
- region: 지역
- form_type: 형태
- consultation_content: 상담내용(EA)
- consultation_request: 상담요청
- phone_number: 전화번호
- name: 이름
- first_call: 1차콜
- notes: 비고
- sync_timestamp: 동기화 시간
```

### 2. 케어온 신청 데이터 (careon_applications)
```sql
- id: 고유 ID
- application_datetime: 신청일시
- name: 이름
- phone_number: 연락처
- installation_location: 설치장소
- address: 주소
- installation_count: 설치대수
- privacy_consent: 개인정보동의
- sync_timestamp: 동기화 시간
```

### 3. 동기화 로그 (sync_log)
```sql
- id: 고유 ID
- sync_timestamp: 동기화 시간
- sheet_name: 시트명
- records_count: 레코드 수
- status: 상태 (SUCCESS/ERROR)
- error_message: 오류 메시지
```

## 🚀 설치 및 설정

### 1. 의존성 설치
```bash
# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. Supabase 테이블 생성
1. Supabase 대시보드에 접속
2. SQL Editor 열기
3. `supabase_schema.sql` 파일 내용을 복사하여 실행

### 3. 환경 변수 설정
`.env` 파일이 올바르게 설정되었는지 확인:
```env
# Google Sheets 설정
GOOGLE_SERVICE_ACCOUNT_FILE=cctvtec-mail-b013de0946d8.json
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/...

# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# 스케줄 설정
SYNC_INTERVAL_MINUTES=30
```

## 🔧 사용법

### 자동 실행 (추천)
```bash
./run_sync.sh
```

### 수동 실행
```bash
source venv/bin/activate
python3 cctv_supabase_sync.py
```

### 테스트 실행
```bash
# 한 번만 동기화 실행
source venv/bin/activate
python3 -c "
from cctv_supabase_sync import CCTVSupabaseSync
sync = CCTVSupabaseSync()
sync.sync_data()
"
```

## 📊 모니터링

### 로그 확인
```bash
# 실시간 로그 확인
tail -f cctv_sync.log

# 최근 100줄 로그 확인
tail -n 100 cctv_sync.log

# 에러 로그만 확인
grep "ERROR" cctv_sync.log
```

### Supabase에서 동기화 상태 확인
```sql
-- 최근 동기화 로그 확인
SELECT * FROM sync_log 
ORDER BY sync_timestamp DESC 
LIMIT 10;

-- 시트별 최근 동기화 상태
SELECT 
    sheet_name,
    MAX(sync_timestamp) as last_sync,
    status,
    records_count
FROM sync_log 
GROUP BY sheet_name, status, records_count
ORDER BY last_sync DESC;

-- 에러 발생 내역 확인
SELECT * FROM sync_log 
WHERE status = 'ERROR' 
ORDER BY sync_timestamp DESC;
```

## 🛠️ 문제 해결

### 1. 권한 오류
```bash
# Google Sheets 접근 권한 확인
# Service Account 이메일: cctvtec@cctvtec-mail.iam.gserviceaccount.com
# 해당 이메일에 Google Sheets 읽기 권한 부여 필요
```

### 2. Supabase 연결 오류
```bash
# 환경 변수 확인
cat .env

# Supabase 연결 테스트
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
print('Supabase 연결 성공!')
"
```

### 3. 동기화 실패
```bash
# 로그 확인
grep "ERROR" cctv_sync.log

# 수동 동기화 테스트
python3 -c "
from cctv_supabase_sync import CCTVSupabaseSync
sync = CCTVSupabaseSync()
sync.sync_data()
"
```

## 🔄 동기화 프로세스

1. **데이터 추출**: Google Sheets API를 통해 스프레드시트 데이터 가져오기
2. **데이터 변환**: 헤더 정규화 및 데이터 타입 변환
3. **데이터 검증**: 필수 필드 검증 및 데이터 무결성 확인
4. **데이터 적재**: 기존 데이터 삭제 후 새 데이터 삽입
5. **로그 기록**: 동기화 결과 및 오류 로그 저장

## 📅 스케줄링

- **기본 주기**: 30분마다 실행
- **설정 변경**: `.env` 파일의 `SYNC_INTERVAL_MINUTES` 값 수정
- **즉시 실행**: 프로그램 시작 시 즉시 한 번 실행

## 🔒 보안 고려사항

1. **API 키 관리**: `.env` 파일을 Git에 커밋하지 않도록 주의
2. **네트워크 보안**: HTTPS 연결 사용
3. **데이터 암호화**: 민감한 데이터는 적절히 암호화
4. **접근 제어**: Supabase RLS 설정 권장

## 📁 파일 구조

```
MQI/
├── cctv_supabase_sync.py          # 메인 동기화 스크립트
├── google_sheets_manager_improved.py  # Google Sheets 관리자
├── supabase_schema.sql            # 테이블 생성 SQL
├── run_sync.sh                    # 실행 스크립트
├── .env                           # 환경 변수
├── requirements.txt               # 의존성 패키지
├── cctv_sync.log                  # 동기화 로그
└── README_SUPABASE_SYNC.md        # 이 파일
```

## 🚨 주의사항

- **데이터 덮어쓰기**: 동기화 시 기존 데이터가 삭제되고 새로 삽입됩니다
- **API 할당량**: Google Sheets API 할당량 초과 시 오류 발생 가능
- **네트워크 안정성**: 네트워크 연결이 불안정할 경우 재시도 로직 작동
- **데이터 크기**: 대용량 데이터 처리 시 성능 저하 가능

## 📞 지원

문제 발생 시 다음 정보를 포함하여 문의:
- 에러 로그 (`cctv_sync.log`)
- 환경 설정 (민감한 정보 제외)
- 재현 단계

---

**마지막 업데이트**: 2025년 7월 17일
**버전**: 1.0.0