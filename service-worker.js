// ---
// layout: null
//---

var staticCacheName = "np-v33";

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(staticCacheName).then(function (cache) {
            return cache.addAll([
                "/",
                "/index-data.json",
                "/css/main.css",
                "/js/ga-events.js",
                "https://cdnjs.cloudflare.com/ajax/libs/balance-text/3.3.0/balancetext.min.js",
                "https://fonts.googleapis.com/css2?family=Noto+Sans&family=Noto+Serif&display=swap",
                "https://fonts.gstatic.com/s/notosans/v6/LeFlHvsZjXu2c3ZRgBq9nFtXRa8TVwTICgirnJhmVJw.woff2",
                "https://fonts.gstatic.com/s/notoserif/v4/eCpfeMZI7q4jLksXVRWPQ_k_vArhqVIZ0nv9q090hN8.woff2",
                "https://fonts.gstatic.com/s/notoserif/v4/1_daFS3X6gkNOcmGmHl7UiEAvth_LlrfE80CYdSH47w.woff2",
                "/js/loadRemainingContent.js",
            ]);
        })
    );
});

// self.addEventListener('fetch', function(event) {
//   event.respondWith(
//     caches.match(event.request).then(function(response) {
//       //console.log("getting ", event.request, response);
//       setTimeout(otherstuff, 0);
//       return response || fetch(event.request);
//     })
//   );
// });

self.addEventListener("fetch", function (event) {
    event.respondWith(
        caches.open(staticCacheName).then(function (cache) {
            return cache.match(event.request).then(function (response) {
                var fetchPromise = fetch(event.request).then(function (
                    networkResponse
                ) {
                    // if we got a response from the cache, update the cache
                    if (response) {
                        cache.put(event.request, networkResponse.clone());
                    }
                    return networkResponse;
                });

                // respond from the cache, or the network
                return response || fetchPromise;
            });
        })
    );
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames
                    .filter(function (cacheName) {
                        return (
                            cacheName.startsWith("np-") &&
                            cacheName != staticCacheName
                        );
                    })
                    .map(function (cacheName) {
                        console.log("deleting " + cacheName);
                        return caches.delete(cacheName);
                    })
            );
        })
    );
});
