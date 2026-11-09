(function () {
  'use strict';
  // Perfil → temas que se priorizan (orientación por palabras clave, no elegibilidad).
  var PERFILES = {
    autonomo: ['Empresas y empleo', 'Vivienda y fachadas', 'Agro, pesca y animales'],
    pyme: ['Empresas y empleo', 'Agro, pesca y animales'],
    emprendedor: ['Empresas y empleo'],
    entidad: ['Cultura y festejos', 'Deporte', 'Social y salud', 'Otros'],
    familia: ['Educación y becas', 'Social y salud', 'Vivienda y fachadas', 'Deporte']
  };
  var COLOR = {
    'Agro, pesca y animales': '#16a34a', 'Educación y becas': '#2563eb', 'Social y salud': '#e11d48',
    'Cultura y festejos': '#a855f7', 'Deporte': '#f59e0b', 'Empresas y empleo': '#0891b2',
    'Vivienda y fachadas': '#ea580c', 'Otros': '#64748b'
  };
  var AMBITOS = { LOCAL: 'Local', AUTONOMICA: 'Autonómico', ESTADO: 'Estatal', OTROS: 'Otros' };
  var COL_AMB = { LOCAL: '#00e08a', AUTONOMICA: '#3b82f6', ESTADO: '#f59e0b', OTROS: '#94a3b8' };
  var PAGINA = 24;

  var $ = function (id) { return document.getElementById(id); };
  var datos = [], temaSel = '', orgSel = '', visibles = PAGINA, ultima = '', hayViejas = false;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function plano(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function fecha(f) { var p = (f || '').split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : ''; }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function color(t) { return COLOR[t] || '#64748b'; }

  function filtradas() {
    var q = plano($('q').value).trim(), am = $('ambito').value, pf = PERFILES[$('perfil').value];
    return datos.filter(function (c) {
      if (am && c.ambito !== am) return false;
      if (temaSel && c.tema !== temaSel) return false;
      if (orgSel && c.organismo !== orgSel) return false;
      if (pf && !temaSel && pf.indexOf(c.tema) < 0) return false;
      if (q && plano(c.descripcion + ' ' + c.organismo).indexOf(q) < 0) return false;
      return true;
    });
  }

  function cuenta(lista, campo) {
    var m = {}; lista.forEach(function (c) { m[c[campo]] = (m[c[campo]] || 0) + 1; });
    return Object.keys(m).map(function (k) { return [k, m[k]]; }).sort(function (a, b) { return b[1] - a[1]; });
  }

  function barras(cont, filas, col, activo, onclick) {
    cont.textContent = '';
    var max = filas.length ? filas[0][1] : 1, pend = [];
    filas.forEach(function (f) {
      var b = el('button', 'bar-row'); b.type = 'button'; b.style.setProperty('--c', col(f[0]));
      b.setAttribute('aria-pressed', String(activo === f[0])); b.title = f[0] + ': ' + f[1];
      b.appendChild(el('span', 'n', f[0]));
      var t = el('span', 't'), i = el('i'); t.appendChild(i); b.appendChild(t);
      b.appendChild(el('span', 'v', String(f[1])));
      b.onclick = function () { onclick(activo === f[0] ? '' : f[0]); };
      cont.appendChild(b);
      pend.push([i, Math.max(4, Math.round(100 * f[1] / max)) + '%']);
    });
    pend.forEach(function (p) { if (reduce) p[0].style.width = p[1]; else requestAnimationFrame(function () { requestAnimationFrame(function () { p[0].style.width = p[1]; }); }); });
  }

  function paneles() {
    barras($('gtemas'), cuenta(datos, 'tema'), color, temaSel, function (v) { temaSel = v; visibles = PAGINA; render(); });
    var orgs = cuenta(datos, 'organismo').slice(0, 7);
    barras($('gorg'), orgs, function () { return '#00b36b'; }, orgSel, function (v) { orgSel = v; visibles = PAGINA; render(); });
    var g = $('gambito'); g.textContent = '';
    var am = cuenta(datos, 'ambito'), tot = datos.length || 1;
    var st = el('div', 'stack'), lg = el('div', 'leg');
    am.forEach(function (a) {
      var seg = el('i'); seg.style.width = (100 * a[1] / tot) + '%'; seg.style.background = COL_AMB[a[0]] || '#94a3b8';
      seg.title = (AMBITOS[a[0]] || a[0]) + ': ' + a[1]; st.appendChild(seg);
      var l = el('span', '', (AMBITOS[a[0]] || a[0]) + ' · ' + a[1]); l.style.setProperty('--c', COL_AMB[a[0]] || '#94a3b8'); lg.appendChild(l);
    });
    g.appendChild(st); g.appendChild(lg);
  }

  function chipsFiltro() {
    var c = $('filtrando'); c.textContent = '';
    var act = [];
    if (temaSel) act.push([temaSel, function () { temaSel = ''; }]);
    if (orgSel) act.push([orgSel, function () { orgSel = ''; }]);
    c.hidden = !act.length;
    if (!act.length) return;
    c.appendChild(el('span', '', 'Filtrando por:'));
    act.forEach(function (a) {
      var b = el('button', 'fchip', a[0] + '  ✕'); b.type = 'button';
      b.onclick = function () { a[1](); visibles = PAGINA; render(); }; c.appendChild(b);
    });
  }

  function render() {
    var r = filtradas(), lista = $('lista');
    paneles(); chipsFiltro();
    lista.textContent = '';
    r.slice(0, visibles).forEach(function (c) {
      var li = el('li', 'card'), meta = el('div', 'meta');
      li.style.setProperty('--c', color(c.tema));
      meta.appendChild(el('span', 'pill', c.tema));
      if (hayViejas && c.fecha === ultima) meta.appendChild(el('span', 'nueva', 'NUEVA'));
      meta.appendChild(el('span', '', (AMBITOS[c.ambito] || c.ambito) + ' · ' + fecha(c.fecha)));
      li.appendChild(meta);
      li.appendChild(el('h3', '', c.descripcion || '(sin descripción)'));
      li.appendChild(el('div', 'meta org', c.organismo));
      var a = el('a', 'go', 'Ver convocatoria oficial en BDNS ↗');
      a.href = c.url; a.target = '_blank'; a.rel = 'noopener';
      li.appendChild(a);
      lista.appendChild(li);
    });
    $('cuenta').textContent = r.length + ' de ' + datos.length + ' convocatorias';
    $('vacio').hidden = r.length > 0;
    $('mas').hidden = r.length <= visibles;
  }

  function contar(nodo, fin) {
    if (reduce || fin < 2) { nodo.textContent = fin; return; }
    var t0 = performance.now(), dur = 900;
    (function paso(t) {
      var p = Math.min(1, (t - t0) / dur); nodo.textContent = Math.round(fin * (1 - Math.pow(1 - p, 3)));
      if (p < 1) requestAnimationFrame(paso);
    })(t0);
  }

  function kpis() {
    var k = $('kpis'); k.textContent = '';
    var org = {}; datos.forEach(function (c) { org[c.organismo] = 1; });
    var nuevas = datos.filter(function (c) { return c.fecha === ultima; }).length, ntemas = Object.keys(cuenta(datos, 'tema').reduce(function (m, x) { m[x[0]] = 1; return m; }, {})).length;
    [[datos.length, 'convocatorias en el radar', '#00e08a'], (hayViejas ? [nuevas, 'nuevas en el último día', '#3b82f6'] : [ntemas, 'temas detectados', '#3b82f6']),
     [Object.keys(org).length, 'organismos convocantes', '#a855f7'],
     [datos.filter(function (c) { return c.ambito === 'LOCAL'; }).length, 'de ámbito local', '#f59e0b']].forEach(function (x) {
      var d = el('div', 'kpi'), b = el('b', '', '0'); d.style.setProperty('--c', x[2]);
      d.appendChild(b); d.appendChild(el('span', '', x[1])); k.appendChild(d); contar(b, x[0]);
    });
  }

  function blips() {
    var cont = $('blips'); cont.textContent = '';
    var n = Math.min(14, datos.length);
    for (var i = 0; i < n; i++) {
      var ang = (i * 137.5) * Math.PI / 180, rad = 0.18 + 0.78 * (((i * 53) % 100) / 100) * 0.5 + 0.16 * (i % 3);
      var b = el('i', 'blip'); b.style.left = (50 + 46 * rad * Math.cos(ang)) + '%'; b.style.top = (50 + 46 * rad * Math.sin(ang)) + '%';
      b.style.animationDelay = (-(ang / (2 * Math.PI)) * 5) + 's'; cont.appendChild(b);
    }
  }

  fetch('data/convocatorias.json').then(function (r) { return r.json(); }).then(function (j) {
    datos = j.convocatorias || [];
    datos.forEach(function (c) { if (c.fecha > ultima) ultima = c.fecha; });
    hayViejas = datos.some(function (c) { return c.fecha < ultima; });
    var vistos = {}; datos.forEach(function (c) { vistos[c.ambito] = 1; });
    Object.keys(vistos).forEach(function (a) { var o = el('option', '', AMBITOS[a] || a); o.value = a; $('ambito').appendChild(o); });
    $('actualizado').textContent = 'Última actualización de datos: ' + (j.actualizado || 'desconocida') + ' · ' + (j.fuente || '');
    kpis(); blips(); render();
  }).catch(function () {
    $('cuenta').textContent = 'No se han podido cargar las convocatorias. Inténtalo de nuevo más tarde.';
  });

  ['perfil', 'ambito'].forEach(function (id) { $(id).onchange = function () { visibles = PAGINA; render(); }; });
  $('q').oninput = function () { visibles = PAGINA; render(); };
  $('mas').onclick = function () { visibles += PAGINA; render(); };
})();
