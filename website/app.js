/* ─── Configuration ────────────────────────────────────────── */
const API = (typeof __API_BASE__ !== "undefined") ? __API_BASE__ : "http://localhost:8000";

// ─── State ───────────────────────────────────────────────────
const state = {
  currentQuestion: null,
  history: [],
  scores: [],
  stats: { attempted: 0, avgScore: 0, best: 0 },
  userId: localStorage.getItem("userId") || "guest",
};

// ─── DOM Helpers ─────────────────────────────────────────────
const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

function toast(msg, type = "info") {
  const c = document.getElementById("toast-container");
  const t = document.createElement("div");
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity = "0"; t.style.transition = "opacity .3s"; setTimeout(() => t.remove(), 300); }, 3000);
}

function show(id) { $$(".page").forEach((p) => p.classList.remove("active")); document.getElementById(id).classList.add("active"); }
function $$show(id) { document.getElementById(id).classList.add("visible"); }
function $$hide(id) { document.getElementById(id).classList.remove("visible"); }

function navigate(page) {
  $$(".nav-btn").forEach((b) => b.classList.remove("active"));
  document.querySelector(`.nav-btn[data-page="${page}"]`)?.classList.add("active");
  if (page === "dashboard") show("page-dashboard");
  else if (page === "questions") { show("page-questions"); loadQuestions(); }
  else if (page === "history") { show("page-history"); renderHistory(); }
}

// ─── API Helpers ─────────────────────────────────────────────
async function apiGet(path) {
  try {
    const r = await fetch(`${API}${path}`, { signal: AbortSignal.timeout(15000) });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    toast(`API error: ${e.message}`, "error");
    return null;
  }
}

