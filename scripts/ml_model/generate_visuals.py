# -*- coding: utf-8 -*-
"""
Gemi_pjt - Step 3: Visualization Generator
머신러닝 소비 예측 및 갭 분석 결과 고해상도 시각화 차트 10종 생성
- 저장 경로: Gemi_pjt/image/
- 폰트: Windows 한글 시스템 폰트(Malgun Gothic) 적용
"""

import sys
from pathlib import Path

# 콘솔 UTF-8 출력 보장
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Matplotlib 한글 폰트 설정
plt.rc("font", family="Malgun Gothic")
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 300

# 경로 설정
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
IN_RESIDUALS = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "dong_consumption_residuals.csv"
IN_CATEGORIES = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "category_gap_analysis.csv"
IN_FEATURES = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "dong_features_processed.csv"
IMAGE_DIR = WORKSPACE_ROOT / "Gemi_pjt" / "image"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

# 시각화 전용 컬러 팔레트
PALETTE = {
    "primary": "#1f77b4",
    "overachieve": "#e74c3c",    # 핫스팟 (레드/코랄)
    "potential": "#2ecc71",      # 잠재력 (에메랄드 그린)
    "balanced": "#95a5a6",       # 균형 (그레이)
    "niche": "#9b59b6",          # 로컬 핫플 (퍼플)
    "low": "#34495e"             # 위축 (네이비)
}

def clean_dong_name(name):
    """'?' 문자로 깨진 동 이름 교정 (예: 상계3?4동 -> 상계3·4동)"""
    return str(name).replace("?", "·")

