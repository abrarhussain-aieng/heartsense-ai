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

function getLast6Months() {
  const months = [];
  const d = new Date();
  for (let i = 5; i >= 0; i--) {
    const pastDate = new Date(d.getFullYear(), d.getMonth() - i, 1);
    months.push(pastDate.toLocaleString('en-US', { month: 'short' }));
  }
  return months;
}

// --- MAIN DASHBOARD CHART (Bar + Line) ---
function renderHealthChart(dailyData) {
  const canvas = document.getElementById('healthChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (healthChartInstance) healthChartInstance.destroy();

  const last6Months = getLast6Months();
  const riskData = [0, 0, 0, 0, 0, 0];
  const scoreData = [0, 0, 0, 0, 0, 0];

  if (dailyData && dailyData.length > 0) {
    dailyData.forEach(item => {
      const itemDate = new Date(item.date);
      const monthStr = itemDate.toLocaleString('en-US', { month: 'short' });
      const monthIndex = last6Months.indexOf(monthStr);
      
      if (monthIndex !== -1) {
        riskData[monthIndex] += item.count;
        scoreData[monthIndex] = Math.min(100, scoreData[monthIndex] + (item.count * 10));
      }
    });
  }

  // Fill empty months with baseline data so the chart doesn't look empty
  for(let i=0; i<6; i++) {
     if(riskData[i] > 0 && scoreData[i] === 0) scoreData[i] = 80;
     if(riskData[i] === 0 && scoreData[i] === 0) scoreData[i] = 50;
  }

  healthChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: last6Months,
      datasets: [
        {
          type: 'line',
          label: 'Health Score',
          data: scoreData,
          borderColor: '#8b5cf6',
          backgroundColor: '#8b5cf6',
          borderWidth: 3,
          pointRadius: 4,
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          type: 'bar',
          label: 'Predictions',
          data: riskData,
          backgroundColor: '#3b82f6',
          borderRadius: 6,
          barThickness: 20,
          yAxisID: 'y'
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
// --- MAIN DASHBOARD CHART (Date by Date) ---
function renderHealthChart(dailyData) {
  const canvas = document.getElementById('healthChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (healthChartInstance) healthChartInstance.destroy();

  let labels = [];
  let data = [];

  // If we have data, plot it exactly as it comes from the database
  if (dailyData && dailyData.length > 0) {
    // Sort dates from oldest to newest
    dailyData.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Use the exact date string (e.g., '2026-11-08')
    labels = dailyData.map(d => d.date);
    data = dailyData.map(d => d.count);
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
          backgroundColor: '#3b82f6', // Blue bars
          borderRadius: 6,
          barThickness: 'flex',
          maxBarThickness: 40
        }
      ]
    },
    // Using your existing theme-aware chart options
    options: getChartOptions(false) 
  });
}