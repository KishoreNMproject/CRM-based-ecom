(async () => {
  // Helper: get country code based on domain
  function getCountryCode() {
    const hostname = window.location.hostname;
    if (hostname.includes(".in")) return "in";
    if (hostname.includes(".com")) return "us"; // or 'global'
    return "us"; // default
  }

  // Helper: extract search term from Amazon or Flipkart
  function getSearchQuery() {
    // Try Amazon
    const amazonSearchBox = document.querySelector("#twotabsearchtextbox");
    if (amazonSearchBox && amazonSearchBox.value.trim() !== "") {
      return amazonSearchBox.value.trim();
    }

    // Try Flipkart
    const flipkartSearchBox = document.querySelector("input[type='text'][title='Search for products, brands and more']");
    if (flipkartSearchBox && flipkartSearchBox.value.trim() !== "") {
      return flipkartSearchBox.value.trim();
    }

    return null;
  }

  const query = getSearchQuery();
  const country = getCountryCode();

  if (!query) {
    console.warn("No search query found on this page.");
    return;
  }

  console.log("🟢 Sending query to backend:", query, "| Country:", country);

  try {
    const response = await fetch("http://127.0.0.1:8000/priceapi-proxy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, country })
    });

    const result = await response.json();
    console.log("📦 PriceAPI Result:", result);
  } catch (err) {
    console.error("❌ Failed to fetch price data:", err);
  }
})();
