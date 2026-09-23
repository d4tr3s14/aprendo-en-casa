/* ==========================================================================
   SELVA v2 · comportamiento común
   1. Guarda el progreso (veces jugada y mejor puntaje) para que la portada
      muestre las estrellas ganadas. Solo en este dispositivo, sin internet.
   2. Si ya hay estrellas en la ronda, "Inicio" pregunta antes de salir.
   3. Hace saltar el contador cuando se gana una estrella.
   4. Etiqueta los botones que solo tienen un ícono.
   ========================================================================== */
(function(){
  var CLAVE = "aprendo:progreso";
  var ruta = decodeURIComponent(location.pathname).replace(/^.*?(\d+-basico\/)/, "$1");
  var $ = function(s){ return document.querySelector(s); };

  function estrellas(){
    var el = $("#puntaje, #cuenta");
    var m = el && el.textContent.match(/\d+/);
    return m ? +m[0] : 0;
  }
  function registrar(){
    var d = {};
    try{ d = JSON.parse(localStorage.getItem(CLAVE)) || {}; }catch(e){}
    var r = d[ruta] || { veces:0, mejor:0 };
    r.veces++;
    r.mejor = Math.max(r.mejor || 0, estrellas());
    r.ultima = new Date().toISOString().slice(0, 10);
    d[ruta] = r;
    try{ localStorage.setItem(CLAVE, JSON.stringify(d)); }catch(e){}
  }

  /* 1. fin de la actividad: pantalla #final (juegos) o #pFinal (misiones) */
  var fin = $("#final, #pFinal");
  if(fin){
    var visto = false;
    new MutationObserver(function(){
      var ve = fin.classList.contains("activa") || (fin.id === "pFinal" && !fin.hidden);
      if(ve && !visto){ visto = true; setTimeout(registrar, 400); }
      if(!ve) visto = false;
    }).observe(fin, { attributes:true, attributeFilter:["class", "hidden"] });
  }
  /* presentaciones: cuenta como vista al llegar a la última diapositiva */
  var cont = $("#contador");
  if(cont && !fin){
    var vista = false;
    new MutationObserver(function(){
      var p = cont.textContent.match(/(\d+)\s*\/\s*(\d+)/);
      if(p && p[1] === p[2] && !vista){ vista = true; registrar(); }
    }).observe(cont, { childList:true, characterData:true, subtree:true });
  }

  /* 2. confirmar antes de salir a mitad de una ronda */
  function enRonda(){
    return !!$("#juego.activa, #ensayo.activa, #pJuego:not([hidden])") && estrellas() > 0;
  }
  var dlg = null;
  function preguntarSalida(destino){
    if(!window.HTMLDialogElement){ location.href = destino; return; }
    if(!dlg){
      dlg = document.createElement("dialog");
      dlg.className = "selva-dialogo";
      dlg.innerHTML =
        '<div class="selva-dialogo-emo" aria-hidden="true">🏠</div>' +
        '<h2>¿Quieres salir?</h2>' +
        '<p>Si sales ahora, se pierden las estrellas de esta ronda.</p>' +
        '<button class="selva-seguir" value="seguir">▶️ Seguir jugando</button>' +
        '<button class="selva-salir" value="salir">Salir</button>';
      dlg.addEventListener("click", function(e){
        var b = e.target.closest("button");
        if(!b) return;
        dlg.close();
        if(b.value === "salir") location.href = dlg.dataset.destino;
      });
      document.body.appendChild(dlg);
    }
    dlg.dataset.destino = destino;
    dlg.showModal();
    try{
      if(window.speechSynthesis){
        speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance("¿Quieres salir? Si sales ahora, se pierden las estrellas de esta ronda.");
        u.lang = "es-ES"; speechSynthesis.speak(u);
      }
    }catch(e){}
    dlg.querySelector(".selva-seguir").focus();
  }
  document.addEventListener("click", function(e){
    var a = e.target.closest && e.target.closest('a[href$="index.html"]');
    if(!a || !enRonda()) return;
    e.preventDefault();
    preguntarSalida(a.href);
  }, true);

  /* 3. el contador salta al ganar una estrella */
  var pts = $("#puntaje");
  if(pts){
    var antes = estrellas();
    new MutationObserver(function(){
      var ahora = estrellas();
      if(ahora > antes){
        pts.classList.remove("salta"); void pts.offsetWidth; pts.classList.add("salta");
      }
      antes = ahora;
    }).observe(pts, { childList:true, characterData:true, subtree:true });
  }

  /* 4. etiquetas para lectores de pantalla */
  var nombres = { btnGeneral:"Ver todas las diapositivas", btnPantalla:"Pantalla completa", btnVoz:"Voz", sonido:"Voz y sonidos" };
  Object.keys(nombres).forEach(function(id){
    var b = document.getElementById(id);
    if(b && !b.getAttribute("aria-label") && !/[a-záéíóú]{3}/i.test(b.textContent)) b.setAttribute("aria-label", nombres[id]);
  });
  /* el iPhone no permite pantalla completa en páginas web: se oculta el botón */
  var d = document.documentElement;
  if(!(document.fullscreenEnabled || document.webkitFullscreenEnabled)) d.classList.add("selva-sin-pantalla-completa");
})();
