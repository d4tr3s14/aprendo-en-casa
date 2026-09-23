/* Aprendo en casa · funciona sin internet
   Estrategia "primero la red": si hay conexión siempre se ve lo último que
   subiste a GitHub; si no hay, se usa la copia guardada de la última visita.
   No hay que cambiar nada aquí al agregar actividades nuevas. */
const CACHE = "aprendo-v2";

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(["./", "index.html", "actividades.json", "manifest.webmanifest"])));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if(req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  e.respondWith(
    fetch(req)
      .then(res => {
        const copia = res.clone();
        const clave = req.url.split("?")[0];
        if(res.ok) caches.open(CACHE).then(c => c.put(clave, copia));
        return res;
      })
      .catch(() => caches.match(req.url.split("?")[0]).then(r => r || caches.match("index.html")))
  );
});
