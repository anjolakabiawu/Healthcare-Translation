"use strict";

/* ─────────────────────────────────────────────────────────────
   Pill-bar tab navigation.
   Switches between the Translate and History panels. The History
   data itself is still loaded/managed by app.js — this only toggles
   which panel is visible.
   ───────────────────────────────────────────────────────────── */

(function () {
  const nav = document.getElementById("appNav");
  if (!nav) return;

  const pills = Array.from(nav.querySelectorAll(".pill"));
  const panels = {
    translate: document.getElementById("tab-translate"),
    history: document.getElementById("tab-history"),
  };

  function activate(tab) {
    pills.forEach((p) => {
      const on = p.dataset.tab === tab;
      p.classList.toggle("active", on);
      if (on) p.setAttribute("aria-current", "page");
      else p.removeAttribute("aria-current");
    });
    Object.entries(panels).forEach(([name, el]) => {
      if (el) el.hidden = name !== tab;
    });
  }

  pills.forEach((pill) => {
    pill.addEventListener("click", () => activate(pill.dataset.tab));
  });

  // default panel
  activate("translate");
})();
