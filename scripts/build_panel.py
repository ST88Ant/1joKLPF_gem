# -*- coding: utf-8 -*-
"""
행정동 × 분기 금융 건전성 패널 구축 (2023Q1 ~ 2025Q4)

축 구성
  소득   : 국민연금 시군구 평균소득월액 (자치구×연)  → 상대지수
  자산   : 상권분석 아파트 평균시가        (행정동×분기)
  소비   : SKT 소액결재 사용금액 평균      (행정동×성×연령, 야간상주지=거주지 기준)
  연체   : SKT 최근 3개월 내 요금 연체 비율 (동)
  1인가구 : SKT 1인가구수                   (동)
  인구   : 상권분석 상주인구 연령대별       (행정동×분기)
  상권   : 상권분석 지출총액/집객시설/유동인구 → 보조지표
"""
import re, zipfile, io, sys, warnings
warnings.filterwarnings("ignore")
from pathlib import Path
import pandas as pd, numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW, LIV, OUT = ROOT/"data"/"raw", ROOT/"data"/"raw"/"living", ROOT/"data"/"processed"
OUT.mkdir(parents=True, exist_ok=True)

QUARTERS = [f"{y}{q}" for y in (2023, 2024, 2025) for q in (1, 2, 3, 4)]
QMONTH   = {"1": "03", "2": "06", "3": "09", "4": "12"}

def norm(s):
    """행정동명 조인키: 가운뎃점(·)과 물음표(?) 혼용 + 공백 제거.
    서울 열린데이터광장 원본 CSV는 '종로1?2?3?4가동'처럼 ·를 ?로 저장한다."""
    return re.sub(r"[·\?\s]", "", str(s))

# ---------------------------------------------------------------- 상권분석 CSV
_GU = None
def gu_map():
    """자치구_코드(5자리) → 자치구명. 행정동_코드 앞 5자리와 일치한다."""
    global _GU
    if _GU is None:
        g = pd.read_csv(RAW/"OA-22182_상주인구_자치구.csv", encoding="utf-8-sig",
                        dtype={"자치구_코드": str})
        _GU = dict(zip(g["자치구_코드"], g["자치구_코드_명"]))
    return _GU

def load_sang(fname, cols=None):
    df = pd.read_csv(RAW/fname, encoding="utf-8-sig", dtype={"행정동_코드": str})
    df = df[df["기준_년분기_코드"].astype(str).isin(QUARTERS)].copy()
    df["분기"] = df["기준_년분기_코드"].astype(str)
    df["동키"] = df["행정동_코드_명"].map(norm)
    df["자치구"] = df["행정동_코드"].str[:5].map(gu_map())
    return df[["분기", "자치구", "동키", "행정동_코드", "행정동_코드_명"] + (cols or [])]

# ------------------------------------------------------------------- SKT XLSX
def skt_sources(kind):
    """(분기코드, 읽기함수) 목록. 2023은 zip 내부에서, 2024~25는 개별 xlsx."""
    zf = LIV/("통신정보_2023_전체.zip" if kind == "tel" else "관심집단_2023_전체.zip")
    z = zipfile.ZipFile(zf)
    names = {}
    for i in z.infolist():
        try: nm = i.filename.encode("cp437").decode("cp949")
        except Exception: nm = i.filename
        m = re.match(r"2023\.(\d+)월", nm)
        if m: names[int(m.group(1))] = i.filename
    for q in "1234":
        mth = int(QMONTH[q])
        if mth in names:
            yield f"2023{q}", (lambda fn=names[mth]: io.BytesIO(z.read(fn)))
    pre_ = "통신정보" if kind == "tel" else "관심집단"
    for y in (2024, 2025):
        for q in "1234":
            p = LIV/f"{pre_}_{y}.{QMONTH[q]}.xlsx"
            if p.exists():
                yield f"{y}{q}", (lambda pp=p: pp)

def wmean(v, w):
    v, w = pd.to_numeric(v, errors="coerce"), pd.to_numeric(w, errors="coerce")
    m = v.notna() & w.notna() & (w > 0)
    return np.nan if not m.any() or w[m].sum() == 0 else float((v[m]*w[m]).sum()/w[m].sum())

