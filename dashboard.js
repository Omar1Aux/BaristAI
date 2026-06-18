let chart;
let lastTimestamp = null;

const HISTORY_URL = "http://127.0.0.1:5000/history";
const LIVE_URL = "http://127.0.0.1:5000/influx/live";

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
                    label: "Temperature (°C)",
                    data: [],
                    borderColor: "#d46f12",
                    backgroundColor: "transparent",
                    tension: 0.35,
                    borderWidth: 3,
                    pointRadius: 4
                },
                {
                    label: "Pressure (bar)",
                    data: [],
                    borderColor: "#1f5d22",
                    backgroundColor: "transparent",
                    tension: 0.35,
                    borderWidth: 3,
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                legend: {
                    labels: {
                        color: "#2b1a12",
                        font: {
                            size: 13,
                            weight: "bold",
                            family: "Arial"
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#3a2417",
                        maxRotation: 35,
                        minRotation: 35,
                        font: {
                            size: 11,
                            weight: "bold",
                            family: "Arial"
                        }
                    },
                    grid: {
                        color: "rgba(90, 55, 25, 0.18)"
                    }
                },
                y: {
                    ticks: {
                        color: "#3a2417",
                        font: {
                            size: 12,
                            weight: "bold",
                            family: "Arial"
                        }
                    },
                    grid: {
                        color: "rgba(90, 55, 25, 0.18)"
                    }
                }
            }
        }
    });
}

function updateStates(temp, pressure, time) {
    setState(
        "tempState",
        temp >= 90 && temp <= 96 ? "✓ OPTIMAL" : "▲ NOT OPTIMAL",
        temp >= 90 && temp <= 96 ? "optimal" : "warning"
    );

    setState(
        "pressureState",
        pressure >= 9 && pressure <= 10 ? "✓ OPTIMAL" : "▲ NOT OPTIMAL",
        pressure >= 9 && pressure <= 10 ? "optimal" : "warning"
    );

    setState(
        "timeState",
        time >= 25 && time <= 30 ? "✓ OPTIMAL" : "▲ NOT OPTIMAL",
        time >= 25 && time <= 30 ? "optimal" : "warning"
    );
}

function updateFeedback(temp, pressure, time, score) {
    const issues = [];

    if (temp < 90) {
        issues.push("temperature is low");
    } else if (temp > 96) {
        issues.push("temperature is high");
    }

    if (pressure < 9) {
        issues.push("pressure is low");
    } else if (pressure > 10) {
        issues.push("pressure is high");
    }

    if (time < 25) {
        issues.push("extraction time is short");
    } else if (time > 30) {
        issues.push("extraction time is long");
    }

    let tip = "Extraction looks stable.";

    if (issues.length === 1) {
        tip = "Issue detected: " + issues[0] + ".";
    } else if (issues.length > 1) {
        tip = "Issues detected: " + issues.join(", ") + ".";
    }

    if (score < 40) {
        tip += " Adjust grind size, pressure, and temperature.";
    }

    setText("tip", tip);
}

function updateStatus(score, temp, pressure, time) {
    const statusLabel = document.getElementById("statusLabel");
    const statusIcon = document.getElementById("statusIcon");
    const confidenceFill = document.getElementById("confidenceFill");

    const tempOk = temp >= 90 && temp <= 96;
    const pressureOk = pressure >= 9 && pressure <= 10;
    const timeOk = time >= 25 && time <= 30;

    if (tempOk && pressureOk && timeOk && score >= 70) {
        setText("statusLabel", "GOOD EXTRACTION");
        setText("statusText", "Your espresso is within the optimal range.");
        setText("statusIcon", "✓");

        statusLabel.style.color = "#1f5d22";
        statusIcon.style.color = "#1f5d22";
        statusIcon.style.borderColor = "#1f5d22";
        confidenceFill.style.background = "#1f5d22";
    } else if (score >= 40) {
        setText("statusLabel", "WARNING EXTRACTION");
        setText("statusText", "Some extraction values are outside the target range.");
        setText("statusIcon", "!");

        statusLabel.style.color = "#9a4a12";
        statusIcon.style.color = "#9a4a12";
        statusIcon.style.borderColor = "#9a4a12";
        confidenceFill.style.background = "#9a4a12";
    } else {
        setText("statusLabel", "POOR EXTRACTION");
        setText("statusText", "Adjust grind size, pressure, and temperature.");
        setText("statusIcon", "!");

        statusLabel.style.color = "#8b1e12";
        statusIcon.style.color = "#8b1e12";
        statusIcon.style.borderColor = "#8b1e12";
        confidenceFill.style.background = "#8b1e12";
    }
}

function updateDashboard(data) {
    const temp = Number(data.temperature.current);
    const pressure = Number(data.pressure.current);
    const time = Number(data.extractionTime.current);
    const score = Number(data.prediction.quality_score);

    setText("temp", temp);
    setText("pressure", pressure);
    setText("time", time);
    setText("confidence", Math.round(score) + "%");

    setWidth("tempBar", Math.min(100, temp));
    setWidth("pressureBar", Math.min(100, (pressure / 12) * 100));
    setWidth("timeBar", Math.min(100, (time / 30) * 100));
    setWidth("confidenceFill", Math.max(0, Math.min(100, score)));

    updateStates(temp, pressure, time);
    updateFeedback(temp, pressure, time, score);
    updateStatus(score, temp, pressure, time);
}

function addPointToChart(data) {
    if (!chart) return;

    const label = data.time
        ? new Date(data.time).toLocaleTimeString()
        : new Date().toLocaleTimeString();

    const temp = Number(data.temperature.current);
    const pressure = Number(data.pressure.current);

    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(temp);
    chart.data.datasets[1].data.push(pressure);

    if (chart.data.labels.length > 30) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
        chart.data.datasets[1].data.shift();
    }

    chart.update("none");
}

async function loadInitialHistory() {
    try {
        const response = await fetch(HISTORY_URL);

        if (!response.ok) {
            console.warn("No history data yet.");
            return;
        }

        const history = await response.json();

        if (!history.length) {
            console.warn("History is empty.");
            return;
        }

        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.data.datasets[1].data = [];

        history.forEach(item => {
            addPointToChart(item);
        });

        const latest = history[history.length - 1];
        lastTimestamp = latest.time;
        updateDashboard(latest);

    } catch (error) {
        console.error("Initial history error:", error);
    }
}

async function loadLiveData() {
    try {
        const response = await fetch(LIVE_URL);

        if (!response.ok) {
            console.warn("No live InfluxDB data yet.");
            return;
        }

        const data = await response.json();

        updateDashboard(data);

        if (data.time && data.time === lastTimestamp) {
            return;
        }

        lastTimestamp = data.time;
        addPointToChart(data);

    } catch (error) {
        console.error("Live update error:", error);
    }
}

createChart();
loadInitialHistory();
setInterval(loadLiveData, 1000);