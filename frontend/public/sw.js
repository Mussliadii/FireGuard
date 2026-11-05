self.addEventListener("push", (event) => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || "FireGuard AI";
  const options = {
    body: data.body || "New alert available.",
    icon: "/icon.svg",
    data: { lat: data.lat, lon: data.lon },
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow("/"));
});
