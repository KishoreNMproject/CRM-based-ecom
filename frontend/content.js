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

// --- IMPORTANT: Replace this with your actual Render.com backend's clustering URL ---
const RENDER_BACKEND_URL = "[https://your-render-backend.onrender.com/cluster-data](https://your-render-backend.onrender.com/cluster-data)"; 

async function sendDataToBackend(data) {
    try {
        const response = await fetch(RENDER_BACKEND_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            console.error(`Backend API error: ${response.status} ${response.statusText}`);
        } else {
            const result = await response.json();
            console.log("Data sent to backend successfully:", result);
        }
    } catch (error) {
        console.error("Error sending data to backend:", error);
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "start_deal_analysis") {
        console.log("Content script: Received start_deal_analysis message from popup.");
        
        const query = extractSearchQuery();
        const currentUrl = window.location.href;

        if (query) {
            sendDataToBackend({
                userId: "user_id_placeholder", 
                searchQuery: query,
                timestamp: new Date().toISOString(),
                urlVisited: currentUrl
            });
        }

        chrome.runtime.sendMessage({
            type: "analyze_deals",
            query: query || "general online deals",
            sourceUrl: currentUrl 
        }, (responseFromBackground) => {
            console.log("Content script: Received response from background script:", responseFromBackground);
            sendResponse(responseFromBackground);
        });

        return true; 
    }
});