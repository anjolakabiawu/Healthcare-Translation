"use strict";

/* ─────────────────────────────────────────────────────────────
   Waveform visualizer — the signature element.
   Renders a live amber wave from the microphone while recording.
   Respects prefers-reduced-motion (static breathing pulse instead).

   It drives itself off the #recordBtn `.recording` class so app.js
   needs no changes: when the button gains `.recording` we start,
   when it loses it we stop.
   ───────────────────────────────────────────────────────────── */

(function () {
  const canvas = document.getElementById("waveform");
  const stage = document.getElementById("stage");
  const statusText = document.getElementById("stageStatusText");
  const recordBtn = document.getElementById("recordBtn");
  if (!canvas || !stage) return;

  const ctx = canvas.getContext("2d");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Pull theme colours from CSS tokens so the wave always matches the theme.
  const css = getComputedStyle(document.documentElement);
  const ACCENT = (css.getPropertyValue("--accent") || "#e8b84b").trim();
  const ACCENT3 = (css.getPropertyValue("--accent-3") || "#f5cf76").trim();
  const FAINT = (css.getPropertyValue("--faint") || "#586480").trim();

  let audioCtx = null;
  let analyser = null;
  let source = null;
  let stream = null;
  let raf = null;
  let running = false;
  let phase = 0;

  function fit() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(rect.width * dpr));
    canvas.height = Math.max(1, Math.floor(rect.height * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener("resize", fit);

  function clear() {
    const rect = canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
  }

  // Idle baseline — a flat faint line with a soft node in the centre.
  function drawIdle() {
    const { width: w, height: h } = canvas.getBoundingClientRect();
    clear();
    ctx.strokeStyle = FAINT;
    ctx.globalAlpha = 0.5;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, h / 2);
    ctx.lineTo(w, h / 2);
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  // Reduced-motion: a calm breathing pulse instead of a reactive wave.
  function drawReducedPulse() {
    const { width: w, height: h } = canvas.getBoundingClientRect();
    phase += 0.03;
    const amp = (Math.sin(phase) * 0.5 + 0.5) * (h * 0.18) + 4;
    clear();
    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    for (let x = 0; x <= w; x += 4) {
      const env = Math.sin((x / w) * Math.PI);
      const y = h / 2 + Math.sin(x * 0.05) * amp * env * 0.0 + (env * amp * Math.sin(phase));
      x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
    raf = requestAnimationFrame(drawReducedPulse);
  }

  // Live wave from the analyser's time-domain data.
  function drawLive() {
    const { width: w, height: h } = canvas.getBoundingClientRect();
    const buf = new Uint8Array(analyser.fftSize);
    analyser.getByteTimeDomainData(buf);

    clear();

    // soft glow underlay
    ctx.save();
    ctx.shadowColor = ACCENT;
    ctx.shadowBlur = 14;

    const grad = ctx.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, ACCENT);
    grad.addColorStop(0.5, ACCENT3);
    grad.addColorStop(1, ACCENT);

    ctx.strokeStyle = grad;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = "round";
    ctx.beginPath();

    const slice = w / buf.length;
    for (let i = 0; i < buf.length; i++) {
      const v = (buf[i] - 128) / 128;          // -1..1
      const env = Math.sin((i / buf.length) * Math.PI); // taper the ends
      const y = h / 2 + v * (h * 0.42) * env;
      const x = i * slice;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();

    raf = requestAnimationFrame(drawLive);
  }

  async function start() {
    if (running) return;
    running = true;
    stage.classList.add("is-recording");
    if (statusText) statusText.textContent = "Listening…";

    if (reduceMotion) {
      raf = requestAnimationFrame(drawReducedPulse);
      return;
    }

    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.78;
      source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);
      raf = requestAnimationFrame(drawLive);
    } catch (err) {
      // Mic blocked or unavailable — fall back to the synthetic pulse.
      raf = requestAnimationFrame(drawReducedPulse);
    }
  }

  function stop() {
    if (!running) return;
    running = false;
    stage.classList.remove("is-recording");
    if (statusText) statusText.textContent = "Ready to record";

    if (raf) cancelAnimationFrame(raf);
    raf = null;
    phase = 0;

    if (source) { try { source.disconnect(); } catch (e) {} source = null; }
    if (stream) { stream.getTracks().forEach((t) => t.stop()); stream = null; }
    if (audioCtx) { audioCtx.close().catch(() => {}); audioCtx = null; }
    analyser = null;

    fit();
    drawIdle();
  }

  // Observe the record button's `.recording` class — no app.js changes needed.
  if (recordBtn) {
    const obs = new MutationObserver(() => {
      recordBtn.classList.contains("recording") ? start() : stop();
    });
    obs.observe(recordBtn, { attributes: true, attributeFilter: ["class"] });
  }

  // Expose a manual API too, in case it's wanted later.
  window.Waveform = { start, stop };

  // Initial paint.
  fit();
  drawIdle();
})();
