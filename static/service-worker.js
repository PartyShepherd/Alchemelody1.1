self.addEventListener('install', event => self.skipWaiting());

self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));

self.addEventListener('message', event => {
  const planet = event.data.planet;
  const soundUrl = `/static/sounds/${planet}.wav`;
  const colorEmoji = {
    "Sun":"🟧","Mars":"🟥","Venus":"🟩",
    "Jupiter":"🟪","Moon":"🟦","Mercury":"🟨","Saturn":"🟦"
  }[planet] || "🔔";

  // Show notification
  self.registration.showNotification(`Planetary Hour: ${planet}`, {
    body: `Time for ${planet}`,
    icon: '/static/images/favicon.ico'
  });

  // Play sound (works in Android PWA)
  event.waitUntil(
    fetch(soundUrl).then(r => r.arrayBuffer()).then(buf => {
      const ac = new AudioContext();
      ac.decodeAudioData(buf, decoded => {
        const src = ac.createBufferSource();
        src.buffer = decoded;
        src.connect(ac.destination);
        src.start();
      });
    })
  );
});
