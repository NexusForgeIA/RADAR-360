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
  var AMBITOS = { LOCAL: 'Local', AUTONOMICA: 'Autonómico', ESTADO: 'Estatal', OTROS: 'Otros' };
  var PAGINA = 20;

  var $ = function (id) { return document.getElementById(id); };
  var datos = [], temaSel = '', visibles = PAGINA;

  function plano(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function fecha(f) { var p = (f || '').split('-'); return p.length === 3 ? p[2] + '/' + p[1] + '/' + p[0] : ''; }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }

  function filtradas() {
    var q = plano($('q').value).trim(), am = $('ambito').value, pf = PERFILES[$('perfil').value];
    var r = datos.filter(function (c) {
      if (am && c.ambito !== am) return false;
      if (temaSel && c.tema !== temaSel) return false;
      if (pf && !temaSel && pf.indexOf(c.tema) < 0) return false;
      if (q && plano(c.descripcion + ' ' + c.organismo).indexOf(q) < 0) return false;
      return true;
    });
    return r;
  }

  function pintaTemas() {
    var cont = $('temas'), cuenta = {};
    datos.forEach(function (c) { cuenta[c.tema] = (cuenta[c.tema] || 0) + 1; });
    cont.textContent = '';
    Object.keys(cuenta).sort(function (a, b) { return cuenta[b] - cuenta[a]; }).forEach(function (t) {
      var b = el('button', 'chip', t + ' · ' + cuenta[t]);
      b.type = 'button'; b.setAttribute('aria-pressed', String(temaSel === t));
      b.onclick = function () { temaSel = temaSel === t ? '' : t; visibles = PAGINA; render(); };
      cont.appendChild(b);
    });
  }

  function render() {
    var r = filtradas(), lista = $('lista');
    pintaTemas();
    lista.textContent = '';
    r.slice(0, visibles).forEach(function (c) {
      var li = el('li', 'card'), meta = el('div', 'meta');
      meta.appendChild(el('span', 'pill', c.tema));
      meta.appendChild(el('span', '', AMBITOS[c.ambito] || c.ambito));
      meta.appendChild(el('span', '', 'Recibida el ' + fecha(c.fecha)));
      li.appendChild(meta);
      li.appendChild(el('h3', '', c.descripcion || '(sin descripción)'));
      li.appendChild(el('div', 'meta', c.organismo));
      var a = el('a', 'go', 'Ver convocatoria oficial en BDNS ↗');
      a.href = c.url; a.target = '_blank'; a.rel = 'noopener';
      li.appendChild(a);
      lista.appendChild(li);
    });
    $('cuenta').textContent = r.length + ' de ' + datos.length + ' convocatorias';
    $('vacio').hidden = r.length > 0;
    $('mas').hidden = r.length <= visibles;
  }

  function kpis() {
    var k = $('kpis'); k.textContent = '';
    var org = {}; datos.forEach(function (c) { org[c.organismo] = 1; });
    [[datos.length, 'convocatorias recientes'], [Object.keys(org).length, 'organismos convocantes'],
     [datos.filter(function (c) { return c.ambito === 'LOCAL'; }).length, 'locales']].forEach(function (x) {
      var d = el('div', 'kpi'); d.appendChild(el('b', '', String(x[0]))); d.appendChild(el('span', '', x[1])); k.appendChild(d);
    });
  }

  function reset() { $('perfil').value = ''; $('ambito').value = ''; $('q').value = ''; temaSel = ''; visibles = PAGINA; render(); }

  fetch('data/convocatorias.json').then(function (r) { return r.json(); }).then(function (j) {
    datos = j.convocatorias || [];
    var vistos = {}; datos.forEach(function (c) { vistos[c.ambito] = 1; });
    Object.keys(vistos).forEach(function (a) { var o = el('option', '', AMBITOS[a] || a); o.value = a; $('ambito').appendChild(o); });
    $('actualizado').textContent = 'Última actualización de datos: ' + (j.actualizado || 'desconocida') + ' · ' + (j.fuente || '');
    kpis(); render();
  }).catch(function () {
    $('cuenta').textContent = 'No se han podido cargar las convocatorias. Inténtalo de nuevo más tarde.';
  });

  ['perfil', 'ambito'].forEach(function (id) { $(id).onchange = function () { visibles = PAGINA; render(); }; });
  $('q').oninput = function () { visibles = PAGINA; render(); };
  $('limpiar').onclick = reset;
  $('mas').onclick = function () { visibles += PAGINA; render(); };
})();
