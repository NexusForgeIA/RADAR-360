(function () {
  'use strict';
  var $ = function (i) { return document.getElementById(i); };
  var todas = [], vista = [], pag = 25, mostradas = 0;
  function plano(s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
  function fecha(i) { return i ? i.split('-').reverse().join('/') : ''; }
  function eur(n) { return n ? Math.round(n).toLocaleString('es-ES') + ' €' : ''; }
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }

  function filtra() {
    var cc = $('ccaa').value, tp = $('tipo').value, q = plano($('q').value.trim());
    vista = todas.filter(function (r) {
      if (cc && (r.ccaa || []).indexOf(cc) < 0 && !r.nacional) return false;
      if (tp && r.tipo !== tp) return false;
      if (q && plano(r.titulo + ' ' + r.organismo).indexOf(q) < 0) return false;
      return true;
    });
    var o = $('ord').value;
    vista.sort(function (a, b) {
      if (o === 'imp') return (b.presupuesto || 0) - (a.presupuesto || 0);
      if (o === 'rec') return (b.actualizado || '').localeCompare(a.actualizado || '');
      return (a.plazo || '9999').localeCompare(b.plazo || '9999');
    });
    $('lista').textContent = ''; mostradas = 0; pinta();
  }

  function pinta() {
    var f = document.createDocumentFragment();
    vista.slice(mostradas, mostradas + pag).forEach(function (r) {
      var li = el('li'), a = el('a', '', r.titulo);
      if (r.url) { a.href = r.url; a.rel = 'noopener nofollow'; }
      var meta = [r.organismo, r.tipo, r.presupuesto ? 'presupuesto ' + eur(r.presupuesto) : '',
        r.plazo ? 'plazo hasta ' + fecha(r.plazo) : 'plazo: ver ficha', (r.ccaa || []).join(', ')].filter(Boolean).join(' · ');
      li.appendChild(a); li.appendChild(el('small', '', meta)); f.appendChild(li);
    });
    $('lista').appendChild(f); mostradas = Math.min(vista.length, mostradas + pag);
    $('cuenta').textContent = vista.length + ' licitaciones abiertas' + (vista.length > mostradas ? ' (mostrando ' + mostradas + ')' : '');
    $('vacio').hidden = vista.length > 0; $('mas').hidden = mostradas >= vista.length;
  }

  function opciones(id, valores) { valores.forEach(function (v) { var o = el('option', '', v); o.value = v; $(id).appendChild(o); }); }

  fetch('../data/licitaciones.json', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
    todas = d.licitaciones || [];
    $('upd').textContent = 'Datos actualizados el ' + (d.actualizado || '').slice(0, 10).split('-').reverse().join('/') + '. Origen: Plataforma de Contratación del Sector Público.';
    var cc = {}, tp = {};
    todas.forEach(function (r) { (r.ccaa || []).forEach(function (x) { cc[x] = 1; }); if (r.tipo) tp[r.tipo] = 1; });
    opciones('ccaa', Object.keys(cc).sort()); opciones('tipo', Object.keys(tp).sort());
    ['ccaa', 'tipo', 'ord'].forEach(function (i) { $(i).addEventListener('change', filtra); });
    $('q').addEventListener('input', filtra); $('mas').addEventListener('click', pinta);
    filtra();
  }).catch(function () {
    $('upd').textContent = 'Todavía no hay datos cargados. Se publican tras la primera actualización automática.';
    $('cuenta').textContent = '';
  });
})();
