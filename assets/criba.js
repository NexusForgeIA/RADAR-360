(function () {
  'use strict';
  var $ = function (i) { return document.getElementById(i); };
  function el(t, c, x) { var e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
  // peso: 3 = elimina si la respuesta es "no"; 1-2 = resta. donde: qué mirar en el pliego
  var P = [
    { t: 'Solvencia económica', q: '¿Tu facturación anual supera lo que suele exigirse (normalmente 1,5 veces el valor anual estimado)?', p: 3, d: 'Solvencia económica y financiera en el PCAP (cuadro de características): volumen anual de negocios exigido.' },
    { t: 'Solvencia técnica', q: '¿Has ejecutado contratos del mismo tipo y tamaño parecido en los últimos años?', p: 3, d: 'Solvencia técnica: relación de trabajos similares exigida, importes y años que cuentan.' },
    { t: 'Clasificación', q: 'Si el pliego exige clasificación (grupo y subgrupo), ¿la tienes? Si no la exige, marca «Sí».', p: 3, d: 'Clasificación del contratista: grupo, subgrupo y categoría (obras y algunos servicios).' },
    { t: 'Habilitaciones', q: '¿Cumples las habilitaciones o titulaciones que pida la actividad (profesionales, registros, certificados)?', p: 3, d: 'Habilitación empresarial o profesional y adscripción de medios personales.' },
    { t: 'Medios personales y materiales', q: '¿Puedes comprometer el equipo y los medios que exige el contrato sin dejar otros trabajos sin atender?', p: 2, d: 'Medios adscritos al contrato y condiciones especiales de ejecución.' },
    { t: 'Plazo para preparar la oferta', q: '¿Tienes tiempo real para preparar bien la oferta antes del cierre (documentación, memoria, firma)?', p: 2, d: 'Fecha y hora límite de presentación y plazo para pedir aclaraciones.' },
    { t: 'Garantías', q: '¿Puedes asumir la garantía definitiva (habitualmente el 5 % del importe sin IVA) y, si se pide, la provisional?', p: 2, d: 'Garantías provisional y definitiva: importe, forma y cuándo se exigen.' },
    { t: 'Margen', q: 'Con el presupuesto de licitación, ¿te sale un margen razonable, incluso con una baja competitiva?', p: 3, d: 'Presupuesto base, valor estimado y criterio de precio (fórmula y bajas temerarias).' },
    { t: 'Criterios de adjudicación', q: '¿Te favorecen los criterios (precio, calidad, mejoras) o se ajustan a lo que mejor sabes hacer?', p: 1, d: 'Cuadro de criterios: puntos del precio frente a los criterios de calidad.' },
    { t: 'Pago y penalidades', q: '¿Te encajan las condiciones de pago, la revisión de precios y las penalidades?', p: 1, d: 'Régimen de pago, penalidades por incumplimiento y revisión de precios.' },
    { t: 'Competencia', q: '¿Conoces el organismo o sabes quién suele ganar en él y a qué precio, y tienes opciones reales?', p: 1, d: 'Adjudicaciones anteriores del mismo órgano de contratación en la Plataforma de Contratación.' },
    { t: 'Capacidad de presentación', q: '¿Tienes certificado digital y alguien que sepa presentar la oferta en la plataforma indicada?', p: 2, d: 'Plataforma y medio de presentación: licitación electrónica, firma y sobres.' }
  ];
  var R = ['Sí', 'No lo sé', 'No'];

  P.forEach(function (x, i) {
    var f = el('fieldset', 'crib-q'), l = el('legend', '', (i + 1) + '. ' + x.t);
    f.appendChild(l); f.appendChild(el('p', '', x.q));
    var g = el('div', 'crib-opts');
    R.forEach(function (r, k) {
      var lab = el('label'), inp = document.createElement('input');
      inp.type = 'radio'; inp.name = 'q' + i; inp.value = k;
      lab.appendChild(inp); lab.appendChild(document.createTextNode(' ' + r)); g.appendChild(lab);
    });
    f.appendChild(g); $('cr').appendChild(f);
  });

  $('calc').addEventListener('click', function () {
    var sin = [], nos = [], duda = [], pts = 0, max = 0, bloq = 0;
    P.forEach(function (x, i) {
      var s = document.querySelector('input[name="q' + i + '"]:checked');
      if (!s) { sin.push(i + 1); return; }
      var v = +s.value; max += x.p;
      if (v === 0) pts += x.p;
      else if (v === 1) { pts += x.p * 0.5; duda.push(x); }
      else { nos.push(x); if (x.p === 3) bloq++; }
    });
    if (sin.length) {
      $('res').hidden = false; $('veredicto').textContent = 'Faltan respuestas';
      $('expl').textContent = 'Responde todas las preguntas para valorar. Te faltan: ' + sin.join(', ') + '.'; $('rev').textContent = ''; return;
    }
    var ratio = pts / max, v, e;
    if (bloq > 0) { v = 'No-Go probable'; e = 'Hay requisitos que suelen ser excluyentes y los marcas como «No». Salvo que el pliego los plantee de otra forma, o puedas cubrirlos con una UTE o con medios de otra empresa, lo prudente es no presentarte.'; }
    else if (ratio >= 0.8 && duda.length <= 2) { v = 'Go: merece que abras el pliego'; e = 'Encaja bien con tu empresa. Antes de decidir del todo, confirma en el pliego los puntos que marcas como dudosos.'; }
    else if (ratio >= 0.55) { v = 'Revisar con cuidado'; e = 'No hay un bloqueo claro, pero hay varios puntos débiles o dudosos. Léelos en el pliego antes de gastar horas en la oferta.'; }
    else { v = 'No-Go probable'; e = 'Demasiados puntos en contra o en duda para que compense el esfuerzo de la oferta.'; }
    $('res').hidden = false; $('veredicto').textContent = v; $('expl').textContent = e;
    var rev = $('rev'); rev.textContent = '';
    function bloque(tit, arr) {
      if (!arr.length) return;
      rev.appendChild(el('h3', '', tit));
      var ul = el('ul'); arr.forEach(function (x) { var li = el('li'); li.appendChild(el('b', '', x.t + ': ')); li.appendChild(document.createTextNode(x.d)); ul.appendChild(li); });
      rev.appendChild(ul);
    }
    bloque('Qué te falta (marcaste «No»)', nos);
    bloque('Qué comprobar en el pliego (marcaste «No lo sé»)', duda);
    rev.appendChild(el('p', 'mini', 'Resultado orientativo. No sustituye la lectura del pliego ni constituye asesoramiento jurídico.'));
    $('res').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
