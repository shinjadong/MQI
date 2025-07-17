#!/usr/bin/env python3
"""
Google Sheets Manager
구글 시트 리스팅 및 엑셀 다운로드 도구

사용법:
    python google_sheets_manager.py list                 # 모든 시트 리스팅
    python google_sheets_manager.py download [sheet_id]  # 특정 시트 다운로드
    python google_sheets_manager.py download-all         # 모든 시트 다운로드
"""

import os
import json
import argparse
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsManager:
    """Google Sheets API를 사용하여 시트를 관리하는 클래스"""
    
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
    
    def list_sheets(self) -> list:
        """
        액세스 가능한 모든 Google Sheets 파일 리스팅
        
        Returns:
            list: 시트 정보 목록
        """
        try:
            print("🔍 Google Sheets 파일 검색 중...")
            
            # Google Drive에서 스프레드시트 파일 검색
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
            
        except HttpError as error:
            print(f"❌ API 오류 발생: {error}")
            return []
        except Exception as e:
            print(f"❌ 예상치 못한 오류 발생: {e}")
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
    
    def get_sheet_data(self, spreadsheet_id: str) -> dict:
        """
        특정 스프레드시트의 모든 시트 데이터 가져오기
        
        Args:
            spreadsheet_id: 스프레드시트 ID
            
        Returns:
            dict: 시트별 데이터
        """
        try:
            print(f"📊 스프레드시트 데이터 읽는 중... (ID: {spreadsheet_id})")
            
            # 스프레드시트 메타데이터 가져오기
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            spreadsheet_title = spreadsheet.get('properties', {}).get('title', 'Unknown')
            sheets = spreadsheet.get('sheets', [])
            
            all_data = {}
            
            for sheet in sheets:
                sheet_title = sheet.get('properties', {}).get('title', 'Unknown')
                print(f"  📄 시트 '{sheet_title}' 읽는 중...")
                
                # 시트 데이터 가져오기
                range_name = f"'{sheet_title}'"
                result = self.sheets_service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name
                ).execute()
                
                values = result.get('values', [])
                
                if values:
                    # 첫 번째 행을 헤더로 사용
                    headers = values[0] if values else []
                    data_rows = values[1:] if len(values) > 1 else []
                    
                    # 데이터를 DataFrame으로 변환 (헤더와 데이터 길이 맞추기)
                    if data_rows:
                        # 모든 행의 최대 길이 찾기
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
                        
                        print(f"    ✅ {len(data_rows)}행 데이터 읽기 완료 (컬럼 수: {max_cols})")
                    else:
                        # 헤더만 있는 경우
                        df = pd.DataFrame(columns=headers)
                        all_data[sheet_title] = df
                        print(f"    ⚠️  헤더만 있는 시트입니다.")
                else:
                    print(f"    ⚠️  빈 시트입니다.")
                    all_data[sheet_title] = pd.DataFrame()
            
            return {
                'title': spreadsheet_title,
                'data': all_data
            }
            
        except HttpError as error:
            print(f"❌ API 오류 발생: {error}")
            return {}
        except Exception as e:
            print(f"❌ 예상치 못한 오류 발생: {e}")
            return {}
    
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
            
            # 스프레드시트 데이터 가져오기
            sheet_data = self.get_sheet_data(spreadsheet_id)
            
            if not sheet_data:
                print("❌ 데이터를 가져올 수 없습니다.")
                return
            
            # 파일명 생성 (안전한 파일명으로 변환)
            safe_title = "".join(c for c in sheet_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}.xlsx"
            filepath = os.path.join(output_dir, filename)
            
            # 엑셀 파일로 저장
            print(f"💾 엑셀 파일로 저장 중: {filepath}")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, df in sheet_data['data'].items():
                    # 시트명이 엑셀에서 허용하지 않는 문자 제거
                    safe_sheet_name = "".join(c for c in sheet_name if c not in ['/', '\\', '?', '*', ':', '[', ']'])
                    safe_sheet_name = safe_sheet_name[:31]  # 엑셀 시트명 길이 제한
                    
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
                    print(f"  ✅ 시트 '{sheet_name}' 저장 완료")
            
            print(f"🎉 다운로드 완료: {filepath}")
            
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
    
    def download_all_sheets(self, output_dir: str = "downloads"):
        """모든 액세스 가능한 시트를 다운로드"""
        sheet_list = self.list_sheets()
        
        if not sheet_list:
            print("📄 다운로드할 시트가 없습니다.")
            return
        
        print(f"\n📥 총 {len(sheet_list)}개 시트 다운로드 시작...")
        
        for i, sheet in enumerate(sheet_list, 1):
            print(f"\n[{i}/{len(sheet_list)}] 다운로드 중: {sheet['name']}")
            self.download_to_excel(sheet['id'], output_dir)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Google Sheets 관리 도구')
    parser.add_argument('action', choices=['list', 'download', 'download-all'], 
                       help='수행할 작업')
    parser.add_argument('sheet_id', nargs='?', 
                       help='다운로드할 시트 ID (download 작업 시 필요)')
    parser.add_argument('--output', '-o', default='downloads',
                       help='다운로드 디렉토리 (기본값: downloads)')
    parser.add_argument('--service-account', '-s', default='cctvtec-mail-b013de0946d8.json',
                       help='Service Account 키 파일 (기본값: cctvtec-mail-b013de0946d8.json)')
    
    args = parser.parse_args()
    
    # Service Account 키 파일 확인
    if not os.path.exists(args.service_account):
        print(f"❌ Service Account 키 파일을 찾을 수 없습니다: {args.service_account}")
        return
    
    try:
        # Google Sheets Manager 초기화
        manager = GoogleSheetsManager(args.service_account)
        
        if args.action == 'list':
            # 시트 리스팅
            sheet_list = manager.list_sheets()
            manager.print_sheet_list(sheet_list)
            
        elif args.action == 'download':
            # 특정 시트 다운로드
            if not args.sheet_id:
                print("❌ 시트 ID를 입력해주세요.")
                print("사용법: python google_sheets_manager.py download [sheet_id]")
                return
            
            manager.download_to_excel(args.sheet_id, args.output)
            
        elif args.action == 'download-all':
            # 모든 시트 다운로드
            manager.download_all_sheets(args.output)
            
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()