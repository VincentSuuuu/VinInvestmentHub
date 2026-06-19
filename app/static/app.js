let latestPayload = null;

const fields = {
  sourceType: document.getElementById("source-type"),
  theme: document.getElementById("suggested-theme"),
  geography: document.getElementById("suggested-geography"),
  assetClass: document.getElementById("suggested-asset-class"),
  entities: document.getElementById("suggested-entities"),
  taxonomyL1: document.getElementById("taxonomy-l1"),
  taxonomyL2: document.getElementById("taxonomy-l2"),
  taxonomyL3: document.getElementById("taxonomy-l3"),
  confidence: document.getElementById("confidence"),
  status: document.getElementById("classification-status"),
  reason: document.getElementById("classification-reason"),
};

const status = document.getElementById("status");
const rawJson = document.getElementById("raw-json");

function setStatus(message) {
  status.textContent = message;
}

function toCsv(values) {
  return Array.isArray(values) ? values.join(", ") : "";
}

function fromCsv(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function populateReviewForm(payload) {
  const classification = payload.classification || {};
  fields.sourceType.value = classification.source_type || "";
  fields.theme.value = toCsv(classification.theme);
  fields.geography.value = toCsv(classification.geography);
  fields.assetClass.value = toCsv(classification.asset_class);
  fields.entities.value = toCsv(classification.entities);
  fields.taxonomyL1.value = toCsv(classification.taxonomy_l1);
  fields.taxonomyL2.value = toCsv(classification.taxonomy_l2);
  fields.taxonomyL3.value = toCsv(classification.taxonomy_l3);
  fields.confidence.value = classification.confidence || "Low";
  fields.status.value = classification.classification_status || "Needs Review";
  fields.reason.value = classification.reason || "";
  rawJson.textContent = JSON.stringify(payload, null, 2);
}

function buildEditedPayload() {
  const payload = structuredClone(latestPayload);
  payload.classification.source_type = fields.sourceType.value;
  payload.classification.theme = fromCsv(fields.theme.value);
  payload.classification.geography = fromCsv(fields.geography.value);
  payload.classification.asset_class = fromCsv(fields.assetClass.value);
  payload.classification.entities = fromCsv(fields.entities.value);
  payload.classification.taxonomy_l1 = fromCsv(fields.taxonomyL1.value);
  payload.classification.taxonomy_l2 = fromCsv(fields.taxonomyL2.value);
  payload.classification.taxonomy_l3 = fromCsv(fields.taxonomyL3.value);
  payload.classification.confidence = fields.confidence.value;
  payload.classification.classification_status = fields.status.value;
  payload.classification.needs_review = fields.status.value === "Needs Review" || fields.confidence.value === "Low";
  payload.classification.reason = fields.reason.value;
  return payload;
}

document.getElementById("classify").addEventListener("click", async () => {
  const payload = {
    title: document.getElementById("title").value,
    url: document.getElementById("url").value,
    text: document.getElementById("text").value,
  };

  setStatus("Analyzing source...");
  const response = await fetch("/api/classify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  latestPayload = await response.json();
  populateReviewForm(latestPayload);
  document.getElementById("sync").disabled = !response.ok;
  setStatus(response.ok ? "Review suggestions before syncing." : "Classification failed.");
});

document.getElementById("sync").addEventListener("click", async () => {
  if (!latestPayload) return;
  const editedPayload = buildEditedPayload();
  setStatus("Syncing suggested fields to Notion...");
  const response = await fetch("/api/sync", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(editedPayload),
  });
  const result = await response.json();
  rawJson.textContent = JSON.stringify(result, null, 2);
  setStatus(response.ok ? "Synced to Notion." : "Sync failed.");
});
