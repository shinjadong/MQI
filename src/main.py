#!/usr/bin/env python3
"""
CCTV Google Sheets to Supabase 자동 동기화 시스템
30분마다 Google Sheets 데이터를 읽어 Supabase와 동기화하고,
신규 데이터가 있을 경우 알림을 발송합니다.
"""

import os
import sys
import logging
import schedule
import time
import traceback
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
import re

# src 디렉토리를 sys.path에 추가 (로컬 실행 시)
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .google_sheets_manager import GoogleSheetsManager
from .supabase_manager import SupabaseManager
from .notification.notification_manager import NotificationManager

# --- 환경변수 로드 ---
load_dotenv()

# --- 설정 ---
# 로그 디렉토리 설정 (프로젝트 루트 기준)
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 로깅 설정
log_file_path = os.path.join(LOG_DIR, 'sync.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 스케줄링 간격 (분)
SCHEDULE_MINUTES = 30

def get_supabase_client() -> Client:
    """Supabase 클라이언트를 생성하고 반환합니다."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        raise ValueError("Supabase URL 또는 Service Role Key가 .env 파일에 설정되지 않았습니다.")
    return create_client(url, key)


def sync_and_notify():
    """
    데이터 동기화 및 알림 발송 작업을 수행하는 메인 함수.
    """
    excel_path = None
    try:
        logger.info("="*50)
        logger.info("🚀 동기화 작업을 시작합니다.")
        logger.info(f"실행 시간: {datetime.now()}")

        supabase_client = get_supabase_client()
        gs_manager = GoogleSheetsManager()
        sb_manager = SupabaseManager(supabase_client)
        notification_manager = NotificationManager()

        # 1. Supabase에서 기존 데이터의 고유 식별자(PK) 가져오기
        #    'name'과 'phone_number'를 조합하여 고유 식별자로 사용합니다.
        existing_identifiers = sb_manager.get_existing_identifiers('careon_applications', ['name', 'phone_number'])
        logger.info(f"Supabase에 존재하는 데이터 식별자 {len(existing_identifiers)}개를 가져왔습니다.")

        # 2. Google Sheets에서 최신 데이터 가져오기 (엑셀로 다운로드)
        excel_path = gs_manager.download_sheet_as_excel()
        if not excel_path:
            logger.error("Google Sheets 다운로드에 실패하여 동기화를 중단합니다.")
            return

        # 3. 다운로드한 엑셀 파일에서 '케어온' 시트 읽기
        try:
            latest_data_df = pd.read_excel(excel_path, sheet_name='케어온')
        except Exception as e:
            logger.error(f"'케어온' 시트를 읽는 중 오류 발생: {e}. 엑셀 파일에 해당 시트가 존재하는지 확인하세요.")
            return
            
        logger.info(f"Google Sheets '{latest_data_df.name if hasattr(latest_data_df, 'name') else '케어온'}' 시트에서 {len(latest_data_df)}개의 데이터를 가져왔습니다.")

        # 4. 신규 데이터 필터링 (Delta 동기화)
        new_records_to_insert = filter_new_data(latest_data_df, existing_identifiers)

        if not new_records_to_insert:
            logger.info("✅ 새로운 데이터가 없습니다. 동기화가 최신 상태입니다.")
        else:
            logger.info(f"🆕 {len(new_records_to_insert)}개의 신규 데이터를 발견했습니다.")
            
            # 5. 신규 데이터 Supabase에 삽입
            sb_manager.insert_customer_inquiries(new_records_to_insert)

            # 6. 신규 데이터에 대한 알림 발송
            # notification_manager.send_notifications_for_new_data(new_records_to_insert)

    except Exception as e:
        logger.error("동기화 작업 중 심각한 오류가 발생했습니다.")
        logger.error(traceback.format_exc())
    finally:
        # 7. 임시 엑셀 파일 삭제
        if excel_path:
            gs_manager.cleanup_temp_file(excel_path)
            
        logger.info("✨ 동기화 작업이 종료되었습니다.")
        logger.info("="*50 + "\n")

def filter_new_data(df, existing_identifiers):
    """DataFrame에서 신규 데이터를 필터링하고 유효성을 검사합니다."""
    new_records = []
    df = df.where(pd.notnull(df), None) # NaN을 None으로 변환

    for index, row in df.iterrows():
        # Google Sheet의 '이름'과 '연락처' 컬럼을 사용
        name = row.get('이름')
        phone = row.get('연락처')

        # 필수 값 유효성 검사
        if not name or not phone:
            logger.warning(f"Skipping row {index+2}: 필수 값(이름 또는 연락처)이 누락되었습니다. Data: {row.to_dict()}")
            continue
        
        # 연락처 정제 (숫자만 추출)
        phone_cleaned = re.sub(r'\D', '', str(phone))
        
        current_identifier = (str(name), phone_cleaned)
        
        if current_identifier not in existing_identifiers:
            # DB 스키마에 맞게 데이터 매핑
            record = {
                'name': name,
                'phone': phone_cleaned,  # phone_number가 아닌 phone
                'application_datetime': row.get('신청일시'),
                'installation_location': row.get('설치장소'),
                'address': row.get('주소'),
                'installation_count': row.get('설치대수'),
                'privacy_consent': row.get('개인정보동의'),
                'sheet_name': 'careon_applications' # 출처 시트 이름 추가
            }
            new_records.append(record)
            
    return new_records

def main():
    """
    스케줄러를 설정하고 동기화 작업을 주기적으로 실행하는 진입점 함수.
    """
    logger.info("CCTV 데이터 동기화 시스템이 시작되었습니다.")
    logger.info(f"매 {SCHEDULE_MINUTES}분마다 동기화 작업이 실행됩니다.")
    
    # 프로그램 시작 시 한 번 즉시 실행
    sync_and_notify()
    
    # 스케줄 설정
    schedule.every(SCHEDULE_MINUTES).minutes.do(sync_and_notify)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()