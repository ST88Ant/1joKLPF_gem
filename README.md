# 🏙️ 서울시 상권 소비 예측 및 소비 잠재력 상권 분석 프로젝트

> **패스트캠퍼스 데이터 분석 프로젝트 2 (1조 KLPF)**  
> 서울 25개 자치구 · 425개 행정동의 인구·인프라·금융 데이터를 결합하여 **기대 소비 대비 실제 소비(소비 갭)를 분석**하고, **신규 창업 및 틈새 상권 발굴 인사이트**를 제공하는 통합 프로젝트 저장소입니다.

---

## 📂 저장소 디렉터리 구조

```
T_PJT2/
├─ dashboard/            # 📊 서울 행정동 상권 기회 Streamlit 대시보드 (통합 버전)
├─ Clau_pjt/             # 🧠 상권 기회 분석, EDA 리포트 및 Streamlit 대시보드 프로젝트
├─ Gemi_pjt/             # 📈 소비 예측 머신러닝 모델 & 웹 대시보드 (HTML/JS/CSS)
├─ data/                 # 💾 데이터 저장소
│  ├─ processed/         #    - 전처리 완료 데이터 (특성 테이블, MBTI 군집, 상권 키워드 등)
│  ├─ raw/               #    - 원천 데이터 (공공데이터 및 서울시 열린데이터)
│  └─ 데이터_출처.md     #    - 원천 데이터 상세 출처 및 다운로드 스크립트 가이드
├─ docs/                 # 📑 행정동별 상권분석 키워드 가이드 & EDA 보고서 (MD / PDF)
├─ scripts/              # ⚙️ 데이터 수집, 패널 구축, MBTI 군집화 등 파이프라인 스크립트
├─ 수집데이터/           # 📋 가계금융복지조사(가구/가구원) 및 서울시민 생활금융 통계
├─ fintech_ai_project_proposals.md          # 핀테크 AI 프로젝트 제안서
├─ loan_ai_project_proposals.md             # 대출 AI 프로젝트 제안서
├─ loan_consumption_pattern_analysis.md     # 대출 및 소비 패턴 분석
├─ 네이버_검색트렌드_온오프라인_소비결합_분석보고서.md # 네이버 검색 트렌드 결합 보고서
├─ 서울_상권분석_대시보드.xlsx               # 상권 분석 집계 엑셀
└─ 틈새상권_발굴_솔루션_기획서.md            # 틈새상권 솔루션 기획서
```

---

## 🚀 빠른 시작 (대시보드 실행)

### 1. Streamlit 상권 기회 대시보드 (`dashboard/`)

서울 25개 자치구 및 행정동 지도, 기회 탐색, 분포/관계 분석을 인터랙티브하게 확인할 수 있습니다.

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```
> 브라우저에서 `http://localhost:8501` 접속

### 2. 머신러닝 소비 갭 웹 대시보드 (`Gemi_pjt/`)

인구 및 인프라 기반 다중회귀/Ridge 모델로 산출된 기대 소비 대비 실제 소비의 갭(Residual)을 시각화한 경량 웹 대시보드입니다.

- `Gemi_pjt/index.html` 파일을 브라우저로 직접 더블클릭하여 열거나, 로컬 웹 서버(Live Server 등)로 실행할 수 있습니다.

---

## 📊 데이터 안내

- **전처리 데이터(`data/processed/`)**: 모델 학습 및 대시보드 구동에 필요한 전처리 결과 파일들이 포함되어 있어 클론 후 바로 실행 가능합니다.
- **대용량 원본 데이터(`data/raw/`)**: GitHub의 100MB 단일 파일 제한 정책에 따라 100MB 이상의 대용량 원본 파일(`소상공인_상가정보_서울.csv`, `통신정보_2023_전체.zip` 등)은 제외되어 있습니다.
- 원본 데이터 공식 출처와 다운로드 방법은 **[RAW_DATA_SOURCES.md](RAW_DATA_SOURCES.md)** 및 [data/데이터_출처.md](data/데이터_출처.md)와 `scripts/` 내의 자동 수집 스크립트(`fetch_seoul_open_data.sh`, `download_sbiz_data.py` 등)를 참고해주세요.

---

## 👥 팀 프로젝트 협업 가이드

1. **저장소 복제(Clone)**:
   ```bash
   git clone https://github.com/ST88Ant/1joKLPF_gem.git
   cd 1joKLPF_gem
   ```
2. **의존성 설치**:
   ```bash
   pip install -r dashboard/requirements.txt
   ```
3. 작업 시 대용량 파일(100MB 이상)은 `.gitignore`에 유지되도록 주의해주세요.
