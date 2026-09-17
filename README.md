# ⚡ [Gemi_pjt] 인구·인프라 기반 소비 예측 모델 및 ‘소비 잠재력’ 상권 발굴

> **"인구와 인프라 대비 실제 소비가 초과 달성되거나, 반대로 저평가된 동네는 어디인가?"**  
> 서울시 425개 행정동의 상주·직장·유동인구와 집객시설, 교통, 주거자산 데이터를 머신러닝 공식형 모델(Log-Log Ridge)로 학습하여 **동네별 기대 소비액**을 산출하고, 실제 카드 소비액과의 **격차(Residual, 잔차)**를 분석하여 **초과 달성 핫스팟 상권**과 **숨은 소비 잠재력 상권**을 발굴하는 프로젝트입니다.

---

## 📁 프로젝트 폴더 구조

원본 데이터(`data/raw`, `수집데이터`)는 일체 수정 없이 그대로 보존되었으며, 모든 산출물과 가공 데이터는 본 `Gemi_pjt` 폴더 안에 체계적으로 분류되어 있습니다:

```text
Gemi_pjt/
├── index.html                  # 🌟 반응형 인터랙티브 웹 대시보드 (더블클릭으로 즉시 실행)
├── README.md                   # 프로젝트 전체 안내 및 가이드
├── src/                        # 분석 및 구동 파이썬 소스코드
│   ├── data_prep.py            # Step 1: 7대 공공데이터 정제 및 2025 분기평균 병합
│   ├── train_and_gap_analysis.py # Step 2: 공식형 회귀 학습, 잔차 계산, 5대 업종 갭 분석
│   ├── generate_visuals.py     # Step 3: 10종 고해상도 시각화 차트 생성 (Malgun Gothic)
│   ├── build_dashboard_data.py # Step 4: 대시보드용 경량 패키지 데이터셋(JSON) 생성
│   ├── build_dashboard_html.py # Step 5: 웹 대시보드(index.html) 빌드 스크립트
│   └── run_dashboard.py        # 대시보드 로컬 웹서버 실행기 (브라우저 자동 실행)
├── data/                       # 가공 완료된 데이터셋 (결측치 제로)
│   ├── dong_features_processed.csv    # 425개 동 인구·인프라 통합 특성 데이터 (70컬럼)
│   ├── dong_consumption_residuals.csv # 기대소비, 실제소비, 잔차, 상권유형 매핑 데이터
│   ├── category_gap_analysis.csv      # 5대 세부 업종별 갭 분석 데이터 (2,550행)
│   ├── dashboard_data.json            # 웹 대시보드 임베드용 JSON 패키지 (270 KB)
│   └── model_summary.json             # 회귀 공식, 탄력성 계수 및 메타데이터
├── image/                      # 고해상도 분석 시각화 차트 10종 (PNG)
│   ├── 01_feature_correlation_heatmap.png # 인구·인프라와 소비액 상관계수 히트맵
│   ├── 02_actual_vs_expected_scatter.png  # 기대 소비액 vs 실제 소비액 산점도 (기준선)
│   ├── 03_residual_distribution.png       # 소비 잔차(소비 갭) 정규분포 적합 곡선
│   ├── 04_top15_overachiever_dongs.png    # 서울시 초과 달성 상권 Top 15 바 차트
│   ├── 05_top15_potential_growth_dongs.png# 서울시 저평가 소비 잠재력 상권 Top 15 바 차트
│   ├── 06_consumption_gap_quadrant.png    # 4분면 상권 기회 진단 매트릭스
│   ├── 07_formula_elasticity_weights.png  # 공식형 모델 핵심 탄력성 가중치 랭킹
│   ├── 08_gu_residual_summary.png         # 서울시 25개 구별 평균 소비 갭 비교
│   ├── 09_category_gap_comparison.png     # 5대 세부 업종별 소비 갭 분포 박스플롯
│   └── 10_potential_dongs_deepdive.png    # 소비 잠재력 5개 동 업종별 결핍 히트맵
├── docs/                       # 문서 및 기술 가이드
│   ├── data_dictionary.md      # 데이터 변수 및 파생지표 상세 정의서
│   └── methodology_guide.md    # 공식형 모델 선정 이유 및 누구나 쉬운 결과 해석 가이드
└── report/                     # 종합 분석 최종 보고서
    └── consumption_gap_analysis_report.md # 비즈니스/정책 제언 포함 심층 분석 리포트
```

---

## 🚀 빠른 실행 가이드

### 1. 인터랙티브 웹 대시보드 바로 열기
* `Gemi_pjt/index.html` 파일을 더블클릭하여 크롬(Chrome)이나 엣지(Edge) 브라우저에서 바로 열 수 있습니다.
* 또는 터미널에서 다음 명령어를 실행하면 로컬 웹서버가 구동되며 자동으로 브라우저가 열립니다:
  ```bash
  python Gemi_pjt/src/run_dashboard.py
  ```

### 2. 전체 데이터 및 모델링 파이프라인 재실행 (One-Click)
```bash
python Gemi_pjt/src/data_prep.py
python Gemi_pjt/src/train_and_gap_analysis.py
python Gemi_pjt/src/generate_visuals.py
python Gemi_pjt/src/build_dashboard_data.py
python Gemi_pjt/src/build_dashboard_html.py
```

---

## 💡 주요 분석 결과 요약

### 1. 공식형 머신러닝 예측 공식 (Log-Log Model, $R^2 = 60.5\%$)
$$\log(\text{기대 소비액}) = 12.1371 + 0.710 \log(\text{집객}) + 0.432 \log(\text{은행}) + 0.318 \log(\text{유동}) - 0.192 \log(\text{상주}) + \dots$$
* **집객시설(+0.71)과 은행(+0.43)**이 서울시 소비를 견인하는 가장 강력한 1, 2순위 요인입니다.
* **상주인구(-0.19)**의 음수 부호는 아파트/주택만 밀집한 베드타운 주민들의 **소비 역외 유출**을 실증합니다.

### 2. 상권 발굴 결과
* **🏆 초과 달성 핫스팟 상권**: `소공동`(+4,836%), `용산2가동`(+8,376%), `구로3동`(+7,010%), `문래동`(+6,335%), `역삼2동`(+1,950%)
* **🌟 저평가 소비 잠재력 상권**: `반포본동`(-89.6%), `개포1동`(-77.7%), `충현동`(-76.2%), `이촌1동`(-73.7%), `공덕동`(-69.4%)
  * 이 지역들은 높은 인구와 소득 수준 대비 상권 인프라가 부족하여 소비가 외부로 새고 있는 **신규 출점 및 상권 기획의 1순위 타깃**입니다.
