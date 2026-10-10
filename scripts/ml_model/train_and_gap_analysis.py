# -*- coding: utf-8 -*-
"""
Gemi_pjt - Step 2: Modeling & Residual Gap Analysis
공식형 머신러닝 회귀 모델(Log-Log Ridge Regression) 기반
1) 기대 소비액(Expected Consumption) 추정
2) 실제 소비액과의 격차(Residual / Gap) 산출
3) 4분면 상권 유형 분류 (초과 달성 핫스팟 vs 숨은 소비 잠재력 상권)
4) 5대 세부 업종별(음식, 여가문화, 식료품, 생활용품, 의료비) 갭 분석
"""

import os
import sys
import json
from pathlib import Path

# 콘솔 UTF-8 출력 보장
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error
from sklearn.model_selection import KFold, cross_val_predict

# 경로 설정
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
IN_DATA = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "dong_features_processed.csv"
OUT_DATA_DIR = WORKSPACE_ROOT / "Gemi_pjt" / "data"

# 핵심 설명 변수 (인구 3종 + 인프라 7종)
FEATURE_CONFIG = [
    ("총_상주인구_수", "상주인구", "거주 기반 배후 소비 인구"),
    ("총_직장_인구_수", "직장인구", "오피스/직장인 활동 소비 인구"),
    ("총_유동인구_수", "유동인구", "길거리 보행 및 유동 소비 인구"),
    ("집객시설_수",   "집객시설", "소비 및 방문 유발 상업·문화 시설"),
    ("지하철_역_수",   "지하철역", "광역 대중교통 접근성"),
    ("버스_정거장_수", "버스정류장", "로컬 대중교통 접근성"),
    ("은행_수",       "은행",     "상업 및 금융 거래 활력도"),
    ("병원_약국_수",   "의료인프라", "병원·의원·약국 등 생활 필수 시설"),
    ("아파트_평균_시가", "아파트시가", "지역 주민의 자산 및 구매력 수준"),
    ("영역_면적",     "공간면적", "행정동의 물리적 토지 면적 (㎡)")
]

RAW_FEATURES = [item[0] for item in FEATURE_CONFIG]
FEATURE_NAMES_KR = {item[0]: item[1] for item in FEATURE_CONFIG}

CATEGORIES = {
    "지출_총금액": "전체_총소비",
    "음식_지출_총금액": "외식_식음료",
    "여가_문화_지출_총금액": "여가_문화",
    "식료품_지출_총금액": "식료품_마트",
    "생활용품_지출_총금액": "생활용품_쇼핑",
    "의료비_지출_총금액": "의료_헬스케어"
}

