#!/usr/bin/env python3
"""
Google Sheets Manager (개선된 버전)
구글 시트 리스팅 및 엑셀 다운로드 도구 - 향상된 데이터 추출 기능

사용법:
    python google_sheets_manager_improved.py list                    # 모든 시트 리스팅
    python google_sheets_manager_improved.py download [sheet_id]     # 특정 시트 다운로드
    python google_sheets_manager_improved.py download-url [url]      # URL에서 시트 다운로드
    python google_sheets_manager_improved.py download-all            # 모든 시트 다운로드
"""

import os
import re
import io
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from typing import Optional, List
from datetime import datetime
import pandas as pd

class GoogleSheetsManager:
    """Google Sheets API 관련 작업을 관리하는 클래스"""

    def __init__(self, credentials_path=None):
        """
        GoogleSheetsManager를 초기화합니다.
        
        :param credentials_path: Google 서비스 계정 인증서 파일 경로
        """
        self.logger = logging.getLogger(__name__)
        self.sheets_url = os.getenv('GOOGLE_SHEETS_URL')
        
        if not self.sheets_url:
            self.logger.critical("GOOGLE_SHEETS_URL이 환경 변수에 설정되지 않았습니다.")
            raise ValueError("GOOGLE_SHEETS_URL이 필요합니다.")
            
        self.credentials_path = credentials_path or os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        if not self.credentials_path:
            self.logger.critical("Google 서비스 계정 파일 경로가 제공되지 않았습니다.")
            raise ValueError("Google 서비스 계정 파일 경로가 필요합니다.")
        
        self.creds = self._get_credentials()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        
    def _get_credentials(self) -> Credentials:
        """서비스 계정 파일을 사용하여 인증 정보를 가져옵니다."""
        try:
            scopes = [
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/spreadsheets.readonly'
            ]
            return Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
        except Exception as e:
            self.logger.error(f"Google 인증 실패: {e}")
            raise

    def _extract_spreadsheet_id_from_url(self) -> str:
        """Google Sheets URL에서 스프레드시트 ID를 추출합니다."""
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', self.sheets_url)
        if not match:
            self.logger.error("URL에서 스프레드시트 ID를 찾을 수 없습니다.")
            raise ValueError("유효하지 않은 Google Sheets URL입니다.")
        return match.group(1)

    def get_sheet_names(self) -> List[str]:
        """
        스프레드시트의 모든 시트 이름을 가져옵니다.
        
        :return: 시트 이름 리스트 (순서대로)
        """
        try:
            spreadsheet_id = self._extract_spreadsheet_id_from_url()
            
            # 스프레드시트 메타데이터 가져오기
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            # 시트 이름 추출 (순서대로)
            sheet_names = []
            for sheet in spreadsheet['sheets']:
                sheet_names.append(sheet['properties']['title'])
                
            self.logger.info(f"스프레드시트에서 {len(sheet_names)}개의 시트를 찾았습니다: {sheet_names}")
            return sheet_names
            
        except Exception as e:
            self.logger.error(f"시트 목록 가져오기 실패: {e}")
            return []

    def download_sheet_as_excel(self, output_dir: str = "downloads") -> Optional[str]:
        """
        Google Drive API를 사용하여 스프레드시트를 엑셀 파일로 다운로드합니다.

        :param output_dir: 다운로드할 디렉토리
        :return: 다운로드된 파일의 경로 또는 실패 시 None
        """
        try:
            spreadsheet_id = self._extract_spreadsheet_id_from_url()
            self.logger.info(f"스프레드시트 다운로드를 시작합니다 (ID: {spreadsheet_id}).")

            request = self.drive_service.files().export_media(
                fileId=spreadsheet_id,
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            os.makedirs(output_dir, exist_ok=True)
            
            file_info = self.drive_service.files().get(fileId=spreadsheet_id, fields='name').execute()
            sheet_name = file_info.get('name', 'spreadsheet')
            safe_sheet_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_sheet_name}_{timestamp}.xlsx"
            filepath = os.path.join(output_dir, filename)

            fh = io.FileIO(filepath, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                self.logger.info(f"다운로드 진행률: {int(status.progress() * 100)}%")

            self.logger.info(f"✅ 파일이 성공적으로 다운로드되었습니다: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"스프레드시트 다운로드 실패: {e}")
            return None
            
    def cleanup_temp_file(self, filepath: str):
        """
        처리 완료 후 임시 파일을 삭제합니다.

        :param filepath: 삭제할 파일 경로
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"🗑️ 임시 파일 삭제 완료: {filepath}")
        except Exception as e:
            self.logger.error(f"임시 파일 삭제 실패: {e}")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Google Sheets 관리 도구 (개선된 버전)')
    parser.add_argument('action', choices=['list', 'download', 'download-url', 'download-all'], 
                       help='수행할 작업')
    parser.add_argument('target', nargs='?', 
                       help='시트 ID 또는 URL')
    parser.add_argument('--output', '-o', default='downloads',
                       help='다운로드 디렉토리 (기본값: downloads)')
    parser.add_argument('--service-account', '-s', default='cctvtec-mail-b013de0946d8.json',
                       help='Service Account 키 파일 (기본값: cctvtec-mail-b013de0946d8.json)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.service_account):
        print(f"❌ Service Account 키 파일을 찾을 수 없습니다: {args.service_account}")
        return
    
    try:
        manager = GoogleSheetsManager(args.service_account)
        
        if args.action == 'list':
            sheet_list = manager.list_sheets()
            manager.print_sheet_list(sheet_list)
            
        elif args.action == 'download':
            if not args.target:
                print("❌ 시트 ID를 입력해주세요.")
                return
            manager.download_to_excel(args.target, args.output)
            
        elif args.action == 'download-url':
            if not args.target:
                print("❌ Google Sheets URL을 입력해주세요.")
                return
            manager.download_from_url(args.target, args.output)
            
        elif args.action == 'download-all':
            sheet_list = manager.list_sheets()
            for sheet in sheet_list:
                print(f"\n📥 다운로드 중: {sheet['name']}")
                manager.download_to_excel(sheet['id'], args.output)
            
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류: {e}")


if __name__ == "__main__":
    main()