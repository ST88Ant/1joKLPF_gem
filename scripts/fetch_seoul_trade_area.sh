#!/usr/bin/env bash
# 서울 상권 소비 MBTI (상권 단위) — 서울 열린데이터광장 상권분석서비스 CSV 수집 (인증키 불필요)
# 출처: 팀 Notion "데이터 셋 정하기" (2026-09-12) 필요한 링크 + 매출 축용 추정매출·지도용 영역
# 사용법: bash scripts/fetch_seoul_trade_area.sh
set -u
OUT="$(dirname "$0")/../data/raw/상권"
mkdir -p "$OUT"
EP="https://datafile.seoul.go.kr/bigfile/iot/sheet/csv/download.do"

fetch() {
  local id="$1" name="$2"
  local tmp="$OUT/.$id.cp949"
  printf '  %-12s %-34s ' "$id" "$name"
  curl -s --max-time 900 -X POST "$EP" \
    -d "infId=$id&srvType=S&serviceKind=1&isLogin=&stcRow=&fileType=csv" \
    -H "Referer: https://data.seoul.go.kr/dataList/$id/S/1/datasetView.do" \
    -o "$tmp"
  if [ ! -s "$tmp" ] || head -c 20 "$tmp" | grep -qi '<!DOCTYPE\|<html'; then
    echo "실패"; rm -f "$tmp"; return 1
  fi
  # 열린데이터광장 CSV는 CP949 인코딩 → UTF-8(BOM) 변환
  { printf '\xef\xbb\xbf'; iconv -f CP949 -t UTF-8 "$tmp"; } > "$OUT/${id}_${name}.csv"
  rm -f "$tmp"
  echo "OK  $(( $(wc -l < "$OUT/${id}_${name}.csv") - 1 ))행"
}

echo "[Notion 필요한 링크]"
fetch OA-15577 점포_상권
fetch OA-15569 직장인구_상권
fetch OA-15584 상주인구_상권
fetch OA-15580 집객시설_상권
fetch OA-15576 상권변화지표_상권

echo "[MBTI 축 계산용 추가]"
fetch OA-15572 추정매출_상권      # 연령·시간대·요일·업종별 매출
fetch OA-15560 영역_상권          # 상권 좌표·면적 (지도)
fetch OA-15568 길단위인구_상권    # 시간대·요일·연령별 유동인구

# 추정매출·점포는 시트 다운로드가 최신 연도(2025~)만 준다 → 과거 연도는 파일(zip)로 받음
# seq는 데이터셋 페이지의 downloadFile('seq') 값, infSeq=3(파일 탭)
FEP="https://datafile.seoul.go.kr/bigfile/iot/inf/nio_download.do?&useCache=false"
dl() { # infId seq infSeq outfile
  printf '  %-12s seq=%-7s %-34s ' "$1" "$2" "$4"
  curl -s --max-time 900 -X POST "$FEP" -d "infId=$1&seq=$2&infSeq=$3&seqNo=" \
    -H "Referer: https://data.seoul.go.kr/dataList/$1/S/1/datasetView.do" -o "$OUT/$4"
  if [ -s "$OUT/$4" ] && ! head -c 20 "$OUT/$4" | grep -qi '<html'; then
    echo "OK $(du -h "$OUT/$4" | cut -f1)"
  else echo "실패"; rm -f "$OUT/$4"; fi
}

echo "[과거 연도 파일]"
dl OA-15572 49 3 추정매출_상권_2023.zip
dl OA-15572 50 3 추정매출_상권_2024.zip
dl OA-15577 18 3 점포_상권_2023.zip
dl OA-15577 19 3 점포_상권_2024.zip

# 서울 체류인구(250m, 내국인)는 일별 파일. seq = 날짜 YYMMDD (최근 파일만 목록에 있음)
echo "[체류인구 샘플 1일]"
dl OA-22892 260911 1 체류인구_내국인_250m_20260911.zip
