let chart;

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

function setWidth(id, value) {
    const element = document.getElementById(id);
    if (element) element.style.width = value + "%";
}

function setState(id, text, type) {
    const element = document.getElementById(id);
    if (!element) return;

    element.textContent = text;
    element.className = "state " + type;
}

function createChart() {
    const ctx = document.getElementById("chart");

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Temperature",
                    data: [],
                    borderColor: "#d96b2b",
                    backgroundColor: "transparent",
                    tension: 0.35,
                    borderWidth: 3
                },
                {
                    label: "Pressure",
                    data: [],
                    borderColor: "#90c77b",
                    backgroundColor: "transparent",
                    tension: 0.35,
                    borderWidth: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#f5e6d3"
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#f5e6d3",
                        maxRotation: 35,
                        minRotation: 35
                    },
                    grid: {
                        color: "rgba(255,255,255,0.12)"
                    }
                },
                y: {
                    ticks: {
                        color: "#f5e6d3"
                    },
                    grid: {
                        color: "rgba(255,255,255,0.12)"
                    }
                }
            }
        }
    });
}

async function loadData() {
    try {
        const response = await fetch("http://127.0.0.1:5000/live/predict/9");
        const data = await response.json();

        const temp = Number(data.temperature.current);
        const pressure = Number(data.pressure.current);
        const time = Number(data.extractionTime.current);
        const score = Number(data.prediction.quality_score);
        const label = data.prediction.quality_label;

        setText("temp", temp);
        setText("pressure", pressure);
        setText("time", time);
        setText("confidence", Math.round(score) + "%");

        setWidth("tempBar", Math.min(100, temp));
        setWidth("pressureBar", Math.min(100, (pressure / 12) * 100));
        setWidth("timeBar", Math.min(100, (time / 30) * 100));
        setWidth("confidenceFill", Math.max(0, Math.min(100, score)));

        if (temp >= 90 && temp <= 96) {
            setState("tempState", "✓ OPTIMAL", "optimal");
        } else {
            setState("tempState", "▲ NOT OPTIMAL", "warning");
        }

        if (pressure >= 9 && pressure <= 10) {
            setState("pressureState", "✓ OPTIMAL", "optimal");
        } else {
            setState("pressureState", "▲ NOT OPTIMAL", "warning");
        }

        if (time >= 25 && time <= 30) {
            setState("timeState", "✓ OPTIMAL", "optimal");
        } else {
            setState("timeState", "▲ NOT OPTIMAL", "warning");
        }

        let tip = "Extraction looks stable.";

        if (temp < 90) {
            tip = "Temperature is low. Increase boiler temperature.";
        }

        if (pressure < 9) {
            tip = "Pressure is low. Adjust grind size or pump pressure.";
        }

        if (score < 40) {
            tip = "Poor extraction. Adjust grind size, pressure, and temperature.";
        }

        setText("tip", tip);

        const statusLabel = document.getElementById("statusLabel");
        const statusIcon = document.getElementById("statusIcon");
        const confidenceFill = document.getElementById("confidenceFill");

        if (score >= 70) {
            setText("statusLabel", "GOOD EXTRACTION");
            setText("statusText", "Your espresso is within the optimal range.");
            setText("statusIcon", "✓");

            statusLabel.style.color = "#90c77b";
            statusIcon.style.color = "#90c77b";
            statusIcon.style.borderColor = "#90c77b";
            confidenceFill.style.background = "#90c77b";

        } else if (score >= 40) {
            setText("statusLabel", "WARNING");
            setText("statusText", "Extraction needs some adjustment.");
            setText("statusIcon", "!");

            statusLabel.style.color = "#d96b2b";
            statusIcon.style.color = "#d96b2b";
            statusIcon.style.borderColor = "#d96b2b";
            confidenceFill.style.background = "#d96b2b";

        } else {
            setText("statusLabel", "POOR EXTRACTION");
            setText("statusText", "Adjust grind size and pressure.");
            setText("statusIcon", "!");

            statusLabel.style.color = "#d96b2b";
            statusIcon.style.color = "#d96b2b";
            statusIcon.style.borderColor = "#d96b2b";
            confidenceFill.style.background = "#d96b2b";
        }

        if (chart) {
            const now = new Date().toLocaleTimeString();

            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(temp);
            chart.data.datasets[1].data.push(pressure);

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