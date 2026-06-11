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

// ── Recording (MediaRecorder → faster-whisper backend) ────────
// We capture mic audio with MediaRecorder, watch the audio level to
// auto-stop after a stretch of silence, then POST the clip to
// /api/transcribe (faster-whisper) for far better medical-term accuracy
// than the browser's built-in recognizer.

// Stop automatically after this much continuous silence (your 5–10s ask).
const SILENCE_MS = 8000;
// Below this normalized RMS level counts as "silence".
const SILENCE_THRESHOLD = 0.012;

recordBtn.addEventListener("click", () => {
  if (!AppState.isRecording) {
    startRecording();
  } else {
    stopRecording();
  }
});

async function startRecording() {
  if (!navigator.mediaDevices || !window.MediaRecorder) {
    showToast("Audio recording isn't supported in this browser. Please use Chrome or Edge.", "error");
    return;
  }

  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch (err) {
    showToast("Microphone access denied. Please allow microphone access.", "error");
    return;
  }

  // Pick a mime type the browser actually supports (ffmpeg decodes both).
  const mime = MediaRecorder.isTypeSupported("audio/webm")
    ? "audio/webm"
    : (MediaRecorder.isTypeSupported("audio/ogg") ? "audio/ogg" : "");
  const recorder = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
  const chunks = [];
  let spoke = false;       // did we ever detect real speech?
  let silenceTimer = null;
  let rafId = null;

  // ── silence detection via Web Audio ──
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  audioCtx.createMediaStreamSource(stream).connect(analyser);
  const buf = new Float32Array(analyser.fftSize);

  function armSilenceStop() {
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(() => { if (spoke) stopRecording(); }, SILENCE_MS);
  }

  function monitor() {
    analyser.getFloatTimeDomainData(buf);
    let sum = 0;
    for (let i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
    const rms = Math.sqrt(sum / buf.length);
    if (rms > SILENCE_THRESHOLD) {
      spoke = true;
      armSilenceStop();          // reset the countdown whenever we hear speech
    }
    rafId = requestAnimationFrame(monitor);
  }

  recorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };

  recorder.onstart = () => {
    AppState.isRecording = true;
    recordBtn.classList.add("recording");   // also drives the waveform via observer
    recordBtn.setAttribute("aria-pressed", "true");
    recordLabel.textContent = "Stop";
    setStageStatus("Listening…");
    armSilenceStop();
    monitor();
  };

  recorder.onstop = async () => {
    cancelAnimationFrame(rafId);
    clearTimeout(silenceTimer);
    stream.getTracks().forEach((t) => t.stop());
    audioCtx.close().catch(() => {});
    _resetRecordBtn();

    const blob = new Blob(chunks, { type: mime || "audio/webm" });
    if (!spoke || blob.size < 1200) {
      showToast("No speech detected. Please try again.", "info");
      setStageStatus("Ready to record");
      return;
    }
    await transcribeBlob(blob);
  };

  AppState.recorder = recorder;
  recorder.start();
}

function stopRecording() {
  if (AppState.recorder && AppState.recorder.state !== "inactive") {
    AppState.recorder.stop();
  }
}

async function transcribeBlob(blob) {
  setStageStatus("Transcribing…");
  setLoading(true, "Transcribing…");
  try {
    const res = await fetch("/api/transcribe", {
      method: "POST",
      headers: { "Content-Type": blob.type || "audio/webm" },
      body: blob,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Transcription failed");

    const text = (data.text || "").trim();
    if (!text) {
      showToast("Couldn't make out any speech. Please try again.", "info");
    } else {
      // Append to whatever is already in the box.
      const base = inputText.value.trimEnd();
      inputText.value = (base ? base + " " : "") + text;
      charCount.textContent = `${inputText.value.length} / 2000`;
    }
  } catch (err) {
    showToast("Transcription error: " + err.message, "error");
  } finally {
    setLoading(false);
    setStageStatus("Ready to record");
  }
}

function setStageStatus(msg) {
  const el = document.getElementById("stageStatusText");
  if (el) el.textContent = msg;
}

function _resetRecordBtn() {
  AppState.isRecording = false;
  AppState.recorder = null;
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
