# 🚀 슬랙 알림 설정 가이드

새로운 문의가 접수될 때 슬랙(Slack)으로 실시간 알림을 받기 위한 설정 방법입니다.

## 1단계: 슬랙 워크스페이스 및 채널 준비
1.  사용 중인 슬랙 워크스페이스에 접속합니다. (없다면 새로 생성: [slack.com](https://slack.com))
2.  알림을 받을 채널을 생성하거나 기존 채널을 이용합니다. (예: `#cctv-신규문의-알림`)

## 2단계: Webhook URL 생성
1.  **슬랙 앱 관리 페이지**로 이동합니다: [https://api.slack.com/apps](https://api.slack.com/apps)
2.  **"Create New App"** 버튼을 클릭합니다.
3.  **"From scratch"** (처음부터 만들기) 옵션을 선택합니다.
4.  **앱 이름**을 지정하고(예: `신규 문의 알림봇`), 알림을 보낼 **워크스페이스를 선택**한 후 **"Create App"** 버튼을 누릅니다.
5.  왼쪽 메뉴에서 **"Incoming Webhooks"**를 선택합니다.
6.  **"Activate Incoming Webhooks"** 스위치를 **On**으로 변경하여 활성화합니다.
7.  페이지 하단에 나타나는 **"Add New Webhook to Workspace"** 버튼을 클릭합니다.
8.  알림을 게시할 **채널을 선택**하고 **"Allow"** 버튼을 누릅니다.
9.  생성된 **Webhook URL**을 복사합니다. 이 URL은 아래와 같은 형식입니다.
    ```
    https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
    ```

## 3단계: `.env` 파일에 Webhook URL 설정
프로젝트 루트 디렉토리에 있는 `.env` 파일에 복사한 Webhook URL을 추가합니다.

```env
# .env 파일
# ... 다른 설정들 ...

# 슬랙 알림 설정
SLACK_WEBHOOK_URL="여기에 복사한 Webhook URL을 붙여넣으세요"
```

## 4단계: 정상 작동 확인
설정이 완료되면, 동기화 시스템이 실행될 때 새로운 데이터가 감지되면 자동으로 지정된 슬랙 채널에 알림 메시지가 전송됩니다.

---

### 💡 문제 해결
-   **알림이 오지 않는 경우:**
    1.  `.env` 파일에 `SLACK_WEBHOOK_URL`이 정확히 입력되었는지 다시 확인합니다.
    2.  Webhook URL이 올바른 워크스페이스와 채널에 연결되었는지 확인합니다.
    3.  `logs/sync.log` 파일에 슬랙 알림 발송 관련 오류 메시지가 있는지 확인합니다.