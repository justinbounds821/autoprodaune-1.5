// bridge: BEGIN simple health check
const url = (process.env.VITE_API_URL || "http://localhost:8001") + "/health";
fetch(url)
  .then((r) => r.json())
  .then((j) => {
    console.log("[bridge] API health:", j);
    process.exit(0);
  })
  .catch((e) => {
    console.error("[bridge] API health failed:", e);
    process.exit(1);
  });
// bridge: END simple health check
