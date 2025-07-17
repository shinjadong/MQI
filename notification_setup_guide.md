# 📱 CCTV 알림 시스템 설정 가이드

새로운 CCTV 문의나 케어온 신청이 들어올 때 직원들에게 즉시 알림을 보내는 시스템입니다.

## 🎯 알림 방식 선택

### 1️⃣ 슬랙 알림 (추천 - 가장 간단)
- ✅ **무료**
- ✅ **설정 간단** (5분 내 완료)
- ✅ **실시간 알림**
- ✅ **팀 협업 가능**

### 2️⃣ 카카오톡 알림톡
- ⚠️ **유료** (건당 15원)
- ⚠️ **설정 복잡** (승인 1-2일 소요)
- ✅ **높은 확인률**
- ✅ **개인 휴대폰으로 수신**

### 3️⃣ 이메일 알림
- ✅ **무료**
- ✅ **설정 간단**
- ⚠️ **확인률 낮음**
- ✅ **상세 정보 전달 가능**

---

## 🚀 슬랙 알림 설정 (추천)

### 1단계: 슬랙 워크스페이스 생성/접속
1. https://slack.com 접속
2. 회사 워크스페이스 생성 또는 기존 워크스페이스 사용
3. 알림 받을 채널 생성 (예: #cctv-알림)

### 2단계: Webhook URL 생성
1. **슬랙 앱 관리** 페이지 접속: https://api.slack.com/apps
2. **"Create New App"** 클릭
3. **"From scratch"** 선택
4. 앱 이름: `CCTV 알림 시스템`
5. 워크스페이스 선택
6. **"Incoming Webhooks"** 클릭
7. **"Activate Incoming Webhooks"** 활성화
8. **"Add New Webhook to Workspace"** 클릭
9. 알림 받을 채널 선택 (예: #cctv-알림)
10. **Webhook URL 복사** (예: https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX)

### 3단계: 환경 변수 설정
```bash
# .env 파일에 추가
ENABLE_SLACK_NOTIFICATIONS=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 4단계: 테스트 실행
```bash
cd /home/tlswk/projects/MQI
source venv/bin/activate
python slack_notification.py
```

---

## 📞 카카오톡 알림톡 설정

### 1단계: 카카오톡 채널 관리자 센터
1. https://center-pf.kakao.com/ 접속
2. **"메시지 관리" > "알림톡 관리"**
3. **"알림톡 서비스 신청"** (승인 1-2일 소요)

### 2단계: 카카오 개발자 센터
1. https://developers.kakao.com/ 접속
2. **"내 애플리케이션" > "애플리케이션 추가하기"**
3. **"제품 설정" > "카카오톡 메시지"** 활성화
4. **REST API 키** 복사

### 3단계: 알림톡 템플릿 등록
채널 관리자 센터에서 다음 템플릿 등록:

#### 신규 문의 템플릿
```
[CCTV 신규 문의 접수]

🔥 새로운 문의가 접수되었습니다.

📋 기본 정보
• 문의일: #{문의일}
• 문의처: #{문의처}
• 채널: #{채널}
• 지역: #{지역}

👤 고객 정보
• 이름: #{고객명}
• 연락처: #{연락처}
• 요청사항: #{요청사항}

⚡ 즉시 확인하여 빠른 대응 부탁드립니다.
```

### 4단계: 환경 변수 설정
```bash
# .env 파일에 추가
ENABLE_KAKAO_NOTIFICATIONS=true
KAKAO_REST_API_KEY=your_rest_api_key
KAKAO_SENDER_KEY=your_sender_key
KAKAO_TEMPLATE_CODE_INQUIRY=승인된_템플릿_코드
NOTIFICATION_PHONE_NUMBERS=010-1234-5678,010-9876-5432
```

---

## 📧 이메일 알림 설정

### 1단계: Gmail 앱 비밀번호 생성
1. Gmail 계정의 **"계정 관리"** 접속
2. **"보안" > "2단계 인증"** 활성화
3. **"앱 비밀번호"** 생성

### 2단계: 환경 변수 설정
```bash
# .env 파일에 추가
ENABLE_EMAIL_NOTIFICATIONS=true
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_16_digit_app_password
NOTIFICATION_EMAILS=staff1@company.com,staff2@company.com
```

---

## 🛠️ 시스템 실행

### 알림 기능 포함 시스템 실행
```bash
cd /home/tlswk/projects/MQI
source venv/bin/activate

# 알림 기능 포함 버전 실행
python cctv_supabase_sync_with_notifications.py
```

### 테스트 실행
```bash
# 슬랙 알림 테스트
python slack_notification.py

# 카카오톡 알림 테스트  
python kakao_notification.py
```

---

## 📊 알림 내용 예시

### 슬랙 알림 예시
```
🔥 CCTV 신규 문의 접수

문의일: 2025-07-17
문의처: KT
채널: TEL
지역: 서울 강남구

고객명: 홍길동
연락처: 010-1234-5678
형태: 아파트
요청사항: 견적요청

상담내용: 현관 CCTV 2대 설치 문의

⚡ 즉시 확인하여 빠른 대응 부탁드립니다.
```

### 케어온 신청 알림 예시
```
🏠 케어온 신규 신청

신청일시: 2025-07-17 14:30:25
고객명: 김철수
연락처: 010-9876-5432

설치장소: 주택
주소: 서울시 강남구 역삼동 123-456
설치대수: 3대

⚡ 빠른 상담 진행 부탁드립니다.
```

---

## 💰 비용 비교

| 알림 방식 | 초기 비용 | 월 운영비 | 설정 시간 | 확인률 |
|----------|----------|----------|----------|--------|
| 슬랙     | 무료      | 무료      | 5분       | 높음    |
| 카카오톡  | 무료      | 2-5천원   | 2-3일     | 매우높음 |
| 이메일    | 무료      | 무료      | 10분      | 낮음    |

---

## 🎯 권장 설정

### 즉시 시작 (무료)
```bash
# 슬랙 알림만 활성화
ENABLE_SLACK_NOTIFICATIONS=true
ENABLE_KAKAO_NOTIFICATIONS=false
ENABLE_EMAIL_NOTIFICATIONS=false
```

### 완전한 시스템 (유료)
```bash
# 슬랙 + 카카오톡 동시 사용
ENABLE_SLACK_NOTIFICATIONS=true
ENABLE_KAKAO_NOTIFICATIONS=true
ENABLE_EMAIL_NOTIFICATIONS=false
```

---

## 🔧 문제 해결

### 슬랙 알림이 안 올 때
1. Webhook URL 확인
2. 채널 권한 확인
3. 방화벽 설정 확인

### 카카오톡 알림이 안 올 때
1. 템플릿 승인 상태 확인
2. REST API 키 확인
3. 발송 대상 친구추가 확인

### 이메일 알림이 안 올 때
1. 앱 비밀번호 확인
2. 2단계 인증 활성화 확인
3. 스팸함 확인

---

## 📞 지원

설정 중 문제가 발생하면:
1. 로그 파일 확인: `tail -f cctv_sync_with_notifications.log`
2. 테스트 스크립트 실행
3. 환경 변수 설정 재확인

**추천: 일단 슬랙으로 시작하시고, 필요하면 나중에 카카오톡 추가하세요!** 🚀