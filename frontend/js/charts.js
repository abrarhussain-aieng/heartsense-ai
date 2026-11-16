let healthChartInstance = null;
let riskChartInstance = null;
let analyticsChartInstance = null;

function getChartTheme() {
  const isDark = document.documentElement.getAttribute("data-theme") === "dark";
  return {
    textColor: isDark ? '#94a3b8' : '#64748b',
    gridColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
    tooltipBg: isDark ? 'rgba(15, 23, 42, 0.9)' : 'rgba(255, 255, 255, 0.9)',
    tooltipText: isDark ? '#f8fafc' : '#0f172a',
    tooltipBorder: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'
  };
}

function getChartOptions(showLegend = false) {
  const theme = getChartTheme();
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { 
      legend: { display: showLegend, labels: { color: theme.textColor, font: { family: 'Inter', size: 12 } } },
      tooltip: { backgroundColor: theme.tooltipBg, titleColor: theme.tooltipText, bodyColor: theme.textColor, borderColor: theme.tooltipBorder, borderWidth: 1, padding: 10 }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: theme.textColor } },
      y: { grid: { color: theme.gridColor }, ticks: { color: theme.textColor }, beginAtZero: true }
    }
  };
}

function getLocalYYYYMMDD(date) {
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().split('T')[0];
}

function renderHealthChart(dailyData, filter = 'all') {
  const canvas = document.getElementById('healthChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (healthChartInstance) healthChartInstance.destroy();

  let filteredData = [];
  if (dailyData && dailyData.length > 0) {
    dailyData.sort((a, b) => new Date(a.date) - new Date(b.date));
    const todayStr = getLocalYYYYMMDD(new Date());
    const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = getLocalYYYYMMDD(yesterday);
    const lastWeek = new Date(); lastWeek.setDate(lastWeek.getDate() - 7);
    const lastMonth = new Date(); lastMonth.setMonth(lastMonth.getMonth() - 1);
    const lastYear = new Date(); lastYear.setFullYear(lastYear.getFullYear() - 1);

    filteredData = dailyData.filter(item => {
      if (filter === 'today') return item.date === todayStr;
      if (filter === 'yesterday') return item.date === yesterdayStr;
      const itemDate = new Date(item.date);
      if (filter === 'week') return itemDate >= lastWeek;
      if (filter === 'month') return itemDate >= lastMonth;
      if (filter === 'year') return itemDate >= lastYear;
      return true;
    });
  }

  let labels = filteredData.length > 0 ? filteredData.map(d => d.date) : ['No Data'];
  let data = filteredData.length > 0 ? filteredData.map(d => d.count) : [0];

  healthChartInstance = new Chart(ctx, {
    type: 'bar',
    data: { labels: labels, datasets: [{ label: 'Predictions', data: data, backgroundColor: '#3b82f6', borderRadius: 6, barThickness: 'flex', maxBarThickness: 40 }] },
    options: getChartOptions(false) 
  });
}

// UPDATED: Now accepts real data instead of hardcoded [72, 15, 13]
function renderRiskDistribution(lowRisk = 0, highRisk = 0) {
  const canvas = document.getElementById('riskChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (riskChartInstance) riskChartInstance.destroy();

  canvas.width = 150;
  canvas.height = 150;

  const data = (lowRisk === 0 && highRisk === 0) ? [1] : [lowRisk, highRisk];
  const colors = (lowRisk === 0 && highRisk === 0) ? ['#334155'] : ['#10b981', '#ef4444'];
  const labels = (lowRisk === 0 && highRisk === 0) ? ['No Data'] : ['Low Risk', 'High Risk'];

  riskChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: { labels: labels, datasets: [{ data: data, backgroundColor: colors, borderWidth: 0, cutout: '75%' }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
  });
}

function renderAnalyticsChart(dailyData) {
  const canvas = document.getElementById('analyticsChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (analyticsChartInstance) analyticsChartInstance.destroy();
  
  let labels = dailyData && dailyData.length > 0 ? dailyData.map(d => d.date) : ['No Data'];
  let data = dailyData && dailyData.length > 0 ? dailyData.map(d => d.count) : [0];

  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, 'rgba(139, 92, 246, 0.4)'); 
  gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');   

  analyticsChartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels: labels, datasets: [{ label: 'Daily Predictions', data: data, borderColor: '#8b5cf6', backgroundColor: gradient, borderWidth: 3, pointBackgroundColor: '#8b5cf6', pointBorderColor: '#fff', pointBorderWidth: 2, pointRadius: 5, pointHoverRadius: 7, fill: true, tension: 0.4 }] },
    options: getChartOptions(true) 
  });
}