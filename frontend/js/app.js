document.addEventListener("DOMContentLoaded", () => {
  
  // --- 1. THEME SWITCHER ---
  const themeToggle = document.getElementById("theme-toggle");
  const currentTheme = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", currentTheme);
  if (themeToggle) themeToggle.textContent = currentTheme === "dark" ? "🌙" : "☀️";

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const isDark = document.documentElement.getAttribute("data-theme") === "dark";
      const newTheme = isDark ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      themeToggle.textContent = newTheme === "dark" ? "🌙" : "☀️";
      
      if (location.hash === "#analytics" || location.hash === "#dashboard" || location.hash === "") {
        loadDashboard();
        loadAnalytics();
      }
    });
  }

  // --- 2. HELPER: Clean Markdown ---
  function cleanMarkdown(text) {
    if (!text) return "";
    let clean = text;
    
    clean = clean.replace(/[*#_]/g, '');
    clean = clean.replace(/\|/g, '  ');
    clean = clean.replace(/-{3,}/g, '');
    clean = clean.replace(/={3,}/g, '');
    clean = clean.replace(/^\s*$/gm, '');
    clean = clean.replace(/^\s*[-*]\s+/gm, '&bull; ');
    clean = clean.replace(/\n/g, '<br>');
    return clean;
  }

  function appendMessage(winId, role, text) {
    const win = document.getElementById(winId);
    if (!win) return null;
    const div = document.createElement("div");
    div.className = "msg " + role;
    div.innerHTML = cleanMarkdown(text);
    win.appendChild(div);
    win.scrollTop = win.scrollHeight;
    return div;
  }

  // --- 3. ROUTER ---
  const pages = ["dashboard", "predict", "assistant", "analytics", "reports", "monitoring"];
  function showPage(name) {
    if (!pages.includes(name)) name = "dashboard";
    document.querySelectorAll(".page").forEach((el) => el.classList.remove("active"));
    document.querySelectorAll("#nav a").forEach((a) => a.classList.remove("active"));
    
    const pageEl = document.getElementById(`page-${name}`);
    if (pageEl) pageEl.classList.add("active");
    
    const navEl = document.querySelector(`#nav a[data-page="${name}"]`);
    if (navEl) navEl.classList.add("active");

    setTimeout(() => {
      if (name === "analytics") loadAnalytics();
      if (name === "dashboard") loadDashboard();
      if (name === "monitoring") loadMonitoring();
    }, 100);
  }
  window.addEventListener("hashchange", () => showPage(location.hash.slice(1) || "dashboard"));
  showPage(location.hash.slice(1) || "dashboard"); 

  // --- 4. DASHBOARD & MONITORING ---
  async function loadDashboard() {
    try {
      const data = await API.analytics();
      document.getElementById("total-value").textContent = data.total || 0;
      document.getElementById("risk-value").textContent = data.positive > data.negative ? "Elevated" : "Low Risk";
      document.getElementById("score-value").textContent = (data.total ? Math.round((data.negative / data.total) * 100) : 100) + "/100";
      if (typeof renderHealthChart === "function") renderHealthChart(data.daily);
    } catch (e) { console.error(e); }
  }
  
  async function loadMonitoring() {
    const out = document.getElementById("monitoring-output");
    const accBox = document.getElementById("acc-value");
    try {
      const m = await API.monitoring();
      if (m.error) {
        if (accBox) accBox.textContent = "N/A";
        out.innerHTML = `<span style="color: #ef4444; font-weight: bold;">❌ Error: ${m.error}</span>`;
        return;
      }

      if (m.configured && m.runs && m.runs.length) {
        const best = m.runs[0];
        const acc = best.metrics?.accuracy || best.metrics?.["accuracy"];
        if (accBox) accBox.textContent = acc ? (acc * 100).toFixed(1) + "%" : "N/A";
        
        out.innerHTML = `
          <p style="margin-bottom: 15px; font-size: 16px;">Experiment: <b>${m.experiment}</b></p>
          <div class="run" style="padding: 20px; border-radius: 12px; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border);">
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
              <span style="font-family: monospace; color: var(--accent);">Run ID: ${best.run_id.slice(0,8)}</span>
              <span style="color: #10b981; font-weight: bold;">Status: ${best.status}</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
              <div><span style="color: var(--muted); font-size: 12px;">Accuracy</span><br><b>${(best.metrics.accuracy * 100).toFixed(1)}%</b></div>
              <div><span style="color: var(--muted); font-size: 12px;">ROC-AUC</span><br><b>${(best.metrics.roc_auc || 0).toFixed(4)}</b></div>
              <div><span style="color: var(--muted); font-size: 12px;">F1 Score</span><br><b>${(best.metrics.f1 || 0).toFixed(4)}</b></div>
            </div>
          </div>
        `;
      } else {
        if (accBox) accBox.textContent = "N/A";
        out.textContent = "No runs found in MLflow. (Experiment is empty)";
      }
    } catch (e) {
      if (accBox) accBox.textContent = "N/A";
      out.innerHTML = `<span style="color: #ef4444;">❌ Network Error: ${e.message}</span>`;
    }
  }

  // --- 5. PREDICT ---
  const predictForm = document.getElementById("predict-form");
  if (predictForm) {
    predictForm.addEventListener("submit", async (e) => {
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
        const isHigh = r.probabilities[1] > 0.5;
        const risk = isHigh ? "High Risk Detected" : "Low Risk";
        const color = isHigh ? "#ef4444" : "#10b981";
        
        box.innerHTML = "<h3 style='color: " + color + "; margin-bottom: 10px;'>" + risk + "</h3>" +
                        "<p>P(low) = " + r.probabilities[0].toFixed(3) + " | P(high) = " + r.probabilities[1].toFixed(3) + "</p>";
        
        loadDashboard();
      } catch (err) {
        box.textContent = "Error: " + err.message;
      }
    });
  }

  // --- VOICE GLOBAL MANAGER ---
  let activeRecognitions = [];
  function stopAllListening() {
    activeRecognitions.forEach(r => {
      try { r.stop(); } catch(e) {}
    });
  }

  // --- 6. AI CHAT LOGIC ---
  async function handleChatSubmit(e, inputId, winId, btnElement, micBtnElement) {
    e.preventDefault();
    
    stopAllListening();

    const input = document.getElementById(inputId);
    const q = input.value.trim();
    if (!q) return;
    
    appendMessage(winId, "user", q);
    input.value = "";
    const thinking = appendMessage(winId, "bot", "⏳ Analyzing...");
    
    if (btnElement) btnElement.disabled = true;
    if (micBtnElement) micBtnElement.disabled = true;

    const phrases = ["⏳ Analyzing...", "🧠 Routing...", "📚 Searching...", "✍️ Writing..."];
    let phraseIdx = 0;
    const thinkInterval = setInterval(() => {
      if (phraseIdx < phrases.length) {
        thinking.innerHTML = `<span style="color: var(--muted); font-style: italic;">${phrases[phraseIdx]}</span>`;
        phraseIdx++;
      }
    }, 1500);

    try {
      const r = await API.assistant(q);
      clearInterval(thinkInterval); 
      thinking.innerHTML = cleanMarkdown(r.answer);
    } catch (err) {
      clearInterval(thinkInterval);
      let errMsg = err.message;
      try {
        const parsed = JSON.parse(errMsg);
        if (parsed.detail) errMsg = parsed.detail;
      } catch (e) {}

      if (errMsg.includes("429") || errMsg.includes("Rate limit") || errMsg.includes("TPD")) {
        thinking.innerHTML = "<span style='color:#f87171;'>⏳ API Rate Limit reached. Please wait 15 minutes and try again.</span>";
      } else {
        thinking.innerHTML = "<span style='color:#f87171;'>" + errMsg + "</span>";
      }
    } finally {
      if (btnElement) btnElement.disabled = false;
      if (micBtnElement) micBtnElement.disabled = false;
    }
  }

  const dashForm = document.getElementById("chat-form");
  if (dashForm) {
    dashForm.addEventListener("submit", (e) => handleChatSubmit(e, "chat-input", "chat-window", dashForm.querySelector("button[type='submit']"), document.getElementById("mic-btn")));
  }
  
  const mainForm = document.getElementById("chat-form-2");
  if (mainForm) {
    mainForm.addEventListener("submit", (e) => handleChatSubmit(e, "chat-input-2", "chat-window-2", mainForm.querySelector("button[type='submit']"), document.getElementById("mic-btn-2")));
  }

  // --- 7. VOICE AGENT ---
  function setupVoice(micBtnId, inputId) {
    const micBtn = document.getElementById(micBtnId);
    if (!micBtn) return;
    
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      micBtn.style.display = "none";
      return;
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SR();
    recognition.lang = "en-US";
    recognition.continuous = true; 
    recognition.interimResults = true; 
    
    let isListening = false;
    let finalTranscript = "";

    activeRecognitions.push(recognition);

    micBtn.addEventListener("click", () => {
      if (isListening) { 
        recognition.stop(); 
        return; 
      }
      isListening = true;
      finalTranscript = "";
      document.getElementById(inputId).value = "";
      micBtn.classList.add("listening");
      micBtn.textContent = "🛑 Stop";
      try { recognition.start(); } catch(e) {}
    });

    recognition.onresult = (event) => {
      let interimTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + " ";
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }
      document.getElementById(inputId).value = finalTranscript + interimTranscript;
    };

    recognition.onend = () => {
      isListening = false;
      micBtn.classList.remove("listening");
      micBtn.textContent = "🎤";
    };
    
    recognition.onerror = () => {
      isListening = false;
      micBtn.classList.remove("listening");
      micBtn.textContent = "🎤";
    };
  }
  
  setupVoice("mic-btn", "chat-input");
  setupVoice("mic-btn-2", "chat-input-2");

  // --- 8. ANALYTICS & REPORTS ---
  async function loadAnalytics() {
    try {
      const data = await API.analytics();
      if (typeof renderAnalyticsChart === "function") renderAnalyticsChart(data.daily);
    } catch (e) { console.error(e); }
  }

  const reportForm = document.getElementById("report-form");
  if (reportForm) {
    reportForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const out = document.getElementById("report-output");
      out.textContent = "Generating...";
      
      try {
        const res = await fetch("/api/report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ patient_id: fd.get("patient_id") }),
        });
        
        if (res.ok) {
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `report_${fd.get("patient_id")}.txt`;
          document.body.appendChild(a);
          a.click();
          a.remove();
          out.textContent = "✅ Report downloaded successfully!";
        } else {
          out.textContent = "Error: " + (await res.text());
        }
      } catch (err) {
        out.textContent = "Error: " + err.message;
      }
    });
  }
});