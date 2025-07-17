#!/usr/bin/env python3
"""
슬랙 알림 시스템 (카카오톡 대안)
CCTV 신규 문의 및 케어온 신청 시 슬랙으로 알림 발송
"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

logger = logging.getLogger(__name__)


class SlackNotification:
    """슬랙 알림 클래스 (카카오톡보다 간단하고 무료)"""
    
    def __init__(self):
        """슬랙 알림 초기화"""
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL이 설정되지 않았습니다.")
    
    def send_inquiry_notification(self, inquiry_data: Dict) -> bool:
        """신규 문의 슬랙 알림 발송"""
        try:
            # 슬랙 메시지 구성
            message = {
                "text": "🔥 CCTV 신규 문의 접수",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🔥 CCTV 신규 문의 접수"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*문의일:*\n{inquiry_data.get('entry_date', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*문의처:*\n{inquiry_data.get('inquiry_source', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*채널:*\n{inquiry_data.get('channel', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*지역:*\n{inquiry_data.get('region', 'N/A')}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*고객명:*\n{inquiry_data.get('name', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*연락처:*\n{inquiry_data.get('phone_number', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*형태:*\n{inquiry_data.get('form_type', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*요청사항:*\n{inquiry_data.get('consultation_request', 'N/A')}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*상담내용:*\n{inquiry_data.get('consultation_content', 'N/A')}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "⚡ 즉시 확인하여 빠른 대응 부탁드립니다."
                            }
                        ]
                    }
                ]
            }
            
            # 슬랙 Webhook으로 메시지 발송
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(message)
            )
            
            if response.status_code == 200:
                logger.info("슬랙 신규 문의 알림 발송 성공")
                return True
            else:
                logger.error(f"슬랙 알림 발송 실패: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"슬랙 알림 발송 오류: {e}")
            return False
    
    def send_careon_notification(self, careon_data: Dict) -> bool:
        """케어온 신청 슬랙 알림 발송"""
        try:
            # 슬랙 메시지 구성
            message = {
                "text": "🏠 케어온 신규 신청",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🏠 케어온 신규 신청"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*신청일시:*\n{careon_data.get('application_datetime', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*고객명:*\n{careon_data.get('name', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*연락처:*\n{careon_data.get('phone_number', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*설치대수:*\n{careon_data.get('installation_count', 'N/A')}"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*설치장소:*\n{careon_data.get('installation_location', 'N/A')}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*주소:*\n{careon_data.get('address', 'N/A')}"
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "⚡ 빠른 상담 진행 부탁드립니다."
                            }
                        ]
                    }
                ]
            }
            
            # 슬랙 Webhook으로 메시지 발송
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(message)
            )
            
            if response.status_code == 200:
                logger.info("슬랙 케어온 신청 알림 발송 성공")
                return True
            else:
                logger.error(f"슬랙 알림 발송 실패: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"슬랙 알림 발송 오류: {e}")
            return False
    
    def send_batch_inquiry_notification(self, batch_data: List[Dict]) -> bool:
        """배치 신규 문의 알림 발송 (여러 건을 요약해서 발송)"""
        try:
            if not batch_data:
                return False
                
            total_count = len(batch_data)
            
            # 지역별 집계
            region_stats = {}
            for item in batch_data:
                region = item.get('region', 'N/A')
                if region in region_stats:
                    region_stats[region] += 1
                else:
                    region_stats[region] = 1
            
            # 상위 3개 지역 표시
            top_regions = sorted(region_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # 최근 3건 상세 정보
            latest_items = batch_data[-3:]
            
            # 슬랙 메시지 구성
            message = {
                "text": f"🔥 CCTV 신규 문의 {total_count}건 접수",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🔥 CCTV 신규 문의 {total_count}건 접수"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*총 문의 수:*\n{total_count}건"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*동기화 시간:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
            
            # 지역별 통계 추가
            if top_regions:
                region_text = "\n".join([f"• {region}: {count}건" for region, count in top_regions])
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*지역별 통계:*\n{region_text}"
                    }
                })
            
            # 최근 문의 3건 상세 정보
            if latest_items:
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*최근 접수 문의 (최대 3건):*"
                    }
                })
                
                for i, item in enumerate(latest_items):
                    message["blocks"].append({
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*{i+1}. {item.get('name', 'N/A')}*\n{item.get('phone_number', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*지역:*\n{item.get('region', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*문의내용:*\n{item.get('consultation_content', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*요청사항:*\n{item.get('consultation_request', 'N/A')}"
                            }
                        ]
                    })
            
            # 액션 메시지 추가
            message["blocks"].append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "⚡ 즉시 확인하여 빠른 대응 부탁드립니다."
                    }
                ]
            })
            
            # 슬랙 Webhook으로 메시지 발송
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(message)
            )
            
            if response.status_code == 200:
                logger.info(f"슬랙 배치 신규 문의 알림 발송 성공: {total_count}건")
                return True
            else:
                logger.error(f"슬랙 배치 알림 발송 실패: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"슬랙 배치 알림 발송 오류: {e}")
            return False
    
    def send_batch_careon_notification(self, batch_data: List[Dict]) -> bool:
        """배치 케어온 신청 알림 발송 (여러 건을 요약해서 발송)"""
        try:
            if not batch_data:
                return False
                
            total_count = len(batch_data)
            
            # 설치 대수 총합 계산
            total_installations = 0
            for item in batch_data:
                try:
                    count_str = str(item.get('installation_count', '0'))
                    count = int(''.join(filter(str.isdigit, count_str))) if count_str else 0
                    total_installations += count
                except:
                    pass
            
            # 최근 3건 상세 정보
            latest_items = batch_data[-3:]
            
            # 슬랙 메시지 구성
            message = {
                "text": f"🏠 케어온 신규 신청 {total_count}건",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🏠 케어온 신규 신청 {total_count}건"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*총 신청 수:*\n{total_count}건"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*총 설치 예상:*\n{total_installations}대"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*동기화 시간:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            }
                        ]
                    }
                ]
            }
            
            # 최근 신청 3건 상세 정보
            if latest_items:
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*최근 신청 내역 (최대 3건):*"
                    }
                })
                
                for i, item in enumerate(latest_items):
                    message["blocks"].append({
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*{i+1}. {item.get('name', 'N/A')}*\n{item.get('phone_number', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*설치장소:*\n{item.get('installation_location', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*설치대수:*\n{item.get('installation_count', 'N/A')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*주소:*\n{item.get('address', 'N/A')}"
                            }
                        ]
                    })
            
            # 액션 메시지 추가
            message["blocks"].append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "⚡ 빠른 상담 진행 부탁드립니다."
                    }
                ]
            })
            
            # 슬랙 Webhook으로 메시지 발송
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(message)
            )
            
            if response.status_code == 200:
                logger.info(f"슬랙 배치 케어온 신청 알림 발송 성공: {total_count}건")
                return True
            else:
                logger.error(f"슬랙 배치 알림 발송 실패: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"슬랙 배치 알림 발송 오류: {e}")
            return False
    
    def send_test_notification(self) -> bool:
        """슬랙 테스트 알림 발송"""
        try:
            message = {
                "text": "🧪 CCTV 알림 시스템 테스트",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🧪 CCTV 알림 시스템 테스트"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*테스트 시간:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*상태:*\n정상 작동"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "✅ 슬랙 알림 시스템이 정상적으로 작동합니다!"
                        }
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(message)
            )
            
            if response.status_code == 200:
                logger.info("슬랙 테스트 알림 발송 성공")
                return True
            else:
                logger.error(f"슬랙 테스트 알림 발송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"슬랙 테스트 알림 오류: {e}")
            return False


def test_slack_notification():
    """슬랙 알림 테스트"""
    print("🧪 슬랙 알림 시스템 테스트 시작")
    
    slack = SlackNotification()
    
    # 테스트 알림 발송
    print("📱 슬랙 테스트 알림 발송...")
    if slack.send_test_notification():
        print("✅ 슬랙 테스트 알림 성공")
    else:
        print("❌ 슬랙 테스트 알림 실패")
    
    # 테스트 문의 데이터 (개별)
    test_inquiry = {
        'entry_date': '2025-07-17',
        'inquiry_source': 'KT',
        'channel': 'TEL',
        'region': '서울 강남구',
        'name': '홍길동',
        'phone_number': '010-1234-5678',
        'consultation_request': '견적요청',
        'form_type': '아파트',
        'consultation_content': '현관 CCTV 2대 설치 문의'
    }
    
    print("📋 신규 문의 알림 테스트...")
    if slack.send_inquiry_notification(test_inquiry):
        print("✅ 신규 문의 알림 성공")
    else:
        print("❌ 신규 문의 알림 실패")
    
    # 배치 문의 데이터 테스트
    batch_inquiries = [
        {
            'entry_date': '2025-07-17',
            'inquiry_source': 'KT',
            'channel': 'TEL',
            'region': '서울 강남구',
            'name': '홍길동',
            'phone_number': '010-1234-5678',
            'consultation_request': '견적요청',
            'form_type': '아파트',
            'consultation_content': '현관 CCTV 2대 설치 문의'
        },
        {
            'entry_date': '2025-07-17',
            'inquiry_source': 'LG',
            'channel': 'WEB',
            'region': '부산 해운대구',
            'name': '김철수',
            'phone_number': '010-9876-5432',
            'consultation_request': '상담요청',
            'form_type': '주택',
            'consultation_content': '마당 CCTV 4대 설치 문의'
        },
        {
            'entry_date': '2025-07-17',
            'inquiry_source': 'SK',
            'channel': 'TEL',
            'region': '대구 중구',
            'name': '이영희',
            'phone_number': '010-5555-7777',
            'consultation_request': '견적요청',
            'form_type': '상가',
            'consultation_content': '매장 CCTV 6대 설치 문의'
        }
    ]
    
    print("📋 배치 신규 문의 알림 테스트...")
    if slack.send_batch_inquiry_notification(batch_inquiries):
        print("✅ 배치 신규 문의 알림 성공")
    else:
        print("❌ 배치 신규 문의 알림 실패")
    
    # 배치 케어온 데이터 테스트
    batch_careon = [
        {
            'application_datetime': '2025-07-17 14:30:25',
            'name': '박민수',
            'phone_number': '010-1111-2222',
            'installation_location': '주택',
            'address': '서울시 강남구 역삼동',
            'installation_count': '3대'
        },
        {
            'application_datetime': '2025-07-17 15:45:10',
            'name': '정수진',
            'phone_number': '010-3333-4444',
            'installation_location': '아파트',
            'address': '부산시 해운대구 우동',
            'installation_count': '2대'
        }
    ]
    
    print("🏠 배치 케어온 신청 알림 테스트...")
    if slack.send_batch_careon_notification(batch_careon):
        print("✅ 배치 케어온 신청 알림 성공")
    else:
        print("❌ 배치 케어온 신청 알림 실패")


if __name__ == "__main__":
    test_slack_notification()