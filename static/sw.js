// SSAS service worker — minimal offline shell
const CACHE = "ssas-v1";
const PRECACHE = ["/", "/static/styles.css", "/static/icon.svg", "/static/favicon.svg"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => k !== CACHE).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Network-first for HTML & API; cache-first for static assets
  if (url.pathname.startsWith("/static/") || url.pathname === "/manifest.webmanifest"){
    e.respondWith(
      caches.match(req).then(hit => hit || fetch(req).then(resp => {
        const copy = resp.clone();
        caches.open(CACHE).then(c => c.put(req, copy)).catch(()=>{});
        return resp;
      }).catch(() => hit))
    );
  } else {
    e.respondWith(
      fetch(req).then(resp => {
        if (resp.ok && req.headers.get("accept")?.includes("text/html")){
          const copy = resp.clone();
          caches.open(CACHE).then(c => c.put(req, copy)).catch(()=>{});
        }
        return resp;
      }).catch(() => caches.match(req).then(hit => hit || caches.match("/")))
    );
  }
});
