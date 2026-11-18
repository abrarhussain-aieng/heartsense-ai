const API = {
  // Helper to get token
  getToken: () => localStorage.getItem("token"),
  setToken: (token) => localStorage.setItem("token", token),
  removeToken: () => localStorage.removeItem("token"),

  // Generic fetch wrapper with Auth Header
  async request(url, options = {}) {
    const token = this.getToken();
    const headers = {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    const res = await fetch(url, { ...options, headers });
    
    if (res.status === 401) {
      this.removeToken();
      window.location.reload(); // Force back to login
      throw new Error("Unauthorized");
    }
    
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Auth endpoints
    async login(username, password) {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const text = await res.text();
      try {
        const data = JSON.parse(text);
        throw new Error(data.detail || "Login failed");
      } catch (e) {
        throw new Error(text || "Server error during login");
      }
    }
    const data = await res.json();
    this.setToken(data.access_token);
    return data;
  },

  async register(username, password) {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const text = await res.text();
      try {
        const data = JSON.parse(text);
        throw new Error(data.detail || "Registration failed");
      } catch (e) {
        throw new Error(text || "Server error during registration");
      }
    }
    return res.json();
  },

  // Existing endpoints using the request wrapper
  async predict(payload) { return this.request("/api/predict", { method: "POST", body: JSON.stringify(payload) }); },
  async analytics() { return this.request("/api/analytics"); },
  async history() { return this.request("/api/history"); },
  
  // --- MODIFIED: Added context parameter ---
  async assistant(question, context = null) { 
    return this.request("/api/assistant", { method: "POST", body: JSON.stringify({ question, context }) }); 
  },
  
  async monitoring() { return this.request("/api/monitoring"); },
};