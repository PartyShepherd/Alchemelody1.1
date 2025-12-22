const PLANETS = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"];
const PLANET_SOUNDS = {};
PLANETS.forEach(planet => {
    PLANET_SOUNDS[planet] = `/static/sounds/${planet}.wav`;
});

self.addEventListener('install', event => {
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    self.clients.claim();
});

// Background alarm check every minute
setInterval(async () => {
    const clientsList = await self.clients.matchAll({includeUncontrolled: true});
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    
    // Simple planetary hour check approximation (replace with exact calculation if needed)
    const planetIndex = hours % 7;
    const planet = PLANETS[planetIndex];

    // Fire notification for this planetary hour
    self.registration.showNotification(`Planetary Hour: ${planet}`, {
        body: `It's the hour of ${planet}`,
        icon: '/static/images/favicon.ico',
        tag: `planet-hour-${planet}`,
        renotify: true
    });

    // Try to play sound via clients
    clientsList.forEach(client => {
        client.postMessage({type: 'play-sound', planet});
    });

}, 60 * 1000); // every minute

