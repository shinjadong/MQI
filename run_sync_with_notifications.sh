#!/bin/bash

# CCTV Google Sheets to Supabase 동기화 시스템 (알림 기능 포함) 실행 스크립트

echo "🚀 CCTV 알림 시스템을 시작합니다..."

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 가상환경 활성화 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다. 먼저 setup.sh를 실행하세요."
    exit 1
fi

echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 필수 파일 존재 확인
required_files=(".env" "cctvtec-mail-b013de0946d8.json" "cctv_supabase_sync_with_notifications.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 필수 파일이 없습니다: $file"
        exit 1
    fi
done

# 환경변수 로드 테스트
echo "🔍 환경변수 확인 중..."
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

# 필수 환경변수 확인
required_vars = ['GOOGLE_SHEETS_URL', 'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f'❌ 필수 환경변수가 설정되지 않았습니다: {missing_vars}')
    exit(1)

# 알림 설정 확인
notifications = []
if os.getenv('ENABLE_SLACK_NOTIFICATIONS', 'false').lower() == 'true':
    notifications.append('슬랙')
if os.getenv('ENABLE_KAKAO_NOTIFICATIONS', 'false').lower() == 'true':
    notifications.append('카카오톡')
if os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true':
    notifications.append('이메일')

if notifications:
    print(f'📱 활성화된 알림: {', '.join(notifications)}')
else:
    print('⚠️  활성화된 알림이 없습니다. .env 파일에서 ENABLE_*_NOTIFICATIONS를 설정하세요.')

print('✅ 환경변수 설정 완료')
"

if [ $? -ne 0 ]; then
    echo "❌ 환경변수 설정을 확인하세요."
    exit 1
fi

# 의존성 확인
echo "📦 의존성 확인 중..."
python3 -c "
try:
    import pandas, supabase, schedule, google.auth
    print('✅ 모든 의존성이 설치되어 있습니다.')
except ImportError as e:
    print(f'❌ 의존성 부족: {e}')
    print('pip install -r requirements.txt를 실행하세요.')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

# 백그라운드 실행 여부 확인
if [ "$1" == "--background" ] || [ "$1" == "-bg" ]; then
    echo "🌙 백그라운드 모드로 실행합니다..."
    nohup python3 cctv_supabase_sync_with_notifications.py > cctv_sync_notifications.log 2>&1 &
    PID=$!
    echo "✅ 백그라운드에서 실행 중입니다. (PID: $PID)"
    echo "📋 로그 확인: tail -f cctv_sync_notifications.log"
    echo "🛑 종료 방법: kill $PID"
    echo $PID > sync_notifications.pid
elif [ "$1" == "--test" ] || [ "$1" == "-t" ]; then
    echo "🧪 테스트 모드로 실행합니다..."
    python3 -c "
from cctv_supabase_sync_with_notifications import CCTVSupabaseSyncWithNotifications
try:
    sync_system = CCTVSupabaseSyncWithNotifications()
    sync_system.test_notifications()
    print('✅ 테스트 완료')
except Exception as e:
    print(f'❌ 테스트 실패: {e}')
    exit(1)
"
else
    echo "🔄 포그라운드 모드로 실행합니다... (Ctrl+C로 종료)"
    python3 cctv_supabase_sync_with_notifications.py
fi

echo "👋 프로그램이 종료되었습니다."