document.addEventListener("DOMContentLoaded", () => {
  
  if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  }

  // --- 0. DYNAMIC USER UI UPDATE ---
  function updateUserUI() {
    const userName = localStorage.getItem("user_name") || "User";
    const firstName = userName.split(" ")[0];
    
    const greetingName = document.getElementById("greeting-name");
    if (greetingName) greetingName.textContent = firstName;
    
    const sidebarName = document.getElementById("sidebar-name");
    if (sidebarName) sidebarName.textContent = userName;
    
    const sidebarAvatar = document.getElementById("sidebar-avatar");
    if (sidebarAvatar) sidebarAvatar.textContent = firstName.charAt(0).toUpperCase();

    const aiGreeting = document.getElementById("ai-greeting");
    if (aiGreeting) aiGreeting.textContent = `Hello ${firstName}! Ask me anything about your heart health.`;
  }

  if (localStorage.getItem("token")) {
    const authOverlay = document.getElementById("auth-overlay");
    if (authOverlay) authOverlay.style.display = "none";
    updateUserUI();
  }

  // --- 1. AUTHENTICATION LOGIC ---
  const authForm = document.getElementById("auth-form");
  const authTitle = document.getElementById("auth-title");
  const authError = document.getElementById("auth-error");
  const nameGroup = document.getElementById("name-group");
  const submitBtn = document.getElementById("auth-submit-btn");
  const toggleLink = document.getElementById("auth-toggle-link");
  const toggleText = document.getElementById("auth-toggle-text");
  
  let isLoginMode = true;

  if (toggleLink) {
    toggleLink.addEventListener("click", (e) => {
      e.preventDefault();
      isLoginMode = !isLoginMode;
      authTitle.textContent = isLoginMode ? "Welcome Back" : "Create Account";
      
      // Use innerHTML to keep the FontAwesome icons
      if (isLoginMode) {
        submitBtn.innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i> Login';
      } else {
        submitBtn.innerHTML = '<i class="fa-solid fa-user-plus"></i> Sign Up';
      }
      
      toggleText.textContent = isLoginMode ? "Don't have an account?" : "Already have an account?";
      toggleLink.textContent = isLoginMode ? "Sign up" : "Login";
      nameGroup.style.display = isLoginMode ? "none" : "block";
      authError.textContent = "";
    });
  }

  if (authForm) {
    authForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      submitBtn.disabled = true;
      authError.textContent = "";
      
      const email = document.getElementById("auth-email").value;
      const password = document.getElementById("auth-password").value;
      const name = document.getElementById("auth-name").value;
      
      const endpoint = isLoginMode ? "/api/auth/login" : "/api/auth/register";
      const payload = isLoginMode ? { email, password } : { email, password, name };

      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Authentication failed");
        
        if (isLoginMode) {
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("user_name", data.name); 
          window.location.reload(); 
        } else {
          const loginRes = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
          });
          const loginData = await loginRes.json();
          localStorage.setItem("token", loginData.access_token);
          localStorage.setItem("user_name", loginData.name);
          window.location.reload();
        }
      } catch (err) {
        authError.textContent = err.message;
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  // --- 2. THEME SWITCHER ---
  const themeToggle = document.getElementById("theme-toggle");
  const currentTheme = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", currentTheme);
  
  function updateThemeUI(theme) {
    if (!themeToggle) return;
    if (theme === "dark") {
      themeToggle.innerHTML = '<i class="fa-solid fa-moon"></i> <span>Dark Mode</span>';
    } else {
      themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i> <span>Light Mode</span>';
    }
  }
  updateThemeUI(currentTheme);

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const isDark = document.documentElement.getAttribute("data-theme") === "dark";
      const newTheme = isDark ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
      updateThemeUI(newTheme);
      
      if (location.hash === "#analytics" || location.hash === "#dashboard" || location.hash === "") {
        loadDashboard();
        loadAnalytics();
      }
    });
  }

  // --- 3. HELPERS ---
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

  // --- 4. ROUTER ---
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
      if (name === "dashboard") {
        loadDashboard();
      }
      if (name === "monitoring") loadMonitoring();
    }, 150);
  }
  window.addEventListener("hashchange", () => showPage(location.hash.slice(1) || "dashboard"));
  showPage(location.hash.slice(1) || "dashboard"); 

  // --- 5. DASHBOARD & MONITORING ---
  async function loadDashboard() {
    try {
      const data = await API.analytics();
      document.getElementById("total-value").textContent = data.total || 0;
      document.getElementById("risk-value").textContent = data.positive > data.negative ? "Elevated" : "Low Risk";
      document.getElementById("score-value").textContent = (data.total ? Math.round((data.negative / data.total) * 100) : 100) + "/100";
      
      if (typeof renderHealthChart === "function") renderHealthChart(data.daily);
      if (typeof renderRiskDistribution === "function") renderRiskDistribution();
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

  // --- 6. PREDICT ---
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
      performPrediction(payload);
    });
  }

  async function performPrediction(payload) {
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
  }

  // --- 7. UPLOAD REPORT LOGIC (Pure Tesseract.js OCR) ---
  const reportUpload = document.getElementById("report-upload");
  if (reportUpload) {
    reportUpload.addEventListener("change", async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      const resultBox = document.getElementById("predict-result");
      resultBox.textContent = "Initializing OCR engine...";
      window.location.hash = "#predict";

      try {
        let extractedText = "";

        // 1. Handle JSON directly
        if (file.type === "application/json") {
          const text = await file.text();
          const data = JSON.parse(text);
          return performPrediction(data);
        }

        // 2. Handle PDFs using pdf.js
        if (file.type === "application/pdf") {
          const arrayBuffer = await file.arrayBuffer();
          const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
          let fullText = "";
          for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            fullText += textContent.items.map(item => item.str).join(" ") + " ";
          }
          extractedText = fullText;
        }

        // 3. Handle Images using Tesseract.js (No Lens)
        if (file.type.startsWith("image/")) {
          resultBox.textContent = "Loading Tesseract.js...";
          
          // Dynamically load Tesseract.js
          if (typeof Tesseract === 'undefined') {
            await new Promise((resolve, reject) => {
              const script = document.createElement('script');
              script.src = 'https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js';
              script.onload = resolve;
              script.onerror = reject;
              document.head.appendChild(script);
            });
          }

          resultBox.textContent = "Running OCR (this may take a few seconds)...";

          // Run Tesseract with progress logging
          const { data: { text } } = await Tesseract.recognize(
            file,
            'eng', 
            {
              logger: m => {
                if (m.status === 'recognizing text') {
                  const progress = Math.round(m.progress * 100);
                  resultBox.textContent = `Reading image: ${progress}%`;
                }
              }
            }
          );
          
          extractedText = text;
        }

        // 4. Validate and proceed
        if (!extractedText || extractedText.trim() === "") {
          throw new Error("No text could be extracted from the file.");
        }

        resultBox.textContent = "Analyzing extracted medical data...";
        const vitals = extractVitalsFromText(extractedText);
        performPrediction(vitals);

      } catch (err) {
        console.error("OCR Error:", err);
        resultBox.textContent = "Error processing file: " + (err.message || "Unknown error");
      }
    });
  }

  function extractVitalsFromText(text) {
    const vitals = {
        Age: 50, Sex: "M", ChestPainType: "ATA", 
        RestingBP: 120, Cholesterol: 200, FastingBS: 0, 
        RestingECG: "Normal", MaxHR: 150, ExerciseAngina: "N", 
        Oldpeak: 1.0, ST_Slope: "Up"
    };
    const ageMatch = text.match(/Age[:\s]+(\d+)/i);
    if (ageMatch) vitals.Age = parseInt(ageMatch[1]);
    const sexMatch = text.match(/(?:Sex|Gender)[:\s]+(M|F|Male|Female)/i);
    if (sexMatch) {
        const val = sexMatch[1].toLowerCase();
        vitals.Sex = (val === 'm' || val === 'male') ? 'M' : 'F';
    }
    const bpMatch = text.match(/(?:Resting\s*BP|Blood\s*Pressure)[:\s]+(\d+)/i);
    if (bpMatch) vitals.RestingBP = parseInt(bpMatch[1]);
    const cholMatch = text.match(/Cholesterol[:\s]+(\d+)/i);
    if (cholMatch) vitals.Cholesterol = parseInt(cholMatch[1]);
    const hrMatch = text.match(/(?:Max\s*HR|Heart\s*Rate)[:\s]+(\d+)/i);
    if (hrMatch) vitals.MaxHR = parseInt(hrMatch[1]);
    return vitals;
  }

  // --- 8. QUICK ACTIONS LOGIC ---
  window.triggerRecommendations = function() {
    window.location.hash = "#assistant";
    setTimeout(() => {
      const input = document.getElementById("chat-input-2");
      const form = document.getElementById("chat-form-2");
      if (input && form) {
        input.value = "Based on my latest health data and predictions, what are your top health recommendations for me?";
        form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
      }
    }, 300);
  };

  // --- 9. VOICE & CHAT LOGIC ---
  let activeRecognitions = [];
  function stopAllListening() {
    activeRecognitions.forEach(r => {
      try { r.stop(); } catch(e) {}
    });
  }

  async function handleChatSubmit(e, inputId, winId, btnElement, micBtnElement) {
    if (e && e.preventDefault) e.preventDefault();
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
      thinking.innerHTML = `<span style="color:#f87171;">${errMsg}</span>`;
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

  function setupVoice(micBtnId, inputId, isDirectVoice = false) {
    const micBtn = document.getElementById(micBtnId);
    if (!micBtn) return;
    
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      micBtn.style.display = "none";
      return;
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SR();
    recognition.lang = "en-US";
    recognition.continuous = false; 
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
      if (inputId) document.getElementById(inputId).value = "";
      micBtn.classList.add("listening");
      micBtn.innerHTML = '<i class="fa-solid fa-stop"></i>';
      
      const statusEl = document.getElementById("voice-status");
      if (statusEl) statusEl.textContent = "Listening...";

      try { recognition.start(); } catch(e) { console.error(e); }
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
      if (inputId) {
        document.getElementById(inputId).value = finalTranscript + interimTranscript;
      }
    };

    recognition.onend = () => {
      isListening = false;
      micBtn.classList.remove("listening");
      micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
      
      const statusEl = document.getElementById("voice-status");
      if (statusEl) statusEl.textContent = "Click to talk";

      if (isDirectVoice && finalTranscript.trim() !== "") {
        window.location.hash = "#assistant";
        setTimeout(() => {
          const chatInput = document.getElementById("chat-input-2");
          const chatForm = document.getElementById("chat-form-2");
          if (chatInput && chatForm) {
            chatInput.value = finalTranscript.trim();
            chatForm.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
          }
        }, 300);
      }
    };
    
    recognition.onerror = () => {
      isListening = false;
      micBtn.classList.remove("listening");
      micBtn.innerHTML = '<i class="fa-solid fa-microphone"></i>';
      const statusEl = document.getElementById("voice-status");
      if (statusEl) statusEl.textContent = "Error accessing mic";
    };
  }
  
  setupVoice("mic-btn", "chat-input");
  setupVoice("mic-btn-2", "chat-input-2");
  setupVoice("mic-btn-voice", null, true); 

  // --- 10. ANALYTICS & REPORTS ---
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