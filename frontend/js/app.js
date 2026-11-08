// ---- Theme ----
const root = document.documentElement;
const savedTheme = localStorage.getItem("theme") || "dark";
root.setAttribute("data-theme", savedTheme);
document.getElementById("theme-toggle").textContent = savedTheme === "dark" ? "🌙" : "☀️";
document.getElementById("theme-select").value = savedTheme;

function setTheme(next) {
  root.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
  document.getElementById("theme-toggle").textContent = next === "dark" ? "🌙" : "☀️";
  document.getElementById("theme-select").value = next;
}
document.getElementById("theme-toggle").addEventListener("click", () => {
  setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
});
document.getElementById("theme-select").addEventListener("change", (e) => setTheme(e.target.value));

// ---- Hash router ----
const pages = ["dashboard", "predict", "assistant", "voice", "analytics", "reports", "monitoring", "settings"];
function showPage(name) {
  if (!pages.includes(name)) name = "dashboard";
  document.querySelectorAll(".page").forEach((el) => el.classList.remove("active"));
  document.querySelectorAll("#nav a").forEach((a) => a.classList.remove("active"));
  document.getElementById(`page-${name}`).classList.add("active");
  document.querySelector(`#nav a[data-page="${name}"]`).classList.add("active");
  if (name === "analytics") loadAnalytics();
  if (name === "monitoring") loadMonitoring();
  if (name === "settings") checkApiStatus();
}
window.addEventListener("hashchange", () => showPage(location.hash.slice(1) || "dashboard"));
showPage(location.hash.slice(1) || "dashboard");

// ---- Dashboard cards ----
async function loadDashboard() {
  try {
    const data = await API.analytics();
    document.getElementById("total-value").textContent = data.total;
    document.getElementById("risk-value").textContent =
      data.positive > data.negative ? "Elevated" : "Low Risk";
    const score = data.total ? Math.round((data.negative / data.total) * 100) : 0;
    document.getElementById("score-value").textContent = score + "/100";
    renderHealthChart(data.daily);
  } catch (e) { console.error(e); }
}

async function loadMonitoring() {
  const out = document.getElementById("monitoring-output");
  try {
    const m = await API.monitoring();
    if (m.configured && m.runs && m.runs.length) {
      const best = m.runs[0];
      const acc = best.metrics?.accuracy ?? best.metrics?.["accuracy"];
      if (acc) document.getElementById("acc-value").textContent = (acc * 100).toFixed(1) + "%";
      out.innerHTML = `<p>Experiment: <b>${m.experiment}</b></p>` +
        m.runs.map((r) =>
          `<div class="run"><code>${r.run_id.slice(0, 8)}</code> ` +
          `status=${r.status} ` +
          `roc_auc=${(r.metrics.roc_auc ?? 0).toFixed(4)}</div>`
        ).join("");
    } else {
      document.getElementById("acc-value").textContent = "N/A";
      out.textContent = "MLflow not configured or no runs found.";
    }
  } catch (e) {
    out.textContent = "Error loading MLflow: " + e.message;
  }
}

// ---- Predict form ----
document.getElementById("predict-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {};
  fd.forEach((v, k) => {
    payload[k] = ["Age", "RestingBP", "Cholesterol", "FastingBS", "MaxHR"].includes(k)
      ? parseInt(v, 10)
      : k === "Oldpeak" ? parseFloat(v) : v;
  });
  const box = document.getElementById("predict-result");
  box.textContent = "Predicting…";
  try {
    const r = await API.predict(payload);
    const risk = r.prediction === 1 ? "Elevated risk" : "Low risk";
    box.innerHTML = `<h3>${risk}</h3>
      <p>P(low) = ${r.probabilities[0].toFixed(3)} · P(high) = ${r.probabilities[1].toFixed(3)}</p>`;
  } catch (err) {
    box.textContent = "Error: " + err.message;
  }
});

// ---- Assistant chat ----
const chatWindow = document.getElementById("chat-window");
function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return div;
}
document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const q = input.value.trim();
  if (!q) return;
  appendMessage("user", q);
  input.value = "";
  const thinking = appendMessage("bot", "…thinking");
  try {
    const r = await API.assistant(q);
    thinking.textContent = r.answer;
    if (r.route === "guardrail") thinking.classList.add("guardrail");
  } catch (err) {
    thinking.textContent = "Error: " + err.message;
  }
});

// ---- Voice agent (Web Speech API) ----
let recognition = null;
let listening = false;
const micBtn = document.getElementById("mic-btn");

if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
  micBtn.disabled = true;
  micBtn.textContent = "Voice not supported in this browser";
} else {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  micBtn.addEventListener("click", () => {
    if (listening) { recognition.stop(); return; }
    listening = true;
    micBtn.textContent = "🛑 Listening…";
    document.getElementById("voice-transcript").textContent = "";
    document.getElementById("voice-response").textContent = "";
    recognition.start();
  });

  recognition.onresult = async (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("voice-transcript").textContent = "You said: " + transcript;
    try {
      const r = await API.assistant(transcript);
      document.getElementById("voice-response").textContent = r.answer;
      const utter = new SpeechSynthesisUtterance(r.answer);
      utter.lang = "en-US";
      speechSynthesis.speak(utter);
    } catch (err) {
      document.getElementById("voice-response").textContent = "Error: " + err.message;
    }
  };

  recognition.onend = () => {
    listening = false;
    micBtn.textContent = "🎤 Start Listening";
  };
  recognition.onerror = (e) => {
    listening = false;
    micBtn.textContent = "🎤 Start Listening";
    document.getElementById("voice-response").textContent = "Voice error: " + e.error;
  };
}

// ---- Analytics page ----
async function loadAnalytics() {
  try {
    const data = await API.analytics();
    renderAnalyticsChart(data.daily);
  } catch (e) { console.error(e); }
}

// ---- Reports ----
document.getElementById("report-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const out = document.getElementById("report-output");
  out.textContent = "Generating…";
  try {
    const res = await fetch("/api/report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ patient_id: fd.get("patient_id") }),
    });
    out.textContent = res.ok ? await res.text() : "Error: " + (await res.text());
  } catch (err) {
    out.textContent = "Error: " + err.message;
  }
});

// ---- Settings ----
async function checkApiStatus() {
  const span = document.getElementById("api-status");
  try {
    const res = await fetch("/api/health");
    const j = await res.json();
    span.textContent = j.status === "ok"
      ? `OK · Gemini=${j.gemini_configured} · Groq=${j.groq_configured} · MLflow=${j.mlflow_configured}`
      : "Degraded";
  } catch (e) {
    span.textContent = "Unreachable";
  }
}

// ---- Init ----
loadDashboard();