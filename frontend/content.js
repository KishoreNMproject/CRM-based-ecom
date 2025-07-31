// content.js
const searchTriggers = ["search", "q", "query", "keyword", "k"];

function extractSearchQuery() {
  for (const name of searchTriggers) {
    const el = document.querySelector(`input[name="${name}"]`);
    if (el && el.value && el.value.length > 3) return el.value;
  }

  const urlParams = new URLSearchParams(window.location.search);
  for (const name of searchTriggers) {
    if (urlParams.has(name) && urlParams.get(name).length > 3) {
      return urlParams.get(name);
    }
  }
  return null;
}

// ✅ Use your actual backend
const RENDER_BACKEND_URL = "https://crm-based-ecom.onrender.com/cluster-data";

// Send search query and context to backend
async function sendDataToBackend(data) {
  try {
    const response = await fetch(RENDER_BACKEND_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      console.error(`Backend API error: ${response.status} ${response.statusText}`);
      alert(`SmartShopper: Backend Error ${response.status}`);
    } else {
      const result = await response.json();
      console.log("SmartShopper: Backend responded:", result);
      // Optional: Handle/display result here
    }

  } catch (error) {
    console.error("SmartShopper: Failed to send data:", error);
    alert("SmartShopper: Backend unreachable. Try again in 30 seconds.");
  }
}

// Trigger only on relevant pages (Amazon, Flipkart, etc.)
window.addEventListener("load", () => {
  const query = extractSearchQuery();
  if (query) {
    const data = {
      query: query,
      url: window.location.href,
      timestamp: new Date().toISOString()
    };
    sendDataToBackend(data);
  }
});
