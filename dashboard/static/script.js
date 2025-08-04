async function fetchAndRender() {
    const insight = document.getElementById("insightType").value;
    const chartType = document.getElementById("chartType").value;
    const backendURL = "https://crm-based-ecom.onrender.com";  // Adjust if local

    let endpointMap = {
        rfm: "/rfm",
        shap: "/shap",
        lime: "/lime",
        rules: "/rules"
    };

    try {
        const res = await fetch(`${backendURL}${endpointMap[insight]}`);
        const data = await res.json();

        let labels = Object.keys(data);
        let values = Object.values(data);

        let chartURL = `https://quickchart.io/chart?c=${encodeURIComponent(JSON.stringify({
            type: chartType,
            data: {
                labels: labels,
                datasets: [{ label: `${insight} data`, data: values }]
            }
        }))}`;

        document.getElementById("chartImage").src = chartURL;
    } catch (err) {
        alert("Failed to fetch data or render chart.");
        console.error(err);
    }
}
