import urllib.request
import urllib.parse
import zipfile
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
ZIP_PATH = os.path.join(OUT_DIR, 'temp_sbiz.zip')

cookie_handler = urllib.request.HTTPCookieProcessor()
opener = urllib.request.build_opener(cookie_handler)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.data.go.kr/data/15083033/fileData.do'
}

print("[1/3] data.go.kr 세션 및 다운로드 체크...")
opener.open(urllib.request.Request("https://www.data.go.kr/data/15083033/fileData.do", headers=headers), timeout=15)

check_url = "https://www.data.go.kr/cmm/cmm/check-limit.json"
check_data = urllib.parse.urlencode({'atchFileId': 'FILE_000000003695831', 'fileDetailSn': '1'}).encode()
res_check = opener.open(urllib.request.Request(check_url, data=check_data, headers={**headers, 'X-Requested-With': 'XMLHttpRequest'}), timeout=15)
print("Limit Check:", res_check.read().decode())

print("[2/3] 소상공인 상가(상권)정보 ZIP 다운로드 중... (약 350MB)")
down_url = "https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=FILE_000000003695831&fileDetailSn=1&dataNm=" + urllib.parse.quote("소상공인시장진흥공단_상가(상권)정보_20260630")
req_down = urllib.request.Request(down_url, headers=headers)

with opener.open(req_down, timeout=120) as resp, open(ZIP_PATH, 'wb') as out_f:
    total_len = resp.headers.get('Content-Length')
    total_bytes = int(total_len) if total_len else None
    downloaded = 0
    chunk_size = 1024 * 1024 * 4 # 4MB
    while True:
        chunk = resp.read(chunk_size)
        if not chunk:
            break
        out_f.write(chunk)
        downloaded += len(chunk)
        if total_bytes:
            sys.stdout.write(f"\r진행률: {downloaded / 1024 / 1024:.1f}MB / {total_bytes / 1024 / 1024:.1f}MB ({downloaded / total_bytes * 100:.1f}%)")
        else:
            sys.stdout.write(f"\r진행률: {downloaded / 1024 / 1024:.1f}MB")
        sys.stdout.flush()

print("\n[3/3] 서울 데이터 압축 해제 및 정리 중...")
extracted_files = []
with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    for name in z.namelist():
        # 서울 관련 CSV 파일 추출
        if '서울' in name and name.endswith('.csv'):
            print(f"추출 대상: {name}")
            target_path = os.path.join(OUT_DIR, '소상공인_상가정보_서울.csv')
            with z.open(name) as source, open(target_path, 'wb') as target:
                target.write(source.read())
            extracted_files.append(target_path)
            print(f"저장 완료: {target_path} ({os.path.getsize(target_path) / 1024 / 1024:.1f}MB)")

# 임시 zip 삭제
if os.path.exists(ZIP_PATH):
    os.remove(ZIP_PATH)
    print("임시 ZIP 파일 삭제 완료.")

print("작업 완료! 추출된 파일:", extracted_files)
