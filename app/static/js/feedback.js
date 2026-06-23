"use strict";

/* ─────────────────────────────────────────────────────────────
   Feature 4 (corrections) + Feature 5 (OOV log) frontend.

   - Click a flagged word in the confidence transcript to correct it.
     The correction is stored server-side and the word turns green.
   - The header badge shows the total corrections stored.
   - The OOV tab lists out-of-vocabulary terms flagged this session,
     with a CSV export of corrections.
   ───────────────────────────────────────────────────────────── */

(function () {
  const countEl = document.getElementById("correctionCount");
  const statEl = document.getElementById("correctionStat");

  function escapeHtml(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function toast(msg, type) {
    if (window.showToast) window.showToast(msg, type);
  }

  // ── correction count badge ──
  function setCount(n) {
    if (countEl) countEl.textContent = n;
  }

  async function refreshCount() {
    try {
      const res = await fetch("/api/feedback/corrections");
      const data = await res.json();
      if (data.success) setCount(data.data.count);
    } catch { /* ignore */ }
  }

  // ── inline correction editing ──
  // Delegated: clicking a .conf-word turns it into an input.
  document.addEventListener("click", (e) => {
    const word = e.target.closest(".conf-word");
    if (!word || word.querySelector("input") || word.classList.contains("corrected")) return;
    beginEdit(word);
  });

  function beginEdit(word) {
    const original = word.textContent;
    const input = document.createElement("input");
    input.type = "text";
    input.className = "conf-edit";
    input.value = original;
    input.setAttribute("aria-label", "Correct term");
    // size the field to its content so longer corrections fit
    input.size = Math.max(original.length + 2, 6);
    word.textContent = "";
    word.appendChild(input);
    input.focus();
    input.select();

    // Guard so Enter + the resulting blur don't both run finish().
    let done = false;
    function finish(commit) {
      if (done) return;
      done = true;
      const corrected = input.value.trim();
      if (commit && corrected && corrected !== original) {
        saveCorrection(word, original, corrected);
      } else {
        word.textContent = original;   // revert
      }
    }
    input.addEventListener("keydown", (ev) => {
      ev.stopPropagation();
      if (ev.key === "Enter") { ev.preventDefault(); finish(true); }
      else if (ev.key === "Escape") { ev.preventDefault(); finish(false); }
    });
    input.addEventListener("blur", () => finish(true));
  }

  async function saveCorrection(word, original, corrected) {
    word.textContent = corrected;
    word.classList.remove("uncertain", "high-risk");
    word.classList.add("corrected");
    word.title = `Corrected from “${original}”`;

    const src = document.getElementById("sourceLang");
    const tgt = document.getElementById("targetLang");
    try {
      const res = await fetch("/api/feedback/correction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_term: original,
          corrected_term: corrected,
          context_phrase: document.getElementById("confidenceTranscript")?.textContent || "",
          source_language: src ? src.value : "",
          target_language: tgt ? tgt.value : "",
        }),
      });
      const data = await res.json();
      if (data.success) {
        setCount(data.data.count);
        toast("Correction saved.", "success");
      } else {
        toast(data.error || "Could not save correction.", "error");
      }
    } catch (err) {
      toast("Could not save correction.", "error");
    }
  }

  // ── CSV export (click the header corrections chip) ──
  if (statEl) {
    statEl.style.cursor = "pointer";
    statEl.title = "Click to export corrections as CSV";
    statEl.addEventListener("click", () => {
      window.location.href = "/api/feedback/corrections/export";
    });
  }

  // ── OOV log ──
  const oovList = document.getElementById("oovList");
  const oovStats = document.getElementById("oovStats");
  const oovBadge = document.getElementById("oovBadge");

  function renderOOV(log, stats) {
    if (oovBadge) {
      oovBadge.hidden = !log.length;
      oovBadge.textContent = log.length;
    }
    if (oovStats) {
      oovStats.textContent = log.length
        ? `${stats.total} flagged · ${Object.entries(stats.by_category).map(([k, v]) => `${v} ${k.replace("_", " ")}`).join(", ")}`
        : "No terms flagged this session.";
    }
    if (!oovList) return;
    oovList.innerHTML = log.length
      ? log.slice().reverse().map((r) => `
          <div class="oov-item oov-${escapeHtml(r.category)}">
            <div class="oov-term">${escapeHtml(r.term)}</div>
            <div class="oov-meta">
              <span class="oov-cat">${escapeHtml(r.category.replace("_", " "))}</span>
              <span class="oov-conf">${Math.round((r.confidence || 0) * 100)}%</span>
            </div>
            <div class="oov-signals">${(r.signals || []).map((s) => `<span class="oov-sig">${escapeHtml(s.replace(/_/g, " "))}</span>`).join("")}</div>
          </div>`).join("")
      : `<p class="history-empty">Out-of-vocabulary terms from your transcripts appear here.</p>`;
  }

  async function refreshOOV() {
    try {
      const [logRes, statsRes] = await Promise.all([
        fetch("/api/oov/log"), fetch("/api/oov/stats"),
      ]);
      const logData = await logRes.json();
      const statsData = await statsRes.json();
      if (logData.success && statsData.success) {
        renderOOV(logData.data.log, statsData.data);
      }
    } catch { /* ignore */ }
  }

  // Called by app.js after each transcription, and by nav.js on tab open.
  window.OOV = { refresh: refreshOOV, render: renderOOV };
  window.Feedback = { refreshCount, setCount };

  // initial load
  refreshCount();
})();
