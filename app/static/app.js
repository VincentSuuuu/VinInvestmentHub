let latestPayload = null;

document.getElementById("classify").addEventListener("click", async () => {
  const payload = {
    title: document.getElementById("title").value,
    url: document.getElementById("url").value,
    text: document.getElementById("text").value,
  };

  const response = await fetch("/api/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  latestPayload = await response.json();
  document.getElementById("result").textContent = JSON.stringify(latestPayload, null, 2);
  document.getElementById("sync").disabled = !response.ok;
});

document.getElementById("sync").addEventListener("click", async () => {
  if (!latestPayload) return;
  const response = await fetch("/api/sync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(latestPayload),
  });
  const result = await response.json();
  document.getElementById("result").textContent = JSON.stringify(result, null, 2);
});
