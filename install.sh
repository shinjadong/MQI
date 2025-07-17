#!/bin/bash

# CCTV AI 동기화 시스템 설치 스크립트
# 사용법: ./install.sh

set -e

echo "🚀 CCTV AI 동기화 시스템 설치를 시작합니다..."

# 1. Python 버전 확인
echo "📋 Python 버전 확인 중..."
python3 --version

# 2. 가상환경 생성
echo "🔧 가상환경 생성 중..."
python3 -m venv venv

# 3. 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 4. pip 업그레이드
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip

# 5. 의존성 패키지 설치
echo "📦 의존성 패키지 설치 중..."
pip install -r requirements.txt

# 6. 환경 변수 파일 복사
echo "⚙️ 환경 변수 파일 설정 중..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env 파일이 생성되었습니다."
    echo "⚠️  .env 파일을 편집하여 필요한 API 키와 설정을 입력하세요."
else
    echo "⚠️  .env 파일이 이미 존재합니다."
fi

# 7. 로그 디렉토리 생성
echo "📁 로그 디렉토리 생성 중..."
mkdir -p logs

# 8. 실행 권한 설정
echo "🔑 실행 권한 설정 중..."
chmod +x run_sync.sh
chmod +x run_sync_with_notifications.sh

# 9. 설치 완료 메시지
echo ""
echo "🎉 설치가 완료되었습니다!"
echo ""
echo "📝 다음 단계:"
echo "1. .env 파일을 편집하여 API 키와 설정을 입력하세요"
echo "2. Google Service Account 키 파일을 프로젝트 루트에 배치하세요"
echo "3. 시스템을 테스트하세요:"
echo "   source venv/bin/activate"
echo "   python cctv_supabase_sync.py"
echo ""
echo "🐳 Docker 사용 시:"
echo "   docker build -t cctv-sync ."
echo "   docker run -d --name cctv-sync --env-file .env cctv-sync"
echo ""
echo "📚 자세한 내용은 README.md 파일을 참고하세요."

# 10. 가상환경 비활성화
deactivate

echo ""
echo "✅ 설치 스크립트가 완료되었습니다!" 