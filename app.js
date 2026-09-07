/* ============================================================
   LooksTest — лендинг. Скриптов минимум: демо-разбор в герое
   и подсветка шапки при прокрутке.
   ============================================================ */
(function () {
  'use strict';

  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ----------------------------------------------------------
     Демо-разбор.
     Состояние читаем из классов на элементе, а не из переменной:
     иначе оно расходится с DOM, если анимация оборвётся.
     ---------------------------------------------------------- */
  function initScan() {
    var box = document.getElementById('heroScan');
    if (!box) return;

    var btn = box.querySelector('.scan__run');
    var rows = [].slice.call(box.querySelectorAll('.scan__row'));
    var score = box.querySelector('[data-role="score"]');
    if (!btn || !rows.length || !score) return;

    var RUN = reduced ? 0 : 1900;
    var timer = null;

    function state() {
      return box.classList.contains('is-running') ? 'running'
           : box.classList.contains('is-done') ? 'done' : 'idle';
    }

    // средний балл из метрик, чтобы цифра не расходилась с полосами
    var target = rows.reduce(function (s, r) {
      return s + (parseInt(r.getAttribute('data-val'), 10) || 0);
    }, 0) / rows.length / 10;

    function fill() {
      rows.forEach(function (r) {
        var v = parseInt(r.getAttribute('data-val'), 10) || 0;
        r.querySelector('.scan__fill').style.width = v + '%';
        r.querySelector('.scan__val').textContent = v;
      });
    }

    function clear() {
      rows.forEach(function (r) {
        r.querySelector('.scan__fill').style.width = '0';
        r.querySelector('.scan__val').textContent = '0';
      });
      score.textContent = '0.0';
    }

    // счётчик балла: короткий, чтобы догонял полосы, а не отставал
    function countUp() {
      if (reduced) { score.textContent = target.toFixed(1); return; }
      var t0 = null;
      var DUR = 1100;
      function step(ts) {
        if (t0 === null) t0 = ts;
        var p = Math.min((ts - t0) / DUR, 1);
        score.textContent = (target * (1 - Math.pow(1 - p, 3))).toFixed(1);
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    function run() {
      clearTimeout(timer);
      box.classList.remove('is-done');
      box.classList.add('is-running');
      btn.textContent = 'Идёт разбор…';
      btn.disabled = true;
      fill();
      countUp();
      timer = setTimeout(function () {
        box.classList.remove('is-running');
        box.classList.add('is-done');
        btn.textContent = 'Показать снова';
        btn.disabled = false;
      }, RUN);
    }

    function reset() {
      clearTimeout(timer);
      box.classList.remove('is-done', 'is-running');
      clear();
      btn.textContent = 'Запустить разбор';
    }

    btn.addEventListener('click', function () {
      if (state() === 'done') { reset(); setTimeout(run, 160); return; }
      if (state() === 'running') return;
      run();
    });

    clear();
  }

  /* ----------------------------------------------------------
     Шапка: тень появляется, когда страница ушла вверх
     ---------------------------------------------------------- */
  function initNav() {
    var nav = document.querySelector('.nav');
    if (!nav) return;
    var ticking = false;
    function upd() {
      nav.classList.toggle('is-stuck', window.scrollY > 12);
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(upd); }
    }, { passive: true });
    upd();
  }

  function boot() { initScan(); initNav(); }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
