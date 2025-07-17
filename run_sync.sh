#!/bin/bash

# CCTV Google Sheets to Supabase 동기화 실행 스크립트

echo "🚀 CCTV Google Sheets to Supabase 동기화 시스템 시작"
echo "=================================================="

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
else
    echo "❌ 가상환경을 찾을 수 없습니다. 먼저 가상환경을 설정하세요."
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# 필요한 파일 확인
echo "📋 필요한 파일 확인 중..."

required_files=(
    ".env"
    "cctvtec-mail-b013de0946d8.json"
    "cctv_supabase_sync.py"
    "google_sheets_manager_improved.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 필요한 파일이 없습니다: $file"
        exit 1
    fi
done

echo "✅ 모든 필요한 파일이 준비되었습니다."

# 로그 디렉토리 생성
if [ ! -d "logs" ]; then
    mkdir -p logs
    echo "📁 로그 디렉토리를 생성했습니다."
fi

# Python 스크립트 실행
echo "🔄 동기화 시스템을 시작합니다..."
echo "💡 중지하려면 Ctrl+C를 누르세요."
echo ""

python3 cctv_supabase_sync.py