def agg_tel():
    rows = []
    for qcode, src in skt_sources("tel"):
        df = pd.read_excel(src())
        df.columns = [str(c).strip() for c in df.columns]
        c_gu, c_dong = "자치구", ("행정동" if "행정동" in df.columns else "행정동명")
        c_pop = "총인구수" if "총인구수" in df.columns else "총인구"
        c_dlq = next(c for c in df.columns if "연체" in c)
        c_pay = next(c for c in df.columns if "소액결재 사용금액 평균" in c)
        c_age, c_solo = "연령대", "1인가구수"
        df["_age"] = pd.to_numeric(df[c_age], errors="coerce")
        for (gu, dong), g in df.groupby([c_gu, c_dong]):
            y = g[g["_age"].between(20, 39)]
            rows.append(dict(
                분기=qcode, 자치구=gu, 동키=norm(dong), 행정동명=dong,
                SKT_총인구=pd.to_numeric(g[c_pop], errors="coerce").sum(),
                SKT_1인가구수=pd.to_numeric(g[c_solo], errors="coerce").sum(),
                연체비율=wmean(g[c_dlq], g[c_pop]),
                소액결제_사용금액=wmean(g[c_pay], g[c_pop]),
                청년_인구=pd.to_numeric(y[c_pop], errors="coerce").sum(),
                청년_1인가구수=pd.to_numeric(y[c_solo], errors="coerce").sum(),
                청년_연체비율=wmean(y[c_dlq], y[c_pop]),
                청년_소액결제=wmean(y[c_pay], y[c_pop]),
            ))
        print(f"  [통신정보] {qcode}  {len(df):>6}행 → 동 집계", flush=True)
    return pd.DataFrame(rows)

def agg_interest():
    rows = []
    for qcode, src in skt_sources("int"):
        df = pd.read_excel(src())
        df.columns = [str(c).strip() for c in df.columns]
        c_dong = "행정동명" if "행정동명" in df.columns else "행정동"
        c_pop = "총인구" if "총인구" in df.columns else "총인구수"
        c_fin = next((c for c in df.columns if "재정상태" in c), None)
        for (gu, dong), g in df.groupby(["자치구", c_dong]):
            rows.append(dict(분기=qcode, 자치구=gu, 동키=norm(dong),
                             재정관심집단=pd.to_numeric(g[c_fin], errors="coerce").sum() if c_fin else np.nan,
                             재정관심_인구=pd.to_numeric(g[c_pop], errors="coerce").sum()))
        print(f"  [관심집단] {qcode}  {len(df):>6}행 → 동 집계", flush=True)
    return pd.DataFrame(rows)

# ------------------------------------------------------------------------ 실행
print("1) 상권분석 로드")
pop = load_sang("OA-22183_상주인구_행정동.csv",
                ["총_상주인구_수", "연령대_20_상주인구_수", "연령대_30_상주인구_수",
                 "총_가구_수", "아파트_가구_수"])
apt = load_sang("OA-22163_아파트_행정동.csv", ["아파트_평균_시가"]).drop(columns=["행정동_코드", "행정동_코드_명"])
cons = load_sang("OA-22166_소비_행정동.csv", ["지출_총금액"]).drop(columns=["행정동_코드", "행정동_코드_명"])
fclt = load_sang("OA-22169_집객시설_행정동.csv", ["집객시설_수", "은행_수"]).drop(columns=["행정동_코드", "행정동_코드_명"])
print(f"   상주인구 {len(pop)}행 / 아파트 {len(apt)} / 소비 {len(cons)} / 집객시설 {len(fclt)}")

print("2) SKT 통신정보 집계 (12분기)")
tel = agg_tel()
print("3) SKT 관심집단 집계 (12분기)")
itr = agg_interest()

print("4) 소득 (국민연금, 자치구×연)")
inc = pd.read_csv(RAW/"국민연금_시군구_평균소득월액_2020-2024.csv", encoding="utf-8-sig")
inc = inc[inc["시군구"].str.startswith("서울특별시")].copy()
inc["자치구"] = inc["시군구"].str.replace("서울특별시", "", regex=False)
inc["연도"] = inc["기준년월"].str[:4]
inc = inc[["연도", "자치구", "평균소득월액"]]

print("5) 병합")
p = (pop.merge(apt, on=["분기", "자치구", "동키"], how="left")
        .merge(cons, on=["분기", "자치구", "동키"], how="left")
        .merge(fclt, on=["분기", "자치구", "동키"], how="left")
        .merge(tel.drop(columns=["행정동명"]), on=["분기", "자치구", "동키"], how="left")
        .merge(itr, on=["분기", "자치구", "동키"], how="left"))
p["연도"] = p["분기"].str[:4]

p = p.merge(inc, on=["연도", "자치구"], how="left")
# 2025년 소득은 미공개 → 2024년 값으로 캐리포워드 (플래그 보존)
p["소득_추정연도"] = np.where(p["연도"] == "2025", "2024(캐리포워드)", p["연도"])
inc24 = inc[inc["연도"] == "2024"].set_index("자치구")["평균소득월액"]
p["평균소득월액"] = p["평균소득월액"].fillna(p["자치구"].map(inc24))

assert len(p) == len(pop), f"행수 불일치: 패널 {len(p)} vs 상주인구 {len(pop)} (조인 중복 발생)"
p.to_csv(OUT/"panel_행정동_분기_2023_2025.csv", index=False, encoding="utf-8-sig")
print(f"\n저장: {OUT/'panel_행정동_분기_2023_2025.csv'}  ({len(p)}행 × {p.shape[1]}컬럼)")
print("\n결측 현황")
print(p.isna().sum()[lambda s: s > 0].to_string() or "  없음")
