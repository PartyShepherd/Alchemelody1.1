self.addEventListener('install', event => {
    self.skipWaiting();
    console.log("Service Worker installed");
});

self.addEventListener('activate', event => {
    console.log("Service Worker activated");
});

function playPlanetAlarm(planet, color) {
    self.registration.showNotification("Planetary Hour", {
        body: `It's now ${planet}'s hour!`,
        icon: `/static/images/${planet}.png`,
        badge: `/static/images/${planet}.png`,
        vibrate: [200, 100, 200],
        tag: planet
    });
}

self.addEventListener('periodicsync', event => {
    if (event.tag === 'check-hour') {
        event.waitUntil(checkNextHour());
    }
});

// Fallback: use setInterval in SW for testing
setInterval(async () => {
    const response = await fetch('/');
    const text = await response.text();
    // Here you could parse HTML for hours and trigger playPlanetAlarm
}, 60000);
