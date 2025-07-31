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

// NOTE: This URL is a placeholder. Update with your actual backend URL.
const RENDER_BACKEND_URL = "https://your-customer-data-backend.onrender.com/cluster-data"; 

// A simple way to generate a unique user ID for demonstration.
// In a real application, you would use a more robust authentication system.
function getUserId() {
  let userId = localStorage.getItem('smartshopper_user_id');
  if (!userId) {
    userId = 'user_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('smartshopper_user_id', userId);
  }
  return userId;
}

async function sendDataToBackend(data) {
    try {
        console.log("Content script: Attempting to send data to backend at:", RENDER_BACKEND_URL);
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
        const userId = getUserId();

        // This is where we collect and send the user's data
        if (query) {
            sendDataToBackend({
                userId: userId, 
                searchQuery: query,
                timestamp: new Date().toISOString(),
                urlVisited: currentUrl
            });
        }

        chrome.runtime.sendMessage({
            type: "analyze_deals",
            query: query || "general online deals",
            sourceUrl: currentUrl,
            userId: userId
        }, (responseFromBackground) => {
            console.log("Content script: Received response from background script:", responseFromBackground);
            sendResponse(responseFromBackground);
        });

        return true; 
    }
});
