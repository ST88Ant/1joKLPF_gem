/**
 * Gemi_pjt - 대시보드 인터랙션 및 시각화 로직 (app.js)
 */

const DATA = window.DASHBOARD_DATA;

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

// 금액 단위 포맷팅 (원 -> 억/조)
function formatKRW(num) {
  if (num >= 1e12) return (num / 1e12).toFixed(2) + '조 원';
  if (num >= 1e8) return (num / 1e8).toFixed(1) + '억 원';
  if (num >= 1e4) return (num / 1e4).toFixed(0) + '만 원';
  return Math.round(num).toLocaleString() + '원';
}

// 상권 유형별 배지 생성
function getBadge(type) {
  if (type.includes('초과 달성')) return '<span class="badge badge-superhub">초과 달성 핫스팟</span>';
  if (type.includes('소비 잠재력')) return '<span class="badge badge-potential">소비 잠재력 상권</span>';
  if (type.includes('골목 로컬')) return '<span class="badge badge-niche">골목 로컬 핫플</span>';
  if (type.includes('소비 위축')) return '<span class="badge badge-low">소비 위축 지역</span>';
  return '<span class="badge badge-balanced">균형 상권</span>';
}

// 대시보드 전체 초기화
function initDashboard() {
  if (!DATA) {
    console.error("DASHBOARD_DATA가 로드되지 않았습니다.");
    return;
  }

  // 1. KPI 카드 바인딩
  document.getElementById('kpi-total-dongs').innerText = DATA.dongs.length + '개';
  document.getElementById('kpi-r2').innerText = (DATA.summary.r2_cv * 100).toFixed(1) + '%';
  if (DATA.summary.top_overachievers && DATA.summary.top_overachievers.length > 0) {
    const top1 = DATA.summary.top_overachievers[0];
    document.getElementById('kpi-top-over').innerText = top1.행정동_코드_명;
  }
  if (DATA.summary.top_potentials && DATA.summary.top_potentials.length > 0) {
    const pot1 = DATA.summary.top_potentials[0];
    document.getElementById('kpi-top-potential').innerText = pot1.행정동_코드_명;
  }

  // 2. 자치구 필터 옵션
  const guSelect = document.getElementById('guFilter');
  if (guSelect) {
    DATA.districts.forEach(gu => {
      const opt = document.createElement('option');
      opt.value = gu;
      opt.innerText = gu;
      guSelect.appendChild(opt);
    });
  }

  // 3. 진단실 행정동 선택 셀렉트
  const diagSelect = document.getElementById('diagDongSelect');
  if (diagSelect) {
    DATA.dongs.forEach(dong => {
      const opt = document.createElement('option');
      opt.value = dong.name;
      opt.innerText = `${dong.name} (${dong.gu}) - ${dong.gap_pct > 0 ? '+' : ''}${dong.gap_pct}%`;
      diagSelect.appendChild(opt);
    });
    diagSelect.value = '반포본동';
  }

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

// 랭킹 테이블 렌더링
function renderTable(dongsList) {
  const tbody = document.getElementById('dongTableBody');
  if (!tbody) return;
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

// 필터 적용
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
  if (select) select.value = dongName;
  switchTab('diagnostics');
  renderDiagnostics(dongName);
}

// 4분면 산점도 차트 (Chart.js)
function renderQuadrantChart() {
  const canvas = document.getElementById('quadrantChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

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
  if (!container) return;
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
  if (overBody) {
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
  }

  const potBody = document.getElementById('catPotBody');
  if (potBody) {
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
  const canvas = document.getElementById('radarChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

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
  if (!grid) return;
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
