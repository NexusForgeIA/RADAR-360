/* Barra inferior tipo app (móvil y app instalada). Sin dependencias. */
(function(){
  var T=[["/","Ayudas","M4 6h16M4 12h16M4 18h10"],["/licitaciones/","Licitaciones","M5 4h14v16H5zM9 9h6M9 13h6"],["/puedo-optar/","¿Puedo?","M12 3a9 9 0 100 18 9 9 0 000-18zM9.5 9.5a2.5 2.5 0 115 0c0 1.5-2.5 2-2.5 3.5M12 17v.5"],["/panel/","Panel","M5 20V10M12 20V4M19 20v-7"]];
  var p=location.pathname.replace(/index\.html$/,"");
  function on(h){return h==="/"?(p==="/"||p.indexOf("/ayudas/")===0):p.indexOf(h)===0}
  var css=".tabbar{display:none}@media (max-width:820px),(display-mode:standalone){body{padding-bottom:calc(64px + env(safe-area-inset-bottom))}.tabbar{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:999;background:#081124;border-top:1px solid #1c2c55;padding:6px 4px calc(6px + env(safe-area-inset-bottom))}.tabbar a{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;color:#8fa0c7;text-decoration:none;font:600 11px/1.1 Inter,system-ui,sans-serif;padding:4px 2px;min-width:0}.tabbar a.on{color:#00e08a}.tabbar svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}@media (max-width:820px),(display-mode:standalone){.top .tag .navlink{display:none}.side nav{display:none}}";
  var st=document.createElement("style");st.textContent=css;document.head.appendChild(st);
  var n=document.createElement("nav");n.className="tabbar";n.setAttribute("aria-label","Navegación principal");
  n.innerHTML=T.map(function(t){return '<a href="'+t[0]+'"'+(on(t[0])?' class="on" aria-current="page"':'')+'><svg viewBox="0 0 24 24" aria-hidden="true"><path d="'+t[2]+'"/></svg>'+t[1]+'</a>'}).join("");
  document.body.appendChild(n);
})();
