const CACHE = 'tdapp-v1';

// Assets to pre-cache (shell assets that rarely change)
const PRECACHE = [
  '/',
  '/zanex/css/style.css',
  '/zanex/css/icons.css',
  '/zanex/js/jquery.min.js',
  '/zanex/plugins/bootstrap/js/bootstrap.min.js',
  '/zanex/js/custom.js',
  '/zanex/plugins/sweet-alert/sweetalert.min.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for /convert (must reach server); cache-first for everything else
self.addEventListener('fetch', e => {
  if (e.request.url.includes('/convert')) {
    // Always go to network for file conversion
    e.respondWith(fetch(e.request));
    return;
  }
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(resp => {
        if (resp && resp.status === 200 && resp.type !== 'opaque') {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return resp;
      });
    })
  );
});
