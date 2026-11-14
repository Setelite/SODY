const CACHE='sody-v34';const ASSETS=['./index.html','./manifest.webmanifest?v=21','./icons/icon-192.png','./icons/icon-512.png','./assets/sody-bottle.webp','./assets/sody-molecular-woman.webp','./sody-structure.css?v=34','./assets/sody-glass-capsules-v32.webp?art=32','./assets/sody-woman-cut.webp?art=20'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',event=>{event.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(key=>key.startsWith('sody-')&&key!==CACHE).map(key=>caches.delete(key)))),self.clients.claim()]))});
self.addEventListener('fetch',event=>{
 const request=event.request;
 if(request.method!=='GET'||new URL(request.url).origin!==self.location.origin)return;
 if(request.mode==='navigate'||request.destination==='document'){
   event.respondWith(fetch(request,{cache:'no-store'}).catch(async()=>await caches.match('./index.html')));
   return;
 }
 event.respondWith(caches.match(request).then(cached=>cached||fetch(request).then(response=>{
   if(response.ok){const duplicate=response.clone();event.waitUntil(caches.open(CACHE).then(cache=>cache.put(request,duplicate)))}
   return response;
 })));
});
