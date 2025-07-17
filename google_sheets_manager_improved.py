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
import json
import argparse
import pandas as pd
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsManagerImproved:
    """개선된 Google Sheets API 관리 클래스"""
    
    def __init__(self, service_account_file: str):
        """
        Google Sheets Manager 초기화
        
        Args:
            service_account_file: Google Service Account 키 파일 경로
        """
        self.service_account_file = service_account_file
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        self.credentials = self._authenticate()
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def _authenticate(self) -> Credentials:
        """Google API 인증"""
        try:
            credentials = Credentials.from_service_account_file(
                self.service_account_file, scopes=self.scopes
            )
            return credentials
        except Exception as e:
            print(f"❌ 인증 실패: {e}")
            raise
    
    def extract_spreadsheet_id(self, url: str) -> str:
        """
        Google Sheets URL에서 스프레드시트 ID 추출
        
        Args:
            url: Google Sheets URL
            
        Returns:
            str: 스프레드시트 ID
        """
        try:
            # URL 패턴 매칭
            patterns = [
                r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
                r'id=([a-zA-Z0-9-_]+)',
                r'^([a-zA-Z0-9-_]+)$'  # 직접 ID인 경우
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            raise ValueError("유효한 스프레드시트 ID를 찾을 수 없습니다.")
            
        except Exception as e:
            print(f"❌ URL 파싱 실패: {e}")
            raise
    
    def check_sheet_permissions(self, spreadsheet_id: str) -> bool:
        """
        스프레드시트 접근 권한 확인
        
        Args:
            spreadsheet_id: 스프레드시트 ID
            
        Returns:
            bool: 접근 가능 여부
        """
        try:
            print(f"🔐 권한 확인 중: {spreadsheet_id}")
            
            # 기본 메타데이터 가져오기 시도
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id,
                fields='properties'
            ).execute()
            
            print(f"✅ 접근 가능: {spreadsheet.get('properties', {}).get('title', 'Unknown')}")
            return True
            
        except HttpError as error:
            if error.resp.status == 403:
                print(f"❌ 접근 권한 없음: {error}")
                print("💡 해결 방법:")
                print("   1. 스프레드시트 소유자가 Service Account에 읽기 권한 부여")
                print("   2. 스프레드시트를 '링크가 있는 모든 사용자'로 공유 설정")
                print(f"   3. Service Account 이메일: {self.credentials.service_account_email}")
            else:
                print(f"❌ API 오류: {error}")
            return False
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return False
    
    def get_sheet_info(self, spreadsheet_id: str) -> dict:
        """
        스프레드시트 정보 가져오기
        
        Args:
            spreadsheet_id: 스프레드시트 ID
            
        Returns:
            dict: 스프레드시트 정보
        """
        try:
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            return {
                'title': spreadsheet.get('properties', {}).get('title', 'Unknown'),
                'sheets': spreadsheet.get('sheets', [])
            }
            
        except Exception as e:
            print(f"❌ 스프레드시트 정보 가져오기 실패: {e}")
            return {}
    
    def get_used_range(self, spreadsheet_id: str, sheet_name: str) -> str:
        """
        시트의 실제 사용된 범위 찾기
        
        Args:
            spreadsheet_id: 스프레드시트 ID
            sheet_name: 시트 이름
            
        Returns:
            str: 사용된 범위 (예: A1:Z100)
        """
        try:
            # 큰 범위에서 데이터 가져오기
            range_name = f"'{sheet_name}'!A1:ZZ10000"
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return f"'{sheet_name}'!A1:A1"
            
            # 실제 데이터가 있는 마지막 행과 열 찾기
            last_row = len(values)
            last_col = 0
            
            for row in values:
                if len(row) > last_col:
                    last_col = len(row)
            
            # 열 번호를 문자로 변환
            last_col_letter = self._num_to_col_letter(last_col)
            
            return f"'{sheet_name}'!A1:{last_col_letter}{last_row}"
            
        except Exception as e:
            print(f"⚠️ 범위 계산 실패, 기본 범위 사용: {e}")
            return f"'{sheet_name}'"
    
    def _num_to_col_letter(self, num: int) -> str:
        """숫자를 엑셀 열 문자로 변환"""
        result = ""
        while num > 0:
            num -= 1
            result = chr(num % 26 + ord('A')) + result
            num //= 26
        return result
    
    def get_sheet_data_advanced(self, spreadsheet_id: str) -> dict:
        """
        향상된 스프레드시트 데이터 가져오기
        
        Args:
            spreadsheet_id: 스프레드시트 ID
            
        Returns:
            dict: 시트별 데이터
        """
        try:
            # 권한 확인
            if not self.check_sheet_permissions(spreadsheet_id):
                return {}
            
            print(f"📊 스프레드시트 데이터 읽는 중... (ID: {spreadsheet_id})")
            
            # 스프레드시트 정보 가져오기
            sheet_info = self.get_sheet_info(spreadsheet_id)
            if not sheet_info:
                return {}
            
            spreadsheet_title = sheet_info['title']
            sheets = sheet_info['sheets']
            
            all_data = {}
            
            for sheet in sheets:
                sheet_title = sheet.get('properties', {}).get('title', 'Unknown')
                sheet_id = sheet.get('properties', {}).get('sheetId', 0)
                
                print(f"  📄 시트 '{sheet_title}' (ID: {sheet_id}) 읽는 중...")
                
                # 여러 범위 시도
                ranges_to_try = [
                    f"'{sheet_title}'",  # 전체 시트
                    f"'{sheet_title}'!A:Z",  # A부터 Z열까지
                    f"'{sheet_title}'!A1:Z1000",  # 구체적인 범위
                    self.get_used_range(spreadsheet_id, sheet_title)  # 사용된 범위
                ]
                
                data_found = False
                for range_name in ranges_to_try:
                    try:
                        print(f"    🔍 범위 '{range_name}' 시도 중...")
                        
                        result = self.sheets_service.spreadsheets().values().get(
                            spreadsheetId=spreadsheet_id,
                            range=range_name,
                            valueRenderOption='FORMATTED_VALUE',
                            dateTimeRenderOption='FORMATTED_STRING'
                        ).execute()
                        
                        values = result.get('values', [])
                        
                        if values:
                            # 빈 행 제거
                            filtered_values = []
                            for row in values:
                                if any(cell.strip() if isinstance(cell, str) else str(cell).strip() for cell in row):
                                    filtered_values.append(row)
                            
                            if filtered_values:
                                print(f"    ✅ 데이터 발견: {len(filtered_values)}행")
                                
                                # 첫 번째 행을 헤더로 사용
                                headers = filtered_values[0] if filtered_values else []
                                data_rows = filtered_values[1:] if len(filtered_values) > 1 else []
                                
                                # 데이터 정규화
                                if data_rows:
                                    max_cols = max(len(row) for row in [headers] + data_rows)
                                    
                                    # 헤더 길이 조정
                                    if len(headers) < max_cols:
                                        headers.extend([f'Column_{i}' for i in range(len(headers), max_cols)])
                                    elif len(headers) > max_cols:
                                        headers = headers[:max_cols]
                                    
                                    # 각 행의 길이를 헤더 길이에 맞춤
                                    normalized_rows = []
                                    for row in data_rows:
                                        if len(row) < max_cols:
                                            row.extend([''] * (max_cols - len(row)))
                                        elif len(row) > max_cols:
                                            row = row[:max_cols]
                                        normalized_rows.append(row)
                                    
                                    df = pd.DataFrame(normalized_rows, columns=headers)
                                    all_data[sheet_title] = df
                                    
                                    print(f"    ✅ {len(data_rows)}행 데이터 처리 완료 (컬럼 수: {max_cols})")
                                    data_found = True
                                    break
                                else:
                                    # 헤더만 있는 경우
                                    df = pd.DataFrame(columns=headers)
                                    all_data[sheet_title] = df
                                    print(f"    ⚠️ 헤더만 있는 시트")
                                    data_found = True
                                    break
                    
                    except Exception as e:
                        print(f"    ❌ 범위 '{range_name}' 읽기 실패: {e}")
                        continue
                
                if not data_found:
                    print(f"    ⚠️ 빈 시트이거나 데이터를 읽을 수 없습니다.")
                    all_data[sheet_title] = pd.DataFrame()
            
            return {
                'title': spreadsheet_title,
                'data': all_data
            }
            
        except Exception as e:
            print(f"❌ 데이터 가져오기 실패: {e}")
            return {}
    
    def list_sheets(self) -> list:
        """액세스 가능한 모든 Google Sheets 파일 리스팅"""
        try:
            print("🔍 Google Sheets 파일 검색 중...")
            
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=100,
                fields="nextPageToken, files(id, name, createdTime, modifiedTime, owners)"
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                print("📄 액세스 가능한 스프레드시트가 없습니다.")
                return []
            
            sheet_list = []
            for file in files:
                sheet_info = {
                    'id': file['id'],
                    'name': file['name'],
                    'created_time': file.get('createdTime', ''),
                    'modified_time': file.get('modifiedTime', ''),
                    'owners': [owner.get('displayName', 'Unknown') for owner in file.get('owners', [])]
                }
                sheet_list.append(sheet_info)
            
            return sheet_list
            
        except Exception as e:
            print(f"❌ 리스팅 실패: {e}")
            return []
    
    def print_sheet_list(self, sheet_list: list):
        """시트 목록을 보기 좋게 출력"""
        if not sheet_list:
            print("📄 표시할 시트가 없습니다.")
            return
        
        print(f"\n📋 총 {len(sheet_list)}개의 스프레드시트 발견:")
        print("-" * 80)
        
        for i, sheet in enumerate(sheet_list, 1):
            created_date = sheet['created_time'][:10] if sheet['created_time'] else 'Unknown'
            modified_date = sheet['modified_time'][:10] if sheet['modified_time'] else 'Unknown'
            owners = ', '.join(sheet['owners']) if sheet['owners'] else 'Unknown'
            
            print(f"{i:2d}. 📊 {sheet['name']}")
            print(f"    ID: {sheet['id']}")
            print(f"    소유자: {owners}")
            print(f"    생성일: {created_date}")
            print(f"    수정일: {modified_date}")
            print("-" * 80)
    
    def download_to_excel(self, spreadsheet_id: str, output_dir: str = "downloads"):
        """
        스프레드시트를 엑셀 파일로 다운로드
        
        Args:
            spreadsheet_id: 스프레드시트 ID
            output_dir: 다운로드할 디렉토리
        """
        try:
            # 다운로드 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 스프레드시트 데이터 가져오기 (개선된 방법)
            sheet_data = self.get_sheet_data_advanced(spreadsheet_id)
            
            if not sheet_data:
                print("❌ 데이터를 가져올 수 없습니다.")
                return
            
            # 파일명 생성
            safe_title = "".join(c for c in sheet_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}.xlsx"
            filepath = os.path.join(output_dir, filename)
            
            # 엑셀 파일로 저장
            print(f"💾 엑셀 파일로 저장 중: {filepath}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, df in sheet_data['data'].items():
                    # 안전한 시트명 생성
                    safe_sheet_name = "".join(c for c in sheet_name if c not in ['/', '\\', '?', '*', ':', '[', ']'])
                    safe_sheet_name = safe_sheet_name[:31]
                    
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    print(f"  ✅ 시트 '{sheet_name}' 저장 완료 ({len(df)}행)")
            
            print(f"🎉 다운로드 완료: {filepath}")
            
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
    
    def download_from_url(self, url: str, output_dir: str = "downloads"):
        """
        URL에서 스프레드시트 다운로드
        
        Args:
            url: Google Sheets URL
            output_dir: 다운로드할 디렉토리
        """
        try:
            spreadsheet_id = self.extract_spreadsheet_id(url)
            print(f"📋 추출된 스프레드시트 ID: {spreadsheet_id}")
            self.download_to_excel(spreadsheet_id, output_dir)
            
        except Exception as e:
            print(f"❌ URL 다운로드 실패: {e}")


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
        manager = GoogleSheetsManagerImproved(args.service_account)
        
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