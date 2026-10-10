# 🏙️ 서울 행정동 상권 기회 대시보드

> **패스트캠퍼스 데이터 분석 프로젝트 2 (1조 KLPF)**  
> 서울 25개 자치구 · 425개 행정동의 **인구·인프라 기반 기대 소비 대비 실제 소비(배율)**, 소비 추세, 금융MBTI, 상권 키워드를 분석하고 **소비 잠재력 및 틈새 상권**을 발굴하는 대시보드 프로젝트입니다.

---

## 🌐 배포 대시보드 바로가기

**👉 [https://1joklpfclau-hecsqfwbfsrupvrs8tgdml.streamlit.app/revision](https://1joklpfclau-hecsqfwbfsrupvrs8tgdml.streamlit.app/revision)**

| 주요 메뉴 | URL 바로가기 | 설명 |
|:---|:---|:---|
| 🏠 **홈** | [/](https://1joklpfclau-hecsqfwbfsrupvrs8tgdml.streamlit.app/) | 핵심 지표, 프로젝트 배경 및 주요 발견 |
| 🗺️ **상권 지도** | [/map](https://1joklpfclau-hecsqfwbfsrupvrs8tgdml.streamlit.app/map) | 서울 25개 구 ↔ 425개 행정동 공간 지도 (Folium) |
| 🎯 **기회 탐색** | [/opportunity](https://1joklpfclau-hecsqfwbfsrupvrs8tgdml.streamlit.app/opportunity) | 선점형·유출보완형 Top 10 및 조건별 상권 필터 |
| 🟢 **네이버 트렌드** | [/naver_trend](https://1joklpfclau-hecsqfwbfsrupvrs8tgdml.streamlit.app/naver_trend) | 온·오프라인 검색 트렌드 결합 분석 |
| 🛠️ **수정사항(검증)** | [/revision](https://1joklpfclau-hecsqfwbfsrupvrs8tgdml.streamlit.app/revision) | 모델 타깃 진단, 결론 재검증 및 데이터 정합성 검토 |

> *참고: 일정 시간 동안 접속이 없으면 앱이 절전 모드로 전환됩니다. "Yes, get this app back up!" 버튼을 누르면 1분 내로 다시 실행됩니다.*

---

## 💻 로컬 PC에서 실행하기

```bash
# 1. 저장소 클론
git clone https://github.com/ST88Ant/1joKLPF_gem.git
cd 1joKLPF_gem

# 2. 필수 라이브러리 설치
pip install -r requirements.txt

# 3. Streamlit 대시보드 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 자동 연결되며, 전처리 데이터(`data/processed/`)가 저장소에 모두 포함되어 있어 클론 후 즉시 실행됩니다.

---

## 📂 저장소 디렉터리 구조

```
1joKLPF_gem/
├─ app.py                  # 🚀 Streamlit 대시보드 메인 진입점 (10개 페이지 구성)
├─ pages/                  # 📊 대시보드 세부 페이지
│  ├─ home.py              #    - 🏠 홈
│  ├─ eda_overview.py      #    - 📋 데이터 개요
│  ├─ eda_distribution.py  #    - 📊 분포 분석
│  ├─ eda_relationship.py  #    - 🔗 관계 분석
│  ├─ eda_district.py      #    - 🏙️ 자치구 비교
│  ├─ naver_trend.py       #    - 🟢 네이버 검색 트렌드 (온·오프라인)
│  ├─ map.py               #    - 🗺️ 상권 지도 (Folium 인터랙티브)
│  ├─ opportunity.py       #    - 🎯 기회 탐색 (Top 10 필터링)
│  ├─ dong_detail.py       #    - 🔍 행정동 상세 프로필
│  └─ revision.py          #    - 🛠️ 수정사항 (타깃 진단 및 모델 재검증)
├─ src/                    # 🧩 대시보드 백엔드 & 시각화 모듈
│  ├─ config.py            #    - 경로, 컬러 팔레트, 범주 정의
│  ├─ data.py              #    - DuckDB / Polars 고속 데이터 쿼리
│  ├─ charts.py            #    - Plotly 시각화 빌더
│  ├─ tables.py            #    - EDA 테이블 빌더
│  ├─ maps.py              #    - Folium 지도 빌더
│  ├─ naver_data.py        #    - 네이버 트렌드 데이터 처리
│  ├─ revision_view.py     #    - 재검증 지표 뷰 모듈
│  └─ ui.py                #    - UI 공통 컴포넌트
├─ data/                   # 💾 데이터 저장소
│  ├─ processed/           #    - 대시보드 구동용 Parquet / JSON 전처리 데이터
│  ├─ raw/                 #    - 프로젝트 전체 원천 데이터 (서울시 상권, SKT, 가계금융 등)
│  └─ cache/               #    - 행정동 공간 경계 GeoJSON 캐시
├─ docs/                   # 📚 분석 보고서, 기획서, 데이터 명세서 통합 저장소
│  ├─ reports/             #    - 상권기회 인사이트, 분석결과, 소비갭 등 5종 보고서
│  ├─ proposals/           #    - 틈새상권 솔루션, 핀테크/대출 AI 기획서
│  ├─ guides/              #    - 데이터 사전, EDA 가이드, 키워드 매핑 테이블
│  ├─ images/              #    - 분석 차트 시각화 원본 이미지 (20여 종)
│  └─ README.md            #    - 📑 전체 문서 목차 인덱스
├─ scripts/                # ⚙️ 데이터 파이프라인 및 빌드 스크립트
│  ├─ build_data.py        #    - 대시보드 Parquet 데이터 빌드
│  ├─ build_revision.py    #    - 재검증 Parquet 데이터 빌드
│  ├─ download_sbiz_data.py#    - 소상공인 상가정보 자동 다운로드
│  ├─ fetch_*.sh           #    - 공공데이터/생활데이터 자동 수집 스크립트
│  ├─ analysis/            #    - EDA 및 인사이트 도출 분석 스크립트
│  └─ ml_model/            #    - 머신러닝 모델 학습 및 잔차 분석 스크립트
├─ requirements.txt        # 📦 대시보드 실행 패키지 목록
├─ RAW_DATA_SOURCES.md     # 📑 전체 원천 데이터 공식 출처 명세서
└─ .gitignore              # 🛡️ 대용량 파일(100MB+) 및 캐시 제외 설정
```

---

## 📚 문서 및 데이터 안내

- **전체 기획서 및 분석 보고서**: [docs/README.md](docs/README.md)에서 모든 보고서와 가이드 문서를 바로 열람할 수 있습니다.
- **원천 데이터 공식 출처 및 다운로드**: [RAW_DATA_SOURCES.md](RAW_DATA_SOURCES.md)에서 서울시 및 공공데이터포털 공식 URL과 자동 수집 스크립트 명령어를 확인할 수 있습니다.
- **용량 정책**: GitHub 단일 파일 100MB 제한 정책에 따라 100MB를 초과하는 대용량 원본 파일(`소상공인_상가정보_서울.csv`, `통신정보_2023_전체.zip` 등)은 `.gitignore` 처리되어 있으며, 필요 시 `scripts/`의 명령어로 다시 다운로드할 수 있습니다.
