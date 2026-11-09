(function () {
  'use strict';
  var COLOR = { 'Agro, pesca y animales': '#16a34a', 'Educación y becas': '#3b82f6', 'Social y salud': '#f43f5e', 'Cultura y festejos': '#a855f7',
    'Deporte': '#f59e0b', 'Empresas y empleo': '#06b6d4', 'Vivienda y fachadas': '#f97316', 'Otros': '#64748b' };
  var GREEN = '#22c55e', PURPLE = '#6d4aff', NS = 'http://www.w3.org/2000/svg';
  var MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var $ = function (id) { return document.getElementById(id); };
  var hoy = new Date().toISOString().slice(0, 10);
  var D = null, dias = [], rango = 14;

  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function sv(tag, attrs) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); return e; }
  function fmt(n) { return Number(n).toLocaleString('es-ES'); }
  function corto(f) { var p = f.split('-'); return parseInt(p[2], 10) + ' ' + MES[parseInt(p[1], 10) - 1]; }
  function larga(f) { var p = f.split('-'); return p[2] + '/' + p[1] + '/' + p[0]; }
  function diasHasta(f) { return Math.round((Date.parse(f) - Date.parse(hoy)) / 864e5); }
  function color(t) { return COLOR[t] || '#64748b'; }

  // Curva suave que no se pasa de los datos (Fritsch–Carlson).
  function curva(pts) {
    var n = pts.length; if (n < 2) return '';
    var dx = [], m = [], t = [];
    for (var i = 0; i < n - 1; i++) { dx[i] = pts[i + 1][0] - pts[i][0]; m[i] = (pts[i + 1][1] - pts[i][1]) / dx[i]; }
    t[0] = m[0]; t[n - 1] = m[n - 2];
    for (i = 1; i < n - 1; i++) t[i] = m[i - 1] * m[i] <= 0 ? 0 : (m[i - 1] + m[i]) / 2;
    for (i = 0; i < n - 1; i++) {
      if (m[i] === 0) { t[i] = t[i + 1] = 0; continue; }
      var a = t[i] / m[i], b = t[i + 1] / m[i], s = a * a + b * b;
      if (s > 9) { var k = 3 / Math.sqrt(s); t[i] = k * a * m[i]; t[i + 1] = k * b * m[i]; }
    }
    var d = 'M' + pts[0][0] + ',' + pts[0][1];
    for (i = 0; i < n - 1; i++) d += ' C' + (pts[i][0] + dx[i] / 3) + ',' + (pts[i][1] + t[i] * dx[i] / 3) + ' ' + (pts[i + 1][0] - dx[i] / 3) + ',' + (pts[i + 1][1] - t[i + 1] * dx[i] / 3) + ' ' + pts[i + 1][0] + ',' + pts[i + 1][1];
    return d;
  }

  function serieNegocios(fichados) {
    var m = {};
    fichados.forEach(function (c) { if ((c.perfiles || []).indexOf('negocio') >= 0) m[c.fecha] = (m[c.fecha] || 0) + 1; });
    return m;
  }

  function dibujaGrafico() {
    var cont = $('chart'); cont.textContent = '';
    var lista = rango ? dias.slice(-rango) : dias;
    var fich = D.convocatorias.filter(function (c) { return c.ficha; });
    var neg = serieNegocios(fich);
    var W = 700, H = 300, L = 46, R = 16, T = 16, B = 34;
    var vals = lista.map(function (d) { return D.serie[d]; });
    var max = Math.max.apply(null, vals.concat([1])), paso = Math.pow(10, Math.floor(Math.log10(max))), top = Math.ceil(max / paso) * paso;
    if (top / paso < 2) top = paso * 2;
    var x = function (i) { return L + (lista.length === 1 ? (W - L - R) / 2 : i * (W - L - R) / (lista.length - 1)); };
    var y = function (v) { return T + (1 - v / top) * (H - T - B); };
    var svg = sv('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': 'Convocatorias publicadas por día' });
    var defs = sv('defs', {}), g1 = sv('linearGradient', { id: 'g1', x1: 0, y1: 0, x2: 0, y2: 1 });
    g1.appendChild(sv('stop', { offset: '0%', 'stop-color': GREEN, 'stop-opacity': '.35' })); g1.appendChild(sv('stop', { offset: '100%', 'stop-color': GREEN, 'stop-opacity': '0' }));
    defs.appendChild(g1); svg.appendChild(defs);
    for (var k = 0; k <= 4; k++) {
      var v = top * k / 4, yy = y(v);
      svg.appendChild(sv('line', { x1: L, x2: W - R, y1: yy, y2: yy, stroke: '#1b2850', 'stroke-dasharray': '4 5' }));
      var tx = sv('text', { x: L - 8, y: yy + 4, 'text-anchor': 'end', fill: '#8f9cc0', 'font-size': 11 }); tx.textContent = fmt(Math.round(v)); svg.appendChild(tx);
    }
    var every = Math.ceil(lista.length / 7);
    lista.forEach(function (d, i) {
      if (i % every === 0 || i === lista.length - 1) { var t = sv('text', { x: x(i), y: H - 10, 'text-anchor': 'middle', fill: '#8f9cc0', 'font-size': 11 }); t.textContent = corto(d); svg.appendChild(t); }
    });
    function serie(valores, col, area) {
      var pts = []; valores.forEach(function (v, i) { if (v !== null) pts.push([x(i), y(v)]); });
      if (pts.length > 1) {
        var d = curva(pts);
        if (area) svg.appendChild(sv('path', { d: d + ' L' + pts[pts.length - 1][0] + ',' + (H - B) + ' L' + pts[0][0] + ',' + (H - B) + ' Z', fill: 'url(#g1)' }));
        svg.appendChild(sv('path', { d: d, fill: 'none', stroke: col, 'stroke-width': 3, 'stroke-linecap': 'round' }));
      }
      pts.forEach(function (p) { svg.appendChild(sv('circle', { cx: p[0], cy: p[1], r: 4.5, fill: '#0e1736', stroke: col, 'stroke-width': 2.5 })); });
    }
    serie(vals, GREEN, true);
    var cubre = {}; fich.forEach(function (c) { cubre[c.fecha] = (cubre[c.fecha] || 0) + 1; });
    var vn = lista.map(function (d) { return D.serie[d] >= 20 && (cubre[d] || 0) / D.serie[d] >= 0.8 ? (neg[d] || 0) : null; });   // solo días con la mayoría de fichas cargadas
    var hayNeg = vn.some(function (v) { return v !== null; });
    if (hayNeg) serie(vn, PURPLE, false);
    var tip = el('div', 'tip'); tip.hidden = true;
    lista.forEach(function (d, i) {
      var w = (W - L - R) / Math.max(1, lista.length - 1), r = sv('rect', { x: x(i) - w / 2, y: T, width: w, height: H - T - B, fill: 'transparent' });
      r.addEventListener('mouseenter', function () {
        tip.textContent = corto(d) + ': ' + fmt(D.serie[d]) + ' convocatorias' + (hayNeg && neg[d] !== undefined && D.serie[d] >= 20 && (cubre[d] || 0) / D.serie[d] >= 0.8 ? ' · ' + neg[d] + ' para negocios' : '');
        tip.style.left = (x(i) / W * 100) + '%'; tip.style.top = (y(D.serie[d]) / H * 100) + '%'; tip.hidden = false;
      });
      r.addEventListener('mouseleave', function () { tip.hidden = true; });
      svg.appendChild(r);
    });
    cont.appendChild(svg); cont.appendChild(tip);
    var lg = $('legend'); lg.textContent = '';
    var a = el('span', '', 'Todas las convocatorias'); a.style.setProperty('--c', GREEN); lg.appendChild(a);
    if (hayNeg) { var b = el('span', '', 'Para negocios y autónomos'); b.style.setProperty('--c', PURPLE); lg.appendChild(b); }
    var nota = el('div', 'note');
    nota.textContent = hayNeg ? 'La línea violeta solo se dibuja en los días con la mayoría de fichas oficiales cargadas. Fines de semana y festivos publican muy pocas convocatorias.'
      : 'La línea de "para negocios" aparecerá cuando se carguen las fichas oficiales. Fines de semana y festivos publican muy pocas convocatorias.';
    lg.appendChild(nota);
  }

  function kpis() {
    var c = $('kpis'); c.textContent = '';
    var ult = dias[dias.length - 1], ult14 = dias.slice(-14).reduce(function (s, d) { return s + D.serie[d]; }, 0);
    var fich = D.convocatorias.filter(function (x) { return x.ficha; });
    var vig = fich.filter(function (x) { return x.fin && x.fin >= hoy; }).length;
    var neg = fich.filter(function (x) { return (x.perfiles || []).indexOf('negocio') >= 0; }).length;
    function card(t, v, s, col, ic) {
      var d = el('div', 'kc'); d.appendChild(el('div', 't', t)); d.appendChild(el('b', '', v)); d.appendChild(el('small', '', s));
      var k = el('div', 'corner', ic); k.style.setProperty('--c', col); d.appendChild(k); c.appendChild(d);
    }
    card('Convocatorias en 14 días', fmt(ult14), 'Último día con datos: ' + larga(ult) + ' (' + fmt(D.serie[ult]) + ')', '#16a34a', '⬇');
    card('Con plazo vigente', fich.length ? fmt(vig) : '—', fich.length ? 'de ' + fmt(fich.length) + ' fichas con datos cargados' : 'Pendiente de cargar las fichas oficiales', PURPLE, '⏱');
    card('Para negocios y autónomos', fich.length ? fmt(neg) : '—', fich.length ? 'según el tipo de beneficiario oficial' : 'Pendiente de cargar las fichas oficiales', '#f59e0b', '★');
  }

  function metricas() {
    var fich = D.convocatorias.filter(function (x) { return x.ficha; });
    var neg = fich.filter(function (x) { return (x.perfiles || []).indexOf('negocio') >= 0; }).length;
    var pct = fich.length ? Math.round(100 * neg / fich.length) : null, d = $('donut'); d.textContent = '';
    var svg = sv('svg', { viewBox: '0 0 120 120' }), r = 50, c = 2 * Math.PI * r;
    svg.appendChild(sv('circle', { cx: 60, cy: 60, r: r, fill: 'none', stroke: '#1b2850', 'stroke-width': 11 }));
    if (pct !== null) svg.appendChild(sv('circle', { cx: 60, cy: 60, r: r, fill: 'none', stroke: PURPLE, 'stroke-width': 11, 'stroke-linecap': 'round', 'stroke-dasharray': (c * pct / 100) + ' ' + c, transform: 'rotate(-90 60 60)' }));
    d.appendChild(svg); d.appendChild(el('b', '', pct === null ? '—' : pct + '%'));
    $('donuttxt').textContent = pct === null ? 'Se calculará con las fichas oficiales (tipo de beneficiario).'
      : 'El ' + pct + '% de las convocatorias con ficha cargada admite como beneficiarios a negocios, pymes o autónomos.';

    var lista = dias.slice(-14), sp = $('spark'); sp.textContent = '';
    var W = 240, H = 100, max = Math.max.apply(null, lista.map(function (k) { return D.serie[k]; }).concat([1]));
    var pts = lista.map(function (k, i) { return [8 + i * (W - 16) / Math.max(1, lista.length - 1), 8 + (1 - D.serie[k] / max) * (H - 24)]; });
    var s2 = sv('svg', { viewBox: '0 0 ' + W + ' ' + H }), df = sv('defs', {}), gg = sv('linearGradient', { id: 'g2', x1: 0, y1: 0, x2: 0, y2: 1 });
    gg.appendChild(sv('stop', { offset: '0%', 'stop-color': GREEN, 'stop-opacity': '.4' })); gg.appendChild(sv('stop', { offset: '100%', 'stop-color': GREEN, 'stop-opacity': '0' }));
    df.appendChild(gg); s2.appendChild(df);
    if (pts.length > 1) {
      var p = curva(pts);
      s2.appendChild(sv('path', { d: p + ' L' + pts[pts.length - 1][0] + ',' + (H - 8) + ' L' + pts[0][0] + ',' + (H - 8) + ' Z', fill: 'url(#g2)' }));
      s2.appendChild(sv('path', { d: p, fill: 'none', stroke: GREEN, 'stroke-width': 2.5 }));
    }
    sp.appendChild(s2);
    var lab = lista.filter(function (k) { return D.serie[k] > 50 && k !== dias[dias.length - 1]; }).map(function (k) { return D.serie[k]; });
    var media = lab.length ? Math.round(lab.reduce(function (a, b) { return a + b; }, 0) / lab.length) : null;
    $('sparktxt').textContent = media ? 'Media de los días laborables anteriores: ' + fmt(media) + ' convocatorias al día. Último día con datos: ' + fmt(D.serie[dias[dias.length - 1]]) + ' (puede estar incompleto).' : '';
  }

  function cierres() {
    var l = $('todo'); l.textContent = '';
    var prox = D.convocatorias.filter(function (c) { return c.ficha && c.fin && c.fin >= hoy; }).sort(function (a, b) { return a.fin < b.fin ? -1 : 1; }).slice(0, 5);
    prox.forEach(function (c) {
      var li = document.createElement('li'), a = el('a', '', c.descripcion.length > 70 ? c.descripcion.slice(0, 68) + '…' : c.descripcion);
      a.href = c.url; a.target = '_blank'; a.rel = 'noopener'; li.appendChild(a);
      var n = diasHasta(c.fin); li.appendChild(el('small', '', 'Cierra el ' + larga(c.fin) + (n === 0 ? ' (hoy)' : ' (en ' + n + ' d)')));
      l.appendChild(li);
    });
    $('todonota').textContent = prox.length ? 'Fecha de fin según la ficha oficial. Confirma siempre el plazo en la convocatoria.' : 'Aún no hay plazos con fecha cargados. Aparecerán al descargar las fichas oficiales.';
  }

  function temas() {
    var m = {}; D.convocatorias.forEach(function (c) { m[c.tema] = (m[c.tema] || 0) + 1; });
    var g = $('temagrid'); g.textContent = '';
    Object.keys(m).sort(function (a, b) { return m[b] - m[a]; }).forEach(function (t) {
      var d = el('div', 'tm'); d.style.setProperty('--c', color(t)); d.appendChild(el('b', '', fmt(m[t]))); d.appendChild(el('span', '', t)); g.appendChild(d);
    });
  }

  function ultimas() {
    var l = $('ultimaslist'); l.textContent = '';
    D.convocatorias.slice(0, 8).forEach(function (c) {
      var li = el('li'); li.style.setProperty('--c', color(c.tema));
      var m = el('div', 'm'); m.appendChild(el('em', '', c.tema)); m.appendChild(el('span', '', larga(c.fecha))); m.appendChild(el('span', '', c.organismo)); li.appendChild(m);
      var a = el('a', 't', c.descripcion); a.href = c.url; a.target = '_blank'; a.rel = 'noopener'; li.appendChild(a); l.appendChild(li);
    });
  }

  function saludo() {
    $('saludo').textContent = 'Panel de ayudas y subvenciones';
    $('sub').textContent = 'Lo que se publica en la BDNS, para toda España. Datos oficiales y gratuitos.';
    var u = (D.actualizado || '').match(/^(\d{4})-(\d\d)-(\d\d)T(\d\d:\d\d)/);
    $('upd').textContent = 'Datos actualizados: ' + (u ? u[3] + '/' + u[2] + '/' + u[1] + ' ' + u[4] + ' UTC' : 'desconocido') + ' · Fuente: BDNS (IGAE)';
  }

  fetch('../data/convocatorias.json').then(function (r) { return r.json(); }).then(function (j) {
    D = j; D.serie = D.serie || {}; D.convocatorias = D.convocatorias || [];
    dias = Object.keys(D.serie).sort();
    if (!dias.length) { var m = {}; D.convocatorias.forEach(function (c) { m[c.fecha] = (m[c.fecha] || 0) + 1; }); D.serie = m; dias = Object.keys(m).sort(); }
    saludo(); kpis(); dibujaGrafico(); metricas(); cierres(); temas(); ultimas();
    Array.prototype.forEach.call(document.querySelectorAll('#rango button'), function (b) {
      b.onclick = function () { rango = parseInt(b.getAttribute('data-d'), 10); Array.prototype.forEach.call(document.querySelectorAll('#rango button'), function (x) { x.classList.toggle('on', x === b); }); dibujaGrafico(); };
    });
  }).catch(function () { $('sub').textContent = 'No se han podido cargar los datos. Inténtalo de nuevo más tarde.'; });
})();