def generate_all_visuals():
    print("=" * 60)
    print("🎨 [Step 3] 고해상도 분석 시각화 차트 10종 생성 시작")
    print("=" * 60)

    df_res = pd.read_csv(IN_RESIDUALS, encoding="utf-8-sig")
    df_cat = pd.read_csv(IN_CATEGORIES, encoding="utf-8-sig")
    df_feat = pd.read_csv(IN_FEATURES, encoding="utf-8-sig")

    df_res["표시_동명"] = df_res["행정동_코드_명"].apply(clean_dong_name)
    df_cat["표시_동명"] = df_cat["행정동_코드_명"].apply(clean_dong_name)

    # -------------------------------------------------------------
    # 01. 피처 상관관계 히트맵
    # -------------------------------------------------------------
    print("1) 01_feature_correlation_heatmap.png 생성 중...")
    corr_cols = [
        "지출_총금액", "총_상주인구_수", "총_직장_인구_수", "총_유동인구_수",
        "집객시설_수", "지하철_역_수", "버스_정거장_수", "은행_수",
        "병원_약국_수", "아파트_평균_시가", "영역_면적"
    ]
    corr_labels = [
        "지출 총금액", "상주인구", "직장인구", "유동인구",
        "집객시설 수", "지하철역 수", "버스정류소 수", "은행 수",
        "의료시설 수", "아파트 평균시가", "토지 면적"
    ]
    # 로그 변환 후 상관관계 산출
    corr_data = np.log1p(df_feat[corr_cols]).corr()
    corr_data.columns = corr_labels
    corr_data.index = corr_labels

    fig, ax = plt.subplots(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_data, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(corr_data, mask=mask, cmap="RdYlBu_r", vmin=-0.2, vmax=1.0,
                annot=True, fmt=".2f", square=True, linewidths=.5, cbar_kws={"shrink": .8}, ax=ax)
    ax.set_title("인구·인프라 특성과 상권 소비액 간 상관관계 히트맵 (Log-Scale)", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "01_feature_correlation_heatmap.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 02. 기대 소비액 vs 실제 소비액 산점도 (기준선 & 잔차)
    # -------------------------------------------------------------
    print("2) 02_actual_vs_expected_scatter.png 생성 중...")
    fig, ax = plt.subplots(figsize=(11, 8))

    x_val = np.log10(df_res["기대_소비액_분기"] / 1e8)  # 억원 단위 log10
    y_val = np.log10(df_res["실제_소비액_분기"] / 1e8)

    # 색상 지정: 핫스팟(레드), 잠재력(그린), 균형(그레이)
    colors = []
    for z in df_res["잔차_ZScore"]:
        if z >= 1.0:
            colors.append("#e74c3c")
        elif z <= -1.0:
            colors.append("#2ecc71")
        else:
            colors.append("#95a5a6")

    scatter = ax.scatter(x_val, y_val, c=colors, alpha=0.75, s=55, edgecolors="none")

    # y = x 기준선 (기대치 완벽 일치 선)
    lim_min = min(x_val.min(), y_val.min()) - 0.2
    lim_max = max(x_val.max(), y_val.max()) + 0.2
    ax.plot([lim_min, lim_max], [lim_min, lim_max], color="#2c3e50", linestyle="--", linewidth=1.5, label="기대 소비 기준선 (Y = X)")

    # 상위 이상치 텍스트 라벨링
    top_pos = df_res.nlargest(6, "잔차_ZScore")
    top_neg = df_res.nsmallest(6, "잔차_ZScore")
    for _, row in top_pos.iterrows():
        px = np.log10(row["기대_소비액_분기"] / 1e8)
        py = np.log10(row["실제_소비액_분기"] / 1e8)
        ax.text(px + 0.05, py, clean_dong_name(row["행정동_코드_명"]), fontsize=9, fontweight="bold", color="#c0392b")

    for _, row in top_neg.iterrows():
        px = np.log10(row["기대_소비액_분기"] / 1e8)
        py = np.log10(row["실제_소비액_분기"] / 1e8)
        ax.text(px + 0.05, py, clean_dong_name(row["행정동_코드_명"]), fontsize=9, fontweight="bold", color="#27ae60")

    ax.set_xlabel("공식형 머신러닝 '기대 소비액' (log10 억원)", fontsize=12, fontweight="bold")
    ax.set_ylabel("실제 발생 '소비 지출액' (log10 억원)", fontsize=12, fontweight="bold")
    ax.set_title("서울시 425개 행정동 기대 소비액 vs 실제 소비액 비교 산점도", fontsize=14, fontweight="bold", pad=15)
    ax.grid(True, linestyle=":", alpha=0.6)

    # 커스텀 범례
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color="#2c3e50", lw=1.5, ls="--", label="기대 소비 기준선 (인구·인프라 적정선)"),
        Line2D([0], [0], marker="o", color="w", label="초과 달성 핫스팟 (Z ≥ +1.0)", markerfacecolor="#e74c3c", markersize=9),
        Line2D([0], [0], marker="o", color="w", label="균형 상권 (-1.0 < Z < +1.0)", markerfacecolor="#95a5a6", markersize=9),
        Line2D([0], [0], marker="o", color="w", label="저평가 잠재력 상권 (Z ≤ -1.0)", markerfacecolor="#2ecc71", markersize=9)
    ]
    ax.legend(handles=legend_elements, loc="upper left", frameon=True, facecolor="white", edgecolor="none", shadow=True)

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "02_actual_vs_expected_scatter.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 03. 잔차(소비 갭)의 분포 및 정규성
    # -------------------------------------------------------------
    print("3) 03_residual_distribution.png 생성 중...")
    fig, ax = plt.subplots(figsize=(10, 6))
    residuals = df_res["잔차_로그"]
    sns.histplot(residuals, kde=True, color="#3498db", bins=35, stat="density", ax=ax, alpha=0.6)

    # 정규분포 이론 곡선 추가
    mu, std = stats.norm.fit(residuals)
    x = np.linspace(residuals.min(), residuals.max(), 100)
    p = stats.norm.pdf(x, mu, std)
    ax.plot(x, p, "r--", linewidth=2, label=f"이론 정규곡선 (μ={mu:.2f}, σ={std:.2f})")

    ax.axvline(0, color="#2c3e50", linestyle="-", linewidth=1.5, label="기대치 일치 기준 (Residual = 0)")
    ax.set_title("소비 갭(잔차, Residual) 확률 밀도 분포 (정규성 검정)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("소비 잔차 [ log(실제 소비) - log(기대 소비) ]", fontsize=12)
    ax.set_ylabel("확률 밀도", fontsize=12)
    ax.legend(frameon=True)
    ax.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "03_residual_distribution.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 04. 초과 달성 상권 Top 15 바 차트
    # -------------------------------------------------------------
    print("4) 04_top15_overachiever_dongs.png 생성 중...")
    top15_pos = df_res.nlargest(15, "소비_격차_비율_pct").sort_values("소비_격차_비율_pct", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 8))
    labels = [f"{clean_dong_name(row['행정동_코드_명'])} ({row['자치구']})" for _, row in top15_pos.iterrows()]
    bars = ax.barh(labels, top15_pos["소비_격차_비율_pct"], color="#e74c3c", alpha=0.85, edgecolor="#c0392b")

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 80, bar.get_y() + bar.get_height()/2, f"+{width:,.0f}%",
                ha="left", va="center", fontsize=9, fontweight="bold", color="#c0392b")

    ax.set_title("서울시 초과 달성 소비 핫스팟 Top 15 (인구·인프라 대비 실제소비 초과율)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("기대 소비액 대비 초과 달성 비율 (%)", fontsize=12, fontweight="bold")
    ax.set_xlim(0, top15_pos["소비_격차_비율_pct"].max() * 1.15)
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "04_top15_overachiever_dongs.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 05. 저평가 소비 잠재력 상권 Top 15 바 차트
    # -------------------------------------------------------------
    print("5) 05_top15_potential_growth_dongs.png 생성 중...")
    top15_neg = df_res.nsmallest(15, "소비_격차_비율_pct").sort_values("소비_격차_비율_pct", ascending=False)

    fig, ax = plt.subplots(figsize=(11, 8))
    labels = [f"{clean_dong_name(row['행정동_코드_명'])} ({row['자치구']})" for _, row in top15_neg.iterrows()]
    bars = ax.barh(labels, top15_neg["소비_격차_비율_pct"], color="#2ecc71", alpha=0.85, edgecolor="#27ae60")

    for bar in bars:
        width = bar.get_width()
        ax.text(width - 2, bar.get_y() + bar.get_height()/2, f"{width:.1f}%",
                ha="right", va="center", fontsize=9, fontweight="bold", color="#1e8449")

    ax.set_title("서울시 저평가 소비 잠재력 상권 Top 15 (인구·인프라 대비 소비 저평가율)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("기대 소비액 대비 소비 격차 비율 (%)", fontsize=12, fontweight="bold")
    ax.set_xlim(top15_neg["소비_격차_비율_pct"].min() * 1.15, 0)
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "05_top15_potential_growth_dongs.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 06. 4분면 상권 진단 매트릭스
    # -------------------------------------------------------------
    print("6) 06_consumption_gap_quadrant.png 생성 중...")
    fig, ax = plt.subplots(figsize=(11, 9))

    x_s = df_res["인프라_규모_지수"]
    y_r = df_res["잔차_ZScore"]

    color_map = {
        "초과 달성 핫스팟 (Super-Hub)": "#e74c3c",
        "소비 잠재력 상권 (High Potential)": "#2ecc71",
        "골목 로컬 핫플레이스 (Niche Hotspot)": "#9b59b6",
        "소비 위축 지역 (Low Activity)": "#7f8c8d",
        "균형 상권 (Balanced)": "#bdc3c7"
    }

    for q_type, grp in df_res.groupby("상권_분류_유형"):
        ax.scatter(grp["인프라_규모_지수"], grp["잔차_ZScore"],
                   label=f"{q_type} ({len(grp)}개 동)",
                   color=color_map.get(q_type, "#95a5a6"),
                   s=60, alpha=0.8, edgecolors="none")

    # 4분면 기준선 (X=0, Y=0)
    ax.axvline(0, color="#2c3e50", linestyle="--", linewidth=1.2)
    ax.axhline(0, color="#2c3e50", linestyle="--", linewidth=1.2)

    # 4분면 구역 라벨
    ax.text(2.2, 3.2, "① 초과 달성 핫스팟\n(대형 인프라 + 외부소비 유입)",
            fontsize=11, fontweight="bold", color="#c0392b", ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#fadbd8", alpha=0.8, edgecolor="#e74c3c"))

    ax.text(2.2, -2.2, "② 숨은 소비 잠재력 상권 [핵심기회]\n(배후인구 풍부 + 상권개발 기회)",
            fontsize=11, fontweight="bold", color="#1e8449", ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#d5f5e3", alpha=0.8, edgecolor="#2ecc71"))

    ax.text(-2.2, 3.2, "③ 골목 로컬 핫플레이스\n(소규모 인프라 + 알짜 소비)",
            fontsize=11, fontweight="bold", color="#8e44ad", ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f4ecf7", alpha=0.8, edgecolor="#9b59b6"))

    ax.text(-2.2, -2.2, "④ 소비 위축 지역\n(인프라 낮음 + 소비 침체)",
            fontsize=11, fontweight="bold", color="#566573", ha="center",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#eaecee", alpha=0.8, edgecolor="#bdc3c7"))

    ax.set_title("서울시 425개 행정동 4분면 상권 기회 진단 매트릭스", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlabel("배후 인구 및 인프라 복합 규모 지수 (표준화 Z-Score)", fontsize=12, fontweight="bold")
    ax.set_ylabel("소비 갭 잔차 지수 (실제소비 vs 기대소비 Z-Score)", fontsize=12, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", frameon=True, shadow=True)

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "06_consumption_gap_quadrant.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 07. 공식형 모델 탄력성 계수 가중치 (영향력 랭킹)
    # -------------------------------------------------------------
    print("7) 07_formula_elasticity_weights.png 생성 중...")
    coef_data = pd.DataFrame([
        ("집객시설", 0.7096, "시설 1% 증가 시 소비 +0.71% 증가"),
        ("은행", 0.4322, "은행 1% 증가 시 소비 +0.43% 증가"),
        ("유동인구", 0.3179, "보행인구 1% 증가 시 소비 +0.32% 증가"),
        ("의료인프라", 0.1551, "병원약국 1% 증가 시 소비 +0.16% 증가"),
        ("직장인구", 0.1421, "직장인 1% 증가 시 소비 +0.14% 증가"),
        ("아파트시가", 0.0794, "시가 1% 증가 시 소비 +0.08% 증가"),
        ("공간면적", 0.0502, "면적 1% 증가 시 소비 +0.05% 증가"),
        ("지하철역", 0.0228, "역세권 1% 증가 시 소비 +0.02% 증가"),
        ("버스정류장", -0.1045, "외곽 주거 정류소 밀집 시 분산 효과"),
        ("상주인구", -0.1918, "베드타운 특성 (거주민 외부 소비 유출)")
    ], columns=["변수명", "탄력성계수", "해석"])

    coef_data = coef_data.sort_values("탄력성계수", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 7))
    bar_colors = ["#e74c3c" if c >= 0 else "#3498db" for c in coef_data["탄력성계수"]]
    bars = ax.barh(coef_data["변수명"], coef_data["탄력성계수"], color=bar_colors, alpha=0.85, edgecolor="#2c3e50")

    for bar in bars:
        w = bar.get_width()
        pos_x = w + 0.02 if w >= 0 else w - 0.02
        ha = "left" if w >= 0 else "right"
        ax.text(pos_x, bar.get_y() + bar.get_height()/2, f"{w:+.4f}",
                ha=ha, va="center", fontsize=10, fontweight="bold")

    ax.axvline(0, color="#2c3e50", linestyle="-", linewidth=1.2)
    ax.set_title("공식형 회귀 모델의 핵심 탄력성 계수 (인구·인프라 소비 견인 가중치)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("소비 탄력성 (해당 인프라가 1% 증가할 때 소비액 변화율 %)", fontsize=12, fontweight="bold")
    ax.set_xlim(-0.3, 0.85)
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "07_formula_elasticity_weights.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 08. 25개 자치구별 평균 소비 갭 비교
    # -------------------------------------------------------------
    print("8) 08_gu_residual_summary.png 생성 중...")
    gu_summary = df_res.groupby("자치구")["잔차_ZScore"].mean().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(11, 9))
    gu_colors = ["#e74c3c" if val >= 0 else "#2ecc71" for val in gu_summary.values]
    bars = ax.barh(gu_summary.index, gu_summary.values, color=gu_colors, alpha=0.85)

    for bar in bars:
        w = bar.get_width()
        pos_x = w + 0.03 if w >= 0 else w - 0.03
        ha = "left" if w >= 0 else "right"
        ax.text(pos_x, bar.get_y() + bar.get_height()/2, f"{w:+.2f}",
                ha=ha, va="center", fontsize=9, fontweight="bold")

    ax.axvline(0, color="#2c3e50", linestyle="-", linewidth=1.2)
    ax.set_title("서울시 25개 자치구별 평균 소비 갭(잔차 Z-Score) 비교", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("자치구별 평균 잔차 Z-Score (초과 달성 구 > 0 > 소비 잠재력/유출 구)", fontsize=12, fontweight="bold")
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "08_gu_residual_summary.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 09. 5대 세부 업종별 갭 분포 비교
    # -------------------------------------------------------------
    print("9) 09_category_gap_comparison.png 생성 중...")
    fig, ax = plt.subplots(figsize=(11, 7))
    sns.boxplot(data=df_cat, x="업종_명", y="잔차_ZScore", hue="업종_명", palette="Set2", ax=ax, width=0.5, legend=False)
    ax.axhline(0, color="#e74c3c", linestyle="--", linewidth=1.5, label="기대치 일치 기준")
    ax.set_title("5대 세부 업종별 소비 갭(잔차) 분포 비교", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("소비 세부 카테고리 (업종)", fontsize=12, fontweight="bold")
    ax.set_ylabel("소비 갭 잔차 Z-Score", fontsize=12, fontweight="bold")
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper right")

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "09_category_gap_comparison.png")
    plt.close(fig)

    # -------------------------------------------------------------
    # 10. 소비 잠재력 상위 동네들의 업종별 결핍 현황 딥다이브
    # -------------------------------------------------------------
    print("10) 10_potential_dongs_deepdive.png 생성 중...")
    target_potential_dongs = ["반포본동", "개포1동", "공덕동", "이촌1동", "충현동"]
    sample_cat = df_cat[df_cat["행정동_코드_명"].isin(target_potential_dongs)].copy()

    pivot_cat = sample_cat.pivot_table(index="행정동_코드_명", columns="업종_명", values="소비_격차_비율_pct")
    pivot_cat.index = [clean_dong_name(n) for n in pivot_cat.index]

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot_cat, annot=True, fmt=".1f", cmap="vlag", center=0, cbar_kws={"label": "소비 갭 비율 (%)"}, ax=ax)
    ax.set_title("대표 소비 잠재력 상권 5개 동의 업종별 소비 결핍 현황 (Gap %)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("소비 세부 업종", fontsize=12, fontweight="bold")
    ax.set_ylabel("잠재력 분석 행정동", fontsize=12, fontweight="bold")

    plt.tight_layout()
    fig.savefig(IMAGE_DIR / "10_potential_dongs_deepdive.png")
    plt.close(fig)

    print("\n🎉 [Step 3 완료] 10종 고해상도 시각화 차트 생성 완료!")
    for img_p in sorted(IMAGE_DIR.glob("*.png")):
        print(f"  - {img_p.name} ({img_p.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    generate_all_visuals()
