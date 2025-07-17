#!/usr/bin/env python3
"""
CCTV Google Sheets to Supabase 자동 동기화 시스템
30분마다 Google Sheets를 다운로드하여 Claude AI가 분류한 결과를 customer_inquiries 테이블에 저장
"""

import os
import sys
import json
import logging
import pandas as pd
import schedule
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from supabase import create_client, Client
from google_sheets_manager_improved import GoogleSheetsManagerImproved
import anthropic
import asyncio
import re

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cctv_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIDataClassifier:
    """Claude AI를 활용한 데이터 분류 시스템"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.timeout = int(os.getenv('AI_CLASSIFICATION_TIMEOUT', '30'))
        
    def classify_data(self, sheet_name: str, data_sample: List[Dict]) -> Dict[str, Any]:
        """
        Google Sheets 데이터를 Claude AI가 분석하여 분류
        
        Args:
            sheet_name: 시트 이름
            data_sample: 분석할 데이터 샘플 (최대 5개)
            
        Returns:
            분류 결과 딕셔너리
        """
        try:
            # 샘플 데이터 준비 (최대 5개 레코드)
            sample_data = data_sample[:5] if len(data_sample) > 5 else data_sample
            
            # 분류 프롬프트 생성
            prompt = self._create_classification_prompt(sheet_name, sample_data)
            
            # Claude API 호출
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # 응답 파싱 - 텍스트 블록만 추출
            response_text = ""
            for content_block in response.content:
                if content_block.type == "text":
                    response_text += content_block.text
            
            return self._parse_classification_response(response_text)
            
        except Exception as e:
            logger.error(f"AI 분류 실패: {e}")
            return self._get_fallback_classification(sheet_name)
    
    def _create_classification_prompt(self, sheet_name: str, data_sample: List[Dict]) -> str:
        """분류를 위한 프롬프트 생성"""
        
        # 데이터 샘플을 읽기 쉬운 형태로 변환
        sample_text = ""
        for i, record in enumerate(data_sample, 1):
            sample_text += f"샘플 {i}:\n"
            for key, value in record.items():
                if pd.notna(value) and str(value).strip():
                    sample_text += f"  {key}: {value}\n"
            sample_text += "\n"
        
        prompt = f"""
다음은 Google Sheets에서 가져온 고객 데이터입니다. 이 데이터를 분석하여 어떤 유형의 문의인지 분류해주세요.

**시트 이름**: {sheet_name}

**데이터 샘플**:
{sample_text}

**분류 기준**:
1. **estimate**: 견적 문의 (CCTV 설치 견적, 카메라 개수, 예산 관련)
2. **consultation**: 상담 신청 (전화 상담, 방문 상담 요청)
3. **inquiry**: 일반 문의 (기타 질문, 제품 문의)
4. **cctv_management**: CCTV 관리 업무 (기존 고객 관리, 유지보수)
5. **careon_application**: 케어온 서비스 신청 (케어온 관련 데이터)

**응답 형식** (다음 JSON 형식으로만 응답):
```json
{{
  "inquiry_type": "분류된_타입",
  "confidence": 0.95,
  "reasoning": "분류 근거 설명",
  "suggested_mapping": {{
    "name": "이름_필드명",
    "phone": "전화번호_필드명", 
    "address": "주소_필드명",
    "entry_date": "인입날짜_필드명",
    "inquiry_source": "문의처_필드명",
    "channel": "채널_필드명"
  }}
}}
```

