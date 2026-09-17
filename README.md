# [머신러닝 예측 & 갭 분석] 인구·인프라 기반 소비 예측 모델 및 '소비 잠재력' 상권 발굴 계획서

인구(상주·직장·유동)와 인프라(집객시설, 아파트 시가/세대수, 지하철역, 병원 등) 데이터를 머신러닝 회귀 모델로 학습하여 동네별 **"기대 소비액(Expected Consumption)"**을 산출하고, 실제 상권 소비액과의 **격차(잔차, Residual)**를 분석하여 **초과 달성 상권(Hotspot)** 및 **저평가된 소비 잠재력 상권(Hidden Potential)**을 발굴합니다.

---

## 사용자 피드백 반영 내용

1. **모델 평가 방식 (추천안 채택)**:
   - **쉬운 설명**: "직장인 1만 명이 늘면 소비가 몇 % 증가하는가?"처럼 **원인과 결과를 한눈에 쉽게 설명할 수 있는 '투명한 공식형 모델(다중 선형회귀/Ridge)'을 메인 모델**로 사용합니다.
   - 동시에 **'인공지능 트리 모델(Random Forest)'**을 보조로 함께 돌려 예측력을 비교함으로써, "우리의 공식이 얼마나 정확하고 신뢰성 있는지"를 과학적으로 입증합니다.
2. **세부 소비 카테고리(업종별) 확장 분석 추가**:
   - 총 소비액뿐만 아니라 **'음식/외식', '식료품/생활', '여가/문화', '의료비'** 등 주요 세부 업종별 기대 소비액 및 갭 분석을 파이프라인과 대시보드 전용 탭에 추가 구축합니다.

---

## 프로젝트 폴더 구조 (`Gemi_pjt`)

원본 데이터(`data/raw`, `수집데이터`)는 일체 수정하지 않고 원본 그대로 유지하며, `Gemi_pjt` 폴더 안에 완결형 프로젝트로 구축합니다.

```
T_PJT2/
└── Gemi_pjt/
    ├── src/             # 데이터 전처리, ML 모델 학습/평가, 시각화 생성, 대시보드 스크립트
    │   ├── data_prep.py              # 원본 7대 데이터 병합 및 정제
    │   ├── train_and_gap_analysis.py # 총소비 및 업종별 ML 모델 학습 & 잔차/갭 계산
    │   └── generate_visuals.py       # 고해상도 시각화 차트 10종 생성
    ├── data/            # 전처리 완료된 학습 데이터셋 및 예측/잔차 결과 CSV
    │   ├── dong_features_processed.csv      # 425개 행정동 특성 데이터셋
    │   ├── dong_consumption_residuals.csv   # 총소비 기대치, 실제치, 잔차, 상권유형
    │   └── category_gap_analysis.csv        # 업종별(음식, 여가, 마트 등) 갭 분석 데이터
    ├── image/           # 고화질 분석 시각화 차트 (PNG) 10종
    ├── docs/            # 데이터 정의서 및 쉬운 방법론 해설 문서
    │   ├── data_dictionary.md        # 데이터 변수 사전
    │   └── methodology_guide.md      # 누구나 이해하기 쉬운 분석 방법론 가이드
    ├── report/          # 비즈니스 인사이트 및 상권 분석 종합 보고서
    │   └── consumption_gap_analysis_report.md
    └── index.html       # 프리미엄 반응형 인터랙티브 웹 대시보드 (업종별 확장 탭 포함)
```

---

## 세부 구현 계획

### 1. Data Pipeline (`Gemi_pjt/src/data_prep.py`)
- `data/raw/` 내 7개 핵심 데이터 결합:
  - 상권 소비액: `OA-22166_소비_행정동.csv` (총금액 및 10대 세부 업종 금액)
  - 상주인구/가구: `OA-22183_상주인구_행정동.csv`
  - 직장인구: `OA-22184_직장인구_행정동.csv`
  - 유동인구: `OA-22178_길단위인구_행정동.csv`
  - 집객시설: `OA-22169_집객시설_행정동.csv` (지하철역, 버스정류장, 은행, 병원 등)
  - 주거자산: `OA-22163_아파트_행정동.csv` (아파트 단지수, 평균 시가)
  - 공간정보: `OA-22160_영역_행정동.csv` (면적 및 좌표)
- 분기 평균 산출(계절성 노이즈 보정) 및 결측치 보정 완료 후 `Gemi_pjt/data/dong_features_processed.csv` 저장.

