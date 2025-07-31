document.getElementById("checkDeals").onclick = async () => {
  chrome.runtime.sendMessage({ action: "run_ai_check" }, response => {
    document.getElementById("result").innerText = response?.message || "No response";
  });
};
