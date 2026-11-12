let healthChartInstance = null;
let riskChartInstance = null;
let analyticsChartInstance = null;

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' }, beginAtZero: true }
  }
};

// Helper to get the last 6 months dynamically (e.g., "Jun", "Jul", "Aug", "Sep", "Oct", "Nov")
function getLast6Months() {
  const months = [];
  const d = new Date();
  for (let i = 5; i >= 0; i--) {
    const pastDate = new Date(d.getFullYear(), d.getMonth() - i, 1);
    months.push(pastDate.toLocaleString('en-US', { month: 'short' }));
  }
  return months;
}

function renderHealthChart(dailyData) {
  const canvas = document.getElementById('healthChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (healthChartInstance) healthChartInstance.destroy();

  const last6Months = getLast6Months();
  const riskData = [0, 0, 0, 0, 0, 0];
  const scoreData = [0, 0, 0, 0, 0, 0];

  // Map actual data to the last 6 months
  if (dailyData && dailyData.length > 0) {
    dailyData.forEach(item => {
      const itemDate = new Date(item.date);
      const monthStr = itemDate.toLocaleString('en-US', { month: 'short' });
      const monthIndex = last6Months.indexOf(monthStr);
      
      if (monthIndex !== -1) {
        riskData[monthIndex] += item.count;
        // Generate a dynamic health score based on prediction volume
        scoreData[monthIndex] = Math.min(100, scoreData[monthIndex] + (item.count * 10));
      }
    });
  }

  // Fill score data with some baseline if there's risk data but no score
  for(let i=0; i<6; i++) {
     if(riskData[i] > 0 && scoreData[i] === 0) scoreData[i] = 80;
     if(riskData[i] === 0 && scoreData[i] === 0) scoreData[i] = 50; // Default flatline
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
    options: chartOptions
  });
}

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

function renderAnalyticsChart(dailyData) {
  const canvas = document.getElementById('analyticsChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (analyticsChartInstance) analyticsChartInstance.destroy();
  
  let labels = [];
  let data = [];

  if (dailyData && dailyData.length > 0) {
    // Sort by date
    dailyData.sort((a, b) => new Date(a.date) - new Date(b.date));
    labels = dailyData.map(d => {
      const dt = new Date(d.date);
      return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    data = dailyData.map(d => d.count);
  } else {
    labels = ['No Data'];
    data = [0];
  }

  analyticsChartInstance = new Chart(ctx, {
    type: 'line',
    data: { 
      labels: labels, 
      datasets: [{ 
        label: 'Total Predictions', 
        data: data, 
        borderColor: '#3b82f6', 
        fill: true, 
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      }] 
    },
    options: chartOptions
  });
}