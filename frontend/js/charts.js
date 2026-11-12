let healthChartInstance = null;
let riskChartInstance = null;
let analyticsChartInstance = null;

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
    y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
  }
};

function renderHealthChart(dailyData) {
  const canvas = document.getElementById('healthChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  if (healthChartInstance) healthChartInstance.destroy();

  let labels, dataRisk, dataScore;

  if (!dailyData || dailyData.length < 6) {
    labels = ['May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'];
    dataRisk = [45, 52, 38, 60, 55, 48];
    dataScore = [70, 75, 68, 82, 78, 85];
  } else {
    labels = dailyData.map(d => d.date);
    dataRisk = dailyData.map(d => d.count);
    dataScore = dailyData.map(d => Math.min(100, d.count * 1.5 + 40));
  }

  healthChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          type: 'line',
          label: 'Health Score',
          data: dataScore,
          borderColor: '#8b5cf6',
          backgroundColor: '#8b5cf6',
          borderWidth: 3,
          pointRadius: 4,
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          type: 'bar',
          label: 'Risk Level',
          data: dataRisk,
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
  
  const labels = dailyData && dailyData.length > 0 ? dailyData.map(d => d.date) : ['No Data'];
  const data = dailyData && dailyData.length > 0 ? dailyData.map(d => d.count) : [0];

  analyticsChartInstance = new Chart(ctx, {
    type: 'line',
    data: { labels: labels, datasets: [{ label: 'Predictions', data: data, borderColor: '#3b82f6', fill: true, backgroundColor: 'rgba(59, 130, 246, 0.1)' }] },
    options: chartOptions
  });
}