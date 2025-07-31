
// background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "analyze_deals") {
    const query = request.query;
    const sourceUrl = request.sourceUrl;

    // --- IMPORTANT: Replace this with your actual Render.com backend's proxy endpoint URL ---
    const RENDER_GEMINI_PROXY_URL = "[https://crm-based-ecom.onrender.com/gemini-proxy](https://crm-based-ecom.onrender.com/gemini-proxy)"; 

    console.log("Background script: Received 'analyze_deals' request.");
    console.log("Background script: Sending request to Render.com proxy for Gemini analysis.");

    fetch(RENDER_GEMINI_PROXY_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        query: query,
        sourceUrl: sourceUrl,
      })
    })
    .then(response => {
      console.log("Background script: Received response from Render.com proxy. Status:", response.status);
      if (!response.ok) {
        return response.json().then(errorData => {
          console.error("Background script: Render.com proxy error response:", errorData);
          throw new Error(errorData.error?.message || `HTTP error from proxy! status: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(data => {
      console.log("Background script: Parsed response data from Render.com proxy.");
      if (data && data.candidates && data.candidates[0]?.content?.parts[0]?.text) {
        const aiResponse = data.candidates[0].content.parts[0].text;
        console.log("Background script: Successfully extracted AI response text from proxy response.");
        
        chrome.storage.local.set({ "last_ai_response": aiResponse });
        sendResponse({ success: true, result: aiResponse });
      } else {
        console.error("Background script: Invalid response structure from Render.com proxy:", data);
        const errorMessage = `Analysis failed: Invalid response from proxy. Data: ${JSON.stringify(data)}`;
        chrome.storage.local.set({ "last_ai_response": errorMessage });
        sendResponse({ success: false, error: errorMessage });
      }
    })
    .catch(err => {
      console.error("Background script: Fetch to Render.com proxy failed in catch block:", err);
      const errorMessage = `Analysis failed: ${err.message || "Unknown error during proxy fetch."}`;
      chrome.storage.local.set({ "last_ai_response": errorMessage });
      sendResponse({ success: false, error: errorMessage });
    });

    return true; 
  }
});
