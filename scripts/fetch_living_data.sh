#!/usr/bin/env bash
# 서울 시민생활 데이터 (SKT 가명결합) — 행정동별 1인가구 / 요금연체비율
# 상권분석 분기 패널과 맞추기 위해 분기말 월(3/6/9/12)만 수집
set -u
OUT="$(dirname "$0")/../data/raw/living"
mkdir -p "$OUT"
EP="https://datafile.seoul.go.kr/bigfile/iot/inf/nio_download.do?&useCache=false"

dl() { # infId seq outfile
  printf '  %-10s seq=%-3s -> %-34s ' "$1" "$2" "$3"
  curl -s --max-time 900 -X POST "$EP" -d "infId=$1&seq=$2&infSeq=1&seqNo=" \
    -H "Referer: https://data.seoul.go.kr/dataList/$1/F/1/datasetView.do" -o "$OUT/$3"
  if [ -s "$OUT/$3" ] && ! head -c 20 "$OUT/$3" | grep -qi '<html'; then
    echo "OK $(du -h "$OUT/$3" | cut -f1)"
  else echo "실패"; rm -f "$OUT/$3"; fi
}

echo "[29개 통신정보 — 요금연체비율 포함]"
dl OA-22267 2  통신정보_2023_전체.zip
for p in "7:2024.03" "10:2024.06" "14:2024.09" "17:2024.12" "20:2025.03" "23:2025.06" "26:2025.09" "29:2025.12"; do
  dl OA-22267 "${p%%:*}" "통신정보_${p##*:}.xlsx"
done

echo "[10개 관심집단수 — 성·연령별 1인가구 포함]"
dl OA-22266 2  관심집단_2023_전체.zip
for p in "7:2024.03" "10:2024.06" "15:2024.09" "18:2024.12" "21:2025.03" "24:2025.06" "27:2025.09" "30:2025.12"; do
  dl OA-22266 "${p%%:*}" "관심집단_${p##*:}.xlsx"
done
echo "완료"
