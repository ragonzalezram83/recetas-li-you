// Comportamiento de cada página de receta: pestañas, ingredientes marcados, visor de imágenes, modo cocina.
(function () {
  const R = JSON.parse(document.getElementById("receta-data").textContent);
  const $ = (id) => document.getElementById(id);

  // Pestañas por hash
  const TABS = ["receta", "cuaderno", "fotos"];
  function show() {
    const t = TABS.includes(location.hash.slice(1)) ? location.hash.slice(1) : "receta";
    TABS.forEach((n) => ($("v-" + n).hidden = n !== t));
    document.querySelectorAll("nav.tabs a").forEach((a) =>
      a.dataset.tab === t ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  }
  window.addEventListener("hashchange", show);
  show();

  // Ingredientes marcados (solo en este móvil)
  const KEY = "ingr-" + R.slug;
  let marked = {};
  try { marked = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
  document.querySelectorAll("#ingr input").forEach((cb) => {
    cb.checked = !!marked[cb.id];
    cb.addEventListener("change", () => {
      marked[cb.id] = cb.checked;
      try { localStorage.setItem(KEY, JSON.stringify(marked)); } catch (e) {}
    });
  });

  // Ampliar imágenes
  const zoom = $("zoom");
  document.addEventListener("click", (e) => {
    const img = e.target.closest("[data-zoom]");
    if (!img) return;
    zoom.querySelector("img").src = img.dataset.full || img.src;
    zoom.querySelector("img").alt = img.alt;
    zoom.hidden = false;
  });
  zoom.addEventListener("click", () => (zoom.hidden = true));

  // Temporizadores: solo los tiempos que aparecen escritos en el paso
  const timers = {};
  let audio = null;
  function beep() {
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      [0, 0.4, 0.8].forEach((d) => {
        const o = audio.createOscillator(), g = audio.createGain();
        o.frequency.value = 880; o.connect(g); g.connect(audio.destination);
        g.gain.setValueAtTime(0.25, audio.currentTime + d);
        o.start(audio.currentTime + d); o.stop(audio.currentTime + d + 0.25);
      });
    } catch (e) {}
    try { navigator.vibrate && navigator.vibrate([300, 150, 300, 150, 300]); } catch (e) {}
  }
  const fmt = (s) => Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
  function paintTimer(btn, key) {
    const t = timers[key];
    if (!t) { btn.className = "timer-btn"; btn.textContent = "⏱ " + btn.dataset.label; return; }
    const left = Math.max(0, Math.round((t.end - Date.now()) / 1000));
    if (left === 0) { btn.className = "timer-btn done"; btn.textContent = "¡Tiempo! " + btn.dataset.label; }
    else { btn.className = "timer-btn running"; btn.textContent = fmt(left) + " · tocar para parar"; }
  }
  setInterval(() => {
    Object.entries(timers).forEach(([key, t]) => {
      if (!t.rang && Date.now() >= t.end) { t.rang = true; beep(); }
    });
    document.querySelectorAll(".timer-btn").forEach((b) => paintTimer(b, b.dataset.key));
  }, 500);

  // Modo cocina
  const cook = $("cook");
  let idx = 0, lock = null;
  async function keepAwake() {
    try { lock = navigator.wakeLock ? await navigator.wakeLock.request("screen") : null; } catch (e) { lock = null; }
  }
  function render() {
    const s = R.steps[idx];
    $("cook-phase").textContent = s.phase || "";
    $("cook-text").innerHTML = s.html;
    const box = $("cook-timers");
    box.innerHTML = "";
    (s.timers || []).forEach((t, k) => {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.key = idx + "-" + k;
      b.dataset.label = t.label;
      b.onclick = () => {
        if (audio === null) { try { audio = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} }
        if (timers[b.dataset.key]) delete timers[b.dataset.key];
        else timers[b.dataset.key] = { end: Date.now() + t.seconds * 1000 };
        paintTimer(b, b.dataset.key);
      };
      box.appendChild(b);
      paintTimer(b, b.dataset.key);
    });
    box.hidden = !(s.timers || []).length;
    $("cook-count").textContent = "Paso " + (idx + 1) + " de " + R.steps.length;
    $("cook-prev").disabled = idx === 0;
    $("cook-next").textContent = idx === R.steps.length - 1 ? "Terminar" : "Siguiente";
    $("cook-bar").style.width = ((idx + 1) / R.steps.length) * 100 + "%";
  }
  function openCook() { idx = 0; cook.hidden = false; document.body.style.overflow = "hidden"; render(); keepAwake(); }
  function closeCook() {
    cook.hidden = true; document.body.style.overflow = "";
    try { lock && lock.release(); } catch (e) {}
    lock = null;
  }
  $("start-cook").onclick = openCook;
  $("cook-close").onclick = closeCook;
  $("cook-prev").onclick = () => { if (idx > 0) { idx--; render(); } };
  $("cook-next").onclick = () => { if (idx < R.steps.length - 1) { idx++; render(); } else closeCook(); };
  document.addEventListener("visibilitychange", () => {
    if (!cook.hidden && document.visibilityState === "visible") keepAwake();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !zoom.hidden) { zoom.hidden = true; return; }
    if (cook.hidden) return;
    if (e.key === "ArrowRight") $("cook-next").click();
    if (e.key === "ArrowLeft") $("cook-prev").click();
    if (e.key === "Escape") closeCook();
  });
})();
