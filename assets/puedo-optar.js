(function () {
  'use strict';
  var $ = function (i) { return document.getElementById(i); };
  var PERFIL_TEMAS = {
    negocio: ['Empresas y empleo', 'Vivienda y fachadas', 'Agro, pesca y animales'],
    empresa: ['Empresas y empleo'],
    persona: ['Educación y becas', 'Social y salud', 'Vivienda y fachadas', 'Deporte'],
    entidad: ['Cultura y festejos', 'Deporte', 'Social y salud', 'Otros']
  };
  var conv = [], lic = [];
  function plano(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function fecha(i) { return i ? i.split('-').reverse().join('/') : ''; }
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  function hoy() { return new Date().toISOString().slice(0, 10); }
  function get(u) { return fetch(u, { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; }); }

  function zona(c, cc) { return !cc || (c.ccaa || []).indexOf(cc) >= 0 || !!c.nacional; }

  function ayudas(p) {
    var h = hoy(), q = plano(p.q);
    return conv.filter(function (c) {
      if (c.ficha && c.fin && c.fin < h) return false;
      if (p.cc && c.ficha && !zona(c, p.cc)) return false;
      if (p.tema && c.tema !== p.tema) return false;
      if (c.ficha ? (c.perfiles || []).indexOf(p.perfil) < 0 : PERFIL_TEMAS[p.perfil].indexOf(c.tema) < 0) return false;
      if (q && plano(c.descripcion + ' ' + c.organismo).indexOf(q) < 0) return false;
      return true;
    }).sort(function (a, b) { return (a.fin || '9999').localeCompare(b.fin || '9999') || (b.fecha || '').localeCompare(a.fecha || ''); });
  }
  function licit(p) {
    if (p.perfil === 'persona') return [];
    var q = plano(p.q);
    return lic.filter(function (r) {
      if (p.cc && !zona(r, p.cc)) return false;
      if (q && plano(r.titulo + ' ' + r.organismo).indexOf(q) < 0) return false;
      return true;
    }).sort(function (a, b) { return (a.plazo || '9999').localeCompare(b.plazo || '9999'); });
  }

  function lista(ul, items, tipo) {
    ul.textContent = '';
    items.slice(0, 12).forEach(function (c) {
      var li = el('li'), a = el('a', '', tipo === 'ay' ? c.descripcion : c.titulo);
      a.href = c.url; a.rel = 'noopener nofollow';
      var m = tipo === 'ay'
        ? [c.organismo, c.tema, c.fin ? 'plazo hasta ' + fecha(c.fin) : 'plazo: ver ficha', (c.ccaa || []).join(', ')]
        : [c.organismo, c.tipo, c.plazo ? 'plazo hasta ' + fecha(c.plazo) : 'plazo: ver ficha', (c.ccaa || []).join(', ')];
      li.appendChild(a); li.appendChild(el('small', '', m.filter(Boolean).join(' · '))); ul.appendChild(li);
    });
  }

  function calcula() {
    var p = { perfil: $('perfil').value, cc: $('ccaa').value, tema: $('tema').value, q: $('q').value.trim() };
    var a = ayudas(p), l = licit(p);
    $('res').hidden = false;
    $('r-ay-n').textContent = a.length ? a.length + ' ayudas encajan' + (a.length > 12 ? ' (las 12 con cierre más próximo)' : '') + '.' : 'No hay ayudas abiertas que encajen. Prueba con otro tema o toda España.';
    lista($('l-ay'), a, 'ay');
    $('r-li').hidden = $('r-li-n').hidden = $('l-li').hidden = p.perfil === 'persona';
    if (p.perfil !== 'persona') {
      $('r-li-n').textContent = l.length ? l.length + ' licitaciones abiertas' + (l.length > 12 ? ' (las 12 con cierre más próximo)' : '') + '.' : 'No hay licitaciones abiertas con esos filtros.';
      lista($('l-li'), l, 'li');
    }
    $('res').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  Promise.all([get('../data/convocatorias.json'), get('../data/licitaciones.json')]).then(function (r) {
    conv = r[0].convocatorias || []; lic = r[1].licitaciones || [];
    var cc = {}, tm = {};
    conv.forEach(function (c) { (c.ccaa || []).forEach(function (x) { cc[x] = 1; }); if (c.tema) tm[c.tema] = 1; });
    lic.forEach(function (c) { (c.ccaa || []).forEach(function (x) { cc[x] = 1; }); });
    Object.keys(cc).sort().forEach(function (x) { var o = el('option', '', x); o.value = x; $('ccaa').appendChild(o); });
    Object.keys(tm).sort().forEach(function (x) { var o = el('option', '', x); o.value = x; $('tema').appendChild(o); });
  });
  $('f').addEventListener('submit', function (e) { e.preventDefault(); calcula(); });
})();
