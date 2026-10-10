# -*- coding: utf-8 -*-
"""
Gemi_pjt - Step 1: Data Preprocessing Pipeline
인구·인프라 기반 소비 예측 모델을 위한 7대 공공데이터 정제 및 병합
- 원본 데이터(data/raw/)는 보존하며, 가공 데이터는 Gemi_pjt/data/에 저장합니다.
- 분석 기준: 2025년 4개 분기(2025Q1~2025Q4) 평균을 산출하여 계절성 노이즈를 제거한 연간 분기평균 기준선 구축.
"""

import os
import sys
import re
from pathlib import Path

# 콘솔 UTF-8 출력 보장 (Windows CP949 에러 방지)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np
from pyproj import Transformer

# 경로 설정
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = WORKSPACE_ROOT / "data" / "raw"
PROCESSED_DIR = WORKSPACE_ROOT / "data" / "processed"
OUT_DATA_DIR = WORKSPACE_ROOT / "Gemi_pjt" / "data"
OUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

TARGET_QUARTERS = [20251, 20252, 20253, 20254]

def get_gu_mapping():
    """행정동 코드 앞 5자리로 자치구명 매핑"""
    gu_df = pd.read_csv(RAW_DIR / "OA-22182_상주인구_자치구.csv", encoding="utf-8-sig", dtype={"자치구_코드": str})
    return dict(zip(gu_df["자치구_코드"], gu_df["자치구_코드_명"]))

def load_and_avg(fname, value_cols, filter_q=TARGET_QUARTERS):
    """분기 데이터 로드 후 2025년 4분기 평균 산출"""
    df = pd.read_csv(RAW_DIR / fname, encoding="utf-8-sig", dtype={"행정동_코드": int})
    df = df[df["기준_년분기_코드"].isin(filter_q)].copy()
    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # 4분기 평균 집계
    grouped = df.groupby(["행정동_코드", "행정동_코드_명"])[value_cols].mean().reset_index()
    return grouped

