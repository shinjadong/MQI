import sys
import os

# 프로젝트 루트를 시스템 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import main

if __name__ == "__main__":
    main() 