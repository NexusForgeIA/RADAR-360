(function () {
  'use strict';
  var $ = function (i) { return document.getElementById(i); };
  var orgs = [], vista = [], pag = 25, mostradas = 0;
  function plano(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function n(x) { return x == null ? '—' : Math.round(x).toLocaleString('es-ES'); }
  function d1(x) { return x == null ? '—' : x.toLocaleString('es-ES', { maximumFractionDigits: 1 }); }
  function pc(x) { return x == null ? '—' : d1(x) + ' %'; }
  function eur(x) { return !x ? '—' : x >= 1e6 ? d1(x / 1e6) + ' M€' : n(x) + ' €'; }
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function fila(tr, celdas, th) { celdas.forEach(function (c, i) { var td = el(th ? 'th' : 'td', i ? 'num' : '', c); tr.appendChild(td); }); return tr; }
  function tabla(t, cab, filas) {
    t.textContent = '';
    var th = el('thead'); th.appendChild(fila(el('tr'), cab, true)); t.appendChild(th);
    var tb = el('tbody'); filas.forEach(function (f) { tb.appendChild(fila(el('tr'), f)); }); t.appendChild(tb);
  }
  var CAB = ['', 'Adjudicaciones', 'Importe', 'Una sola oferta', 'Ofertas (media)', 'Baja media'];
  function reg(nombre, r) { return [nombre, n(r.n), eur(r.importe), pc(r.pct_una_oferta), r.ofertas_media == null ? '—' : d1(r.ofertas_media), pc(r.baja_media)]; }

  function pintaOrgs() {
    var q = plano($('q').value.trim());
    vista = orgs.filter(function (o) { return !q || plano(o.organismo).indexOf(q) >= 0; });
    mostradas = Math.min(vista.length, pag);
    dibujaOrgs();
  }
  function dibujaOrgs() {
    var cab = ['Organismo', 'Adjud.', 'Importe', 'Una oferta', 'Ofertas (media)', 'Baja media', 'Más adjudicado a'];
    tabla($('t-org'), cab, vista.slice(0, mostradas).map(function (o) {
      var f = reg(o.organismo, o); f.push(o.top_ganador ? o.top_ganador.nombre + ' (' + o.top_ganador.n + ')' : '—'); return f;
    }));
    $('mas').hidden = mostradas >= vista.length;
  }

  fetch('../data/mercado.json', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (m) {
    var g = m.global, p = m.periodo || {};
    $('upd').textContent = 'Adjudicaciones del ' + (p.desde || '').split('-').reverse().join('/') + ' al ' + (p.hasta || '').split('-').reverse().join('/') +
      '. Fuente: Plataforma de Contratación del Sector Público.';
    var k = $('kpis');
    [['Adjudicaciones analizadas', n(g.n)], ['Importe adjudicado', eur(g.importe)], ['Con una sola oferta', pc(g.pct_una_oferta)],
     ['Ofertas por contrato (media)', g.ofertas_media == null ? '—' : d1(g.ofertas_media)], ['Baja media sobre presupuesto', pc(g.baja_media)]].forEach(function (x) {
      var b = el('div', 'kpi2'); b.appendChild(el('b', '', x[1])); b.appendChild(el('span', '', x[0])); k.appendChild(b);
    });
    tabla($('t-tipo'), ['Tipo'].concat(CAB.slice(1)), Object.keys(m.por_tipo).map(function (t) { return reg(t, m.por_tipo[t]); }));
    tabla($('t-ccaa'), ['Comunidad'].concat(CAB.slice(1)), Object.keys(m.por_ccaa).map(function (t) { return reg(t, m.por_ccaa[t]); }));
    orgs = m.por_organismo || []; pintaOrgs();
    tabla($('t-gan'), ['Adjudicatario', 'Adjudicaciones', 'Importe', 'Organismos distintos'],
      (m.top_adjudicatarios || []).map(function (a) { return [a.nombre, n(a.n), eur(a.importe), n(a.organismos)]; }));
    $('q').addEventListener('input', pintaOrgs);
    $('mas').addEventListener('click', function () { mostradas = Math.min(vista.length, mostradas + pag); dibujaOrgs(); });
  }).catch(function () { $('upd').textContent = ''; $('vacio').hidden = false; });
})();
