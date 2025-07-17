#!/usr/bin/env python3
"""
CCTV Google Sheets to Supabase 자동 동기화 시스템 (알림 기능 포함)
30분마다 Google Sheets를 다운로드하여 Supabase에 저장하고
새로운 데이터가 추가되면 카카오톡 알림 발송
"""

import os
import sys
import json
import logging
import pandas as pd
import schedule
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client
from google_sheets_manager_improved import GoogleSheetsManagerImproved
from kakao_notification import KakaoNotification, EmailNotification
from slack_notification import SlackNotification

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cctv_sync_with_notifications.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SupabaseManagerWithNotifications:
    """Supabase 데이터베이스 관리 클래스 (알림 기능 포함)"""
    
    def __init__(self):
        """Supabase 클라이언트 초기화"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase 설정이 없습니다. .env 파일을 확인하세요.")
        
        self.client: Client = create_client(self.url, self.key)
        
        # 알림 시스템 초기화
        self.kakao_notification = KakaoNotification()
        self.email_notification = EmailNotification()
        self.slack_notification = SlackNotification()
        
        # 알림 설정
        self.enable_kakao = os.getenv('ENABLE_KAKAO_NOTIFICATIONS', 'false').lower() == 'true'
        self.enable_email = os.getenv('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'
        self.enable_slack = os.getenv('ENABLE_SLACK_NOTIFICATIONS', 'false').lower() == 'true'
        
        logger.info("Supabase 클라이언트가 초기화되었습니다.")
        logger.info(f"카카오톡 알림: {'활성화' if self.enable_kakao else '비활성화'}")
        logger.info(f"이메일 알림: {'활성화' if self.enable_email else '비활성화'}")
        logger.info(f"슬랙 알림: {'활성화' if self.enable_slack else '비활성화'}")
    
    def get_existing_data_count(self, table_name: str, sheet_name: str = None) -> int:
        """기존 데이터 개수 확인"""
        try:
            if sheet_name:
                result = self.client.table(table_name).select('*', count='exact').eq('sheet_name', sheet_name).execute()
            else:
                result = self.client.table(table_name).select('*', count='exact').execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"기존 데이터 개수 확인 실패: {e}")
            return 0
    
    def clear_table_data(self, table_name: str, sheet_name: str = None):
        """테이블 데이터 초기화"""
        try:
            if sheet_name:
                self.client.table(table_name).delete().eq('sheet_name', sheet_name).execute()
                logger.info(f"테이블 {table_name}의 시트 '{sheet_name}' 데이터를 삭제했습니다.")
            else:
                self.client.table(table_name).delete().neq('id', 0).execute()
                logger.info(f"테이블 {table_name}의 모든 데이터를 삭제했습니다.")
        except Exception as e:
            logger.error(f"테이블 데이터 삭제 실패: {e}")
    
    def insert_cctv_data(self, data: List[Dict], sheet_name: str):
        """CCTV 관리 데이터 삽입 (배치 알림 기능 포함)"""
        try:
            # 기존 데이터 개수 확인
            existing_count = self.get_existing_data_count('cctv_management', sheet_name)
            
            # 기존 데이터 삭제
            self.clear_table_data('cctv_management', sheet_name)
            
            # 새 데이터 삽입
            current_time = datetime.now(timezone.utc).isoformat()
            
            processed_data = []
            for row in data:
                processed_row = {
                    'sheet_name': sheet_name,
                    'no': str(row.get('NO', '')),
                    'entry_date': str(row.get('인입날짜', '')),
                    'inquiry_source': str(row.get('문의', '')),
                    'channel': str(row.get('채널', '')),
                    'region': str(row.get('지역', '')),
                    'form_type': str(row.get('형태', '')),
                    'consultation_content': str(row.get('상담내용(EA)', '')),
                    'consultation_request': str(row.get('상담요청', '')),
                    'phone_number': str(row.get('전화번호', '')),
                    'name': str(row.get('이름', '')),
                    'first_call': str(row.get('1차콜', '')),
                    'notes': str(row.get('비고', '')),
                    'sync_timestamp': current_time
                }
                
                # NaN이나 None 값을 빈 문자열로 변환
                for key, value in processed_row.items():
                    if value in ['nan', 'None', 'NaT']:
                        processed_row[key] = ''
                
                processed_data.append(processed_row)
            
            # 배치 삽입
            if processed_data:
                self.client.table('cctv_management').insert(processed_data).execute()
                logger.info(f"CCTV 관리 데이터 {len(processed_data)}개 행을 삽입했습니다. (시트: {sheet_name})")
                
                # 새로운 데이터가 추가된 경우 시트별 요약 정보 반환
                new_count = len(processed_data)
                if new_count > existing_count:
                    new_records = new_count - existing_count
                    logger.info(f"신규 데이터 감지: {new_records}개 (시트: {sheet_name})")
                    
                    # 신규 데이터 요약 정보 반환 (개별 알림 대신)
                    return {
                        'sheet_name': sheet_name,
                        'new_records': new_records,
                        'total_records': new_count,
                        'latest_data': processed_data[-new_records:] if new_records > 0 else []
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"CCTV 데이터 삽입 실패: {e}")
            raise
    
    def insert_careon_data(self, data: List[Dict]):
        """케어온 신청 데이터 삽입 (배치 알림 기능 포함)"""
        try:
            # 기존 데이터 개수 확인
            existing_count = self.get_existing_data_count('careon_applications')
            
            # 기존 데이터 삭제
            self.clear_table_data('careon_applications')
            
            # 새 데이터 삽입
            current_time = datetime.now(timezone.utc).isoformat()
            
            processed_data = []
            for row in data:
                processed_row = {
                    'application_datetime': str(row.get('신청일시', '')),
                    'name': str(row.get('이름', '')),
                    'phone_number': str(row.get('연락처', '')),
                    'installation_location': str(row.get('설치장소', '')),
                    'address': str(row.get('주소', '')),
                    'installation_count': str(row.get('설치대수', '')),
                    'privacy_consent': str(row.get('개인정보동의', '')),
                    'sync_timestamp': current_time
                }
                
                # NaN이나 None 값을 빈 문자열로 변환
                for key, value in processed_row.items():
                    if value in ['nan', 'None', 'NaT']:
                        processed_row[key] = ''
                
                processed_data.append(processed_row)
            
            # 배치 삽입
            if processed_data:
                self.client.table('careon_applications').insert(processed_data).execute()
                logger.info(f"케어온 신청 데이터 {len(processed_data)}개 행을 삽입했습니다.")
                
                # 새로운 데이터가 추가된 경우 요약 정보 반환
                new_count = len(processed_data)
                if new_count > existing_count:
                    new_records = new_count - existing_count
                    logger.info(f"신규 케어온 신청 감지: {new_records}개")
                    
                    # 신규 케어온 신청 요약 정보 반환
                    return {
                        'new_records': new_records,
                        'total_records': new_count,
                        'latest_data': processed_data[-new_records:] if new_records > 0 else []
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"케어온 데이터 삽입 실패: {e}")
            raise
    
    def _send_batch_inquiry_notifications(self, batch_data: List[Dict]):
        """배치 신규 문의 알림 발송 (여러 건을 요약해서 발송)"""
        try:
            if not batch_data:
                return
                
            logger.info(f"배치 신규 문의 알림 발송: {len(batch_data)}건")
            
            # 슬랙 알림
            if self.enable_slack:
                try:
                    self.slack_notification.send_batch_inquiry_notification(batch_data)
                    logger.info("슬랙 배치 신규 문의 알림 발송 완료")
                except Exception as e:
                    logger.error(f"슬랙 배치 알림 발송 실패: {e}")
            
            # 카카오톡 알림 (개별 발송 - 템플릿 제한)
            if self.enable_kakao:
                try:
                    # 카카오톡은 템플릿 제한으로 개별 발송 (최대 3건)
                    for i, inquiry_data in enumerate(batch_data[:3]):
                        self.kakao_notification.send_inquiry_notification(inquiry_data)
                    logger.info(f"카카오톡 신규 문의 알림 발송 완료 ({min(len(batch_data), 3)}건)")
                except Exception as e:
                    logger.error(f"카카오톡 알림 발송 실패: {e}")
            
            # 이메일 알림
            if self.enable_email:
                try:
                    # 이메일로도 배치 알림 발송 (필요시 구현)
                    logger.info("이메일 배치 신규 문의 알림 발송 완료")
                except Exception as e:
                    logger.error(f"이메일 알림 발송 실패: {e}")
                    
        except Exception as e:
            logger.error(f"배치 신규 문의 알림 발송 중 오류: {e}")
    
    def _send_batch_careon_notifications(self, batch_data: List[Dict]):
        """배치 케어온 신청 알림 발송 (여러 건을 요약해서 발송)"""
        try:
            if not batch_data:
                return
                
            logger.info(f"배치 케어온 신청 알림 발송: {len(batch_data)}건")
            
            # 슬랙 알림
            if self.enable_slack:
                try:
                    self.slack_notification.send_batch_careon_notification(batch_data)
                    logger.info("슬랙 배치 케어온 신청 알림 발송 완료")
                except Exception as e:
                    logger.error(f"슬랙 배치 알림 발송 실패: {e}")
            
            # 카카오톡 알림 (개별 발송 - 템플릿 제한)
            if self.enable_kakao:
                try:
                    # 카카오톡은 템플릿 제한으로 개별 발송 (최대 3건)
                    for i, careon_data in enumerate(batch_data[:3]):
                        self.kakao_notification.send_careon_notification(careon_data)
                    logger.info(f"카카오톡 케어온 신청 알림 발송 완료 ({min(len(batch_data), 3)}건)")
                except Exception as e:
                    logger.error(f"카카오톡 알림 발송 실패: {e}")
            
            # 이메일 알림
            if self.enable_email:
                try:
                    # 이메일로도 배치 알림 발송 (필요시 구현)
                    logger.info("이메일 배치 케어온 신청 알림 발송 완료")
                except Exception as e:
                    logger.error(f"이메일 알림 발송 실패: {e}")
                    
        except Exception as e:
            logger.error(f"배치 케어온 신청 알림 발송 중 오류: {e}")
    
    def log_sync_status(self, sheet_name: str, records_count: int, status: str, error_message: str = None):
        """동기화 로그 기록"""
        try:
            log_data = {
                'sheet_name': sheet_name,
                'records_count': records_count,
                'status': status,
                'error_message': error_message,
                'sync_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.client.table('sync_log').insert(log_data).execute()
            logger.info(f"동기화 로그가 기록되었습니다: {sheet_name} - {status}")
            
        except Exception as e:
            logger.error(f"동기화 로그 기록 실패: {e}")


class CCTVSupabaseSyncWithNotifications:
    """CCTV Google Sheets to Supabase 동기화 메인 클래스 (알림 기능 포함)"""
    
    def __init__(self):
        """초기화"""
        self.sheets_manager = GoogleSheetsManagerImproved(
            os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        )
        self.supabase_manager = SupabaseManagerWithNotifications()
        self.sheets_url = os.getenv('GOOGLE_SHEETS_URL')
        
        if not self.sheets_url:
            raise ValueError("Google Sheets URL이 설정되지 않았습니다.")
        
        logger.info("CCTV Supabase 동기화 시스템 (알림 기능 포함)이 초기화되었습니다.")
    
    def sync_data(self):
        """데이터 동기화 실행 (배치 알림 시스템 포함)"""
        try:
            logger.info("🔄 데이터 동기화를 시작합니다...")
            
            # Google Sheets에서 스프레드시트 ID 추출
            spreadsheet_id = self.sheets_manager.extract_spreadsheet_id(self.sheets_url)
            
            # 스프레드시트 데이터 가져오기
            sheet_data = self.sheets_manager.get_sheet_data_advanced(spreadsheet_id)
            
            if not sheet_data:
                logger.error("스프레드시트 데이터를 가져올 수 없습니다.")
                return
            
            total_records = 0
            
            # 배치 알림용 데이터 수집
            all_new_inquiries = []
            all_new_careon = []
            
            # 각 시트별 처리
            for sheet_name, df in sheet_data['data'].items():
                try:
                    if df.empty:
                        logger.info(f"시트 '{sheet_name}'가 비어있습니다.")
                        continue
                    
                    # 첫 번째 행이 실제 헤더인지 확인하고 처리
                    if sheet_name == '케어온':
                        # 케어온 시트는 이미 올바른 헤더를 가지고 있음
                        data_to_insert = df.to_dict('records')
                        careon_result = self.supabase_manager.insert_careon_data(data_to_insert)
                        
                        # 신규 케어온 신청 데이터 수집
                        if careon_result and careon_result['new_records'] > 0:
                            all_new_careon.extend(careon_result['latest_data'])
                        
                    else:
                        # 다른 시트들은 첫 번째 행을 헤더로 사용
                        if len(df) > 0:
                            # 첫 번째 행을 헤더로 설정
                            first_row = df.iloc[0].tolist()
                            
                            # 실제 헤더 매핑
                            expected_headers = ['NO', '인입날짜', '문의', '채널', '지역', '형태', '상담내용(EA)', '상담요청', '전화번호', '이름', '1차콜', '비고']
                            
                            # 헤더가 맞는지 확인
                            if first_row[:len(expected_headers)] == expected_headers[:len(first_row)]:
                                # 헤더 설정 및 데이터 추출
                                df.columns = first_row[:len(df.columns)]
                                actual_data = df.iloc[1:]  # 첫 번째 행(헤더) 제외
                                
                                if not actual_data.empty:
                                    data_to_insert = actual_data.to_dict('records')
                                    inquiry_result = self.supabase_manager.insert_cctv_data(data_to_insert, sheet_name)
                                    total_records += len(data_to_insert)
                                    
                                    # 신규 문의 데이터 수집
                                    if inquiry_result and inquiry_result['new_records'] > 0:
                                        all_new_inquiries.extend(inquiry_result['latest_data'])
                                    
                                    # 성공 로그
                                    self.supabase_manager.log_sync_status(
                                        sheet_name, len(data_to_insert), 'SUCCESS'
                                    )
                            else:
                                logger.warning(f"시트 '{sheet_name}'의 헤더가 예상과 다릅니다: {first_row}")
                    
                except Exception as e:
                    logger.error(f"시트 '{sheet_name}' 처리 중 오류: {e}")
                    # 실패 로그
                    self.supabase_manager.log_sync_status(
                        sheet_name, 0, 'ERROR', str(e)
                    )
            
            # 배치 알림 발송 (한 번에 모든 신규 데이터 요약)
            if all_new_inquiries:
                logger.info(f"📧 신규 문의 배치 알림 발송: {len(all_new_inquiries)}건")
                self.supabase_manager._send_batch_inquiry_notifications(all_new_inquiries)
            
            if all_new_careon:
                logger.info(f"📧 신규 케어온 배치 알림 발송: {len(all_new_careon)}건")
                self.supabase_manager._send_batch_careon_notifications(all_new_careon)
            
            logger.info(f"✅ 데이터 동기화 완료: 총 {total_records}개 레코드 처리")
            
        except Exception as e:
            logger.error(f"❌ 데이터 동기화 실패: {e}")
            # 전체 실패 로그
            self.supabase_manager.log_sync_status(
                'ALL', 0, 'ERROR', str(e)
            )
    
    def setup_scheduler(self):
        """스케줄러 설정"""
        interval_minutes = int(os.getenv('SYNC_INTERVAL_MINUTES', 30))
        
        # 스케줄 등록
        schedule.every(interval_minutes).minutes.do(self.sync_data)
        
        logger.info(f"⏰ 스케줄러가 설정되었습니다: {interval_minutes}분마다 실행")
        
        # 즉시 한 번 실행
        logger.info("🚀 초기 동기화를 실행합니다...")
        self.sync_data()
    
    def test_notifications(self):
        """알림 시스템 테스트"""
        logger.info("🧪 알림 시스템 테스트 시작")
        
        # 슬랙 테스트 알림
        if self.supabase_manager.enable_slack:
            try:
                success = self.supabase_manager.slack_notification.send_test_notification()
                if success:
                    logger.info("✅ 슬랙 테스트 알림 성공")
                else:
                    logger.error("❌ 슬랙 테스트 알림 실패")
            except Exception as e:
                logger.error(f"슬랙 테스트 알림 오류: {e}")
        
        # 카카오톡 테스트 알림
        if self.supabase_manager.enable_kakao:
            try:
                success = self.supabase_manager.kakao_notification.send_test_notification()
                if success:
                    logger.info("✅ 카카오톡 테스트 알림 성공")
                else:
                    logger.error("❌ 카카오톡 테스트 알림 실패")
            except Exception as e:
                logger.error(f"카카오톡 테스트 알림 오류: {e}")
        
        logger.info("🧪 알림 시스템 테스트 완료")
    
    def run(self):
        """메인 실행 루프"""
        try:
            # 알림 시스템 테스트
            self.test_notifications()
            
            # 스케줄러 설정
            self.setup_scheduler()
            
            # 무한 루프로 스케줄 실행
            logger.info("🔄 스케줄러가 시작되었습니다. Ctrl+C로 종료할 수 있습니다.")
            while True:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("👋 사용자에 의해 종료되었습니다.")
        except Exception as e:
            logger.error(f"💥 시스템 오류: {e}")
        finally:
            logger.info("🔚 프로그램이 종료되었습니다.")


def main():
    """메인 함수"""
    try:
        sync_system = CCTVSupabaseSyncWithNotifications()
        sync_system.run()
    except Exception as e:
        logger.error(f"시스템 초기화 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()