데이터 내용을 신중히 분석하여 가장 적절한 분류를 선택하고, 각 필드를 올바른 컬럼에 매핑해주세요.
"""
        return prompt
    
    def _parse_classification_response(self, response_text: str) -> Dict[str, Any]:
        """Claude 응답 파싱"""
        try:
            # JSON 블록 추출
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                return json.loads(json_text)
            
            # 직접 JSON 파싱 시도
            return json.loads(response_text.strip())
            
        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 실패: {response_text}")
            return {
                "inquiry_type": "inquiry",
                "confidence": 0.5,
                "reasoning": "파싱 실패로 인한 기본 분류",
                "suggested_mapping": {}
            }
    
    def _get_fallback_classification(self, sheet_name: str) -> Dict[str, Any]:
        """AI 분류 실패 시 기본 분류"""
        # 시트 이름 기반 기본 분류
        if 'careon' in sheet_name.lower() or '케어온' in sheet_name:
            return {
                "inquiry_type": "careon_application",
                "confidence": 0.8,
                "reasoning": "시트 이름 기반 분류 (케어온)",
                "suggested_mapping": {}
            }
        else:
            return {
                "inquiry_type": "cctv_management",
                "confidence": 0.8,
                "reasoning": "시트 이름 기반 분류 (CCTV 관리)",
                "suggested_mapping": {}
            }

class HeaderMapper:
    """시트별 헤더 매핑 클래스"""
    
    # 표준 헤더 매핑
    STANDARD_MAPPING = {
        'NO': 'no',
        'no': 'no',
        '번호': 'no',
        '순번': 'no',
        
        '인입날짜': 'entry_date',
        '날짜': 'entry_date',
        '접수일': 'entry_date',
        '등록일': 'entry_date',
        
        '문의': 'inquiry_source',
        '문의처': 'inquiry_source',
        '접수처': 'inquiry_source',
        
        '채널': 'channel',
        '유입채널': 'channel',
        '경로': 'channel',
        
        '지역': 'region',
        '지역명': 'region',
        '시도': 'region',
        
        '형태': 'form_type',
        '폼타입': 'form_type',
        '문의형태': 'form_type',
        
        '상담내용(EA)': 'consultation_content',
        '상담내용': 'consultation_content',
        '내용': 'consultation_content',
        
        '상담요청': 'consultation_request',
        '요청사항': 'consultation_request',
        
        '전화번호': 'phone',
        '연락처': 'phone',
        '휴대폰': 'phone',
        '핸드폰': 'phone',
        
        '이름': 'name',
        '성명': 'name',
        '고객명': 'name',
        
        '1차콜': 'first_call',
        '통화결과': 'first_call',
        '콜결과': 'first_call',
        
        '비고': 'notes',
        '메모': 'notes',
        '참고사항': 'notes',
        
        # 케어온 전용 필드
        '설치지역': 'installation_location',
        '설치일정': 'installation_schedule',
        '신청일시': 'application_datetime',
        '서비스': 'service_type'
    }
    
    @classmethod
    def map_headers(cls, headers: List[str], ai_mapping: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """헤더를 표준 필드명으로 매핑"""
        mapping = {}
        ai_mapping = ai_mapping or {}  # None인 경우 빈 dict로 초기화
        
        for header in headers:
            if header in cls.STANDARD_MAPPING:
                mapping[header] = cls.STANDARD_MAPPING[header]
            elif header in ai_mapping:
                mapping[header] = ai_mapping[header]
            else:
                # 기본 매핑: 소문자로 변환하고 공백을 언더스코어로 변경
                mapping[header] = header.lower().replace(' ', '_').replace('(', '').replace(')', '')
        
        return mapping

class CCTVSupabaseSync:
    """CCTV Google Sheets와 Supabase 동기화 시스템"""
    
    def __init__(self):
        # 환경 변수 검증
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.google_service_account = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.google_sheets_url = os.getenv('GOOGLE_SHEETS_URL')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # 필수 환경 변수 검증
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase 설정이 누락되었습니다.")
        if not self.google_service_account or not self.google_sheets_url:
            raise ValueError("Google Sheets 설정이 누락되었습니다.")
        
        self.enable_ai_classification = os.getenv('ENABLE_AI_CLASSIFICATION', 'true').lower() == 'true'
        
        # 클라이언트 초기화
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.sheets_manager = GoogleSheetsManagerImproved(self.google_service_account)
        
        # AI 분류기 초기화
        if self.enable_ai_classification and self.anthropic_api_key:
            self.ai_classifier = AIDataClassifier(self.anthropic_api_key)
        else:
            self.ai_classifier = None
            logger.warning("AI 분류 기능이 비활성화되어 있습니다.")
    
    def sync_data(self):
        """Google Sheets 데이터를 Supabase로 동기화"""
        try:
            logger.info("🔄 데이터 동기화 시작...")
            
            # Google Sheets URL 검증
            if not self.google_sheets_url:
                logger.error("❌ Google Sheets URL이 설정되지 않았습니다.")
                return
            
            # 스프레드시트 ID 추출
            spreadsheet_id = self.sheets_manager.extract_spreadsheet_id(self.google_sheets_url)
            
            # 시트 데이터 가져오기
            sheet_data = self.sheets_manager.get_sheet_data_advanced(spreadsheet_id)
            
            if not sheet_data or not sheet_data.get('data'):
                logger.error("❌ 시트 데이터를 가져올 수 없습니다.")
                return
            
            total_processed = 0
            
            for sheet_name, df in sheet_data['data'].items():
                if df.empty:
                    logger.info(f"⚠️ 빈 시트 건너뜀: {sheet_name}")
                    continue
                
                logger.info(f"📊 처리 중인 시트: {sheet_name} ({len(df)} 레코드)")
                
                # AI 분류 수행
                classification_result = self._classify_sheet_data(sheet_name, df)
                
                # 데이터 처리 및 삽입
                processed_count = self._process_and_insert_data(
                    sheet_name, df, classification_result
                )
                
                total_processed += processed_count
                
                # 동기화 로그 업데이트
                self._update_sync_log(sheet_name, processed_count, "success")
            
            logger.info(f"✅ 동기화 완료! 총 {total_processed}개 레코드 처리됨")
            
        except Exception as e:
            logger.error(f"❌ 동기화 실패: {e}")
            self._update_sync_log("전체", 0, "error", str(e))
    
    def _classify_sheet_data(self, sheet_name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """시트 데이터를 AI로 분류"""
        if not self.ai_classifier:
            # AI 분류기가 없을 때는 기본 분류 사용
            if 'careon' in sheet_name.lower() or '케어온' in sheet_name:
                return {
                    "inquiry_type": "careon_application",
                    "confidence": 0.8,
                    "reasoning": "시트 이름 기반 분류 (케어온)",
                    "suggested_mapping": {}
                }
            else:
                return {
                    "inquiry_type": "cctv_management",
                    "confidence": 0.8,
                    "reasoning": "시트 이름 기반 분류 (CCTV 관리)",
                    "suggested_mapping": {}
                }
        
        try:
            # 데이터 샘플 준비
            data_sample = []
            for _, row in df.head(5).iterrows():
                sample = {}
                for col in df.columns:
                    if pd.notna(row[col]):
                        str_value = str(row[col]).strip()
                        if len(str_value) > 0:
                            sample[col] = str_value
                data_sample.append(sample)
            
            logger.info(f"🤖 AI 분류 시작: {sheet_name}")
            
            # AI 분류 실행
            classification_result = self.ai_classifier.classify_data(sheet_name, data_sample)
            
            logger.info(f"🎯 AI 분류 결과: {classification_result['inquiry_type']} "
                       f"(신뢰도: {classification_result['confidence']:.2f})")
            
            return classification_result
            
        except Exception as e:
            logger.error(f"AI 분류 실패: {e}")
            return self.ai_classifier._get_fallback_classification(sheet_name)
    
    def _process_and_insert_data(self, sheet_name: str, df: pd.DataFrame, 
                                classification_result: Dict[str, Any]) -> int:
        """데이터 처리 및 삽입"""
        try:
            # 헤더 매핑
            ai_mapping = classification_result.get('suggested_mapping', {})
            header_mapping = HeaderMapper.map_headers(df.columns.tolist(), ai_mapping)
            
            # 데이터 변환
            processed_records = []
            inquiry_type = classification_result['inquiry_type']
            
            for _, row in df.iterrows():
                record = self._create_standard_record(row, header_mapping, sheet_name, inquiry_type)
                if record:
                    processed_records.append(record)
            
            # 배치 삽입
            if processed_records:
                self.supabase.table('customer_inquiries').insert(processed_records).execute()
                logger.info(f"✅ {len(processed_records)}개 레코드 삽입 완료: {sheet_name}")
                return len(processed_records)
            
            return 0
            
        except Exception as e:
            logger.error(f"데이터 처리 실패: {e}")
            return 0
    
    def _create_standard_record(self, row: pd.Series, header_mapping: Dict[str, str], 
                               sheet_name: str, inquiry_type: str) -> Optional[Dict]:
        """표준 레코드 생성"""
        try:
            # 기본 정보 추출
            name = self._extract_field(row, header_mapping, ['name', 'customer_name'])
            phone = self._extract_field(row, header_mapping, ['phone', 'phone_number'])
            
            # 빈 레코드 필터링 - 문자열 길이로 확인
            if len(name) == 0 and len(phone) == 0:
                return None
            
            # 표준 레코드 생성
            record = {
                'name': name or '',
                'phone': phone or '',
                'email': self._extract_field(row, header_mapping, ['email']),
                'address': self._extract_field(row, header_mapping, ['address']),
                'region': self._extract_field(row, header_mapping, ['region']),
                'inquiry_type': inquiry_type,
                'inquiry_source': self._extract_field(row, header_mapping, ['inquiry_source']),
                'channel': self._extract_field(row, header_mapping, ['channel']),
                'form_type': self._extract_field(row, header_mapping, ['form_type']),
                'consultation_content': self._extract_field(row, header_mapping, ['consultation_content']),
                'consultation_request': self._extract_field(row, header_mapping, ['consultation_request']),
                'first_call': self._extract_field(row, header_mapping, ['first_call']),
                'additional_notes': self._extract_field(row, header_mapping, ['notes']),
                'sheet_name': sheet_name,
                'status': 'pending',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # 케어온 전용 필드 추가
            if inquiry_type == 'careon_application':
                record.update({
                    'installation_location': self._extract_field(row, header_mapping, ['installation_location']),
                    'installation_schedule': self._extract_field(row, header_mapping, ['installation_schedule']),
                    'application_datetime': self._extract_field(row, header_mapping, ['application_datetime']),
                    'service_type': self._extract_field(row, header_mapping, ['service_type'])
                })
            
            return record
            
        except Exception as e:
            logger.error(f"레코드 생성 실패: {e}")
            return None
    
    def _extract_field(self, row: pd.Series, header_mapping: Dict[str, str], 
                      field_names: List[str]) -> str:
        """필드 값 추출"""
        for field_name in field_names:
            # 헤더 매핑에서 해당 필드를 찾음
            for original_header, mapped_field in header_mapping.items():
                if mapped_field == field_name and original_header in row.index:
                    value = row[original_header]
                    if pd.notna(value):
                        str_value = str(value).strip()
                        if len(str_value) > 0:
                            return str_value
        return ''
    
    def _update_sync_log(self, sheet_name: str, records_count: int, status: str, 
                        error_message: Optional[str] = None):
        """동기화 로그 업데이트"""
        try:
            log_entry = {
                'sheet_name': sheet_name,
                'records_count': records_count,
                'status': status,
                'sync_timestamp': datetime.now(timezone.utc).isoformat(),
                'error_message': error_message
            }
            
            self.supabase.table('sync_log').insert(log_entry).execute()
            
        except Exception as e:
            logger.error(f"로그 업데이트 실패: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        interval = int(os.getenv('SYNC_INTERVAL_MINUTES', '30'))
        
        schedule.every(interval).minutes.do(self.sync_data)
        
        logger.info(f"⏰ 스케줄러 시작: {interval}분마다 동기화")
        
        while True:
            schedule.run_pending()
            time.sleep(1)

def main():
    """메인 실행 함수"""
    sync_system = CCTVSupabaseSync()
    
    # 명령행 인자 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == 'once':
            # 한 번만 동기화
            sync_system.sync_data()
        elif sys.argv[1] == 'schedule':
            # 스케줄러 시작
            sync_system.start_scheduler()
    else:
        # 기본: 한 번만 동기화
        sync_system.sync_data()

if __name__ == "__main__":
    main()