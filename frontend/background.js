chrome.runtime.onMessage.addListener(async (request, sender, sendResponse) => {
  if (request.action === "run_ai_check") {
    chrome.tabs.query({ active: true, currentWindow: true }, async tabs => {
      const tab = tabs[0];
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: extractQueryAndRunAI
      }, async results => {
        if (results && results[0] && results[0].result) {
          const aiSummary = results[0].result;
          sendResponse({ message: aiSummary });
        } else {
          sendResponse({ message: "No result from AI" });
        }
      });
    });
    return true; // async
  }
});

async function extractQueryAndRunAI() {
  const title = document.title;
  const query = title.split("|")[0].trim(); // Extract search query from tab title
  const prompt = `Suggest me the best-rated, lowest-priced product with this query: "${query}". Return product name, price, store, rating, shipping info, and URL.`;

  const response = await fetch("https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyD1d7JgdVpJ5JsaPEdh5XAuG6pzC27ZLiU", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
  });

  const result = await response.json();
  const text = result?.candidates?.[0]?.content?.parts?.[0]?.text || "No summary";

  // Send user behavior to backend
  await fetch("https://crm-based-ecom.onrender.com/log_user_action", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: "anonymous_user",  // Ideally get from storage
      query: query,
      ai_response: text,
      timestamp: new Date().toISOString()
    })
  });

  return text;
}
