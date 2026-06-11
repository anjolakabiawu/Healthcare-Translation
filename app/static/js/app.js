"use strict";

const AppState = {
  isRecording: false,
  recognition: null,
  currentTranslation: "",
  selectedSourceLang: "en",
  selectedTargetLang: "es",
};

// ── DOM refs ──────────────────────────────────────────────────
const inputText    = document.getElementById("inputText");
const charCount    = document.getElementById("charCount");
const sourceLang   = document.getElementById("sourceLang");
const targetLang   = document.getElementById("targetLang");
const swapLangs    = document.getElementById("swapLangs");
const recordBtn    = document.getElementById("recordBtn");
const recordLabel  = document.getElementById("recordLabel");
const translateBtn = document.getElementById("translateBtn");
const loadingBar   = document.getElementById("loadingBar");
const loadingText  = document.getElementById("loadingText");
const outputCard   = document.getElementById("outputCard");
const originalOut  = document.getElementById("originalOutput");
const translatedOut= document.getElementById("translatedOutput");
const speakBtn     = document.getElementById("speakBtn");
const copyBtn      = document.getElementById("copyBtn");
const clearHistBtn = document.getElementById("clearHistoryBtn");
const historyGrid  = document.getElementById("historyGrid");
const historyEmpty = document.getElementById("historyEmpty");
const themeToggle  = document.getElementById("themeToggle");
const iconSun      = document.getElementById("iconSun");
const iconMoon     = document.getElementById("iconMoon");
const toastCont    = document.getElementById("toastContainer");

// ── Theme ─────────────────────────────────────────────────────
function applyTheme(theme) {
  document.body.setAttribute("data-theme", theme);
  iconSun.style.display  = theme === "light" ? "" : "none";
  iconMoon.style.display = theme === "dark"  ? "" : "none";
  localStorage.setItem("theme", theme);
}

themeToggle.addEventListener("click", () => {
  const next = document.body.getAttribute("data-theme") === "light" ? "dark" : "light";
  applyTheme(next);
});

applyTheme(localStorage.getItem("theme") || "dark");

// ── Character counter ─────────────────────────────────────────
inputText.addEventListener("input", () => {
  charCount.textContent = `${inputText.value.length} / 2000`;
});

// ── Language swap ─────────────────────────────────────────────
swapLangs.addEventListener("click", () => {
  const s = sourceLang.value;
  const t = targetLang.value;
  sourceLang.value = t;
  targetLang.value = s;
});

// ── Toast ─────────────────────────────────────────────────────
function showToast(message, type = "info", duration = 4000) {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  toastCont.appendChild(el);
  setTimeout(() => el.remove(), duration);
}

// ── Loading state ─────────────────────────────────────────────
function setLoading(active, message = "Processing…") {
  loadingBar.style.display = active ? "flex" : "none";
  loadingBar.setAttribute("aria-busy", String(active));
  loadingText.textContent = message;
  translateBtn.disabled = active;
}

// ── Recording (Web Speech API) ────────────────────────────────
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

recordBtn.addEventListener("click", () => {
  if (!AppState.isRecording) {
    startRecording();
  } else {
    stopRecording();
  }
});

// Medical terms to bias the recognizer toward correct spellings
const MEDICAL_HINTS = [
  "CT scan", "MRI", "ECG", "hypertension", "myocardial infarction",
  "tachycardia", "diagnosis", "prescription", "dosage", "symptom",
  "fracture", "infection", "inflammation", "anesthesia", "antibiotic",
  "blood pressure", "complete blood count", "fever", "nausea", "allergy",
  "emergency", "surgery", "vaccine", "chronic", "acute",
];

function startRecording() {
  if (!SpeechRecognition) {
    showToast("Speech recognition is not supported in this browser. Please use Chrome or Edge.", "error");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = sourceLang.value;
  recognition.continuous = false;   // stop automatically after the speaker pauses
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;

  // Provide medical term hints if the API supports it
  if (window.SpeechGrammarList) {
    const grammar = `#JSGF V1.0; grammar medical; public <term> = ${MEDICAL_HINTS.join(" | ")} ;`;
    const list = new window.SpeechGrammarList();
    list.addFromString(grammar, 1);
    recognition.grammars = list;
  }

  const baseText = inputText.value.trimEnd();
  let finalTranscript = baseText ? baseText + " " : "";
  let silenceTimer = null;

  function resetSilenceTimer() {
    clearTimeout(silenceTimer);
    // Auto-stop after 2.5 s of silence so stray corrections aren't captured
    silenceTimer = setTimeout(() => recognition.stop(), 2500);
  }

  recognition.onstart = () => {
    AppState.isRecording = true;
    recordBtn.classList.add("recording");
    recordBtn.setAttribute("aria-pressed", "true");
    recordLabel.textContent = "Stop";
    resetSilenceTimer();
  };

  recognition.onresult = (e) => {
    resetSilenceTimer();
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) {
        finalTranscript += t.trimEnd() + " ";
      } else {
        interim += t;
      }
    }
    inputText.value = finalTranscript + interim;
    charCount.textContent = `${inputText.value.length} / 2000`;
  };

  recognition.onerror = (e) => {
    clearTimeout(silenceTimer);
    if (e.error === "not-allowed") {
      showToast("Microphone access denied. Please allow microphone access in your browser.", "error");
    } else if (e.error === "no-speech") {
      showToast("No speech detected. Please try again.", "info");
    } else if (e.error !== "aborted") {
      showToast("Speech recognition error: " + e.error, "error");
    }
    _resetRecordBtn();
  };

  recognition.onend = () => {
    clearTimeout(silenceTimer);
    inputText.value = inputText.value.trimEnd();
    charCount.textContent = `${inputText.value.length} / 2000`;
    _resetRecordBtn();
  };

  AppState.recognition = recognition;
  recognition.start();
}