async function apiPost(path, body) {
  try {
    const r = await fetch(`${API}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30000),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    toast(`API error: ${e.message}`, "error");
    return null;
  }
}

// ─── Question Id Helper ──────────────────────────────────────
function qid(q) { return q.id || q._id || ""; }

// ─── Badge HTML ──────────────────────────────────────────────
function badgeHTML(q) {
  const diff = (q.difficulty || "").toLowerCase();
  const topic = (q.topic || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  return `
    <span class="badge badge-${diff}">${diff}</span>
    <span class="badge badge-topic">${topic}</span>
  `;
}

// ─── Score Class ─────────────────────────────────────────────
function scoreClass(s) { if (s >= 70) return "score-high"; if (s >= 40) return "score-mid"; return "score-low"; }

// ─── Dashboard ───────────────────────────────────────────────
function renderDashboard() {
  const h = state.history;
  const attempted = h.length;
  const scores = h.map((x) => x.score || 0);
  const avg = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
  const best = scores.length ? Math.max(...scores) : 0;

  state.stats = { attempted, avgScore: avg, best };
  document.getElementById("stat-attempted").textContent = attempted;
  document.getElementById("stat-avg").textContent = avg;
  document.getElementById("dash-attempted").textContent = attempted;
  document.getElementById("dash-avg").textContent = avg;
  document.getElementById("dash-best").textContent = best;

  // Weakest topic
  const topicScores = {};
  h.forEach((x) => {
    const t = x.topic || "unknown";
    if (!topicScores[t]) topicScores[t] = [];
    topicScores[t].push(x.score || 0);
  });
  const topicAvgs = Object.entries(topicScores).map(([t, sc]) => [t, sc.reduce((a, b) => a + b, 0) / sc.length]);
  const weakest = topicAvgs.length ? topicAvgs.sort((a, b) => a[1] - b[1])[0] : null;
  document.getElementById("dash-weakest").innerHTML = weakest
    ? `${weakest[1].toFixed(0)}<br><span style="font-size:0.65rem;color:var(--danger);">${weakest[0].replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</span>`
    : "\u2014";

  // Chart
  const chart = document.getElementById("topic-chart");
  if (!topicAvgs.length) {
    chart.innerHTML = '<p class="text-muted">Complete some questions to see your chart.</p>';
    return;
  }
  const maxVal = Math.max(...topicAvgs.map((t) => t[1]));
  let html = '<div class="chart-bar-group">';
  topicAvgs.sort((a, b) => b[1] - a[1]).forEach(([t, v]) => {
    const pct = maxVal > 0 ? (v / maxVal) * 100 : 0;
    const label = t.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
    html += `<div class="chart-bar-wrap"><div class="chart-val">${v.toFixed(0)}</div><div class="chart-bar" style="height:${pct}%"></div><div class="chart-label">${label}</div></div>`;
  });
  html += "</div>";
  chart.innerHTML = html;
}

// ─── Questions Page ──────────────────────────────────────────
async function loadQuestions() {
  const topic = document.getElementById("filter-topic").value;
  const diff = document.getElementById("filter-difficulty").value;
  const list = document.getElementById("questions-list");
  const loading = document.getElementById("questions-loading");
  loading.style.display = "block";
  list.innerHTML = "";

  let url = "/questions/";
  const params = [];
  if (topic) params.push(`topic=${topic}`);
  if (diff) params.push(`difficulty=${diff}`);
  if (params.length) url += "?" + params.join("&");

  const data = await apiGet(url);
  loading.style.display = "none";
  if (!data || !data.length) { list.innerHTML = '<div class="empty-state"><p>No questions found for this selection.</p></div>'; return; }

  list.innerHTML = data.map((q) => `
    <div class="q-card" onclick="openQuestion('${qid(q)}')">
      <div class="q-card-title">${q.title || "Untitled"}</div>
      <div class="q-card-meta">${badgeHTML(q)}</div>
      <div class="q-card-desc">${(q.description || "").substring(0, 120)}...</div>
    </div>
  `).join("");
}

async function openQuestion(id) {
  const q = await apiGet(`/questions/${id}`);
  if (!q) return;
  state.currentQuestion = q;
  show("page-question");
  document.getElementById("q-title").textContent = q.title || "Untitled";
  document.getElementById("q-badges").innerHTML = badgeHTML(q);
  document.getElementById("q-description").innerHTML = `<h3>Description</h3><p>${q.description || ""}</p>`;
  const ex = document.getElementById("q-example");
  if (q.example_input || q.example_output) {
    let html = "<h3>Example</h3>";
    if (q.example_input) html += `<p><strong>Input:</strong> ${q.example_input}</p>`;
    if (q.example_output) html += `<p><strong>Output:</strong> ${q.example_output}</p>`;
    ex.innerHTML = html;
    ex.style.display = "block";
  } else { ex.style.display = "none"; }
  const con = document.getElementById("q-constraints");
  if (q.constraints) { con.innerHTML = `<h3>Constraints</h3><p>${q.constraints}</p>`; con.style.display = "block"; }
  else { con.style.display = "none"; }
  document.getElementById("code-editor").value = "";
  $$hide("hint-output");
  $$hide("solution-output");
  $$hide("feedback-output");
}

function quickStart(topic) {
  document.getElementById("filter-topic").value = topic;
  document.getElementById("filter-difficulty").value = "";
  navigate("questions");
}

// ─── Hints, Feedback, Solutions ──────────────────────────────
async function getHint() {
  const q = state.currentQuestion;
  if (!q) return;
  const code = document.getElementById("code-editor").value.trim() || null;
  const data = await apiPost(`/questions/${qid(q)}/hint`, { question_id: qid(q), user_code: code });
  if (data) {
    const el = document.getElementById("hint-output");
    el.innerHTML = `<h3>💡 Hint</h3><p>${data.hint || "No hint returned."}</p>`;
    $$show("hint-output");
  }
}

function selectedLang() {
  const el = document.getElementById("lang-select");
  return el ? el.value : "python";
}

async function getSolution() {
  const q = state.currentQuestion;
  if (!q) return;
  const lang = selectedLang();
  const data = await apiPost(`/questions/${qid(q)}/solution`, { question_id: qid(q), language: lang });
  if (data) {
    const el = document.getElementById("solution-output");
    el.className = "card output-card solution-card visible";
    el.innerHTML = `<h3>📖 Model Solution</h3><pre>${data.solution_code || "No solution returned."}</pre>`;
  }
}

async function saveSession(questionId, topic, score) {
  await apiPost(
    `/history/${state.userId}?topic=${encodeURIComponent(topic)}&question_id=${encodeURIComponent(questionId)}&score=${score}`,
    {}
  );
}

async function loadHistory() {
  const data = await apiGet(`/history/${state.userId}`);
  if (data && data.length) {
    state.history = data.map((s) => ({
      question: s.question_id || "",
      score: s.score || 0,
      topic: s.topic || "unknown",
      timestamp: s.timestamp ? new Date(s.timestamp).toLocaleString() : "",
    }));
    state.scores = state.history.map((h) => h.score);
    renderDashboard();
  }
}

async function submitFeedback() {
  const q = state.currentQuestion;
  if (!q) return;
  const code = document.getElementById("code-editor").value.trim();
  if (!code) { toast("Please write some code before submitting.", "error"); return; }
  const lang = selectedLang();
  const data = await apiPost("/feedback/", { question_id: qid(q), user_code: code, language: lang });
  if (data) {
    let score = 0;
    const fb = data.feedback || "";
    fb.split("\n").forEach((line) => {
      if (line.toLowerCase().includes("rating") && line.includes("10")) {
        const digits = line.match(/\d+/g);
        if (digits) score = parseInt(digits[0], 10) * 10;
      }
    });
    state.history.push({ question: qid(q), score, topic: q.topic || "unknown", timestamp: new Date().toLocaleString() });
    state.scores.push(score);
    renderDashboard();
    await saveSession(qid(q), q.topic || "unknown", score);
    const el = document.getElementById("feedback-output");
    el.className = "card output-card feedback-card visible";
    el.innerHTML = `<h3>✅ Feedback</h3><p>${fb.replace(/\n/g, "<br>")}</p>`;
    $$show("feedback-output");
    toast("Feedback received!", "success");
  }
}

// ─── History ─────────────────────────────────────────────────
function renderHistory() {
  const content = document.getElementById("history-content");
  if (!state.history.length) {
    content.innerHTML = '<p class="text-muted">No history yet. Complete some questions to see your progress.</p>';
    return;
  }
  let html = '<table class="history-table"><thead><tr><th>Question</th><th>Topic</th><th>Score</th><th>Date</th></tr></thead><tbody>';
  [...state.history].reverse().forEach((h) => {
    const sc = h.score || 0;
    html += `<tr><td>${h.question.substring(0, 30)}</td><td>${(h.topic || "").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}</td><td class="${scoreClass(sc)}">${sc}</td><td style="color:var(--text-muted);font-size:0.8rem;">${h.timestamp}</td></tr>`;
  });
  html += "</tbody></table>";
  content.innerHTML = html;
}

// ─── Init ────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  await loadHistory();
  renderDashboard();
  navigate("dashboard");
});