def run_data_prep():
    print("=" * 60)
    print("🚀 [Step 1] 데이터 수집 및 정제 파이프라인 시작")
    print("=" * 60)

    gu_map = get_gu_mapping()

    # 1. 소비 데이터 (지출 총금액 및 세부 업종별 금액)
    spend_cols = [
        "지출_총금액", "식료품_지출_총금액", "의류_신발_지출_총금액", "생활용품_지출_총금액",
        "의료비_지출_총금액", "교통_지출_총금액", "교육_지출_총금액", "유흥_지출_총금액",
        "여가_문화_지출_총금액", "기타_지출_총금액", "음식_지출_총금액"
    ]
    print("1) 소비 데이터 집계 중... (지출 총금액 및 10개 업종)")
    df_spend = load_and_avg("OA-22166_소비_행정동.csv", spend_cols)
    print(f"   -> 총 {len(df_spend)}개 행정동 소비 데이터 확보")

    # 2. 상주인구 데이터
    res_cols = [
        "총_상주인구_수", "남성_상주인구_수", "여성_상주인구_수",
        "연령대_10_상주인구_수", "연령대_20_상주인구_수", "연령대_30_상주인구_수",
        "연령대_40_상주인구_수", "연령대_50_상주인구_수", "연령대_60_이상_상주인구_수",
        "총_가구_수", "아파트_가구_수"
    ]
    print("2) 상주인구 및 가구 수 집계 중...")
    df_res = load_and_avg("OA-22183_상주인구_행정동.csv", res_cols).drop(columns=["행정동_코드_명"])

    # 3. 직장인구 데이터
    work_cols = [
        "총_직장_인구_수", "남성_직장_인구_수", "여성_직장_인구_수",
        "연령대_20_직장_인구_수", "연령대_30_직장_인구_수", "연령대_40_직장_인구_수", "연령대_50_직장_인구_수"
    ]
    print("3) 직장인구 집계 중...")
    df_work = load_and_avg("OA-22184_직장인구_행정동.csv", work_cols).drop(columns=["행정동_코드_명"])

    # 4. 유동인구 데이터
    flow_cols = [
        "총_유동인구_수", "남성_유동인구_수", "여성_유동인구_수",
        "연령대_20_유동인구_수", "연령대_30_유동인구_수", "연령대_40_유동인구_수", "연령대_50_유동인구_수",
        "시간대_11_14_유동인구_수", "시간대_17_21_유동인구_수",
        "월요일_유동인구_수", "화요일_유동인구_수", "수요일_유동인구_수",
        "목요일_유동인구_수", "금요일_유동인구_수", "토요일_유동인구_수", "일요일_유동인구_수"
    ]
    print("4) 길단위 유동인구 집계 중...")
    df_flow = load_and_avg("OA-22178_길단위인구_행정동.csv", flow_cols).drop(columns=["행정동_코드_명"])

    # 5. 집객시설 인프라
    infra_cols = [
        "집객시설_수", "관공서_수", "은행_수", "종합병원_수", "일반_병원_수", "약국_수",
        "백화점_수", "슈퍼마켓_수", "극장_수", "숙박_시설_수", "지하철_역_수", "버스_정거장_수"
    ]
    print("5) 집객시설 및 교통 인프라 집계 중...")
    df_infra = load_and_avg("OA-22169_집객시설_행정동.csv", infra_cols).drop(columns=["행정동_코드_명"])

    # 6. 아파트 주거자산
    apt_cols = [
        "아파트_단지_수", "아파트_평균_면적", "아파트_평균_시가",
        "아파트_가격_6_억_이상_세대_수"
    ]
    print("6) 아파트 주거자산 집계 중...")
    df_apt = load_and_avg("OA-22163_아파트_행정동.csv", apt_cols).drop(columns=["행정동_코드_명"])

    # 7. 행정동 영역 및 좌표
    print("7) 공간 영역 면적 및 위경도(WGS84) 변환 중...")
    df_area = pd.read_csv(RAW_DIR / "OA-22160_영역_행정동.csv", encoding="utf-8-sig", dtype={"행정동_코드": int})
    transformer = Transformer.from_crs("EPSG:5181", "EPSG:4326", always_xy=True)
    lons, lats = transformer.transform(df_area["엑스좌표_값"].values, df_area["와이좌표_값"].values)
    df_area["lon"] = lons
    df_area["lat"] = lats
    df_area = df_area[["행정동_코드", "영역_면적", "lat", "lon"]]

    # 병합
    print("8) 전체 데이터셋 통합 병합 중...")
    merged = df_spend.merge(df_res, on="행정동_코드", how="left")
    merged = merged.merge(df_work, on="행정동_코드", how="left")
    merged = merged.merge(df_flow, on="행정동_코드", how="left")
    merged = merged.merge(df_infra, on="행정동_코드", how="left")
    merged = merged.merge(df_apt, on="행정동_코드", how="left")
    merged = merged.merge(df_area, on="행정동_코드", how="left")

    # 자치구명 부여
    merged["행정동_코드_str"] = merged["행정동_코드"].astype(str).str.zfill(8)
    merged["자치구_코드"] = merged["행정동_코드_str"].str[:5]
    merged["자치구"] = merged["자치구_코드"].map(gu_map).fillna("기타")

    # 결측치 정제 (수치형 컬럼 전체 결측치 0 처리)
    merged["총_직장_인구_수"] = merged["총_직장_인구_수"].fillna(0)
    merged["아파트_단지_수"] = merged["아파트_단지_수"].fillna(0)
    merged["아파트_평균_시가"] = merged["아파트_평균_시가"].fillna(0)
    merged["지하철_역_수"] = merged["지하철_역_수"].fillna(0)
    merged["병원_약국_수"] = merged["종합병원_수"] + merged["일반_병원_수"] + merged["약국_수"]
    merged["주말_유동인구_수"] = merged["토요일_유동인구_수"] + merged["일반_병원_수"] if "토요일_유동인구_수" in merged else 0
    if "토요일_유동인구_수" in merged and "일요일_유동인구_수" in merged:
        merged["주말_유동인구_수"] = merged["토요일_유동인구_수"] + merged["일요일_유동인구_수"]
        merged["주중_유동인구_수"] = (
            merged["월요일_유동인구_수"] + merged["화요일_유동인구_수"] +
            merged["수요일_유동인구_수"] + merged["목요일_유동인구_수"] + merged["금요일_유동인구_수"]
        )

    # 모든 수치형 결측치 일괄 0 채움
    num_cols = merged.select_dtypes(include=[np.number]).columns
    merged[num_cols] = merged[num_cols].fillna(0)

    # 컬럼 순서 재배치
    front_cols = ["행정동_코드", "행정동_코드_명", "자치구", "lat", "lon", "영역_면적"]
    other_cols = [c for c in merged.columns if c not in front_cols and c not in ["행정동_코드_str", "자치구_코드"]]
    final_df = merged[front_cols + other_cols].copy()

    # 결과 저장
    out_path = OUT_DATA_DIR / "dong_features_processed.csv"
    final_df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ [Step 1 완료] 가공 데이터셋 저장 완료: {out_path}")
    print(f"   - 총 행정동 수: {len(final_df)}개")
    print(f"   - 특성 변수 수: {final_df.shape[1]}개")
    print(f"   - 결측치 총합: {final_df.isna().sum().sum()}개 (완전 결측치 제로)")

if __name__ == "__main__":
    run_data_prep()
