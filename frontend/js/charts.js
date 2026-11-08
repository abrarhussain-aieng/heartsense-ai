let healthChart = null;

function renderHealthChart(daily) {
  const ctx = document.getElementById("healthChart").getContext("2d");
  if (healthChart) healthChart.destroy();
  healthChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: daily.map((d) => d.date),
      datasets: [{
        label: "Predictions",
        data: daily.map((d) => d.count),
        backgroundColor: "rgba(59, 130, 246, 0.6)",
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#cbd5e1" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.1)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.1)" } },
      },
    },
  });
}

let analyticsChart = null;
function renderAnalyticsChart(daily) {
  const ctx = document.getElementById("analyticsChart").getContext("2d");
  if (analyticsChart) analyticsChart.destroy();
  analyticsChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: daily.map((d) => d.date),
      datasets: [{
        label: "Daily Predictions",
        data: daily.map((d) => d.count),
        borderColor: "#8b5cf6",
        backgroundColor: "rgba(139,92,246,0.2)",
        fill: true,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#cbd5e1" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.1)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.1)" } },
      },
    },
  });
}