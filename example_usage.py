#!/usr/bin/env python3
"""
Google Sheets Manager 사용 예제
"""

from google_sheets_manager import GoogleSheetsManager

def main():
    # Service Account 키 파일 경로
    service_account_file = 'cctvtec-mail-b013de0946d8.json'
    
    # GoogleSheetsManager 인스턴스 생성
    manager = GoogleSheetsManager(service_account_file)
    
    print("🚀 Google Sheets Manager 시작")
    print("=" * 50)
    
    # 1. 모든 시트 리스팅
    print("\n1️⃣ 모든 시트 리스팅:")
    sheet_list = manager.list_sheets()
    manager.print_sheet_list(sheet_list)
    
    # 2. 첫 번째 시트 다운로드 (시트가 있는 경우)
    if sheet_list:
        first_sheet = sheet_list[0]
        print(f"\n2️⃣ 첫 번째 시트 다운로드: {first_sheet['name']}")
        manager.download_to_excel(first_sheet['id'], "downloads")
    
    # 3. 특정 시트 ID로 다운로드 (예시)
    # sheet_id = "1abcdefghijklmnopqrstuvwxyz"  # 실제 시트 ID로 교체
    # print(f"\n3️⃣ 특정 시트 다운로드: {sheet_id}")
    # manager.download_to_excel(sheet_id, "downloads")
    
    print("\n✅ 작업 완료!")

if __name__ == "__main__":
    main()