### 2. Modeling & Residual Analysis (`Gemi_pjt/src/train_and_gap_analysis.py`)
- **총 소비액 기대 모델**:
  - 다중 회귀(Ridge) 및 Random Forest로 기대 소비액 산출 ($R^2 \approx 0.62$).
  - 실제 소비액 - 기대 소비액 = 잔차(Residual).
  - 4개 상권 그룹 분류:
    1. **초과 달성 상권 (Super-Hub)**: 인구·인프라 대비 외부 소비 유입이 폭발적인 동네
    2. **소비 잠재력 상권 (Growth Potential)**: 인구·인프라가 탄탄한데 소비가 덜 일어나 개발 기회가 큰 동네
    3. **균형 상권 (Balanced)**: 기대치에 맞게 소비가 안정적인 동네
    4. **소비 위축 상권 (Low Activity)**: 인구/인프라/소비 모두 활력이 낮은 동네
- **업종별(카테고리별) 갭 모델**:
  - `음식/외식`, `식료품/생활`, `여가/문화`, `의료비` 등 항목별 기대 소비액 및 갭 산출.
  - "이 동네는 음식점 소비는 넘치는데, 여가/문화 시설 소비는 턱없이 부족하다"와 같은 세부 입체 분석 제공.

### 3. Visualizations (`Gemi_pjt/src/generate_visuals.py` -> `Gemi_pjt/image/`)
한글 폰트(`Malgun Gothic`) 적용, 깔끔하고 직관적인 10대 차트 생성:
1. `01_feature_correlation_heatmap.png`: 어떤 인구/인프라가 소비와 가장 친한가?
2. `02_actual_vs_expected_scatter.png`: 기대치선과 동네들의 위치 (초과 vs 저평가 한눈에 보기)
3. `03_residual_distribution.png`: 소비 격차의 정규분포 적합도
4. `04_top15_overachiever_dongs.png`: 서울에서 가장 소비가 핫한 초과달성 동네 Top 15
5. `05_top15_potential_growth_dongs.png`: 인구는 많은데 소비가 저평가된 잠재력 동네 Top 15
6. `06_consumption_gap_quadrant.png`: 4분면 상권 진단 매트릭스
7. `07_feature_importance.png`: 인프라와 인구의 소비 영향력 랭킹
8. `08_gu_residual_summary.png`: 25개 구별 평균 소비 갭 비교
9. `09_category_gap_comparison.png`: 주요 업종별(음식 vs 여가 vs 쇼핑) 갭 분포 비교
10. `10_potential_dongs_category_breakdown.png`: 잠재력 동네들의 업종별 결핍 현황

### 4. Interactive Web Dashboard (`Gemi_pjt/index.html`)
- 최신 인터페이스 디자인, 반응형 글래스모피즘 UI
- 구성 탭:
  - **탭 1: 종합 갭 분석 (Overview)**: 425개 동네 현황 KPI 카드, 4분면 인터랙티브 산점도, Top 초과달성/잠재력 상권 테이블
  - **탭 2: 업종별 확장 분석 (Category Deep-Dive)**: 음식, 여가문화, 식료품 등 업종별 갭 선택 조회 및 동네별 결핍 업종 비교
  - **탭 3: 동네 1:1 정밀 진단실 (Dong Diagnostics)**: 특정 동네를 선택하면 인구·인프라 레이더 차트, 기대 소비 vs 실제 소비 비교, 추천 입점 업종 자동 진단
  - **탭 4: 시각화 차트 갤러리**: 10종의 고화질 이미지 모아보기 및 모달 확대 뷰
- 별도 설치 없이 브라우저로 더블클릭하면 즉시 실행.

### 5. Documentation & Reports (`Gemi_pjt/docs`, `Gemi_pjt/report`)
- `docs/data_dictionary.md`: 누구나 알기 쉬운 변수 설명서
- `docs/methodology_guide.md`: 수식 대신 일상적인 비유와 예시로 풀어쓴 방법론 설명
- `report/consumption_gap_analysis_report.md`: 발표 및 보고서 제출에 바로 쓸 수 있는 종합 결과 해석 리포트

---

## 검증 계획

1. **데이터 전처리 검증**: 결측치 없이 425개 행정동 정제 및 `Gemi_pjt/data/` 저장 확인
2. **모델링 및 갭 산출 검증**: 회귀 계수 유의성, $R^2$ 점수 확인 및 4개 상권 그룹 분류 정상 매핑 확인
3. **시각화 10종 생성 검증**: `Gemi_pjt/image/` 내 모든 이미지 한글 깨짐 없이 정상 렌더링 확인
4. **대시보드 기능 검증**: 브라우저 서브에이전트를 통해 `Gemi_pjt/index.html` 접속, 탭 전환, 동네 검색, 업종별 인터랙션 완벽 작동 확인
