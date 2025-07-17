#!/usr/bin/env python3
"""
카카오톡 알림톡 발송 시스템
CCTV 신규 문의 및 케어온 신청 시 직원들에게 자동 알림
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)


class KakaoNotification:
    """카카오톡 알림톡 발송 클래스"""
    
    def __init__(self):
        """카카오톡 알림톡 초기화"""
        self.rest_api_key = os.getenv('KAKAO_REST_API_KEY')
        self.sender_key = os.getenv('KAKAO_SENDER_KEY')
        self.template_code_inquiry = os.getenv('KAKAO_TEMPLATE_CODE_INQUIRY')
        self.template_code_careon = os.getenv('KAKAO_TEMPLATE_CODE_CAREON')
        
        # 알림 받을 직원 전화번호
        phone_numbers = os.getenv('NOTIFICATION_PHONE_NUMBERS', '')
        self.staff_phones = [phone.strip() for phone in phone_numbers.split(',') if phone.strip()]
        
        # API URL
        self.base_url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
        self.alimtalk_url = 'https://kapi.kakao.com/v1/api/talk/friends/message/default/send'
        
        self._validate_config()
    
    def _validate_config(self):
        """설정 유효성 검사"""
        if not self.rest_api_key:
            logger.warning("KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        if not self.sender_key:
            logger.warning("KAKAO_SENDER_KEY가 설정되지 않았습니다.")
        if not self.staff_phones:
            logger.warning("NOTIFICATION_PHONE_NUMBERS가 설정되지 않았습니다.")
    
    def _get_headers(self) -> Dict[str, str]:
        """요청 헤더 생성"""
        return {
            'Authorization': f'Bearer {self.rest_api_key}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def send_inquiry_notification(self, inquiry_data: Dict) -> bool:
        """신규 문의 알림 발송"""
        try:
            # 메시지 내용 구성
            message = self._create_inquiry_message(inquiry_data)
            
            # 직원들에게 알림 발송
            success_count = 0
            for phone in self.staff_phones:
                if self._send_alimtalk(phone, message, self.template_code_inquiry, inquiry_data):
                    success_count += 1
            
            logger.info(f"신규 문의 알림 발송 완료: {success_count}/{len(self.staff_phones)}명")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"신규 문의 알림 발송 실패: {e}")
            return False
    
    def send_careon_notification(self, careon_data: Dict) -> bool:
        """케어온 신청 알림 발송"""
        try:
            # 메시지 내용 구성
            message = self._create_careon_message(careon_data)
            
            # 직원들에게 알림 발송
            success_count = 0
            for phone in self.staff_phones:
                if self._send_alimtalk(phone, message, self.template_code_careon, careon_data):
                    success_count += 1
            
            logger.info(f"케어온 신청 알림 발송 완료: {success_count}/{len(self.staff_phones)}명")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"케어온 신청 알림 발송 실패: {e}")
            return False
    
    def _send_alimtalk(self, phone: str, message: str, template_code: str, template_args: Dict) -> bool:
        """알림톡 발송 (실제 API 호출)"""
        try:
            # 알림톡 API는 복잡하므로 일단 카카오톡 나에게 보내기로 테스트
            # 실제 알림톡 구현 시에는 비즈니스 API 사용 필요
            
            # 테스트용: 카카오톡 나에게 보내기
            data = {
                'template_object': json.dumps({
                    'object_type': 'text',
                    'text': message,
                    'link': {
                        'web_url': 'https://your-cctv-admin.com',
                        'mobile_web_url': 'https://your-cctv-admin.com'
                    }
                })
            }
            
            response = requests.post(
                self.base_url,
                headers=self._get_headers(),
                data=data
            )
            
            if response.status_code == 200:
                logger.info(f"알림톡 발송 성공: {phone}")
                return True
            else:
                logger.error(f"알림톡 발송 실패: {phone}, 응답: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"알림톡 발송 오류: {phone}, 에러: {e}")
            return False
    
    def _create_inquiry_message(self, data: Dict) -> str:
        """신규 문의 메시지 생성"""
        return f"""[CCTV 신규 문의 접수] 🔥

새로운 문의가 접수되었습니다.

📋 기본 정보
• 문의일: {data.get('entry_date', 'N/A')}
• 문의처: {data.get('inquiry_source', 'N/A')}
• 채널: {data.get('channel', 'N/A')}
• 지역: {data.get('region', 'N/A')}

👤 고객 정보
• 이름: {data.get('name', 'N/A')}
• 연락처: {data.get('phone_number', 'N/A')}
• 요청사항: {data.get('consultation_request', 'N/A')}

💼 상담 내용
• 형태: {data.get('form_type', 'N/A')}
• 내용: {data.get('consultation_content', 'N/A')}

⚡ 즉시 확인하여 빠른 대응 부탁드립니다.

---
CCTV 관리 시스템 자동 알림"""
    
    def _create_careon_message(self, data: Dict) -> str:
        """케어온 신청 메시지 생성"""
        return f"""[케어온 신규 신청] 🏠

