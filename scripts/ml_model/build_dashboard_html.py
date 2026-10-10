# -*- coding: utf-8 -*-
"""
Gemi_pjt - Step 5: Web Dashboard Builder
HTML/CSS/JS 단일 파일 대시보드(Gemi_pjt/index.html) 생성기
- 반응형 프리미엄 글래스모피즘 다크 UI
- 5대 탭: 종합 갭 분석, 업종별 확장 분석, 동네 1:1 진단실, 시각화 갤러리, 공식 및 방법론 가이드
- 데이터가 JSON으로 직접 임베드되어 서버 없이 더블클릭(file:///)으로도 즉시 실행 가능
"""

import sys
import json
from pathlib import Path

# 콘솔 UTF-8 출력 보장
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
JSON_PATH = WORKSPACE_ROOT / "Gemi_pjt" / "data" / "dashboard_data.json"
OUT_HTML = WORKSPACE_ROOT / "Gemi_pjt" / "index.html"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>서울시 소비 예측 & 갭 분석 대시보드 | Gemi_pjt</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-base: #0b0f19;
      --bg-surface: #111827;
      --bg-card: rgba(30, 41, 59, 0.7);
      --bg-card-hover: rgba(51, 65, 85, 0.8);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(56, 189, 248, 0.3);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-sub: #64748b;
      --accent-blue: #38bdf8;
      --accent-emerald: #10b981;
      --accent-rose: #f43f5e;
      --accent-purple: #a855f7;
      --accent-amber: #f59e0b;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-base);
      color: var(--text-main);
      line-height: 1.6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* 헤더 */
    header {
      background: linear-gradient(180deg, rgba(17, 24, 39, 0.95) 0%, rgba(11, 15, 25, 0.8) 100%);
      border-bottom: 1px solid var(--border-color);
      padding: 24px 32px;
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header-container {
      max-width: 1440px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }

    .logo-area h1 {
      font-size: 22px;
      font-weight: 800;
      background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .logo-area p {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    /* 탭 내비게이션 */
    .nav-tabs {
      display: flex;
      gap: 8px;
      background: rgba(15, 23, 42, 0.6);
      padding: 6px;
      border-radius: 12px;
      border: 1px solid var(--border-color);
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 8px 18px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.05);
    }

    .tab-btn.active {
      color: #0b0f19;
      background: var(--accent-blue);
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.4);
    }

    /* 컨테이너 */
    main {
      max-width: 1440px;
      margin: 0 auto;
      padding: 32px 24px 64px 24px;
      width: 100%;
      flex: 1;
    }

    .tab-content {
      display: none;
      animation: fadeIn 0.3s ease;
    }

    .tab-content.active {
      display: block;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* KPI 요약 카드 그리드 */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 20px;
      margin-bottom: 28px;
    }

    .kpi-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 22px;
      backdrop-filter: blur(10px);
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card:hover {
      transform: translateY(-3px);
      border-color: var(--border-accent);
    }

    .kpi-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .kpi-value {
      font-size: 28px;
      font-weight: 800;
      margin: 10px 0 6px 0;
      font-family: 'Outfit', sans-serif;
    }

    .kpi-desc {
      font-size: 12px;
      color: var(--text-sub);
    }

    /* 그리드 레이아웃 */
    .grid-2 {
      display: grid;
      grid-template-columns: 1.3fr 1fr;
      gap: 24px;
      margin-bottom: 28px;
    }

    @media (max-width: 1024px) {
      .grid-2 { grid-template-columns: 1fr; }
    }

    .card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 24px;
      backdrop-filter: blur(10px);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 12px;
    }

    .card-title {
      font-size: 17px;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* 컨트롤 (검색, 필터) */
    .controls-row {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 18px;
    }

    input[type="text"], select {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 10px 14px;
      border-radius: 10px;
      font-size: 14px;
      font-family: inherit;
      outline: none;
      transition: border-color 0.2s ease;
    }

    input[type="text"]:focus, select:focus {
      border-color: var(--accent-blue);
    }

    .pill-btn {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      padding: 7px 14px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .pill-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-main);
    }

    .pill-btn.active {
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent-blue);
      color: var(--accent-blue);
    }

    /* 테이블 */
    .table-container {
      overflow-x: auto;
      max-height: 520px;
      border-radius: 10px;
      border: 1px solid var(--border-color);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }

    th {
      background: rgba(15, 23, 42, 0.95);
      color: var(--text-muted);
      font-weight: 600;
      padding: 12px 16px;
      position: sticky;
      top: 0;
      z-index: 10;
      border-bottom: 1px solid var(--border-color);
    }

    td {
      padding: 12px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-main);
    }

    tr:hover td {
      background: rgba(255, 255, 255, 0.03);
    }

    /* 배지 */
    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.3px;
    }

    .badge-superhub {
      background: rgba(244, 63, 94, 0.15);
      color: #fda4af;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }

    .badge-potential {
      background: rgba(16, 185, 129, 0.15);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-niche {
      background: rgba(168, 85, 247, 0.15);
      color: #d8b4fe;
      border: 1px solid rgba(168, 85, 247, 0.3);
    }

    .badge-balanced {
      background: rgba(148, 163, 184, 0.15);
      color: #cbd5e1;
      border: 1px solid rgba(148, 163, 184, 0.3);
    }

    .badge-low {
      background: rgba(71, 85, 105, 0.2);
      color: #94a3b8;
      border: 1px solid rgba(71, 85, 105, 0.3);
    }

    /* 진단실 상세 카드 */
    .diag-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    @media (max-width: 900px) {
      .diag-container { grid-template-columns: 1fr; }
    }

    .gauge-container {
      margin: 20px 0;
    }

    .gauge-bar {
      height: 12px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      overflow: hidden;
      position: relative;
    }

    .gauge-fill {
      height: 100%;
      border-radius: 6px;
      transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stat-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 14px;
    }

    .stat-row span:first-child { color: var(--text-muted); }
    .stat-row span:last-child { font-weight: 600; }

    /* 갤러리 */
    .gallery-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 24px;
    }

    .gallery-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.2s, border-color 0.2s;
    }

    .gallery-card:hover {
      transform: translateY(-4px);
      border-color: var(--accent-blue);
    }

    .gallery-img {
      width: 100%;
      height: 220px;
      object-fit: cover;
      background: #1e293b;
      border-bottom: 1px solid var(--border-color);
    }

    .gallery-info {
      padding: 16px;
    }

    .gallery-title {
      font-size: 15px;
      font-weight: 700;
      margin-bottom: 6px;
    }

    .gallery-desc {
      font-size: 12px;
      color: var(--text-muted);
    }

    /* 모달 */
    .modal {
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(8px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal.active { display: flex; }

    .modal-content {
      max-width: 90%;
      max-height: 90%;
      position: relative;
    }

    .modal-content img {
      max-width: 100%;
      max-height: 85vh;
      border-radius: 12px;
      border: 1px solid var(--border-color);
      box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }

    .modal-close {
      position: absolute;
      top: -40px;
      right: 0;
      color: white;
      font-size: 30px;
      cursor: pointer;
    }

    /* 공식 가이드 박스 */
    .formula-box {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-accent);
      border-radius: 14px;
      padding: 24px;
      margin: 20px 0;
      font-family: 'Outfit', monospace;
      font-size: 16px;
      color: #38bdf8;
      overflow-x: auto;
      line-height: 1.8;
    }

    .action-btn {
      background: var(--accent-blue);
      color: #0b0f19;
      border: none;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: opacity 0.2s;
    }

    .action-btn:hover { opacity: 0.9; }

    footer {
      border-top: 1px solid var(--border-color);
      padding: 24px;
      text-align: center;
      font-size: 12px;
      color: var(--text-sub);
      background: var(--bg-surface);
    }
  </style>
</head>
<body>

  <!-- 헤더 -->
  <header>
    <div class="header-container">
      <div class="logo-area">
        <h1><span>⚡</span> 서울시 상권 소비 예측 & 소비 잠재력 갭 분석</h1>
        <p>인구·인프라 기반 기대 소비액 머신러닝 회귀 모델 &amp; 잔차(Residual) 분석 대시보드</p>
      </div>
      <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('overview')">📊 종합 갭 분석</button>
        <button class="tab-btn" onclick="switchTab('category')">🛍️ 업종별 확장 분석</button>
        <button class="tab-btn" onclick="switchTab('diagnostics')">🔍 동네 1:1 진단실</button>
        <button class="tab-btn" onclick="switchTab('gallery')">🖼️ 시각화 갤러리</button>
        <button class="tab-btn" onclick="switchTab('methodology')">📐 공식 &amp; 해석 가이드</button>
      </div>
    </div>
  </header>

  <!-- 메인 컨텐츠 -->
  <main>

    <!-- TAB 1: 종합 갭 분석 -->
    <div id="tab-overview" class="tab-content active">
      <!-- 핵심 KPI 요약 카드 -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title">분석 대상 행정동</div>
          <div class="kpi-value" style="color: var(--accent-blue);" id="kpi-total-dongs">425개</div>
          <div class="kpi-desc">서울시 25개 자치구 전역 (2025년 기준)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">공식형 모델 설명력 (R²)</div>
          <div class="kpi-value" style="color: var(--accent-emerald);" id="kpi-r2">60.5%</div>
          <div class="kpi-desc">인구·인프라로 설명되는 소비 기준선</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">최대 초과 달성 상권</div>
          <div class="kpi-value" style="color: var(--accent-rose);" id="kpi-top-over">용산2가동</div>
          <div class="kpi-desc">기대치 대비 +8,376% (해방촌·경리단 핫플)</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">최대 소비 잠재력 상권</div>
          <div class="kpi-value" style="color: var(--accent-purple);" id="kpi-top-potential">반포본동</div>
          <div class="kpi-desc">기대치 대비 -89.6% (풍부한 배후수요 대비 상권결핍)</div>
        </div>
      </div>

      <!-- 산점도 & 랭킹 그리드 -->
      <div class="grid-2">
        <!-- 4분면 인터랙티브 산점도 차트 -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">🎯 4분면 상권 기회 진단 매트릭스</div>
            <span style="font-size: 12px; color: var(--text-muted);">점 위에 마우스를 올리면 상세 정보를 확인합니다.</span>
          </div>
          <div style="position: relative; height: 420px;">
            <canvas id="quadrantChart"></canvas>
          </div>
        </div>

        <!-- 4분면 요약 정보 -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">💡 4대 상권 유형 진단 가이드</div>
          </div>
          <div style="display: flex; flex-direction: column; gap: 14px;">
            <div style="padding: 12px; background: rgba(244,63,94,0.08); border-left: 4px solid var(--accent-rose); border-radius: 8px;">
              <strong style="color: #fda4af;">① 초과 달성 핫스팟 (37개 동)</strong>
              <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">대형 집객시설과 풍부한 유동인구로 외부 소비를 대규모로 흡수하는 핵심 상권 (예: 소공동, 문래동, 구로3동, 역삼2동)</p>
            </div>
            <div style="padding: 12px; background: rgba(16,185,129,0.08); border-left: 4px solid var(--accent-emerald); border-radius: 8px;">
              <strong style="color: #6ee7b7;">② 숨은 소비 잠재력 상권 🌟 (85개 동)</strong>
              <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">상주·직장 인구와 인프라는 탄탄하나, 자체 상업시설 부족으로 소비가 외부로 유출되는 <strong>신규 출점 및 상권 개발 기회 1순위 지역</strong> (예: 반포본동, 개포1동, 공덕동, 충현동)</p>
            </div>
            <div style="padding: 12px; background: rgba(168,85,247,0.08); border-left: 4px solid var(--accent-purple); border-radius: 8px;">
              <strong style="color: #d8b4fe;">③ 골목 로컬 핫플레이스 (41개 동)</strong>
              <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">인프라 규모는 작지만 개성 있는 F&amp;B와 문화 콘텐츠로 인구 대비 높은 소비 효율을 내는 특색 상권 (예: 용산2가동)</p>
            </div>
            <div style="padding: 12px; background: rgba(148,163,184,0.08); border-left: 4px solid var(--text-muted); border-radius: 8px;">
              <strong style="color: #cbd5e1;">④ 균형 상권 (203개 동) &amp; 소비 위축지 (59개 동)</strong>
              <p style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">인구와 인프라 규모에 비례하여 안정적으로 소비가 발생하는 일반 주거 및 근린 상권</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 행정동 목록 테이블 및 필터링 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">📋 서울시 425개 행정동 소비 갭 랭킹 테이블</div>
          <div class="controls-row">
            <button class="pill-btn active" onclick="filterRankings('all')">전체 동 (425)</button>
            <button class="pill-btn" onclick="filterRankings('overachieve')">🏆 초과 달성 Top 20</button>
            <button class="pill-btn" onclick="filterRankings('potential')">💡 소비 잠재력 Top 20</button>
            <select id="guFilter" onchange="applyFilters()">
              <option value="">전체 자치구 (25개 구)</option>
            </select>
            <input type="text" id="dongSearch" placeholder="동네 이름 검색 (예: 역삼, 공덕)..." oninput="applyFilters()">
          </div>
        </div>

        <div class="table-container">
          <table id="dongTable">
            <thead>
              <tr>
                <th>순위</th>
                <th>행정동명</th>
                <th>자치구</th>
                <th>실제 소비액 (분기)</th>
                <th>기대 소비액 (공식)</th>
                <th>소비 격차 (Gap %)</th>
                <th>상권 유형</th>
                <th>상세 진단</th>
              </tr>
            </thead>
            <tbody id="dongTableBody">
              <!-- 동적으로 생성 -->
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 2: 업종별 확장 분석 -->
    <div id="tab-category" class="tab-content">
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div class="card-title">🛍️ 5대 세부 업종별 소비 갭 분석</div>
          <div class="controls-row" id="catSelectorBtns">
            <!-- 동적 버튼 생성 -->
          </div>
        </div>
        <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 20px;" id="catDescription">
          선택한 업종에 대해 인구·인프라 기준 대비 실제 소비가 초과 달성되었거나, 반대로 결핍되어 잠재력이 큰 동네를 확인합니다.
        </p>

        <div class="grid-2">
          <!-- 좌측: 초과 달성 Top 10 -->
          <div class="card" style="background: rgba(15, 23, 42, 0.6);">
            <div class="card-header">
              <div class="card-title" style="color: var(--accent-rose);">🔥 해당 업종 소비 핫스팟 Top 10</div>
            </div>
            <div class="table-container" style="max-height: 400px;">
              <table>
                <thead>
                  <tr>
                    <th>행정동</th>
                    <th>자치구</th>
                    <th>실제 소비액</th>
                    <th>기대치 대비 격차</th>
                  </tr>
                </thead>
                <tbody id="catOverBody"></tbody>
              </table>
            </div>
          </div>

          <!-- 우측: 잠재력 Top 10 -->
          <div class="card" style="background: rgba(15, 23, 42, 0.6);">
            <div class="card-header">
              <div class="card-title" style="color: var(--accent-emerald);">💡 해당 업종 숨은 잠재력 (공급 결핍) Top 10</div>
            </div>
            <div class="table-container" style="max-height: 400px;">
              <table>
                <thead>
                  <tr>
                    <th>행정동</th>
                    <th>자치구</th>
                    <th>실제 소비액</th>
                    <th>소비 결핍 격차</th>
                  </tr>
                </thead>
                <tbody id="catPotBody"></tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: 동네 1:1 진단실 -->
    <div id="tab-diagnostics" class="tab-content">
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div class="card-title">🔍 행정동 1:1 정밀 진단실</div>
          <div style="display: flex; gap: 12px; align-items: center;">
            <label style="font-size: 14px; color: var(--text-muted);">진단할 동네 선택:</label>
            <select id="diagDongSelect" onchange="renderDiagnostics(this.value)" style="min-width: 220px;">
              <!-- 동적으로 옵션 채움 -->
            </select>
          </div>
        </div>

        <div class="diag-container">
          <!-- 좌측: 소비 지표 및 진단 요약 -->
          <div class="card" style="background: rgba(15, 23, 42, 0.6);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
              <div>
                <h2 id="diag-name" style="font-size: 26px; font-weight: 800; color: var(--text-main);">반포본동</h2>
                <span id="diag-gu" style="font-size: 14px; color: var(--text-muted);">서초구</span>
              </div>
              <div id="diag-badge"></div>
            </div>

            <div class="gauge-container">
              <div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">
                <span>실제 소비액 vs 공식 기대치</span>
                <span id="diag-gap-badge" style="font-weight: 700;">-89.6%</span>
              </div>
              <div class="gauge-bar">
                <div id="diag-gauge-fill" class="gauge-fill" style="width: 20%; background: var(--accent-emerald);"></div>
              </div>
            </div>

            <div class="stat-row">
              <span>실제 분기 소비액</span>
              <span id="diag-actual" style="color: var(--accent-blue);">0 원</span>
            </div>
            <div class="stat-row">
              <span>공식 기반 기대 소비액</span>
              <span id="diag-expected">0 원</span>
            </div>
            <div class="stat-row">
              <span>소비 격차 (Residual)</span>
              <span id="diag-gap-amt">0 원</span>
            </div>
            <div class="stat-row">
              <span>배후 상주인구</span>
              <span id="diag-pop-res">0 명</span>
            </div>
            <div class="stat-row">
              <span>배후 직장인구</span>
              <span id="diag-pop-work">0 명</span>
            </div>
            <div class="stat-row">
              <span>일일 보행 유동인구</span>
              <span id="diag-pop-flow">0 명</span>
            </div>
            <div class="stat-row">
              <span>집객시설 및 지하철역</span>
              <span id="diag-infra">0개 / 0개역</span>
            </div>

            <!-- 종합 진단 처방전 -->
            <div style="margin-top: 20px; padding: 16px; background: rgba(56, 189, 248, 0.08); border-radius: 12px; border: 1px solid var(--border-accent);">
              <h4 style="font-size: 14px; font-weight: 700; color: var(--accent-blue); margin-bottom: 6px;">🩺 AI 상권 분석 진단 처방</h4>
              <p id="diag-prescription" style="font-size: 13px; color: var(--text-muted); line-height: 1.6;">
                진단 소견을 불러오는 중입니다...
              </p>
            </div>
          </div>

          <!-- 우측: 레이더 차트 (서울 평균 대비 경쟁력) -->
          <div class="card" style="background: rgba(15, 23, 42, 0.6); display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <div class="card-title" style="margin-bottom: 12px; align-self: flex-start;">📊 서울시 평균 대비 인구·인프라 레이더 차트</div>
            <div style="position: relative; width: 100%; max-width: 420px; height: 380px;">
              <canvas id="radarChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: 시각화 갤러리 -->
    <div id="tab-gallery" class="tab-content">
      <div class="card" style="margin-bottom: 24px;">
        <div class="card-header">
          <div class="card-title">🖼️ 분석 시각화 고해상도 차트 갤러리 (10종)</div>
          <span style="font-size: 13px; color: var(--text-muted);">이미지를 클릭하면 원본 크기로 확대됩니다.</span>
        </div>
        <div class="gallery-grid" id="galleryGrid">
          <!-- 동적 생성 -->
        </div>
      </div>
    </div>

    <!-- TAB 5: 공식 및 해석 가이드 -->
    <div id="tab-methodology" class="tab-content">
      <div class="card">
        <div class="card-header">
          <div class="card-title">📐 공식형 머신러닝 모델의 수식 및 경제학적 해석 가이드</div>
        </div>

        <h3 style="font-size: 18px; margin-bottom: 12px; color: var(--accent-blue);">1. 왜 "공식형 모델(Log-Log Ridge)"을 선택했는가?</h3>
        <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 16px;">
          서울시 425개 동네의 소비액은 <strong>소공동(약 2.4조원)</strong>부터 <strong>외곽 주거지(수천만원)</strong>까지 10만 배 이상의 극심한 격차가 존재합니다.
          이러한 데이터에 일반 선형회귀를 적용하면 초대형 상권 몇 개에 모델이 끌려가는 심각한 왜곡이 발생합니다.
          따라서 경제학에서 표준적으로 사용하는 <strong>로그-로그(Log-Log) 탄력성 모형</strong>을 채택했습니다.
        </p>

        <h3 style="font-size: 18px; margin: 24px 0 12px 0; color: var(--accent-blue);">2. 실제 도출된 기대 소비액 산출 공식</h3>
        <div class="formula-box">
          log(기대 소비액) = 12.1371<br>
          &nbsp;&nbsp;+ 0.7096 × log(1 + 집객시설 수)<br>
          &nbsp;&nbsp;+ 0.4322 × log(1 + 은행 수)<br>
          &nbsp;&nbsp;+ 0.3179 × log(1 + 총 유동인구 수)<br>
          &nbsp;&nbsp;- 0.1918 × log(1 + 총 상주인구 수)<br>
          &nbsp;&nbsp;+ 0.1551 × log(1 + 병원·약국 수)<br>
          &nbsp;&nbsp;+ 0.1421 × log(1 + 총 직장 인구 수)<br>
          &nbsp;&nbsp;- 0.1045 × log(1 + 버스정류장 수)<br>
          &nbsp;&nbsp;+ 0.0794 × log(1 + 아파트 평균시가)<br>
          &nbsp;&nbsp;+ 0.0502 × log(1 + 영역 면적)<br>
          &nbsp;&nbsp;+ 0.0228 × log(1 + 지하철역 수)
        </div>

        <h3 style="font-size: 18px; margin: 24px 0 12px 0; color: var(--accent-blue);">3. 계수(탄력성, Elasticity)의 쉬운 해석법</h3>
        <ul style="padding-left: 20px; font-size: 14px; color: var(--text-muted); display: flex; flex-direction: column; gap: 8px;">
          <li><strong>집객시설 (+0.710)</strong>: 집객시설이 10% 늘어나면, 동네 상권 소비액은 약 <strong>7.1% 증가</strong>합니다. 서울시 상권 소비를 견인하는 가장 강력한 1순위 인프라입니다.</li>
          <li><strong>은행 (+0.432)</strong>: 상업 및 금융 인프라 밀집도가 높을수록 소비 활력이 약 4.3% 증가합니다.</li>
          <li><strong>유동인구 (+0.318)</strong>: 발걸음이 많은 곳일수록 자연스러운 방문 소비가 발생합니다.</li>
          <li><strong>상주인구 (-0.192)</strong>: 흥미롭게도 상주인구의 계수는 음수(-)입니다. 이는 <strong>아파트나 주택만 밀집한 전형적인 베드타운</strong>일수록 동네 내부 소비가 낮고, 주민들이 강남·종로·홍대 등 외부 상권으로 나가서 돈을 쓴다는 강력한 실증 증거입니다!</li>
        </ul>

        <h3 style="font-size: 18px; margin: 24px 0 12px 0; color: var(--accent-blue);">4. 잔차(Residual)와 갭(Gap %) 해석 기준</h3>
        <p style="font-size: 14px; color: var(--text-muted); margin-bottom: 12px;">
          <strong>잔차(Residual) = 실제 소비액 - 기대 소비액</strong>
        </p>
        <ul style="padding-left: 20px; font-size: 14px; color: var(--text-muted); display: flex; flex-direction: column; gap: 6px;">
          <li><span class="badge badge-superhub">Gap &gt; +50%</span> <strong>초과 달성 핫스팟</strong>: 인구·인프라 대비 외부 유입 소비가 압도적인 핫플레이스</li>
          <li><span class="badge badge-balanced">-30% ~ +30%</span> <strong>균형 상권</strong>: 인구와 시설 규모에 걸맞은 적정 소비 발생</li>
          <li><span class="badge badge-potential">Gap &lt; -30%</span> <strong>소비 잠재력 상권</strong>: 사람은 많은데 상권이 미발달하여 소비가 새는 기회 지역 (F&amp;B 매장, 카페, 문화시설 유치 강력 추천)</li>
        </ul>
      </div>
    </div>

  </main>

  <!-- 모달 라이트박스 -->
  <div id="imageModal" class="modal" onclick="closeModal()">
    <div class="modal-content" onclick="event.stopPropagation()">
      <span class="modal-close" onclick="closeModal()">&times;</span>
      <img id="modalImg" src="" alt="차트 원본">
    </div>
  </div>

  <!-- 푸터 -->
  <footer>
    <p>팀 프로젝트 [머신러닝 예측 &amp; 갭 분석] 인구·인프라 기반 소비 예측 모델 및 ‘소비 잠재력’ 상권 발굴</p>
    <p style="margin-top: 4px; color: var(--text-sub);">데이터 출처: 서울 열린데이터광장(상권분석서비스), 서울 시민생활 데이터 | 생성: Gemi_pjt 파이프라인</p>
  </footer>

  <!-- 인라인 데이터 및 로직 -->
  <script>
    // 파이썬 빌더에서 임베드되는 데이터
    const DATA = __DATA_PLACEHOLDER__;

    let quadrantChartInstance = null;
    let radarChartInstance = null;
    let currentFilterType = 'all';

    // 탭 전환
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');

      const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
      if (btn) btn.classList.add('active');

      if (tabId === 'diagnostics') {
        const select = document.getElementById('diagDongSelect');
        if (select && select.value) renderDiagnostics(select.value);
      }
    }

    // 숫자 포맷
    function formatKRW(num) {
      if (num >= 1e12) return (num / 1e12).toFixed(2) + '조 원';
      if (num >= 1e8) return (num / 1e8).toFixed(1) + '억 원';
      if (num >= 1e4) return (num / 1e4).toFixed(0) + '만 원';
      return Math.round(num).toLocaleString() + '원';
    }

    // 배지 HTML
    function getBadge(type) {
      if (type.includes('초과 달성')) return '<span class="badge badge-superhub">초과 달성 핫스팟</span>';
      if (type.includes('소비 잠재력')) return '<span class="badge badge-potential">소비 잠재력 상권</span>';
      if (type.includes('골목 로컬')) return '<span class="badge badge-niche">골목 로컬 핫플</span>';
      if (type.includes('소비 위축')) return '<span class="badge badge-low">소비 위축 지역</span>';
      return '<span class="badge badge-balanced">균형 상권</span>';
    }

    // 초기화
    function initDashboard() {
      // 1. KPI 설정
      document.getElementById('kpi-total-dongs').innerText = DATA.dongs.length + '개';
      document.getElementById('kpi-r2').innerText = (DATA.summary.r2_cv * 100).toFixed(1) + '%';
      if (DATA.summary.top_overachievers.length > 0) {
        const top1 = DATA.summary.top_overachievers[0];
        document.getElementById('kpi-top-over').innerText = top1.행정동_코드_명;
      }
      if (DATA.summary.top_potentials.length > 0) {
        const pot1 = DATA.summary.top_potentials[0];
        document.getElementById('kpi-top-potential').innerText = pot1.행정동_코드_명;
      }

      // 2. 자치구 셀렉트 옵션
      const guSelect = document.getElementById('guFilter');
      DATA.districts.forEach(gu => {
        const opt = document.createElement('option');
        opt.value = gu;
        opt.innerText = gu;
        guSelect.appendChild(opt);
      });

      // 3. 진단실 행정동 셀렉트 옵션
      const diagSelect = document.getElementById('diagDongSelect');
      DATA.dongs.forEach(dong => {
        const opt = document.createElement('option');
        opt.value = dong.name;
        opt.innerText = `${dong.name} (${dong.gu}) - ${dong.gap_pct > 0 ? '+' : ''}${dong.gap_pct}%`;
        diagSelect.appendChild(opt);
      });
      diagSelect.value = '반포본동';

      // 4. 테이블 렌더링
      renderTable(DATA.dongs);

      // 5. 4분면 산점도 차트 생성
      renderQuadrantChart();

      // 6. 업종별 탭 초기화
      initCategoryTab();

      // 7. 시각화 갤러리 생성
      renderGallery();

      // 8. 기본 진단실 렌더링
      renderDiagnostics('반포본동');
    }

    // 테이블 렌더링
    function renderTable(dongsList) {
      const tbody = document.getElementById('dongTableBody');
      tbody.innerHTML = '';

      dongsList.forEach((dong, idx) => {
        const tr = document.createElement('tr');
        const gapColor = dong.gap_pct >= 0 ? '#fda4af' : '#6ee7b7';
        tr.innerHTML = `
          <td>${idx + 1}</td>
          <td style="font-weight: 700;">${dong.name}</td>
          <td>${dong.gu}</td>
          <td>${formatKRW(dong.actual_spend)}</td>
          <td style="color: var(--text-muted);">${formatKRW(dong.expected_spend)}</td>
          <td style="font-weight: 800; color: ${gapColor};">${dong.gap_pct >= 0 ? '+' : ''}${dong.gap_pct.toLocaleString()}%</td>
          <td>${getBadge(dong.type)}</td>
          <td><button class="action-btn" onclick="openDongDiagnostics('${dong.name}')">진단서</button></td>
        `;
        tbody.appendChild(tr);
      });
    }

    // 필터링 적용
    function applyFilters() {
      const gu = document.getElementById('guFilter').value;
      const search = document.getElementById('dongSearch').value.trim().toLowerCase();

      let filtered = [...DATA.dongs];

      if (currentFilterType === 'overachieve') {
        filtered = filtered.sort((a, b) => b.gap_pct - a.gap_pct).slice(0, 20);
      } else if (currentFilterType === 'potential') {
        filtered = filtered.sort((a, b) => a.gap_pct - b.gap_pct).slice(0, 20);
      }

      if (gu) {
        filtered = filtered.filter(d => d.gu === gu);
      }

      if (search) {
        filtered = filtered.filter(d => d.name.toLowerCase().includes(search));
      }

      renderTable(filtered);
    }

    function filterRankings(type) {
      currentFilterType = type;
      document.querySelectorAll('.controls-row .pill-btn').forEach(btn => {
        btn.classList.remove('active');
        if (type === 'all' && btn.innerText.includes('전체 동')) btn.classList.add('active');
        if (type === 'overachieve' && btn.innerText.includes('초과 달성')) btn.classList.add('active');
        if (type === 'potential' && btn.innerText.includes('소비 잠재력')) btn.classList.add('active');
      });
      applyFilters();
    }

    function openDongDiagnostics(dongName) {
      const select = document.getElementById('diagDongSelect');
      select.value = dongName;
      switchTab('diagnostics');
      renderDiagnostics(dongName);
    }

    // 4분면 산점도 차트 (Chart.js)
    function renderQuadrantChart() {
      const ctx = document.getElementById('quadrantChart').getContext('2d');

      const datasets = [
        {
          label: '초과 달성 핫스팟',
          data: DATA.dongs.filter(d => d.type.includes('초과 달성')).map(d => ({ x: d.infra_scale, y: d.residual_z, dong: d })),
          backgroundColor: '#f43f5e',
          borderColor: 'transparent',
          pointRadius: 5,
          pointHoverRadius: 8
        },
        {
          label: '소비 잠재력 상권 🌟',
          data: DATA.dongs.filter(d => d.type.includes('소비 잠재력')).map(d => ({ x: d.infra_scale, y: d.residual_z, dong: d })),
          backgroundColor: '#10b981',
          borderColor: 'transparent',
          pointRadius: 5,
          pointHoverRadius: 8
        },
        {
          label: '골목 로컬 핫플레이스',
          data: DATA.dongs.filter(d => d.type.includes('골목 로컬')).map(d => ({ x: d.infra_scale, y: d.residual_z, dong: d })),
          backgroundColor: '#a855f7',
          borderColor: 'transparent',
          pointRadius: 4,
          pointHoverRadius: 7
        },
        {
          label: '균형 / 위축 상권',
          data: DATA.dongs.filter(d => !d.type.includes('초과 달성') && !d.type.includes('소비 잠재력') && !d.type.includes('골목 로컬')).map(d => ({ x: d.infra_scale, y: d.residual_z, dong: d })),
          backgroundColor: '#64748b',
          borderColor: 'transparent',
          pointRadius: 3,
          pointHoverRadius: 6
        }
      ];

      quadrantChartInstance = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: { color: '#94a3b8', font: { family: 'Pretendard', size: 12 } }
            },
            tooltip: {
              backgroundColor: 'rgba(15, 23, 42, 0.95)',
              titleColor: '#38bdf8',
              bodyColor: '#f8fafc',
              borderColor: 'rgba(56, 189, 248, 0.3)',
              borderWidth: 1,
              padding: 12,
              displayColors: false,
              callbacks: {
                title: function(items) {
                  const d = items[0].raw.dong;
                  return `${d.name} (${d.gu}) - ${d.type}`;
                },
                label: function(item) {
                  const d = item.raw.dong;
                  return [
                    `• 실제 소비: ${formatKRW(d.actual_spend)}`,
                    `• 공식 기대치: ${formatKRW(d.expected_spend)}`,
                    `• 소비 격차: ${d.gap_pct >= 0 ? '+' : ''}${d.gap_pct}%`,
                    `• 인프라 규모지수: ${d.infra_scale}, 잔차 Z: ${d.residual_z}`
                  ];
                }
              }
            }
          },
          scales: {
            x: {
              title: { display: true, text: '배후 인구 및 인프라 규모 지수 (Z-Score)', color: '#94a3b8' },
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#64748b' }
            },
            y: {
              title: { display: true, text: '소비 잔차 지수 (Residual Z-Score)', color: '#94a3b8' },
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: '#64748b' }
            }
          }
        }
      });
    }

    // 업종별 탭 초기화
    function initCategoryTab() {
      const container = document.getElementById('catSelectorBtns');
      container.innerHTML = '';

      const catNames = Object.keys(DATA.categories);
      catNames.forEach((cat, idx) => {
        const btn = document.createElement('button');
        btn.className = `pill-btn ${idx === 0 ? 'active' : ''}`;
        btn.innerText = cat;
        btn.onclick = () => selectCategory(cat, btn);
        container.appendChild(btn);
      });

      if (catNames.length > 0) {
        selectCategory(catNames[0], container.children[0]);
      }
    }

    function selectCategory(catName, activeBtn) {
      document.querySelectorAll('#catSelectorBtns .pill-btn').forEach(b => b.classList.remove('active'));
      if (activeBtn) activeBtn.classList.add('active');

      const info = DATA.categories[catName];
      if (!info) return;

      const overBody = document.getElementById('catOverBody');
      overBody.innerHTML = '';
      info.top_overachievers.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="font-weight: 700;">${r.표시_동명}</td>
          <td>${r.자치구}</td>
          <td>${formatKRW(r.실제_소비액)}</td>
          <td style="color: var(--accent-rose); font-weight: 700;">+${r.소비_격차_비율_pct.toLocaleString()}%</td>
        `;
        overBody.appendChild(tr);
      });

      const potBody = document.getElementById('catPotBody');
      potBody.innerHTML = '';
      info.top_potentials.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="font-weight: 700;">${r.표시_동명}</td>
          <td>${r.자치구}</td>
          <td>${formatKRW(r.실제_소비액)}</td>
          <td style="color: var(--accent-emerald); font-weight: 700;">${r.소비_격차_비율_pct.toLocaleString()}%</td>
        `;
        potBody.appendChild(tr);
      });
    }

    // 1:1 진단실 렌더링
    function renderDiagnostics(dongName) {
      const dong = DATA.dongs.find(d => d.name === dongName) || DATA.dongs[0];

      document.getElementById('diag-name').innerText = dong.name;
      document.getElementById('diag-gu').innerText = dong.gu + ` (행정동코드: ${dong.code})`;
      document.getElementById('diag-badge').innerHTML = getBadge(dong.type);

      const gapSign = dong.gap_pct >= 0 ? '+' : '';
      const gapColor = dong.gap_pct >= 0 ? 'var(--accent-rose)' : 'var(--accent-emerald)';
      document.getElementById('diag-gap-badge').innerText = `${gapSign}${dong.gap_pct}%`;
      document.getElementById('diag-gap-badge').style.color = gapColor;

      const fill = document.getElementById('diag-gauge-fill');
      const ratio = Math.min(Math.max((dong.actual_spend / dong.expected_spend) * 50, 5), 100);
      fill.style.width = ratio + '%';
      fill.style.background = gapColor;

      document.getElementById('diag-actual').innerText = formatKRW(dong.actual_spend);
      document.getElementById('diag-expected').innerText = formatKRW(dong.expected_spend);
      document.getElementById('diag-gap-amt').innerText = formatKRW(dong.gap_amount);
      document.getElementById('diag-pop-res').innerText = dong.pop_res.toLocaleString() + ' 명';
      document.getElementById('diag-pop-work').innerText = dong.pop_work.toLocaleString() + ' 명';
      document.getElementById('diag-pop-flow').innerText = dong.pop_flow.toLocaleString() + ' 명/분기';
      document.getElementById('diag-infra').innerText = `${dong.facilities}개 집객시설 / 지하철 ${dong.subway}개역`;

      // 처방전 메시지
      let prescription = '';
      if (dong.type.includes('소비 잠재력')) {
        prescription = `<strong>[소비 유출형 성장 잠재 상권]</strong> ${dong.name}은 배후 상주인구(${dong.pop_res.toLocaleString()}명) 및 주거 자산 수준 대비 상권 내부 소비가 <strong>기대치보다 ${Math.abs(dong.gap_pct)}% 낮게</strong> 측정됩니다. 주민들의 소비가 인근 중심 상권으로 유출되고 있음을 시사하며, <strong>F&amp;B 외식 매장, 카페, 문화·생활 편의시설</strong>이 확충될 경우 높은 내부 소비 전환 효과를 기대할 수 있는 골든 스팟입니다.`;
      } else if (dong.type.includes('초과 달성')) {
        prescription = `<strong>[외부 소비 흡수형 슈퍼허브]</strong> ${dong.name}은 배후 인구 공식 예측치 대비 <strong>실제 소비가 +${dong.gap_pct}% 폭발</strong>하고 있는 서울의 핵심 소비 중심지입니다. 직장인 점심/회식 수요 및 광역 유동인구의 집객력이 매우 뛰어나며, 프리미엄 리테일 및 팝업 스토어의 테스트베드로 최적의 입지입니다.`;
      } else if (dong.type.includes('골목 로컬')) {
        prescription = `<strong>[알짜 골목형 로컬 핫플]</strong> 대형 인프라 규모는 크지 않으나, 독창적인 매장과 골목 상권 브랜딩을 통해 인구 대비 높은 소비 효율(${gapSign}${dong.gap_pct}%)을 달성하고 있는 틈새 강소 상권입니다.`;
      } else {
        prescription = `<strong>[안정적 균형 상권]</strong> 인구 및 인프라 규모에 비례하여 기대 소비액 수준에 부합하는 소비 활동이 안정적으로 일어나는 전형적인 지역 상권입니다.`;
      }
      document.getElementById('diag-prescription').innerHTML = prescription;

      // 레이더 차트 갱신
      renderRadarChart(dong);
    }

    // 레이더 차트 (백분위수)
    function renderRadarChart(dong) {
      const ctx = document.getElementById('radarChart').getContext('2d');

      const calcPct = (val, key) => {
        const all = DATA.dongs.map(d => d[key]).sort((a, b) => a - b);
        const rank = all.findIndex(v => v >= val);
        return Math.round(((rank < 0 ? all.length : rank) / all.length) * 100);
      };

      const radarData = [
        calcPct(dong.pop_res, 'pop_res'),
        calcPct(dong.pop_work, 'pop_work'),
        calcPct(dong.pop_flow, 'pop_flow'),
        calcPct(dong.facilities, 'facilities'),
        calcPct(dong.subway, 'subway'),
        calcPct(dong.apt_price, 'apt_price')
      ];

      if (radarChartInstance) {
        radarChartInstance.destroy();
      }

      radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
          labels: ['상주인구', '직장인구', '유동인구', '집객시설', '지하철역', '아파트시가'],
          datasets: [
            {
              label: dong.name + ' (상대 백분위 %)',
              data: radarData,
              backgroundColor: 'rgba(56, 189, 248, 0.25)',
              borderColor: '#38bdf8',
              pointBackgroundColor: '#38bdf8',
              pointBorderColor: '#fff',
              borderWidth: 2
            },
            {
              label: '서울시 중간값 (50%)',
              data: [50, 50, 50, 50, 50, 50],
              borderColor: 'rgba(255, 255, 255, 0.2)',
              borderDash: [4, 4],
              pointRadius: 0,
              fill: false
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              min: 0,
              max: 100,
              ticks: { display: false },
              grid: { color: 'rgba(255, 255, 255, 0.08)' },
              angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
              pointLabels: { color: '#cbd5e1', font: { family: 'Pretendard', size: 12, weight: '600' } }
            }
          },
          plugins: {
            legend: { labels: { color: '#94a3b8' } }
          }
        }
      });
    }

    // 갤러리 렌더링
    function renderGallery() {
      const grid = document.getElementById('galleryGrid');
      grid.innerHTML = '';

      const images = [
        { file: '01_feature_correlation_heatmap.png', title: '인구·인프라와 소비액 상관계수 히트맵', desc: '집객시설(+0.67)과 은행(+0.68)이 소비와 가장 밀접' },
        { file: '02_actual_vs_expected_scatter.png', title: '기대 소비액 vs 실제 소비액 산점도', desc: '기대선(Y=X) 기준 초과 달성과 저평가 상권의 극명한 대조' },
        { file: '03_residual_distribution.png', title: '소비 잔차(Residual) 정규분포 적합 곡선', desc: '로그 스케일 변환을 통해 안정적인 종형 정규분포 검증' },
        { file: '04_top15_overachiever_dongs.png', title: '초과 달성 상권 Top 15 바 차트', desc: '용산2가동, 구로3동, 문래동, 소공동 등 서울의 메가 핫스팟' },
        { file: '05_top15_potential_growth_dongs.png', title: '저평가 소비 잠재력 상권 Top 15 바 차트', desc: '반포본동, 개포1동, 공덕동, 충현동 등 소비 유출 기회 지역' },
        { file: '06_consumption_gap_quadrant.png', title: '4분면 상권 기회 진단 매트릭스', desc: '배후 인프라 규모와 소비 잔차를 교차한 4대 기회 매핑' },
        { file: '07_formula_elasticity_weights.png', title: '공식형 모델 핵심 탄력성 계수 가중치', desc: '시설 1% 증가 시 소비 +0.71% 증가, 상주인구 집중 시 -0.19%' },
        { file: '08_gu_residual_summary.png', title: '서울시 25개 자치구별 평균 소비 갭 비교', desc: '중구·강남구(초과) vs 노원·도봉·서초 일부(소비 유출)' },
        { file: '09_category_gap_comparison.png', title: '5대 세부 업종별 소비 갭 분포 비교', desc: '외식, 여가, 마트, 생활용품, 의료 카테고리별 잔차 분산' },
        { file: '10_potential_dongs_deepdive.png', title: '소비 잠재력 상위 5개 동 업종별 결핍 현황', desc: '잠재력 지역에서 어떤 업종의 소비가 유독 덜 일어나는지 심층 진단' }
      ];

      images.forEach(img => {
        const card = document.createElement('div');
        card.className = 'gallery-card';
        card.onclick = () => openModal('image/' + img.file);
        card.innerHTML = `
          <img class="gallery-img" src="image/${img.file}" alt="${img.title}">
          <div class="gallery-info">
            <div class="gallery-title">${img.title}</div>
            <div class="gallery-desc">${img.desc}</div>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    function openModal(src) {
      document.getElementById('modalImg').src = src;
      document.getElementById('imageModal').classList.add('active');
    }

    function closeModal() {
      document.getElementById('imageModal').classList.remove('active');
    }

    window.onload = initDashboard;
  </script>
</body>
</html>
"""

def generate_html():
    print("=" * 60)
    print("🌐 [Step 4] 인터랙티브 웹 대시보드 (index.html) 생성 시작")
    print("=" * 60)

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data_content = f.read()

    html_content = HTML_TEMPLATE.replace("__DATA_PLACEHOLDER__", data_content)

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ 웹 대시보드 파일 생성 완료: {OUT_HTML} ({OUT_HTML.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    generate_html()
