#!/usr/bin/env python3
"""
슬랙 알림 시스템 (카카오톡 대안)
CCTV 신규 문의 및 케어온 신청 시 슬랙으로 알림 발송
"""

import os
import requests
import logging

class SlackNotification:
    """Slack 알림을 처리하는 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

        if not self.webhook_url:
            self.logger.warning("SLACK_WEBHOOK_URL이 설정되지 않아, 슬랙 알림이 비활성화될 수 있습니다.")
            self.is_configured = False
        else:
            self.is_configured = True

    def send_message(self, message: str) -> bool:
        """
        Slack 웹훅을 사용하여 메시지를 전송합니다.

        :param message: 전송할 메시지 내용
        :return: 성공 여부 (True/False)
        """
        if not self.is_configured:
            self.logger.error("슬랙 웹훅 URL이 없어 메시지를 보낼 수 없습니다.")
            return False

        headers = {'Content-type': 'application/json'}
        data = {'text': message}

        try:
            response = requests.post(self.webhook_url, headers=headers, json=data)
            response.raise_for_status()  # 2xx 응답 코드가 아닐 경우 예외 발생
            self.logger.info("슬랙 메시지가 성공적으로 발송되었습니다.")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"슬랙 메시지 발송 실패: {e}")
            return False