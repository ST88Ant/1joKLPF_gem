# -*- coding: utf-8 -*-
"""
서울시_행정동별_상권분석_통합.csv 기본 EDA 차트
출력: data/processed/eda_통합/*.png
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/processed/서울시_행정동별_상권분석_통합.csv"
OUT = ROOT / "data/processed/eda_통합"
OUT.mkdir(exist_ok=True)

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, MID = "#2a78d6", "#eb6834", "#f0efec"
SEQ = LinearSegmentedColormap.from_list("seq", ["#f3f7fd", "#9cc0ee", BLUE, "#0d3f80"])
DIV = LinearSegmentedColormap.from_list("div", [BLUE, MID, ORANGE])

plt.rcParams.update({
    "font.family": "Malgun Gothic", "axes.unicode_minus": False, "font.size": 10,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.edgecolor": GRID, "axes.titlesize": 12, "axes.titleweight": "bold",
})

OPP_ORDER = ["① 선점형 기회", "② 유출보완형 기회", "③ 확장형", "④ 검증·포화형", "⑤ 경고(둔화)", "⑥ 주의(위축)"]


def clean(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)


def pct_heatmap(df, row, name, title):
    ct = pd.crosstab(df[row], df["기회_유형"]).reindex(columns=OPP_ORDER, fill_value=0)
    ct = ct.loc[ct.sum(axis=1).sort_values(ascending=False).index]
    share = ct.div(ct.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(9, 0.5 * len(ct) + 1.6))
    ax.imshow(share.values, cmap=SEQ, vmin=0, vmax=60, aspect="auto")
    for i in range(share.shape[0]):
        for j in range(share.shape[1]):
            v = share.values[i, j]
            ax.text(j, i, f"{v:.0f}%\n({ct.values[i, j]})", ha="center", va="center", fontsize=8.5,
                    color="white" if v >= 35 else INK)
    ax.set_xticks(range(len(OPP_ORDER)), [o.replace(" ", "\n", 1) for o in OPP_ORDER], fontsize=9)
    ax.set_yticks(range(len(ct)), [f"{i} (n={n})" for i, n in ct.sum(axis=1).items()])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title(title, loc="left")
    save(fig, name)


def main():
    d = pd.read_csv(SRC, encoding="utf-8-sig")
    ok = d[d["기회_유형"] != "데이터점검"]

    # 1. 배율 분포 (로그 축)
    fig, ax = plt.subplots(figsize=(9, 4))
    bins = np.logspace(np.log10(0.1), np.log10(70), 45)
    ax.hist(d["배율"], bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=1)
    ax.set_xscale("log")
    for x, lab, ha in [(2 / 3, "저평가 기준 ×0.67 ", "right"), (1.5, " 초과달성 기준 ×1.5", "left")]:
        ax.axvline(x, color=INK2, lw=1, ls="--")
        ax.text(x, ax.get_ylim()[1] * 0.95, lab, color=INK2, fontsize=9, va="top", ha=ha)
    ax.set_xticks([0.1, 0.25, 0.5, 1, 2, 5, 10, 50], ["×0.1", "×0.25", "×0.5", "×1", "×2", "×5", "×10", "×50"])
    ax.set_xlabel("배율 (실제 소비 ÷ 기대 소비, 로그 축)")
    ax.set_ylabel("행정동 수")
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    clean(ax)
    ax.set_title("배율 분포 — 대부분 ×0.67~×1.5, 양쪽 꼬리가 길다", loc="left")
    save(fig, "01_배율분포.png")

    # 2·3. 기회 유형 구성
    pct_heatmap(ok, "금융MBTI", "02_금융MBTI_기회유형.png", "금융MBTI별 기회 유형 구성 (행 기준 %)")
    pct_heatmap(ok, "상권_원형", "03_상권원형_기회유형.png", "상권 원형별 기회 유형 구성 (행 기준 %)")

    # 4. 스피어만 상관
    cols = ["배율", "잔차_추세", "상주인구", "직장인구", "직주비", "청년비율", "청년인구비율",
            "1인가구비율", "아파트_평균_시가", "아파트비중순위", "지하철역", "집객시설"]
    corr = d[cols].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(9, 7.5))
    ax.imshow(corr.values, cmap=DIV, vmin=-1, vmax=1)
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if abs(v) >= 0.6 else INK)
    ax.set_xticks(range(len(cols)), cols, rotation=45, ha="right")
    ax.set_yticks(range(len(cols)), cols)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("수치 컬럼 간 스피어만 상관 (파랑 -, 주황 +)", loc="left")
    save(fig, "04_상관행렬.png")

    # 5. 청년비율 × 잔차 추세
    fig, ax = plt.subplots(figsize=(9, 4.5))
    s = ok[ok["잔차_추세"].abs() < 0.6]
    ax.scatter(s["청년비율"], s["잔차_추세"] * 100, s=18, color=BLUE, alpha=0.65,
               edgecolor=SURFACE, linewidth=0.8)
    z = np.polyfit(s["청년비율"], s["잔차_추세"] * 100, 1)
    xs = np.linspace(s["청년비율"].min(), s["청년비율"].max(), 50)
    ax.plot(xs, np.polyval(z, xs), color=INK2, lw=2)
    ax.axhline(0, color=GRID, lw=1)
    ax.set_xlabel("청년비율 (20·30대 상주인구 ÷ 상주인구)")
    ax.set_ylabel("잔차 추세 (%/년, +면 개선)")
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    clean(ax)
    ax.set_title("청년 비율이 높을수록 기대 대비 소비가 식는 중 (ρ = -0.45)", loc="left")
    save(fig, "05_청년비율_잔차추세.png")
    print("saved:", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
