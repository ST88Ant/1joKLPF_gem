# -*- coding: utf-8 -*-
"""
행정동별 상권분석 키워드(정성) + 상권기회 인사이트(모델·정량) 통합

입력
  - Clau_pjt/data/서울시_행정동별_상권기회_인사이트.csv   (425동 × 33열)
  - Gemi_pjt/data/서울시_행정동별_상권분석_키워드.csv     (423동 × 17열)
출력
  - data/processed/서울시_행정동별_상권분석_통합.csv       (425동)

결합 규칙
  - 키: 행정동_코드 (양쪽 모두 유일). 이름은 '신사동' 동명이동, 키워드 파일의 '·'→'?' 깨짐(7개 동) 때문에 쓰지 않는다.
  - 인사이트 기준 left join → 키워드 파일에 없는 둔촌1동·항동은 키워드 컬럼만 빈 칸.
  - 양쪽에 같은 값으로 있는 컬럼(자치구, 상권_유형, 대표_아파트_단지, 비추천_주의_업종)과
    아파트시가(=아파트_평균_시가)는 한 번만 남긴다. 행정동_코드_명은 깨지지 않은 인사이트 쪽을 쓴다.
  - 설계상 빈 칸(기회점수·해석주의 등)은 채우지 않는다.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INSIGHT = ROOT / "Clau_pjt/data/서울시_행정동별_상권기회_인사이트.csv"
KEYWORD = ROOT / "Gemi_pjt/data/서울시_행정동별_상권분석_키워드.csv"
OUT = ROOT / "data/processed/서울시_행정동별_상권분석_통합.csv"

COLUMNS = [
    # 행정동 기준
    "자치구", "행정동_코드", "행정동_코드_명",
    # 금융MBTI
    "금융MBTI", "군집",
    # 상권 프로파일
    "대표_아파트_단지", "상권_유형", "상권_원형",
    # 핵심 키워드 (정성 서술)
    "접근성_교통_키워드", "상권_장점_키워드", "상권_단점_리스크_키워드", "주요_배후수요_특성",
    # 키워드 태그 (3축)
    "키워드_접근성인프라", "키워드_소비배후수요", "키워드_환경리스크",
    # 업종 인사이트
    "추천_유망_업종", "비추천_주의_업종", "타깃_업종", "업종_공백", "업종_강점", "상권_한줄평",
    # 상권 기회 (모델)
    "유형", "사분면", "기회_유형", "기회점수", "기회순위",
    "배율", "격차금액_분기", "잔차_추세", "기회_인사이트", "해석주의",
    # 정량 지표
    "상주인구", "직장인구", "직주비", "청년비율", "청년인구비율", "1인가구비율",
    "아파트_평균_시가", "아파트비중순위", "지하철역", "집객시설",
    "경도", "위도",
]


def main():
    ins = pd.read_csv(INSIGHT, encoding="utf-8-sig")
    kw = pd.read_csv(KEYWORD, encoding="utf-8-sig")
    assert ins["행정동_코드"].is_unique and kw["행정동_코드"].is_unique
    assert set(kw["행정동_코드"]) <= set(ins["행정동_코드"])

    # 겹치는 컬럼이 정말 같은 값인지 확인한 뒤 키워드 쪽에서 제거
    shared = ["자치구", "상권_유형", "대표_아파트_단지", "비추천_주의_업종"]
    chk = ins.merge(kw, on="행정동_코드", suffixes=("", "_kw"))
    for c in shared:
        assert (chk[c] == chk[f"{c}_kw"]).all(), f"{c} 값 불일치"
    assert (chk["아파트시가"] == chk["아파트_평균_시가"]).all()

    kw = kw.drop(columns=shared + ["행정동_코드_명", "아파트_평균_시가"])
    ins = ins.rename(columns={"아파트시가": "아파트_평균_시가"})

    out = ins.merge(kw, on="행정동_코드", how="left", validate="one_to_one")
    assert len(out) == len(ins) and out["행정동_코드"].is_unique
    assert set(out.columns) == set(COLUMNS), set(out.columns) ^ set(COLUMNS)

    out = out[COLUMNS].sort_values(["자치구", "행정동_코드"]).reset_index(drop=True)
    out["군집"] = out["군집"].astype("Int64")
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"saved: {OUT.relative_to(ROOT)}  {out.shape}")


if __name__ == "__main__":
    main()
