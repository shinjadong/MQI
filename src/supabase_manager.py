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

    def get_existing_identifiers(self, view_name: str, identifier_columns: List[str]) -> Set[Tuple]:
        """
        지정된 뷰에서 기존 데이터의 고유 식별자 집합을 가져옵니다.

        :param view_name: 조회할 Supabase 뷰 이름
        :param identifier_columns: 고유 식별자로 사용할 컬럼 리스트
        :return: 고유 식별자 튜플의 집합
        """
        try:
            select_query = ", ".join(identifier_columns)
            response = self.client.table(view_name).select(select_query).execute()
            
            if response.data:
                # 데이터베이스에서 받은 각 row를 튜플로 변환하여 집합에 추가
                # None 값을 처리하기 위해 str()으로 감싸서 비교의 안정성을 높임
                return {
                    tuple(str(item.get(col)) for col in identifier_columns) 
                    for item in response.data
                }
            return set()
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