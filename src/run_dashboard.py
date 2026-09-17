# -*- coding: utf-8 -*-
"""
Gemi_pjt - 대시보드 로컬 실행 스크립트
로컬 웹 서버(HTTP Server)를 구동하고 브라우저에서 대시보드를 즉시 엽니다.
실행 방법: python Gemi_pjt/src/run_dashboard.py
"""

import sys
import os
import webbrowser
import http.server
import socketserver
from pathlib import Path

# 콘솔 UTF-8 출력 보장
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PORT = 8501
DIRECTORY = Path(__file__).resolve().parent.parent

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def start_server():
    print("=" * 60)
    print("🌐 [Gemi_pjt] 상권 소비 예측 & 갭 분석 대시보드 서버 시작")
    print(f"👉 로컬 접속 URL: http://localhost:{PORT}")
    print("=" * 60)

    url = f"http://localhost:{PORT}"
    webbrowser.open(url)

    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        print("서버가 정상 구동 중입니다. 종료하려면 Ctrl + C 를 누르세요.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")

if __name__ == "__main__":
    start_server()
