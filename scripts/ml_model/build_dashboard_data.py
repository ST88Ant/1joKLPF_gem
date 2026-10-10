# -*- coding: utf-8 -*-
"""
Gemi_pjt - Step 4: Dashboard Data Builder
웹 대시보드(index.html)에서 빠르고 가볍게 렌더링할 수 있도록
425개 행정동 및 세부 업종 갭 분석 데이터를 JSON으로 압축 패키징
"""

import sys
import json
from pathlib import Path

# 콘솔 UTF-8 출력 보장
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
IN_RESIDUALS = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "dong_consumption_residuals.csv"
IN_CATEGORIES = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "category_gap_analysis.csv"
IN_SUMMARY = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "model_summary.json"
OUT_JSON = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "dashboard_data.json"

def clean_dong_name(name):
    return str(name).replace("?", "·")

def build_data():
    df_res = pd.read_csv(IN_RESIDUALS, encoding="utf-8-sig")
    df_cat = pd.read_csv(IN_CATEGORIES, encoding="utf-8-sig")
    with open(IN_SUMMARY, "r", encoding="utf-8") as f:
        summary = json.load(f)

    df_res["표시_동명"] = df_res["행정동_코드_명"].apply(clean_dong_name)
    df_cat["표시_동명"] = df_cat["행정동_코드_명"].apply(clean_dong_name)

    # 행정동 목록 정제
    dongs = []
    for _, row in df_res.iterrows():
        dongs.append({
            "code": int(row["행정동_코드"]),
            "name": row["표시_동명"],
            "gu": row["자치구"],
            "lat": round(float(row["lat"]), 5),
            "lon": round(float(row["lon"]), 5),
            "actual_spend": round(float(row["실제_소비액_분기"])),
            "expected_spend": round(float(row["기대_소비액_분기"])),
            "gap_amount": round(float(row["소비_격차_금액"])),
            "gap_pct": round(float(row["소비_격차_비율_pct"]), 1),
            "residual_log": round(float(row["잔차_로그"]), 3),
            "residual_z": round(float(row["잔차_ZScore"]), 2),
            "infra_scale": round(float(row["인프라_규모_지수"]), 2),
            "type": row["상권_분류_유형"],
            "pop_res": round(float(row["총_상주인구_수"])),
            "pop_work": round(float(row["총_직장_인구_수"])),
            "pop_flow": round(float(row["총_유동인구_수"])),
            "facilities": round(float(row["집객시설_수"])),
            "subway": round(float(row["지하철_역_수"])),
            "apt_price": round(float(row["아파트_평균_시가"]))
        })

    # 업종별 상위/하위 10개 추출
    cat_summary = {}
    for cat_name, grp in df_cat.groupby("업종_명"):
        top_pos = grp.nlargest(10, "소비_격차_비율_pct")[["표시_동명", "자치구", "소비_격차_비율_pct", "실제_소비액", "기대_소비액"]].to_dict(orient="records")
        top_neg = grp.nsmallest(10, "소비_격차_비율_pct")[["표시_동명", "자치구", "소비_격차_비율_pct", "실제_소비액", "기대_소비액"]].to_dict(orient="records")
        cat_summary[cat_name] = {
            "top_overachievers": top_pos,
            "top_potentials": top_neg,
            "avg_gap_pct": round(float(grp["소비_격차_비율_pct"].median()), 1)
        }

    # 자치구 목록
    districts = sorted(df_res["자치구"].unique().tolist())

    dashboard_pkg = {
        "summary": summary,
        "districts": districts,
        "dongs": dongs,
        "categories": cat_summary
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(dashboard_pkg, f, ensure_ascii=False, indent=2)

    print(f"✅ 대시보드 패키지 데이터 생성 완료: {OUT_JSON} ({OUT_JSON.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    build_data()
