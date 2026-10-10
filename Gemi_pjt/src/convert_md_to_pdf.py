# -*- coding: utf-8 -*-
"""
Markdown to PDF 변환 스크립트
- Headless Chrome/Edge를 활용한 최고 품질 A4 PDF 인쇄
"""

import os
import subprocess
import markdown

def convert_md_to_pdf(md_path, pdf_path):
    if not os.path.exists(md_path):
        print(f"Error: {md_path} does not exist.")
        return False

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Markdown -> HTML 변환
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
    )

    # 미려한 인쇄 전용 CSS 템플릿
    html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>서울시 행정동별 상권 분석 키워드 가이드 및 기본 EDA 보고서</title>
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    @page {{
        size: A4;
        margin: 18mm 16mm 18mm 16mm;
        @bottom-right {{
            content: counter(page);
            font-size: 8pt;
            color: #94a3b8;
        }}
    }}

    body {{
        font-family: 'Pretendard', 'Malgun Gothic', -apple-system, sans-serif;
        color: #1e293b;
        line-height: 1.65;
        font-size: 10pt;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}

    h1 {{
        color: #0f172a;
        font-size: 18pt;
        font-weight: 800;
        border-bottom: 2.5px solid #2563eb;
        padding-bottom: 8px;
        margin-top: 0;
        margin-bottom: 14px;
        letter-spacing: -0.5px;
    }}

    h2 {{
        color: #1e3a8a;
        font-size: 13pt;
        font-weight: 700;
        border-left: 4px solid #2563eb;
        padding-left: 8px;
        margin-top: 22px;
        margin-bottom: 10px;
        letter-spacing: -0.3px;
        page-break-after: avoid;
    }}

    h3 {{
        color: #1d4ed8;
        font-size: 11pt;
        font-weight: 600;
        margin-top: 16px;
        margin-bottom: 8px;
        page-break-after: avoid;
    }}

    h4 {{
        color: #334155;
        font-size: 10pt;
        font-weight: 600;
        margin-top: 12px;
        margin-bottom: 6px;
    }}

    p {{
        margin-top: 0;
        margin-bottom: 8px;
        word-break: keep-all;
    }}

    hr {{
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 16px 0;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        margin-bottom: 16px;
        font-size: 8.5pt;
        page-break-inside: avoid;
    }}

    th, td {{
        border: 1px solid #cbd5e1;
        padding: 6px 9px;
        text-align: left;
        vertical-align: middle;
    }}

    th {{
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: 700;
        text-align: center;
    }}

    tr:nth-child(even) td {{
        background-color: #f8fafc;
    }}

    code {{
        font-family: 'Consolas', monospace;
        background-color: #f1f5f9;
        color: #dc2626;
        padding: 2px 4px;
        border-radius: 4px;
        font-size: 8.5pt;
    }}

    pre {{
        background-color: #0f172a;
        color: #e2e8f0;
        padding: 12px;
        border-radius: 6px;
        font-size: 8.5pt;
        line-height: 1.45;
        overflow-x: auto;
        margin-top: 8px;
        margin-bottom: 12px;
        page-break-inside: avoid;
    }}

    pre code {{
        background-color: transparent;
        color: inherit;
        padding: 0;
    }}

    ul, ol {{
        margin-top: 4px;
        margin-bottom: 10px;
        padding-left: 20px;
    }}

    li {{
        margin-bottom: 3px;
        word-break: keep-all;
    }}

    blockquote {{
        margin: 10px 0;
        padding: 8px 12px;
        background-color: #f0f9ff;
        border-left: 4px solid #0284c7;
        color: #0369a1;
        font-size: 9.5pt;
        border-radius: 0 4px 4px 0;
    }}

    .badge {{
        display: inline-block;
        padding: 2px 6px;
        font-size: 8pt;
        font-weight: bold;
        border-radius: 4px;
        background: #e0f2fe;
        color: #0369a1;
    }}

    a {{
        color: #2563eb;
        text-decoration: none;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""

    temp_html = md_path.replace('.md', '_temp.html')
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"Temporary HTML generated: {temp_html}")

    # Chrome 또는 Edge 찾기
    browser_candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]

    browser_bin = None
    for b in browser_candidates:
        if os.path.exists(b):
            browser_bin = b
            break

    if not browser_bin:
        print("Error: Neither Chrome nor Edge browser executable found.")
        return False

    print(f"Using browser: {browser_bin}")

    # Headless 인쇄 명령
    cmd = [
        browser_bin,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        temp_html
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            print(f"Successfully converted to PDF: {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")
            # 임시 파일 정리
            if os.path.exists(temp_html):
                os.remove(temp_html)
            return True
        else:
            print(f"Failed to generate PDF. Subprocess output: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error during PDF conversion: {e}")
        return False

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.abspath(os.path.join(script_dir, "..", "docs", "서울시_행정동별_상권분석_키워드_가이드_및_EDA.md"))
    pdf_file = md_file.replace('.md', '.pdf')
    convert_md_to_pdf(md_file, pdf_file)
