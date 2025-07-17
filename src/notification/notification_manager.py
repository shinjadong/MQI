import os
import logging
from .kakao_notification import KakaoNotification
from .email_notification import EmailNotification
from .slack_notification import SlackNotification

class NotificationManager:
    """
    여러 알림 채널(카카오, 이메일, 슬랙)을 통합 관리하는 클래스
    """
    def __init__(self):
        """
        NotificationManager를 초기화하고 각 알림 채널의 활성화 여부를 설정합니다.
        """
        self.logger = logging.getLogger(__name__)
        
        # 각 알림 채널의 활성화 여부를 환경 변수에서 읽어옴
        self.enable_kakao = os.getenv('ENABLE_KAKAO_NOTIFICATION', 'false').lower() == 'true'
        self.enable_email = os.getenv('ENABLE_EMAIL_NOTIFICATION', 'false').lower() == 'true'
        self.enable_slack = os.getenv('ENABLE_SLACK_NOTIFICATION', 'false').lower() == 'true'
        
        # 활성화된 채널의 클라이언트만 초기화
        if self.enable_kakao:
            self.kakao_client = KakaoNotification()
            self.logger.info("카카오톡 알림: 활성화")
        else:
            self.logger.info("카카오톡 알림: 비활성화")

        if self.enable_email:
            self.email_client = EmailNotification()
            self.logger.info("이메일 알림: 활성화")
        else:
            self.logger.info("이메일 알림: 비활성화")

        if self.enable_slack:
            self.slack_client = SlackNotification()
            self.logger.info("슬랙 알림: 활성화")
        else:
             self.logger.info("슬랙 알림: 비활성화")

    def send_all(self, message: str):
        """
        활성화된 모든 알림 채널로 메시지를 전송합니다.

        :param message: 전송할 메시지 내용
        """
        if not any([self.enable_kakao, self.enable_email, self.enable_slack]):
            self.logger.info("활성화된 알림 채널이 없어 메시지를 발송하지 않습니다.")
            return

        self.logger.info(f"통합 알림 발송 시작: \"{message[:30]}...\"")
        
        if self.enable_kakao:
            try:
                self.kakao_client.send_message(message)
                self.logger.info("카카오톡 알림 발송 성공")
            except Exception as e:
                self.logger.error(f"카카오톡 알림 발송 실패: {e}")

        if self.enable_email:
            try:
                self.email_client.send_email("신규 문의 접수 알림", message)
                self.logger.info("이메일 알림 발송 성공")
            except Exception as e:
                self.logger.error(f"이메일 알림 발송 실패: {e}")

        if self.enable_slack:
            try:
                self.slack_client.send_message(message)
                self.logger.info("슬랙 알림 발송 성공")
            except Exception as e:
                self.logger.error(f"슬랙 알림 발송 실패: {e}") 