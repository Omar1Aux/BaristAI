let chart;
let startTime = Date.now();

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function setWidth(id, value) {
    const el = document.getElementById(id);
    if (el) el.style.width = value + "%";
}

function createChart() {
    const ctx = document.getElementById("chart");
    if (!ctx) return;

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                { label: "Temperature", data: [], borderColor: "#ef4444", tension: 0.35, borderWidth: 3 },
                { label: "Pressure", data: [], borderColor: "#22c55e", tension: 0.35, borderWidth: 3 },
                { label: "Flow Rate", data: [], borderColor: "#38bdf8", tension: 0.35, borderWidth: 3 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: "white" } } },
            scales: {
                x: { ticks: { color: "white" }, grid: { color: "#334155" } },
                y: { ticks: { color: "white" }, grid: { color: "#334155" } }
            }
        }
    });
}

function setState(id, text, type) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.className = "state " + type;
}

async function loadData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/live/predict/9");
        const data = await response.json();

        const temp = Number(data.temperature.current);
        const pressure = Number(data.pressure.current);
        const flow = Number(data.flowRate.current);
        const score = Number(data.prediction.quality_score);
        const label = data.prediction.quality_label;
        const extractionTime = Math.floor((Date.now() - startTime) / 1000) % 31;

        setText("temp", temp);
        setText("pressure", pressure);
        setText("flow", flow);
        setText("score", score);
        setText("label", label);
        setText("time", extractionTime + " s");

        setWidth("tempBar", Math.min(100, temp));
        setWidth("pressureBar", Math.min(100, (pressure / 12) * 100));
        setWidth("timeBar", Math.min(100, (extractionTime / 30) * 100));
        setWidth("flowBar", Math.min(100, (flow / 10) * 100));

        setState("tempState", temp >= 90 && temp <= 96 ? "✓ OPTIMAL" : "⚠ NOT OPTIMAL", temp >= 90 && temp <= 96 ? "optimal" : "warning");
        setState("pressureState", pressure >= 9 && pressure <= 10 ? "✓ OPTIMAL" : "⚠ NOT OPTIMAL", pressure >= 9 && pressure <= 10 ? "optimal" : "warning");
        setState("timeState", extractionTime >= 25 && extractionTime <= 30 ? "✓ OPTIMAL" : "⚠ NOT OPTIMAL", extractionTime >= 25 && extractionTime <= 30 ? "optimal" : "warning");
        setState("flowState", flow > 0 && flow <= 8 ? "✓ OPTIMAL" : "⚠ NOT OPTIMAL", flow > 0 && flow <= 8 ? "optimal" : "warning");

        let tip = "Extraction looks stable.";
        if (temp < 90) tip = "Temperature is slightly low. Increase boiler temperature.";
        if (pressure < 9) tip = "Pressure is low. Check pump pressure or grind size.";
        if (flow > 8) tip = "Flow rate is high. Try using a finer grind size.";
        if (score < 40) tip = "Poor extraction. Adjust grind size, pressure, and temperature.";
        setText("tip", tip);

        if (score >= 70) {
            setText("statusLabel", "GOOD EXTRACTION");
            setText("statusText", "Your espresso is mostly within the optimal range.");
            setText("statusIcon", "✓");
        } else if (score >= 40) {
            setText("statusLabel", "WARNING");
            setText("statusText", "Extraction needs some adjustment.");
            setText("statusIcon", "!");
        } else {
            setText("statusLabel", "POOR EXTRACTION");
            setText("statusText", "Adjust grind size and pressure.");
            setText("statusIcon", "!");
        }

        setText("confidence", Math.round(score) + "%");
        setWidth("confidenceFill", Math.max(0, Math.min(100, score)));

        if (chart) {
            const now = new Date().toLocaleTimeString();

            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(temp);
            chart.data.datasets[1].data.push(pressure);
            chart.data.datasets[2].data.push(flow);

            if (chart.data.labels.length > 10) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => dataset.data.shift());
            }

            chart.update();
        }

    } catch (error) {
        console.error(error);
    }
}

createChart();
loadData();
setInterval(loadData, 1000);