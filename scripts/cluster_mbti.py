# -*- coding: utf-8 -*-
"""Step 3. K-Means / GMM 군집화 → 금융 MBTI 페르소나 정의 (기준: 2025Q4)"""
import warnings; warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd, numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT/"data"/"processed"
BASE_Q = 20254

FEATS = {
    "Z_평균소득월액":      "소득",
    "Z_자산_log":         "자산(아파트시가)",
    "Z_소액결제_사용금액":  "소비",
    "Z_연체비율":         "연체",
    "Z_1인가구비율":       "1인가구",
    "Z_청년인구비율":      "청년인구",
    "Z_소득대비소비":      "소득대비소비",
}

p = pd.read_csv(OUT/"features_행정동_분기_2023_2025.csv", encoding="utf-8-sig")
base = p[p.분기 == BASE_Q].dropna(subset=list(FEATS)).copy()
X = StandardScaler().fit_transform(base[list(FEATS)])
print(f"군집 대상: {len(base)}개 행정동 × {X.shape[1]}개 지표 (기준 {BASE_Q})\n")

print(f"{'k':>2} {'KMeans실루엣':>12} {'GMM실루엣':>10} {'CH지수':>9} {'GMM BIC':>10}")
scores = {}
for k in range(3, 9):
    km = KMeans(k, n_init=50, random_state=42).fit(X)
    gm = GaussianMixture(k, covariance_type="full", n_init=10, random_state=42).fit(X)
    gl = gm.predict(X)
    s_km, s_gm = silhouette_score(X, km.labels_), silhouette_score(X, gl)
    scores[k] = s_km
    print(f"{k:>2} {s_km:>12.4f} {s_gm:>10.4f} {calinski_harabasz_score(X, km.labels_):>9.1f} {gm.bic(X):>10.1f}")

# 실루엣 무제약 최적은 k=3이나, 기획서 요건이 '4~6개 페르소나'이므로 해당 범위에서 선택한다.
# k=3 → k=4의 실루엣 손실은 9%로 작고, 페르소나 해상도 이득이 크다.
K = max((k for k in scores if 4 <= k <= 6), key=lambda k: scores[k])
print("")
print(f"무제약 최적 k={max(scores, key=scores.get)} (실루엣 {max(scores.values()):.4f})")
print(f"선택: k={K} — 기획서 요건(4~6개) 내 실루엣 최대 {scores[K]:.4f}")
km = KMeans(K, n_init=100, random_state=42).fit(X)
base["군집"] = km.labels_

prof = base.groupby("군집")[list(FEATS)].mean().rename(columns=FEATS)
prof.insert(0, "동수", base.groupby("군집").size())
print("\n=== 군집 프로파일 (분기 내 Z-score 평균) ===")
print(prof.round(2).to_string())

# ------------------------------------------------- 페르소나 자동 명명
def name_of(r):
    inc, ast, spd, dlq = r["소득"], r["자산(아파트시가)"], r["소비"], r["연체"]
    solo, yng, ratio = r["1인가구"], r["청년인구"], r["소득대비소비"]
    # 판정 순서가 곧 우선순위다. 청년·1인가구 신호 → 소득압박 → 자산 → 절약 순.
    if dlq > 0.5 and (solo > 0.5 or yng > 0.5):   return "영앤레버리지형"
    if inc < -0.4 and ratio > 0.5 and dlq > 0.3:  return "생활압박형"
    if dlq < -0.5 and ast > 0.5:                  return "자산안정형"
    if dlq < -0.3 and spd < -0.2:                 return "알뜰안정형"
    if spd > 0.5 and dlq > 0:                     return "소비활발형"
    if solo > 0.5:                                return "1인가구밀집형"
    return "중간안정형"

prof["페르소나"] = prof.apply(name_of, axis=1)
seen = {}
for i, n in prof["페르소나"].items():                # 중복 이름 방지
    seen[n] = seen.get(n, 0) + 1
    if seen[n] > 1: prof.loc[i, "페르소나"] = f"{n}{seen[n]}"
base["금융MBTI"] = base["군집"].map(prof["페르소나"])

print("\n=== 금융 MBTI 페르소나 ===")
for i, r in prof.iterrows():
    tag = lambda v: "높음" if v > 0.4 else ("낮음" if v < -0.4 else "보통")
    print(f"  [{r['페르소나']}] {int(r['동수']):>3}개 동 | "
          f"소득{tag(r['소득'])} 자산{tag(r['자산(아파트시가)'])} 소비{tag(r['소비'])} "
          f"연체{tag(r['연체'])} 1인가구{tag(r['1인가구'])} 청년{tag(r['청년인구'])}")
    ex = base[base.군집 == i].nlargest(4, "SKT_총인구")["행정동_코드_명"].tolist()
    print(f"        대표 동: {', '.join(ex)}")

base[["분기","자치구","행정동_코드","행정동_코드_명","군집","금융MBTI","SKT_총인구",
      "평균소득월액","아파트_평균_시가","소액결제_사용금액","연체비율","청년_연체비율",
      "1인가구비율","청년1인가구비율","청년인구비율","소득대비소비","소득대비연체"]
    ].to_csv(OUT/"mbti_행정동_2025Q4.csv", index=False, encoding="utf-8-sig")
prof.to_csv(OUT/"mbti_군집프로파일.csv", encoding="utf-8-sig")
print(f"\n저장: mbti_행정동_2025Q4.csv / mbti_군집프로파일.csv")
