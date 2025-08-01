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
  const url = window.location.href;

  // Amazon
  const amazonSearchBox = document.querySelector("#twotabsearchtextbox");
  if (amazonSearchBox && amazonSearchBox.value.trim() !== "") {
    return amazonSearchBox.value.trim();
  }

  // Flipkart
  const flipkartSearchBox = document.querySelector("input[type='text'][title='Search for products, brands and more']");
  if (flipkartSearchBox && flipkartSearchBox.value.trim() !== "") {
    return flipkartSearchBox.value.trim();
  }

  // Custom CRM site (adapt this selector to your site's actual HTML)
  const crmSearchBox = document.querySelector("input[name='search']") || document.querySelector("input[type='search']");
  if (crmSearchBox && crmSearchBox.value.trim() !== "") {
    return crmSearchBox.value.trim();
  }

  // Try to extract from heading or title
  const h1 = document.querySelector("h1")?.innerText;
  if (h1 && h1.trim().length > 3) return h1.trim();

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
    const response = await fetch("https://crm-based-ecom.onrender.com/priceapi-proxy", {
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
