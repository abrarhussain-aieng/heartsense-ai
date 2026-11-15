let healthChartInstance = null;
let riskChartInstance = null;
let analyticsChartInstance = null;

// Helper to get theme colors
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
      legend: { 
        display: showLegend,
        labels: { color: theme.textColor, font: { family: 'Inter', size: 12 } }
      },
      tooltip: {
        backgroundColor: theme.tooltipBg,
        titleColor: theme.tooltipText,
        bodyColor: theme.textColor,
        borderColor: theme.tooltipBorder,
        borderWidth: 1,
        padding: 10
      }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: theme.textColor } },
      y: { grid: { color: theme.gridColor }, ticks: { color: theme.textColor }, beginAtZero: true }
    }
  };
}

// Helper to get local YYYY-MM-DD string to avoid timezone bugs
function getLocalYYYYMMDD(date) {
  const offset = date.getTimezoneOffset();
  const localDate = new Date(date.getTime() - (offset * 60 * 1000));
  return localDate.toISOString().split('T')[0];
}

// --- MAIN DASHBOARD CHART (With Bulletproof Time Filtering) ---
function renderHealthChart(dailyData, filter = 'all') {
  const canvas = document.getElementById('healthChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (healthChartInstance) healthChartInstance.destroy();

  let filteredData = [];
  
  if (dailyData && dailyData.length > 0) {
    // Sort from oldest to newest
    dailyData.sort((a, b) => new Date(a.date) - new Date(b.date));

    // 1. Get today's date as a YYYY-MM-DD string (Local Time)
    const todayStr = getLocalYYYYMMDD(new Date());
    
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = getLocalYYYYMMDD(yesterday);

    const lastWeek = new Date();
    lastWeek.setDate(lastWeek.getDate() - 7);
    
    const lastMonth = new Date();
    lastMonth.setMonth(lastMonth.getMonth() - 1);
    
    const lastYear = new Date();
    lastYear.setFullYear(lastYear.getFullYear() - 1);

    // 2. Filter using exact string matches for today/yesterday and date objects for ranges
    filteredData = dailyData.filter(item => {
      if (filter === 'today') return item.date === todayStr;
      if (filter === 'yesterday') return item.date === yesterdayStr;
      
      const itemDate = new Date(item.date);
      if (filter === 'week') return itemDate >= lastWeek;
      if (filter === 'month') return itemDate >= lastMonth;
      if (filter === 'year') return itemDate >= lastYear;
      
      return true; // 'all'
    });
  }

  let labels = [];
  let data = [];

  if (filteredData.length > 0) {
    labels = filteredData.map(d => d.date);
    data = filteredData.map(d => d.count);
  } else {
    labels = ['No Data'];
    data = [0];
  }

  healthChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Predictions',
          data: data,
          backgroundColor: '#3b82f6',
          borderRadius: 6,
          barThickness: 'flex',
          maxBarThickness: 40
        }
      ]
    },
    options: getChartOptions(false) 
  });
}

// --- DOUGHNUT CHART ---
function renderRiskDistribution() {
  const canvas = document.getElementById('riskChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (riskChartInstance) riskChartInstance.destroy();

  canvas.width = 150;
  canvas.height = 150;

  riskChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Low', 'Medium', 'High'],
      datasets: [{
        data: [72, 15, 13],
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
        borderWidth: 0,
        cutout: '75%'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } }
    }
  });
}

// --- ANALYTICS PAGE CHART (Smooth Area Chart) ---
function renderAnalyticsChart(dailyData) {
  const canvas = document.getElementById('analyticsChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (analyticsChartInstance) analyticsChartInstance.destroy();
  
  let labels = [];
  let data = [];

  if (dailyData && dailyData.length > 0) {
    dailyData.sort((a, b) => new Date(a.date) - new Date(b.date));
    labels = dailyData.map(d => d.date);
    data = dailyData.map(d => d.count);
  } else {
    labels = ['No Data'];
    data = [0];
  }

  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, 'rgba(139, 92, 246, 0.4)'); 
  gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');   

  analyticsChartInstance = new Chart(ctx, {
    type: 'line',
    data: { 
      labels: labels, 
      datasets: [{ 
        label: 'Daily Predictions', 
        data: data, 
        borderColor: '#8b5cf6', 
        backgroundColor: gradient,
        borderWidth: 3,
        pointBackgroundColor: '#8b5cf6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: true, 
        tension: 0.4 
      }] 
    },
    options: getChartOptions(true) 
  });
}