/*!
 * DevClean — UI layer
 * Binds the pure functions in tools.js to the page. Every tool page uses the
 * same markup contract, so this one file drives all of them.
 *
 * Expected markup:
 *   #input        textarea
 *   #output       textarea[readonly]
 *   #process      button
 *   [name="op"]   radio inputs whose value is an operation id
 *   [data-opt]    optional inputs feeding the options object
 */
(function () {
  'use strict';

  /* ------------------------------------------------------------ theme */
  // Applied as early as possible; the inline script in <head> handles the
  // first paint so there is no flash of the wrong theme.
  var THEME_KEY = 'devclean-theme';

  function currentTheme() {
    try {
      var saved = localStorage.getItem(THEME_KEY);
      if (saved) return saved;
    } catch (e) { /* storage blocked — fall through to system preference */ }
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches
      ? 'light' : 'dark';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    var btn = document.querySelector('.theme-toggle');
    if (btn) {
      btn.textContent = theme === 'light' ? '☽' : '☀';
      btn.setAttribute('aria-label',
        theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme');
    }
    try { localStorage.setItem(THEME_KEY, theme); } catch (e) { /* ignore */ }
  }

  function initTheme() {
    applyTheme(currentTheme());
    var btn = document.querySelector('.theme-toggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      applyTheme(document.documentElement.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
    });
  }

  /* --------------------------------------------------------- utilities */
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  function formatNumber(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  /* ------------------------------------------------------------- tool */
  function initTool() {
    var input = $('#input');
    var output = $('#output');
    var processBtn = $('#process');
    if (!input || !output) return;

    var status = $('#status');
    var inputMeta = $('#input-meta');
    var outputMeta = $('#output-meta');
    var copyBtn = $('#copy');
    var clearBtn = $('#clear');
    var downloadBtn = $('#download');
    var sampleBtn = $('#sample');
    var MAX_CHARS = 200000;

    function setStatus(msg, kind) {
      if (!status) return;
      status.textContent = msg || '';
      status.className = 'status' + (kind ? ' is-' + kind : '');
    }

    function selectedOp() {
      var checked = $('[name="op"]:checked');
      if (checked) return checked.value;
      var only = $('[name="op"]');
      return only ? only.value : (document.body.getAttribute('data-default-op') || 'clean_spaces');
    }

    // Collects every [data-opt] control into a plain options object.
    function collectOptions() {
      var opts = {};
      $$('[data-opt]').forEach(function (el) {
        var key = el.getAttribute('data-opt');
        if (el.type === 'checkbox') opts[key] = el.checked;
        else if (el.type === 'number') opts[key] = Number(el.value);
        else opts[key] = el.value;
      });
      return opts;
    }

    function describeInput() {
      if (!inputMeta) return;
      var len = input.value.length;
      var lines = input.value ? input.value.split(/\r\n?|\n/).length : 0;
      inputMeta.textContent = formatNumber(len) + ' characters · ' + formatNumber(lines) + ' lines';
      inputMeta.style.color = len > MAX_CHARS ? 'var(--danger)' : '';
    }

    function describeOutput(before, after) {
      if (!outputMeta) return;
      if (!after) { outputMeta.textContent = ''; return; }
      var saved = before - after.length;
      var pct = before > 0 ? Math.round((saved / before) * 100) : 0;
      outputMeta.textContent = saved > 0
        ? formatNumber(after.length) + ' characters · ' + formatNumber(saved) + ' removed (' + pct + '% smaller)'
        : formatNumber(after.length) + ' characters';
    }

    function process() {
      var text = input.value;
      if (!text.trim()) {
        output.value = '';
        describeOutput(0, '');
        setStatus('Paste some text first.', 'error');
        input.focus();
        return;
      }
      if (text.length > MAX_CHARS) {
        setStatus('Text is too long (' + formatNumber(text.length) + ' / ' +
          formatNumber(MAX_CHARS) + ' characters).', 'error');
        return;
      }
      var started = (window.performance && performance.now) ? performance.now() : Date.now();
      try {
        var result = DevClean.run(selectedOp(), text, collectOptions());
        output.value = result;
        describeOutput(text.length, result);
        var ms = ((window.performance && performance.now) ? performance.now() : Date.now()) - started;
        setStatus('Done in ' + (ms < 1 ? '<1' : Math.round(ms)) + ' ms · processed in your browser', 'ok');
        if (typeof gtag === 'function') {
          gtag('event', 'process_text', { operation: selectedOp() });
        }
      } catch (err) {
        output.value = '';
        describeOutput(0, '');
        setStatus(err && err.message ? err.message : 'Something went wrong.', 'error');
      }
    }

    if (processBtn) processBtn.addEventListener('click', process);

    // Ctrl/Cmd+Enter runs the tool from anywhere in the textarea.
    input.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); process(); }
    });
    input.addEventListener('input', function () {
      describeInput();
      setStatus('');
    });

    // Switching operation re-runs immediately when there is already input:
    // it makes the difference between options obvious without extra clicks.
    $$('[name="op"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        if (input.value.trim()) process();
      });
    });
    $$('[data-opt]').forEach(function (el) {
      el.addEventListener('change', function () {
        if (input.value.trim() && output.value) process();
      });
    });

    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        if (!output.value) { setStatus('Nothing to copy yet.', 'error'); return; }
        var done = function () {
          setStatus('Copied to clipboard.', 'ok');
          copyBtn.textContent = 'Copied';
          setTimeout(function () { copyBtn.textContent = 'Copy'; }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(output.value).then(done, function () {
            output.select(); document.execCommand('copy'); done();
          });
        } else {
          output.select(); document.execCommand('copy'); done();
        }
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        input.value = ''; output.value = '';
        describeInput(); describeOutput(0, '');
        setStatus(''); input.focus();
      });
    }

    if (downloadBtn) {
      downloadBtn.addEventListener('click', function () {
        if (!output.value) { setStatus('Nothing to download yet.', 'error'); return; }
        var op = selectedOp();
        var ext = op.indexOf('json') !== -1 ? 'json' : 'txt';
        var blob = new Blob([output.value], { type: 'text/plain;charset=utf-8' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'devclean-' + op.replace(/_/g, '-') + '.' + ext;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        setStatus('Downloaded.', 'ok');
      });
    }

    if (sampleBtn) {
      sampleBtn.addEventListener('click', function () {
        var sample = sampleBtn.getAttribute('data-sample') || '';
        input.value = sample.replace(/\\n/g, '\n').replace(/\\t/g, '\t');
        describeInput();
        process();
      });
    }

    // Drag a file straight onto the textarea.
    ['dragover', 'drop'].forEach(function (evt) {
      input.addEventListener(evt, function (e) {
        e.preventDefault();
        if (evt !== 'drop') return;
        var file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
        if (!file) return;
        if (file.size > 5 * 1024 * 1024) { setStatus('That file is larger than 5 MB.', 'error'); return; }
        var reader = new FileReader();
        reader.onload = function () {
          input.value = String(reader.result);
          describeInput();
          setStatus('Loaded ' + file.name + '.', 'ok');
        };
        reader.readAsText(file);
      });
    });

    describeInput();
  }

  /* ------------------------------------------------------------- init */
  function init() {
    initTheme();
    initTool();
    // Mark the current page in the nav for accessibility and styling.
    var here = location.pathname.replace(/index\.html$/, '');
    $$('.nav a').forEach(function (a) {
      var target = a.getAttribute('href');
      if (!target || target.charAt(0) === '#') return;
      var resolved = new URL(target, location.href).pathname.replace(/index\.html$/, '');
      if (resolved === here) a.setAttribute('aria-current', 'page');
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
