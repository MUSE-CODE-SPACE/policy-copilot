// Front-end chat logic. Talks to POST /api/chat, which streams Server-Sent Events:
//   event: sources -> the handbook chunks we retrieved (shown as pills)
//   event: token   -> one piece of the answer text (appended live)
//   event: done / error
// No framework — this is deliberately small so the mechanics stay visible.

const thread = document.getElementById("thread");
const welcome = document.getElementById("welcome");
const form = document.getElementById("composer");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const history = []; // [{role, content}] kept for follow-up questions

// --- health check -> status dot ---
fetch("/api/health").then(r => r.json()).then(d => {
  const s = document.getElementById("status");
  const t = document.getElementById("status-text");
  if (d.ok) { s.classList.add("ok"); t.textContent = `${d.chunks} passages · ${d.model}`; }
  else { t.textContent = "index not ready"; }
}).catch(() => { document.getElementById("status-text").textContent = "offline"; });

// --- textarea auto-grow ---
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 180) + "px";
});
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); }
});

// --- suggestion chips ---
document.querySelectorAll(".chip").forEach(c =>
  c.addEventListener("click", () => { input.value = c.textContent; form.requestSubmit(); })
);

function addRow(role) {
  if (welcome) welcome.remove();
  const row = document.createElement("div");
  row.className = "msg-row";
  row.innerHTML = `
    <div class="avatar ${role === "user" ? "user" : "bot"}">${role === "user" ? "🧑" : "📘"}</div>
    <div class="bubble">
      <div class="role">${role === "user" ? "You" : "Policy Copilot"}</div>
      <div class="sources"></div>
      <div class="content"></div>
    </div>`;
  thread.appendChild(row);
  thread.scrollTop = thread.scrollHeight;
  return row;
}

// Turn [handbook.pdf] citations and **bold** into styled HTML (minimal, safe-ish).
function render(text) {
  const esc = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return esc
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\[([\w.\- ]+?\.pdf)\]/g, '<span class="cite">$1</span>')
    .replace(/\n/g, "<br>");
}

async function ask(question) {
  addRow("user").querySelector(".content").textContent = question;
  history.push({ role: "user", content: question });

  const botRow = addRow("bot");
  const sourcesEl = botRow.querySelector(".sources");
  const contentEl = botRow.querySelector(".content");
  contentEl.innerHTML = '<span class="cursor"></span>';

  setBusy(true);
  let answer = "";
  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, history: history.slice(0, -1) }),
    });
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const events = buf.split("\n\n");
      buf = events.pop();
      for (const block of events) {
        const ev = /event: (.+)/.exec(block)?.[1];
        const data = /data: (.+)/.exec(block)?.[1];
        if (!ev || !data) continue;
        const payload = JSON.parse(data);
        if (ev === "sources") renderSources(sourcesEl, payload.sources);
        else if (ev === "token") { answer += payload.text; contentEl.innerHTML = render(answer) + '<span class="cursor"></span>'; thread.scrollTop = thread.scrollHeight; }
        else if (ev === "error") { answer += `\n⚠️ ${payload.message}`; contentEl.innerHTML = render(answer); }
      }
    }
  } catch (err) {
    contentEl.innerHTML = render("⚠️ Connection error: " + err.message);
  }
  contentEl.innerHTML = render(answer || "No answer.");
  history.push({ role: "assistant", content: answer });
  setBusy(false);
}

function renderSources(el, sources) {
  if (!sources || !sources.length) {
    el.innerHTML = '<span class="source-pill">no matching passage — I\'ll say I don\'t know</span>';
    return;
  }
  el.innerHTML = sources.map(s =>
    `<span class="source-pill">📄 <b>${s.source}</b> <span class="sc">${s.score}</span></span>`
  ).join("");
}

function setBusy(b) {
  sendBtn.disabled = b;
  input.disabled = b;
  if (!b) input.focus();
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  input.style.height = "auto";
  ask(q);
});
