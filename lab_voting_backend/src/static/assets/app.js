const API = "/api";

const state = {
  weeks: [],
  selectedWeekId: null,
  me: null,
};

function $(sel) { return document.querySelector(sel); }

function showMessage(text, type = "info") {
  const box = $("#message");
  box.className = `message ${type}`;
  box.textContent = text;
  box.style.display = "block";
}

function clearMessage() {
  const box = $("#message");
  box.style.display = "none";
  box.textContent = "";
}

function isoWeekIdFromDateInput(dateStr) {
  // dateStr: "YYYY-MM-DD"
  const d = new Date(dateStr + "T00:00:00");
  // ISO week algorithm (simple)
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const dayNum = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
  const year = date.getUTCFullYear();
  return `${year}-W${String(weekNo).padStart(2, "0")}`;
}

async function apiJson(path, options = {}) {
  const res = await fetch(path, { credentials: "include", ...options });
  const contentType = res.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) {
    // normalize
    const msg = data?.message || data || `Request failed (${res.status})`;
    const code = data?.code || "HTTP_ERROR";
    throw { status: res.status, code, message: msg, data };
  }
  return data;
}

async function loadMe() {
  const data = await apiJson(`${API}/me`);
  state.me = data;
}

async function loadWeeks() {
  const res = await apiJson(`${API}/weeks`);
  // if using response wrapper: res.data
  state.weeks = res.data || res;
  renderWeeks();
  updateCreateButtonState();
}

function renderWeeks() {
  const list = $("#weeksList");
  list.innerHTML = "";
  state.weeks.forEach(w => {
    const item = document.createElement("button");
    item.className = "weekItem";
    item.textContent = w.week_id;
    item.onclick = () => selectWeek(w.week_id);
    list.appendChild(item);
  });
}

function findWeek(weekId) {
  return state.weeks.find(w => w.week_id === weekId);
}

function selectWeek(weekId) {
  state.selectedWeekId = weekId;
  $("#selectedWeek").textContent = weekId || "-";
  const w = findWeek(weekId);
  renderPresentations(w?.presentations || []);
}

function renderPresentations(presentations) {
  const box = $("#presentations");
  box.innerHTML = "";
  if (!presentations.length) {
    box.innerHTML = `<div class="muted">No presentations yet.</div>`;
    return;
  }

  presentations.forEach(p => {
    const row = document.createElement("div");
    row.className = "card";
    row.innerHTML = `
      <div class="cardTop">
        <div>
          <div class="title">${escapeHtml(p.title)}</div>
          <div class="sub">Presenter: ${escapeHtml(p.presenter)}</div>
        </div>
        <div class="votes">
          <div class="votesNum">${p.votes}</div>
          <div class="votesLbl">votes</div>
        </div>
      </div>
      <div class="cardActions">
        <button class="btn" data-vote="${p.id}">Vote</button>
      </div>
    `;
    box.appendChild(row);
  });

  box.querySelectorAll("[data-vote]").forEach(btn => {
    btn.onclick = async () => {
      clearMessage();
      try {
        const id = btn.getAttribute("data-vote");
        const res = await apiJson(`${API}/presentations/${id}/vote`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        showMessage(res.message || "Vote recorded", "success");
        await loadWeeks();
        selectWeek(state.selectedWeekId);
      } catch (e) {
        showMessage(e.message || "Vote failed", "error");
      }
    };
  });
}

function updateCreateButtonState() {
  const dateStr = $("#dateInput").value;
  const btn = $("#createWeekBtn");
  if (!dateStr) {
    btn.disabled = true;
    btn.textContent = "Create Week";
    return;
  }
  const weekId = isoWeekIdFromDateInput(dateStr);
  const exists = !!findWeek(weekId);
  btn.disabled = false;
  btn.textContent = exists ? "Go to Week" : "Create Week";
}

async function onCreateWeek() {
  clearMessage();
  const dateStr = $("#dateInput").value;
  if (!dateStr) return;
  const weekId = isoWeekIdFromDateInput(dateStr);

  const exists = findWeek(weekId);
  if (exists) {
    showMessage("Week already exists — opening it.", "info");
    selectWeek(weekId);
    scrollToWeeks();
    return;
  }

  try {
    const res = await apiJson(`${API}/weeks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ week_id: weekId }),
    });
    const created = res.data || res;
    showMessage(res.message || "Week created", "success");
    await loadWeeks();
    selectWeek(created.week_id || weekId);
    scrollToWeeks();
  } catch (e) {
    // if backend returns WEEK_EXISTS with data, navigate
    if (e.code === "WEEK_EXISTS" && e.data?.data?.week_id) {
      showMessage("Week already exists — opening it.", "info");
      await loadWeeks();
      selectWeek(e.data.data.week_id);
      scrollToWeeks();
      return;
    }
    showMessage(e.message || "Failed to create week", "error");
  }
}

function scrollToWeeks() {
  $("#weeksSection").scrollIntoView({ behavior: "smooth", block: "start" });
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function init() {
  $("#dateInput").addEventListener("input", updateCreateButtonState);
  $("#createWeekBtn").addEventListener("click", onCreateWeek);

  await loadMe();
  await loadWeeks();

  // default pick latest
  if (state.weeks.length) {
    selectWeek(state.weeks[0].week_id);
  }

  // Live updates (polling)
  setInterval(async () => {
    const current = state.selectedWeekId;
    await loadWeeks();
    if (current) selectWeek(current);
  }, 5000);
}

document.getElementById("root").innerHTML = `
  <div class="container">
    <h1>Lab Presentation Voting</h1>

    <div id="message" class="message" style="display:none;"></div>

    <section class="panel">
      <div class="row">
        <label class="lbl">Select Date</label>
        <input id="dateInput" type="date" />
        <button id="createWeekBtn" class="btn primary" disabled>Create Week</button>
      </div>
      <div class="muted">Selected Week: <b id="selectedWeek">-</b></div>
    </section>

    <section id="weeksSection" class="panel">
      <h2>Weeks</h2>
      <div id="weeksList" class="weeks"></div>
    </section>

    <section class="panel">
      <h2>Presentations</h2>
      <div id="presentations"></div>
    </section>
  </div>
`;

init().catch(e => {
  console.error(e);
  showMessage("App failed to load. Check console/logs.", "error");
});
