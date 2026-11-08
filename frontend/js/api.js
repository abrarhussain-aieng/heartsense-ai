const API = {
  async predict(payload) {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async analytics() {
    const res = await fetch("/api/analytics");
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async history() {
    const res = await fetch("/api/history");
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async assistant(question) {
    const res = await fetch("/api/assistant", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  async monitoring() {
    const res = await fetch("/api/monitoring");
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
};