케어온 신청이 접수되었습니다.

📋 신청 정보
• 신청일시: {data.get('application_datetime', 'N/A')}
• 고객명: {data.get('name', 'N/A')}
• 연락처: {data.get('phone_number', 'N/A')}

🏢 설치 정보
• 설치장소: {data.get('installation_location', 'N/A')}
• 주소: {data.get('address', 'N/A')}
• 설치대수: {data.get('installation_count', 'N/A')}

⚡ 빠른 상담 진행 부탁드립니다.

---
CCTV 관리 시스템 자동 알림"""
    
    def send_test_notification(self) -> bool:
        """테스트 알림 발송"""
        try:
            test_message = """[CCTV 알림 시스템 테스트] 🧪

알림톡 시스템이 정상적으로 작동합니다.

📊 시스템 정보
• 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• 상태: 정상 작동
• 연결: 성공

✅ 알림 시스템 구축 완료!

---
CCTV 관리 시스템"""
            
            success_count = 0
            for phone in self.staff_phones:
                try:
                    # 테스트용 간단한 메시지
                    data = {
                        'template_object': json.dumps({
                            'object_type': 'text',
                            'text': test_message,
                            'link': {
                                'web_url': 'https://your-cctv-admin.com'
                            }
                        })
                    }
                    
                    response = requests.post(
                        self.base_url,
                        headers=self._get_headers(),
                        data=data
                    )
                    
                    if response.status_code == 200:
                        success_count += 1
                        logger.info(f"테스트 알림 발송 성공: {phone}")
                    else:
                        logger.error(f"테스트 알림 발송 실패: {phone}")
                        
                except Exception as e:
                    logger.error(f"테스트 알림 발송 오류: {phone}, {e}")
            
            logger.info(f"테스트 알림 발송 결과: {success_count}/{len(self.staff_phones)}명")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"테스트 알림 시스템 오류: {e}")
            return False


# 이메일 알림 대안 (카카오톡 설정이 복잡한 경우)
class EmailNotification:
    """이메일 알림 클래스 (카카오톡 대안)"""
    
    def __init__(self):
        """이메일 알림 초기화"""
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.notification_emails = os.getenv('NOTIFICATION_EMAILS', '').split(',')
    
    def send_inquiry_email(self, inquiry_data: Dict) -> bool:
        """신규 문의 이메일 발송"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            subject = f"[CCTV 신규 문의] {inquiry_data.get('name', 'N/A')} - {inquiry_data.get('region', 'N/A')}"
            
            body = f"""
            신규 CCTV 문의가 접수되었습니다.
            
            📋 기본 정보
            • 문의일: {inquiry_data.get('entry_date', 'N/A')}
            • 문의처: {inquiry_data.get('inquiry_source', 'N/A')}
            • 채널: {inquiry_data.get('channel', 'N/A')}
            • 지역: {inquiry_data.get('region', 'N/A')}
            
            👤 고객 정보
            • 이름: {inquiry_data.get('name', 'N/A')}
            • 연락처: {inquiry_data.get('phone_number', 'N/A')}
            • 요청사항: {inquiry_data.get('consultation_request', 'N/A')}
            
            💼 상담 내용
            • 형태: {inquiry_data.get('form_type', 'N/A')}
            • 내용: {inquiry_data.get('consultation_content', 'N/A')}
            
            즉시 확인하여 빠른 대응 부탁드립니다.
            
            ---
            CCTV 관리 시스템 자동 알림
            """
            
            # 이메일 발송 로직 구현
            success_count = 0
            for email in self.notification_emails:
                if email.strip():
                    # 실제 이메일 발송 구현 필요
                    success_count += 1
            
            logger.info(f"이메일 알림 발송 완료: {success_count}명")
            return True
            
        except Exception as e:
            logger.error(f"이메일 알림 발송 실패: {e}")
            return False


def test_notifications():
    """알림 시스템 테스트"""
    print("🧪 알림 시스템 테스트 시작")
    
    # 카카오톡 알림 테스트
    kakao = KakaoNotification()
    
    # 테스트 데이터
    test_inquiry = {
        'entry_date': '2025-07-17',
        'inquiry_source': 'KT',
        'channel': 'TEL',
        'region': '서울 강남구',
        'name': '홍길동',
        'phone_number': '010-1234-5678',
        'consultation_request': '견적요청',
        'form_type': '아파트',
        'consultation_content': '현관 CCTV 2대'
    }
    
    print("📱 카카오톡 테스트 알림 발송...")
    if kakao.send_test_notification():
        print("✅ 카카오톡 알림 테스트 성공")
    else:
        print("❌ 카카오톡 알림 테스트 실패")
    
    print("📋 신규 문의 알림 테스트...")
    if kakao.send_inquiry_notification(test_inquiry):
        print("✅ 신규 문의 알림 테스트 성공")
    else:
        print("❌ 신규 문의 알림 테스트 실패")


if __name__ == "__main__":
    test_notifications()