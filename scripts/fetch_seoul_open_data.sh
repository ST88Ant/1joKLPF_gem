#!/usr/bin/env bash
# 서울 열린데이터광장 CSV 대량 수집 (인증키 불필요)
# 사용법: bash scripts/fetch_seoul_open_data.sh
set -u
OUT="$(dirname "$0")/../data/raw"
mkdir -p "$OUT"
EP="https://datafile.seoul.go.kr/bigfile/iot/sheet/csv/download.do"

fetch() {
  local id="$1" name="$2"
  local tmp="$OUT/.$id.cp949"
  printf '  %-12s %-34s ' "$id" "$name"
  curl -s --max-time 300 -X POST "$EP" \
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

echo "[상권분석서비스 - 행정동 단위]"
fetch OA-22166 소비_행정동
fetch OA-22183 상주인구_행정동
fetch OA-22163 아파트_행정동
fetch OA-22184 직장인구_행정동
fetch OA-22178 길단위인구_행정동
fetch OA-22169 집객시설_행정동
fetch OA-22160 영역_행정동

echo "[상권분석서비스 - 자치구 단위 (롤업 검증용)]"
fetch OA-22167 소비_자치구
fetch OA-22182 상주인구_자치구
fetch OA-22164 아파트_자치구
