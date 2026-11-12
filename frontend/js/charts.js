let healthChart = null;
let analyticsChart = null;

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { 
    legend: { labels: { color: "#94a3b8", font: { family: 'Inter' } } } 
  },
  scales: {
    x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.05)" } },
    y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.05)" } }
  }
};

function renderHealthChart(daily) {
  const canvas = document.getElementById("healthChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (healthChart) healthChart.destroy();
  
  healthChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: daily.map((d) => d.date),
      datasets: [{
        label: "Predictions",
        data: daily.map((d) => d.count),
        backgroundColor: "rgba(59, 130, 246, 0.6)",
        borderColor: "#3b82f6",
        borderWidth: 1,
        borderRadius: 6,
      }],
    },
    options: chartOptions
  });
}

function renderAnalyticsChart(daily) {
  const canvas = document.getElementById("analyticsChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  if (analyticsChart) analyticsChart.destroy();
  
  analyticsChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: daily.map((d) => d.date),
      datasets: [{
        label: "Daily Predictions",
        data: daily.map((d) => d.count),
        borderColor: "#8b5cf6",
        backgroundColor: "rgba(139,92,246,0.15)",
        fill: true,
        tension: 0.4,
        pointBackgroundColor: "#8b5cf6"
      }],
    },
    options: chartOptions
  });
}