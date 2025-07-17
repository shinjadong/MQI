import os
import smtplib
from email.mime.text import MIMEText
import logging

class EmailNotification:
    """이메일 알림을 처리하는 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 587))
        self.smtp_user = os.getenv("EMAIL_SMTP_USER")
        self.smtp_password = os.getenv("EMAIL_SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.receiver_email = os.getenv("RECEIVER_EMAIL")

        if not all([self.smtp_server, self.smtp_port, self.smtp_user, self.smtp_password, self.sender_email, self.receiver_email]):
            self.logger.warning("이메일 설정이 완전하지 않아, 이메일 알림이 비활성화될 수 있습니다.")
            self.is_configured = False
        else:
            self.is_configured = True

    def send_email(self, subject: str, body: str) -> bool:
        """
        이메일을 전송합니다.

        :param subject: 이메일 제목
        :param body: 이메일 본문
        :return: 성공 여부 (True/False)
        """
        if not self.is_configured:
            self.logger.error("이메일 설정이 없어 메일을 보낼 수 없습니다.")
            return False

        msg = MIMEText(body)
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = subject

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                self.logger.info(f"이메일이 성공적으로 발송되었습니다: {self.receiver_email}")
                return True
        except Exception as e:
            self.logger.error(f"이메일 발송 실패: {e}")
            return False 