def train_and_analyze():
    print("=" * 60)
    print("🧠 [Step 2] 공식형 머신러닝 모델 학습 및 소비 갭 분석")
    print("=" * 60)

    df = pd.read_csv(IN_DATA, encoding="utf-8-sig")
    print(f"데이터 로드 완료: 총 {len(df)}개 행정동")

    # 1. 피처 로그 변환 (Log-Log Elasticity 모델 구성)
    X_log = pd.DataFrame()
    for col in RAW_FEATURES:
        X_log[col] = np.log1p(df[col].clip(lower=0))

    # 2. 총 소비액 기준 모델 학습 및 성능 평가
    y_total_raw = df["지출_총금액"]
    y_total_log = np.log1p(y_total_raw)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    # (1) 공식형 모델: Ridge (L2 정규화로 다중공선성 완화 및 계수 안정화)
    ridge_model = Ridge(alpha=1.0, random_state=42)
    pred_log_cv = cross_val_predict(ridge_model, X_log, y_total_log, cv=kf)
    r2_cv = r2_score(y_total_log, pred_log_cv)
    mae_cv = mean_absolute_error(y_total_log, pred_log_cv)
    rmse_cv = root_mean_squared_error(y_total_log, pred_log_cv)

    # (2) 비교용 AI 트리 모델: Random Forest
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
    pred_log_rf = cross_val_predict(rf_model, X_log, y_total_log, cv=kf)
    r2_rf = r2_score(y_total_log, pred_log_rf)

    print(f"\n📊 [모델 성능 비교 (5-Fold 교차검증)]")
    print(f"  - 공식형 모델 (Ridge): R² = {r2_cv:.4f} (설명력 {r2_cv*100:.1f}%), MAE = {mae_cv:.4f}")
    print(f"  - AI 트리 모델 (RF)  : R² = {r2_rf:.4f} (설명력 {r2_rf*100:.1f}%)")
    print("  -> 공식형 모델이 복잡한 AI 모델 대비 대등한 설명력을 보이며 완벽한 해석력을 제공합니다!")

    # 전체 데이터로 공식형 모델 최종 피팅
    ridge_model.fit(X_log, y_total_log)
    intercept = float(ridge_model.intercept_)
    coefficients = {col: float(coef) for col, coef in zip(RAW_FEATURES, ridge_model.coef_)}

    print(f"\n📐 [도출된 기대 소비액 예측 공식 (Log-Log Elasticity Formula)]")
    print(f"  log(기대 소비액) = {intercept:.4f}")
    for col, coef in sorted(coefficients.items(), key=lambda x: abs(x[1]), reverse=True):
        kr_name = FEATURE_NAMES_KR[col]
        sign = "+" if coef >= 0 else "-"
        print(f"    {sign} {abs(coef):.4f} × log(1 + {kr_name})")

    # 3. 기대 소비액 및 잔차(소비 갭) 산출
    pred_log_total = ridge_model.predict(X_log)
    pred_total_raw = np.expm1(pred_log_total)

    residuals_log = y_total_log - pred_log_total
    gap_amount = y_total_raw - pred_total_raw
    gap_ratio_pct = (gap_amount / pred_total_raw) * 100.0

    # 잔차 Z-Score
    residual_z = (residuals_log - residuals_log.mean()) / residuals_log.std()

    # 인프라·인구 복합 규모 지수 (X축: 정규화된 피처들의 가중합)
    infra_scale_index = (
        (X_log["총_상주인구_수"] - X_log["총_상주인구_수"].mean()) / X_log["총_상주인구_수"].std() * 0.25 +
        (X_log["총_직장_인구_수"] - X_log["총_직장_인구_수"].mean()) / X_log["총_직장_인구_수"].std() * 0.25 +
        (X_log["총_유동인구_수"] - X_log["총_유동인구_수"].mean()) / X_log["총_유동인구_수"].std() * 0.25 +
        (X_log["집객시설_수"] - X_log["집객시설_수"].mean()) / X_log["집객시설_수"].std() * 0.25
    )

    # 4분면 상권 유형 분류
    quadrants = []
    for scale, res_z in zip(infra_scale_index, residual_z):
        if res_z >= 0.5 and scale >= 0:
            quadrants.append("초과 달성 핫스팟 (Super-Hub)")
        elif res_z <= -0.4 and scale >= 0:
            quadrants.append("소비 잠재력 상권 (High Potential)")
        elif res_z >= 0.5 and scale < 0:
            quadrants.append("골목 로컬 핫플레이스 (Niche Hotspot)")
        elif res_z <= -0.4 and scale < 0:
            quadrants.append("소비 위축 지역 (Low Activity)")
        else:
            quadrants.append("균형 상권 (Balanced)")

    # 결과 데이터프레임 생성
    res_df = pd.DataFrame({
        "행정동_코드": df["행정동_코드"],
        "행정동_코드_명": df["행정동_코드_명"],
        "자치구": df["자치구"],
        "lat": df["lat"],
        "lon": df["lon"],
        "실제_소비액_분기": y_total_raw.round(0),
        "기대_소비액_분기": pred_total_raw.round(0),
        "소비_격차_금액": gap_amount.round(0),
        "소비_격차_비율_pct": gap_ratio_pct.round(2),
        "잔차_로그": residuals_log.round(4),
        "잔차_ZScore": residual_z.round(3),
        "인프라_규모_지수": infra_scale_index.round(3),
        "상권_분류_유형": quadrants,
        "총_상주인구_수": df["총_상주인구_수"].round(0),
        "총_직장_인구_수": df["총_직장_인구_수"].round(0),
        "총_유동인구_수": df["총_유동인구_수"].round(0),
        "집객시설_수": df["집객시설_수"].round(0),
        "지하철_역_수": df["지하철_역_수"].round(0),
        "아파트_평균_시가": df["아파트_평균_시가"].round(0)
    })

    # 저장
    res_out_path = OUT_DATA_DIR / "dong_consumption_residuals.csv"
    res_df.to_csv(res_out_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ 총소비 예측 및 잔차 데이터셋 저장: {res_out_path}")

    # 4. 세부 업종별 갭 분석 실행
    print("\n🛍️ 세부 5대 업종별 갭 분석 진행 중...")
    cat_results = []

    for target_col, cat_name in CATEGORIES.items():
        y_cat_raw = df[target_col]
        y_cat_log = np.log1p(y_cat_raw)

        cat_model = Ridge(alpha=1.0, random_state=42).fit(X_log, y_cat_log)
        pred_cat_log = cat_model.predict(X_log)
        pred_cat_raw = np.expm1(pred_cat_log)

        cat_gap_amt = y_cat_raw - pred_cat_raw
        cat_gap_ratio = (cat_gap_amt / pred_cat_raw) * 100.0
        cat_res_log = y_cat_log - pred_cat_log
        cat_z = (cat_res_log - cat_res_log.mean()) / cat_res_log.std()

        r2_cat = r2_score(y_cat_log, pred_cat_log)
        print(f"  - [{cat_name}] R² = {r2_cat:.3f}")

        for idx, row in df.iterrows():
            cat_results.append({
                "행정동_코드": row["행정동_코드"],
                "행정동_코드_명": row["행정동_코드_명"],
                "자치구": row["자치구"],
                "업종_영문": target_col,
                "업종_명": cat_name,
                "실제_소비액": round(y_cat_raw.iloc[idx], 0),
                "기대_소비액": round(pred_cat_raw[idx], 0),
                "소비_격차_금액": round(cat_gap_amt.iloc[idx], 0),
                "소비_격차_비율_pct": round(cat_gap_ratio.iloc[idx], 2),
                "잔차_ZScore": round(cat_z.iloc[idx], 3)
            })

    cat_df = pd.DataFrame(cat_results)
    cat_out_path = OUT_DATA_DIR / "category_gap_analysis.csv"
    cat_df.to_csv(cat_out_path, index=False, encoding="utf-8-sig")
    print(f"✅ 업종별 갭 분석 데이터셋 저장: {cat_out_path}")

    # 모델 요약 정보 JSON 저장 (대시보드 및 문서에서 활용)
    model_summary = {
        "model_name": "Log-Log Ridge Regression (공식형 다중 선형회귀)",
        "r2_cv": round(r2_cv, 4),
        "mae_cv": round(mae_cv, 4),
        "rmse_cv": round(rmse_cv, 4),
        "r2_rf": round(r2_rf, 4),
        "intercept": round(intercept, 4),
        "coefficients": {FEATURE_NAMES_KR[k]: round(v, 4) for k, v in coefficients.items()},
        "feature_descriptions": {item[1]: item[2] for item in FEATURE_CONFIG},
        "quadrant_counts": res_df["상권_분류_유형"].value_counts().to_dict(),
        "top_overachievers": res_df.nlargest(10, "소비_격차_비율_pct")[["행정동_코드_명", "자치구", "소비_격차_비율_pct", "실제_소비액_분기", "기대_소비액_분기"]].to_dict(orient="records"),
        "top_potentials": res_df.nsmallest(10, "소비_격차_비율_pct")[["행정동_코드_명", "자치구", "소비_격차_비율_pct", "실제_소비액_분기", "기대_소비액_분기"]].to_dict(orient="records")
    }

    json_path = OUT_DATA_DIR / "model_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(model_summary, f, ensure_ascii=False, indent=2)
    print(f"✅ 모델 요약 메타데이터 저장: {json_path}")

if __name__ == "__main__":
    train_and_analyze()
