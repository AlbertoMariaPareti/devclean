/*!
 * DevClean — text processing engine
 * ---------------------------------
 * Every operation is a pure function: (text, options) -> string
 * Nothing here touches the DOM and nothing here makes network requests,
 * so the exact same file can be reused in a Node script or a service worker.
 *
 * This is what makes DevClean work with no backend: the text never leaves
 * the browser.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.DevClean = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  /* ---------------------------------------------------------------------
   * Helpers
   * ------------------------------------------------------------------ */

  // Normalises CRLF / CR line endings so every operation sees plain \n.
  function splitLines(text) {
    return String(text).replace(/\r\n?/g, '\n').split('\n');
  }

  function joinLines(lines) {
    return lines.join('\n');
  }

  // Splits an identifier-ish string into lowercase words, handling
  // camelCase, snake_case, kebab-case and plain spaced text alike.
  function toWords(str) {
    return String(str)
      .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
      .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
      .split(/[^A-Za-z0-9]+/)
      .filter(Boolean)
      .map(function (w) { return w.toLowerCase(); });
  }

  // Applies a transformation line by line, preserving the line structure.
  function perLine(text, fn) {
    return joinLines(splitLines(text).map(fn));
  }

  /* ---------------------------------------------------------------------
   * Whitespace
   * ------------------------------------------------------------------ */

  function cleanSpaces(text, opts) {
    opts = opts || {};
    var keepIndent = opts.keepIndent !== false; // default: preserve indentation
    var lines = splitLines(text).map(function (line) {
      var indent = '';
      if (keepIndent) {
        var m = line.match(/^[ \t]*/);
        indent = m ? m[0] : '';
      }
      var body = line.slice(indent.length)
        .replace(/[ \t]+/g, ' ')   // collapse runs of spaces/tabs
        .replace(/[ \t]+$/, '');   // strip trailing whitespace
      return indent + body;
    });
    // Drop empty lines entirely. No document-level .trim() here: that would
    // eat the indentation of the very first line, which defeats keepIndent.
    return joinLines(lines.filter(function (l) { return l.trim() !== ''; }));
  }

  // Removes blank lines from the start and end of a document without
  // touching the indentation of the first surviving line.
  function trimBlankEdges(lines) {
    var start = 0, end = lines.length;
    while (start < end && lines[start].trim() === '') start++;
    while (end > start && lines[end - 1].trim() === '') end--;
    return lines.slice(start, end);
  }

  function trimLines(text) {
    return perLine(text, function (l) { return l.trim(); });
  }

  function collapseBlankLines(text) {
    // Many consecutive blank lines become exactly one blank line.
    var collapsed = splitLines(text).reduce(function (acc, line) {
      var blank = line.trim() === '';
      if (blank && acc.length && acc[acc.length - 1].trim() === '') return acc;
      acc.push(blank ? '' : line.replace(/[ \t]+$/, ''));
      return acc;
    }, []);
    return joinLines(trimBlankEdges(collapsed));
  }

  function removeAllBlankLines(text) {
    return joinLines(splitLines(text).filter(function (l) { return l.trim() !== ''; }));
  }

  /* ---------------------------------------------------------------------
   * Duplicates
   * ------------------------------------------------------------------ */

  function removeDuplicates(text, opts) {
    opts = opts || {};
    var seen = Object.create(null);
    var out = [];
    splitLines(text).forEach(function (line) {
      var key = line;
      if (opts.ignoreCase) key = key.toLowerCase();
      if (opts.ignoreWhitespace) key = key.trim();
      // Object.create(null) has no prototype, so no __proto__ collisions.
      if (seen[key]) return;
      seen[key] = true;
      out.push(line);
    });
    return joinLines(out);
  }

  function keepOnlyDuplicates(text, opts) {
    opts = opts || {};
    var counts = Object.create(null);
    var lines = splitLines(text);
    var norm = function (l) {
      var k = l;
      if (opts.ignoreCase) k = k.toLowerCase();
      if (opts.ignoreWhitespace) k = k.trim();
      return k;
    };
    lines.forEach(function (l) {
      var k = norm(l);
      counts[k] = (counts[k] || 0) + 1;
    });
    var emitted = Object.create(null);
    return joinLines(lines.filter(function (l) {
      var k = norm(l);
      if (counts[k] > 1 && !emitted[k]) { emitted[k] = true; return true; }
      return false;
    }));
  }

  function removeUniqueLines(text, opts) {
    // Alias kept explicit for clarity in the UI: "show me what repeats"
    return keepOnlyDuplicates(text, opts);
  }

  /* ---------------------------------------------------------------------
   * JSON / structure
   * ------------------------------------------------------------------ */

  function toJsonArray(text, opts) {
    opts = opts || {};
    var items = splitLines(text)
      .map(function (l) { return l.trim(); })
      .filter(function (l) { return l !== ''; });
    if (opts.numeric) {
      items = items.map(function (v) {
        var n = Number(v);
        return (v !== '' && isFinite(n)) ? n : v;
      });
    }
    return JSON.stringify(items, null, opts.compact ? 0 : 2);
  }

  function toJsonObject(text) {
    // "key,value" or "key: value" per line -> JSON object
    var obj = {};
    splitLines(text).forEach(function (line) {
      if (!line.trim()) return;
      var m = line.match(/^\s*([^,:]+)\s*[,:]\s*(.*)$/);
      if (m) obj[m[1].trim()] = m[2].trim();
      else obj[line.trim()] = '';
    });
    return JSON.stringify(obj, null, 2);
  }

  function csvToJson(text, opts) {
    opts = opts || {};
    var delimiter = opts.delimiter || ',';
    var rows = splitLines(text).filter(function (l) { return l.trim() !== ''; });
    if (!rows.length) return '[]';
    var headers = splitCsvRow(rows[0], delimiter);
    var out = rows.slice(1).map(function (row) {
      var cells = splitCsvRow(row, delimiter);
      var obj = {};
      headers.forEach(function (h, i) { obj[h] = cells[i] !== undefined ? cells[i] : ''; });
      return obj;
    });
    return JSON.stringify(out, null, 2);
  }

  // Minimal RFC-4180-ish splitter: handles quoted cells and escaped quotes.
  function splitCsvRow(row, delimiter) {
    var out = [], cur = '', inQuotes = false;
    for (var i = 0; i < row.length; i++) {
      var ch = row[i];
      if (inQuotes) {
        if (ch === '"' && row[i + 1] === '"') { cur += '"'; i++; }
        else if (ch === '"') { inQuotes = false; }
        else { cur += ch; }
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === delimiter) {
        out.push(cur.trim()); cur = '';
      } else {
        cur += ch;
      }
    }
    out.push(cur.trim());
    return out;
  }

  /* ---------------------------------------------------------------------
   * Case conversion
   * ------------------------------------------------------------------ */

  var caseOps = {
    upper: function (t) { return String(t).toUpperCase(); },
    lower: function (t) { return String(t).toLowerCase(); },
    title: function (t) {
      return String(t).replace(/\w\S*/g, function (w) {
        return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
      });
    },
    sentence: function (t) {
      return perLine(t, function (line) {
        var lower = line.toLowerCase();
        return lower.replace(/(^\s*\w)|([.!?]\s+\w)/g, function (m) { return m.toUpperCase(); });
      });
    },
    camel: function (t) {
      return perLine(t, function (line) {
        var w = toWords(line);
        if (!w.length) return line;
        return w[0] + w.slice(1).map(function (x) {
          return x.charAt(0).toUpperCase() + x.slice(1);
        }).join('');
      });
    },
    pascal: function (t) {
      return perLine(t, function (line) {
        var w = toWords(line);
        if (!w.length) return line;
        return w.map(function (x) { return x.charAt(0).toUpperCase() + x.slice(1); }).join('');
      });
    },
    snake: function (t) {
      return perLine(t, function (line) {
        var w = toWords(line);
        return w.length ? w.join('_') : line;
      });
    },
    kebab: function (t) {
      return perLine(t, function (line) {
        var w = toWords(line);
        return w.length ? w.join('-') : line;
      });
    },
    constant: function (t) {
      return perLine(t, function (line) {
        var w = toWords(line);
        return w.length ? w.join('_').toUpperCase() : line;
      });
    }
  };

  /* ---------------------------------------------------------------------
   * Sorting and line order
   * ------------------------------------------------------------------ */

  function sortLines(text, opts) {
    opts = opts || {};
    var lines = splitLines(text);
    var trailingNewline = lines.length > 1 && lines[lines.length - 1] === '';
    if (trailingNewline) lines.pop();

    var mode = opts.mode || 'asc';
    var collator = typeof Intl !== 'undefined' && Intl.Collator
      ? new Intl.Collator(undefined, { numeric: true, sensitivity: 'base' })
      : null;
    var cmp = function (a, b) {
      if (collator) return collator.compare(a, b);
      return a < b ? -1 : a > b ? 1 : 0;
    };

    if (mode === 'asc') lines.sort(cmp);
    else if (mode === 'desc') lines.sort(function (a, b) { return cmp(b, a); });
    else if (mode === 'length') lines.sort(function (a, b) { return a.length - b.length || cmp(a, b); });
    else if (mode === 'length_desc') lines.sort(function (a, b) { return b.length - a.length || cmp(a, b); });
    else if (mode === 'reverse') lines.reverse();
    else if (mode === 'shuffle') {
      for (var i = lines.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = lines[i]; lines[i] = lines[j]; lines[j] = tmp;
      }
    }
    if (trailingNewline) lines.push('');
    return joinLines(lines);
  }

  function numberLines(text, opts) {
    opts = opts || {};
    var start = opts.start === undefined ? 1 : Number(opts.start);
    var sep = opts.separator === undefined ? '. ' : opts.separator;
    var lines = splitLines(text);
    var width = String(start + lines.length - 1).length;
    return joinLines(lines.map(function (line, i) {
      var n = String(start + i);
      if (opts.pad) while (n.length < width) n = '0' + n;
      return n + sep + line;
    }));
  }

  function addPrefixSuffix(text, opts) {
    opts = opts || {};
    var pre = opts.prefix || '';
    var suf = opts.suffix || '';
    var skipEmpty = opts.skipEmpty !== false;
    return perLine(text, function (line) {
      if (skipEmpty && line.trim() === '') return line;
      return pre + line + suf;
    });
  }

  /* ---------------------------------------------------------------------
   * Tabs and spaces
   * ------------------------------------------------------------------ */

  function tabsToSpaces(text, opts) {
    opts = opts || {};
    var size = Number(opts.tabSize) || 4;
    // Expand tabs to the next tab stop rather than blindly substituting,
    // so mixed tab/space indentation still lines up.
    return perLine(text, function (line) {
      var out = '';
      for (var i = 0; i < line.length; i++) {
        if (line[i] === '\t') {
          var next = size - (out.length % size);
          out += new Array(next + 1).join(' ');
        } else {
          out += line[i];
        }
      }
      return out;
    });
  }

  function spacesToTabs(text, opts) {
    opts = opts || {};
    var size = Number(opts.tabSize) || 4;
    var re = new RegExp(' {' + size + '}', 'g');
    return perLine(text, function (line) {
      var m = line.match(/^[ \t]*/);
      var indent = m ? m[0] : '';
      return indent.replace(re, '\t') + line.slice(indent.length);
    });
  }

  /* ---------------------------------------------------------------------
   * Encoding
   * ------------------------------------------------------------------ */

  function base64Encode(text) {
    var str = String(text);
    if (typeof TextEncoder !== 'undefined' && typeof btoa !== 'undefined') {
      var bytes = new TextEncoder().encode(str);
      var bin = '';
      for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
      return btoa(bin);
    }
    // Node fallback
    return Buffer.from(str, 'utf8').toString('base64');
  }

  function base64Decode(text) {
    var str = String(text).trim().replace(/\s+/g, '');
    if (!str) return '';
    try {
      if (typeof TextDecoder !== 'undefined' && typeof atob !== 'undefined') {
        var bin = atob(str);
        var bytes = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return new TextDecoder().decode(bytes);
      }
      return Buffer.from(str, 'base64').toString('utf8');
    } catch (e) {
      throw new Error('That does not look like valid Base64. Check for missing characters or padding.');
    }
  }

  function urlEncode(text, opts) {
    opts = opts || {};
    return opts.component === false
      ? encodeURI(String(text))
      : encodeURIComponent(String(text));
  }

  function urlDecode(text, opts) {
    opts = opts || {};
    try {
      return opts.component === false
        ? decodeURI(String(text))
        : decodeURIComponent(String(text).replace(/\+/g, ' '));
    } catch (e) {
      throw new Error('That string contains an invalid percent-encoding sequence.');
    }
  }

  var HTML_ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, function (c) { return HTML_ESCAPES[c]; });
  }

  function unescapeHtml(text) {
    return String(text)
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&nbsp;/g, ' ')
      .replace(/&amp;/g, '&');
  }

  /* ---------------------------------------------------------------------
   * HTML stripping
   * ------------------------------------------------------------------ */

  function stripHtml(text, opts) {
    opts = opts || {};
    var src = String(text);
    // DOMParser does not execute scripts and does not load resources,
    // so this is safe for untrusted input — and far more accurate than regex.
    if (typeof DOMParser !== 'undefined') {
      var doc = new DOMParser().parseFromString(src, 'text/html');
      doc.querySelectorAll('script, style, noscript').forEach(function (n) { n.remove(); });
      // Turn block-level tags into line breaks so structure survives.
      doc.querySelectorAll('br').forEach(function (n) { n.replaceWith('\n'); });
      doc.querySelectorAll('p, div, li, tr, h1, h2, h3, h4, h5, h6').forEach(function (n) {
        n.appendChild(doc.createTextNode('\n'));
      });
      var out = doc.body ? doc.body.textContent : '';
      out = unescapeHtml(out);
      return opts.collapse === false ? out.trim() : collapseBlankLines(out);
    }
    var stripped = src
      .replace(/<(script|style)[\s\S]*?<\/\1>/gi, '')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/<\/(p|div|li|tr|h[1-6])>/gi, '\n')
      .replace(/<[^>]+>/g, '');
    return collapseBlankLines(unescapeHtml(stripped));
  }

  /* ---------------------------------------------------------------------
   * Statistics
   * ------------------------------------------------------------------ */

  function stats(text) {
    var src = String(text);
    var lines = splitLines(src);
    var words = src.trim() ? src.trim().split(/\s+/).filter(Boolean) : [];
    var sentences = src.trim() ? src.split(/[.!?]+(?=\s|$)/).filter(function (s) { return s.trim(); }) : [];
    var paragraphs = src.trim() ? src.split(/\n\s*\n/).filter(function (p) { return p.trim(); }) : [];
    var uniqueWords = Object.create(null);
    words.forEach(function (w) {
      var k = w.toLowerCase().replace(/[^\w'-]/g, '');
      if (k) uniqueWords[k] = (uniqueWords[k] || 0) + 1;
    });
    var longest = words.reduce(function (a, b) { return b.length > a.length ? b : a; }, '');
    return {
      characters: src.length,
      charactersNoSpaces: src.replace(/\s/g, '').length,
      words: words.length,
      uniqueWords: Object.keys(uniqueWords).length,
      lines: lines.length,
      nonEmptyLines: lines.filter(function (l) { return l.trim() !== ''; }).length,
      sentences: sentences.length,
      paragraphs: paragraphs.length,
      longestWord: longest,
      averageWordLength: words.length
        ? Math.round((words.join('').length / words.length) * 10) / 10
        : 0,
      // 225 wpm is the commonly cited average adult silent reading speed.
      readingTimeMinutes: Math.max(1, Math.round(words.length / 225)),
      speakingTimeMinutes: Math.max(1, Math.round(words.length / 130))
    };
  }

  function formatStats(text) {
    var s = stats(text);
    var rows = [
      ['Characters', s.characters],
      ['Characters (no spaces)', s.charactersNoSpaces],
      ['Words', s.words],
      ['Unique words', s.uniqueWords],
      ['Lines', s.lines],
      ['Non-empty lines', s.nonEmptyLines],
      ['Sentences', s.sentences],
      ['Paragraphs', s.paragraphs],
      ['Average word length', s.averageWordLength],
      ['Longest word', s.longestWord || '—'],
      ['Reading time', '~' + s.readingTimeMinutes + ' min'],
      ['Speaking time', '~' + s.speakingTimeMinutes + ' min']
    ];
    var width = rows.reduce(function (m, r) { return Math.max(m, r[0].length); }, 0);
    return rows.map(function (r) {
      var label = r[0];
      while (label.length < width) label += ' ';
      return label + '  ' + r[1];
    }).join('\n');
  }

  /* ---------------------------------------------------------------------
   * Extraction
   * ------------------------------------------------------------------ */

  var EMAIL_RE = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g;
  var URL_RE = /\bhttps?:\/\/[^\s<>"')\]]+/gi;
  var NUMBER_RE = /-?\d+(?:[.,]\d+)?/g;

  function extract(text, opts) {
    opts = opts || {};
    var re = opts.what === 'urls' ? URL_RE
      : opts.what === 'numbers' ? NUMBER_RE
        : EMAIL_RE;
    var found = String(text).match(re) || [];
    if (opts.unique !== false) {
      var seen = Object.create(null);
      found = found.filter(function (v) {
        var k = v.toLowerCase();
        if (seen[k]) return false;
        seen[k] = true;
        return true;
      });
    }
    return found.join('\n');
  }

  /* ---------------------------------------------------------------------
   * Operation registry — this is what the UI binds to.
   * ------------------------------------------------------------------ */

  var operations = {
    // whitespace
    clean_spaces:          function (t, o) { return cleanSpaces(t, o); },
    trim_lines:            function (t) { return trimLines(t); },
    collapse_blank_lines:  function (t) { return collapseBlankLines(t); },
    remove_blank_lines:    function (t) { return removeAllBlankLines(t); },
    // duplicates
    remove_duplicates:     function (t, o) { return removeDuplicates(t, o); },
    keep_duplicates:       function (t, o) { return keepOnlyDuplicates(t, o); },
    remove_unique:         function (t, o) { return removeUniqueLines(t, o); },
    // json
    to_json_array:         function (t, o) { return toJsonArray(t, o); },
    to_json_object:        function (t) { return toJsonObject(t); },
    csv_to_json:           function (t, o) { return csvToJson(t, o); },
    // case
    upper_case:            caseOps.upper,
    lower_case:            caseOps.lower,
    title_case:            caseOps.title,
    sentence_case:         caseOps.sentence,
    camel_case:            caseOps.camel,
    pascal_case:           caseOps.pascal,
    snake_case:            caseOps.snake,
    kebab_case:            caseOps.kebab,
    constant_case:         caseOps.constant,
    // order
    sort_asc:              function (t) { return sortLines(t, { mode: 'asc' }); },
    sort_desc:             function (t) { return sortLines(t, { mode: 'desc' }); },
    sort_length:           function (t) { return sortLines(t, { mode: 'length' }); },
    sort_length_desc:      function (t) { return sortLines(t, { mode: 'length_desc' }); },
    reverse_lines:         function (t) { return sortLines(t, { mode: 'reverse' }); },
    shuffle_lines:         function (t) { return sortLines(t, { mode: 'shuffle' }); },
    number_lines:          function (t, o) { return numberLines(t, o); },
    add_prefix_suffix:     function (t, o) { return addPrefixSuffix(t, o); },
    // indentation
    tabs_to_spaces:        function (t, o) { return tabsToSpaces(t, o); },
    spaces_to_tabs:        function (t, o) { return spacesToTabs(t, o); },
    // encoding
    base64_encode:         function (t) { return base64Encode(t); },
    base64_decode:         function (t) { return base64Decode(t); },
    url_encode:            function (t, o) { return urlEncode(t, o); },
    url_decode:            function (t, o) { return urlDecode(t, o); },
    html_escape:           function (t) { return escapeHtml(t); },
    html_unescape:         function (t) { return unescapeHtml(t); },
    // html
    strip_html:            function (t, o) { return stripHtml(t, o); },
    // analysis
    text_stats:            function (t) { return formatStats(t); },
    extract_emails:        function (t, o) { return extract(t, Object.assign({}, o, { what: 'emails' })); },
    extract_urls:          function (t, o) { return extract(t, Object.assign({}, o, { what: 'urls' })); },
    extract_numbers:       function (t, o) { return extract(t, Object.assign({}, o, { what: 'numbers' })); }
  };

  // Legacy aliases so the original API option names keep working.
  operations.to_json_keys = operations.to_json_array;

  function run(operation, text, options) {
    var fn = operations[operation];
    if (typeof fn !== 'function') {
      throw new Error('Unknown operation: ' + operation);
    }
    return fn(String(text == null ? '' : text), options || {});
  }

  return {
    run: run,
    operations: operations,
    stats: stats,
    formatStats: formatStats,
    // exported individually for reuse / testing
    cleanSpaces: cleanSpaces,
    removeDuplicates: removeDuplicates,
    toJsonArray: toJsonArray,
    csvToJson: csvToJson,
    sortLines: sortLines,
    tabsToSpaces: tabsToSpaces,
    spacesToTabs: spacesToTabs,
    base64Encode: base64Encode,
    base64Decode: base64Decode,
    stripHtml: stripHtml,
    escapeHtml: escapeHtml,
    unescapeHtml: unescapeHtml
  };
});
