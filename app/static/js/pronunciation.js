"use strict";

/* ─────────────────────────────────────────────────────────────
   Pronunciation tooltip (Feature 2 frontend).

   Any element with `.rx-term` and a `data-pron` JSON payload gets a
   hover/focus tooltip showing: term, IPA, simplified guide, stress
   pattern dots, and a "Hear it" button that speaks the simplified
   pronunciation via the browser's SpeechSynthesis.

   Event-delegated, so it works for terms injected after page load
   (e.g. the annotated translation output).
   ───────────────────────────────────────────────────────────── */

(function () {
  let tip = null;
  let hideTimer = null;

  function ensureTip() {
    if (tip) return tip;
    tip = document.createElement("div");
    tip.className = "pron-tooltip";
    tip.setAttribute("role", "tooltip");
    document.body.appendChild(tip);

    // keep tooltip open while the pointer is over it (so the button is usable)
    tip.addEventListener("mouseenter", () => clearTimeout(hideTimer));
    tip.addEventListener("mouseleave", scheduleHide);
    return tip;
  }

  function parsePayload(el) {
    try {
      return JSON.parse(el.getAttribute("data-pron"));
    } catch {
      return null;
    }
  }

  function stressDots(syllables, stress) {
    const set = new Set(stress || []);
    return (syllables || [])
      .map((_, i) => `<span class="syl-dot${set.has(i + 1) ? " stressed" : ""}"></span>`)
      .join("");
  }

  function render(p) {
    const t = ensureTip();
    t.innerHTML = `
      <div class="pron-term">${escapeHtml(p.term || "")}</div>
      ${p.ipa ? `<div class="pron-ipa">${escapeHtml(p.ipa)}</div>` : ""}
      ${p.simplified ? `<div class="pron-simplified">${escapeHtml(p.simplified)}</div>` : ""}
      ${(p.syllables && p.syllables.length)
        ? `<div class="pron-stress" aria-hidden="true">${stressDots(p.syllables, p.stress)}</div>`
        : ""}
      <button class="pron-hear" type="button" aria-label="Hear pronunciation">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
        Hear it
      </button>`;
    t.querySelector(".pron-hear").addEventListener("click", (e) => {
      e.stopPropagation();
      speak(p);
    });
  }

  function speak(p) {
    if (!("speechSynthesis" in window)) return;
    // Speak the actual word so the TTS engine pronounces it naturally — NOT
    // the dashed guide ("ay-TOR-va...") which makes it read syllable-by-syllable.
    const phrase = (p.term || p.simplified || "").replace(/-/g, "");
    const utt = new SpeechSynthesisUtterance(phrase);
    utt.lang = "en-US";
    utt.rate = 0.8;   // slightly slow for clarity on long medical words
    speechSynthesis.cancel();
    speechSynthesis.speak(utt);
  }

  function position(el) {
    const t = ensureTip();
    const r = el.getBoundingClientRect();
    const tr = t.getBoundingClientRect();
    let left = r.left + r.width / 2 - tr.width / 2;
    let top = r.top - tr.height - 8;

    // clamp horizontally
    left = Math.max(8, Math.min(left, window.innerWidth - tr.width - 8));
    // flip below if no room above
    if (top < 8) top = r.bottom + 8;

    t.style.left = `${left}px`;
    t.style.top = `${top}px`;
  }

  function show(el) {
    const p = parsePayload(el);
    if (!p) return;
    clearTimeout(hideTimer);
    render(p);
    const t = ensureTip();
    // position needs the rendered size, so show invisibly first
    t.classList.add("show");
    position(el);
  }

  function scheduleHide() {
    hideTimer = setTimeout(() => {
      if (tip) tip.classList.remove("show");
    }, 140);
  }

  // event delegation on the document
  document.addEventListener("mouseover", (e) => {
    const el = e.target.closest(".rx-term");
    if (el) show(el);
  });
  document.addEventListener("mouseout", (e) => {
    if (e.target.closest(".rx-term")) scheduleHide();
  });
  document.addEventListener("focusin", (e) => {
    const el = e.target.closest(".rx-term");
    if (el) show(el);
  });
  document.addEventListener("focusout", (e) => {
    if (e.target.closest(".rx-term")) scheduleHide();
  });
  // keyboard: Enter/Space on a focused term speaks it
  document.addEventListener("keydown", (e) => {
    const el = e.target.closest && e.target.closest(".rx-term");
    if (el && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      const p = parsePayload(el);
      if (p) speak(p);
    }
  });

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // expose for app.js to render server-provided annotated HTML
  window.Pronunciation = { speak };
})();
