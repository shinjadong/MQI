import logging
from typing import List, Dict, Any, Set, Tuple

class SupabaseManager:
    """Supabase 데이터베이스 관련 작업을 관리하는 클래스"""

    def __init__(self, supabase_client):
        """
        SupabaseManager를 초기화합니다.

        :param supabase_client: Supabase 클라이언트 인스턴스
        """
        self.client = supabase_client
        self.logger = logging.getLogger(__name__)

    def get_existing_identifiers(self, view_name: str, identifier_columns: list) -> set:
        """
        지정된 뷰에서 기존 데이터의 고유 식별자를 가져옵니다.
        
        Args:
            view_name: 조회할 뷰 이름
            identifier_columns: 고유 식별자로 사용할 컬럼 리스트
            
        Returns:
            (name, phone) 튜플의 집합
        """
        try:
            # careon_applications는 phone_number를 사용하고, 나머지는 phone를 사용
            if view_name == 'careon_applications':
                response = self.client.table(view_name).select(','.join(identifier_columns)).execute()
                existing_identifiers = set()
                
                for row in response.data:
                    name = row.get('name')
                    phone = row.get('phone_number')
                    if name and phone:
                        existing_identifiers.add((str(name), str(phone)))
            else:
                # identifier_columns에서 phone_number를 phone으로 변경
                db_columns = []
                for col in identifier_columns:
                    if col == 'phone_number':
                        db_columns.append('phone')
                    else:
                        db_columns.append(col)
                
                response = self.client.table(view_name).select(','.join(db_columns)).execute()
                existing_identifiers = set()
                
                for row in response.data:
                    name = row.get('name')
                    phone = row.get('phone')
                    if name and phone:
                        existing_identifiers.add((str(name), str(phone)))
                    
            return existing_identifiers
        except Exception as e:
            self.logger.error(f"'{view_name}' 뷰에서 기존 식별자 조회 실패: {e}")
            return set()

    def insert_customer_inquiries(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        'customer_inquiries' 테이블에 여러 레코드를 한 번에 삽입합니다.

        :param records: 삽입할 레코드 딕셔너리의 리스트
        :return: 삽입에 성공한 레코드 리스트
        """
        if not records:
            return []
        
        try:
            response = self.client.table('customer_inquiries').insert(records).execute()
            if len(response.data) > 0:
                self.logger.info(f"{len(records)}개의 신규 문의를 'customer_inquiries'에 성공적으로 삽입했습니다.")
                return response.data
            else:
                self.logger.error(f"데이터 삽입 실패 (No data returned): {response}")
                return []
        except Exception as e:
            self.logger.error(f"'customer_inquiries'에 데이터 삽입 실패: {e}")
            return []

    def log_sync_status(self, sheet_name: str, status: str, count: int = 0, error_message: str = None):
        """
        동기화 작업의 결과를 'sync_log' 테이블에 기록합니다.

        :param sheet_name: 동기화된 시트 이름
        :param status: 동기화 상태 ('SUCCESS' 또는 'ERROR')
        :param count: 처리된 레코드 수
        :param error_message: 오류 발생 시 기록할 메시지
        """
        try:
            log_entry = {
                'sheet_name': sheet_name,
                'status': status,
                'records_count': count,
                'error_message': error_message
            }
            self.client.table('sync_log').insert(log_entry).execute()
            self.logger.info(f"동기화 로그가 기록되었습니다: {sheet_name} - {status}")
        except Exception as e:
            self.logger.error(f"동기화 로그 기록 실패: {e}") 