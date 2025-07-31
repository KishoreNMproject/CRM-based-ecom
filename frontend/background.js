chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "analyze_deals") {
    const query = request.query;
    const sourceUrl = request.sourceUrl; // Received the source URL for context

    // !! WARNING: HARDCODED API KEY. Secure this for production!
    const GEMINI_API_KEY = ""; 
    const MODEL_NAME = "gemini-1.5-flash"; 

    // --- Placeholder for your Render.com Backend URL ---
    // You MUST replace this with your actual deployed Render.com backend URL
    const RENDER_BACKEND_URL = "https://your-render-backend.onrender.com/cluster-data"; 

    // Adjust the prompt to focus on general deal analysis across e-commerce networks
    const prompt = `Given the search term "${query}", provide general advice or insights on finding good deals across various e-commerce sites like Amazon, Flipkart, eBay, Newegg, and Best Buy. 
    Suggest common strategies or types of products that often have good discounts for this category.
    Keep the response concise and actionable.`;

    console.log("Background script: Received 'analyze_deals' request.");
    console.log("Background script: Query:", query);
    console.log("Background script: Source URL:", sourceUrl);
    console.log("Background script: Sending prompt to Gemini API. Model:", MODEL_NAME);
    console.log("Background script: Prompt content:", prompt.substring(0, 200) + "..."); // Log first 200 chars of prompt

    // Make the Gemini API call
    fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: prompt
          }]
        }]
      })
    })
    .then(response => {
      console.log("Background script: Received response from Gemini API. Status:", response.status);
      if (!response.ok) {
        // If response is not OK (e.g., 400, 404, 500), try to parse error message
        return response.json().then(errorData => {
          console.error("Background script: Gemini API error response:", errorData);
          throw new Error(errorData.error?.message || `HTTP error! status: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(data => {
      console.log("Background script: Parsed Gemini API response data.");
      if (data && data.candidates && data.candidates[0]?.content?.parts[0]?.text) {
        const aiResponse = data.candidates[0].content.parts[0].text;
        console.log("Background script: Successfully extracted AI response text.");
        console.log("Background script: AI Response (first 100 chars):", aiResponse.substring(0, 100) + "...");

        chrome.storage.local.set({ "last_ai_response": aiResponse }, () => {
          console.log("Background script: AI response stored in local storage.");
          sendResponse({ success: true, result: aiResponse });
        });
      } else {
        console.error("Background script: Invalid Gemini response structure or no candidates:", data);
        chrome.storage.local.set({ "last_ai_response": "Analysis failed: Invalid AI response structure." });
        sendResponse({ success: false, error: `Analysis failed: Invalid AI response. Data: ${JSON.stringify(data)}` });
      }
    })
    .catch(err => {
      console.error("Background script: Gemini fetch failed in catch block:", err);
      chrome.storage.local.set({ "last_ai_response": `Analysis failed: ${err.message || "Unknown error during fetch."}` });
      sendResponse({ success: false, error: `Analysis failed: ${err.message || "Unknown error during fetch."}` });
    });

    // --- Placeholder for sending data to your Render.com Backend ---
    // This part would typically be handled by the content script, but
    // if you want background.js to also send data (e.g., if content script
    // can't do it directly due to CSP or other reasons), you could put it here.
    // For now, content.js is handling it. If you move it here, ensure you have
    // the necessary user data available in background.js (e.g., via storage or message passing).
    /*
    sendDataToBackend({
        userId: "user_id_placeholder_from_background", 
        searchQuery: query,
        timestamp: new Date().toISOString(),
        urlVisited: sourceUrl
    });
    */

    return true; // keeps the message port alive for async response
  }
});

// Example function to send data to your Render.com backend (if called from background.js)
// This is commented out as content.js is currently handling it.
/*
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
            console.error(`Backend API error from background: ${response.status} ${response.statusText}`);
        } else {
            const result = await response.json();
            console.log("Data sent to backend from background successfully:", result);
        }
    } catch (error) {
        console.error("Error sending data to backend from background:", error);
    }
}
*/