function stopRecording() {
  AppState.recognition?.stop();
}

function _resetRecordBtn() {
  AppState.isRecording = false;
  AppState.recognition = null;
  recordBtn.classList.remove("recording");
  recordBtn.setAttribute("aria-pressed", "false");
  recordLabel.textContent = "Record";
}

// ── Translation ───────────────────────────────────────────────
translateBtn.addEventListener("click", doTranslate);

async function doTranslate() {
  const text = inputText.value.trim();
  if (!text) {
    showToast("Please enter text to translate.", "error");
    return;
  }
  if (sourceLang.value === targetLang.value) {
    showToast("Source and target languages must be different.", "error");
    return;
  }

  setLoading(true, "Translating…");

  try {
    const res = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source_lang: sourceLang.value,
        target_lang: targetLang.value,
      }),
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Translation failed");

    AppState.currentTranslation = data.translated_text;

    // Prefer the IPA-annotated original (tooltip-ready) when the server
    // supplied it; otherwise fall back to glossary highlighting.
    originalOut.innerHTML  = data.annotated_original || data.highlighted_original || escapeHtml(data.original_text);
    translatedOut.innerHTML= data.highlighted_translated || escapeHtml(data.translated_text);

    outputCard.style.display = "";
    outputCard.scrollIntoView({ behavior: "smooth", block: "nearest" });

    addHistoryCard(data);
  } catch (err) {
    showToast("Translation error: " + err.message, "error");
  } finally {
    setLoading(false);
  }
}

// ── Speak ─────────────────────────────────────────────────────
speakBtn.addEventListener("click", () => {
  if (!AppState.currentTranslation) return;
  const utt = new SpeechSynthesisUtterance(AppState.currentTranslation);
  utt.lang = targetLang.value;
  speechSynthesis.cancel();
  speechSynthesis.speak(utt);
});

// ── Copy ──────────────────────────────────────────────────────
copyBtn.addEventListener("click", () => {
  if (!AppState.currentTranslation) return;
  navigator.clipboard.writeText(AppState.currentTranslation)
    .then(() => showToast("Translation copied to clipboard.", "success"))
    .catch(() => showToast("Could not copy text.", "error"));
});

// ── History ───────────────────────────────────────────────────
function addHistoryCard(entry) {
  historyEmpty.style.display = "none";

  const card = document.createElement("div");
  card.className = "history-card-item";

  const time = new Date(entry.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const date = new Date(entry.timestamp).toLocaleDateString([], { month: "short", day: "numeric" });

  card.innerHTML = `
    <div class="history-langs">
      ${escapeHtml(entry.source_lang.toUpperCase())}
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
      ${escapeHtml(entry.target_lang.toUpperCase())}
    </div>
    <div class="history-original">${escapeHtml(entry.original_text)}</div>
    <div class="history-translated">${escapeHtml(entry.translated_text)}</div>
    <div class="history-footer">
      <span class="history-time">${date} ${time}</span>
      <button class="history-copy" title="Copy translation" aria-label="Copy translation">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
      </button>
    </div>
  `;

  card.querySelector(".history-copy").addEventListener("click", () => {
    navigator.clipboard.writeText(entry.translated_text)
      .then(() => showToast("Copied.", "success"))
      .catch(() => showToast("Could not copy.", "error"));
  });

  historyGrid.prepend(card);
}

clearHistBtn.addEventListener("click", async () => {
  try {
    await fetch("/api/history", { method: "DELETE" });
    const cards = historyGrid.querySelectorAll(".history-card-item");
    cards.forEach(c => c.remove());
    historyEmpty.style.display = "";
    showToast("History cleared.", "info");
  } catch {
    showToast("Could not clear history.", "error");
  }
});

// Load history on page load
(async () => {
  try {
    const res = await fetch("/api/history");
    if (!res.ok) return;
    const history = await res.json();
    if (Array.isArray(history) && history.length > 0) {
      history.forEach(addHistoryCard);
    }
  } catch {
    // silently ignore
  }
})();

// ── Helpers ───────────────────────────────────────────────────
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
