let chart;
let currentProcessId = null;
let currentStream = null;
let currentSegments = [];

const segmentColors = {
    1: "#8fd19e",
    2: "#9ecff0",
    3: "#b7a3e3",
    4: "#f2d37b",
    5: "#cfcfcf"
};

const segmentPlugin = {
    id: "segmentShading",
    beforeDatasetsDraw(chart) {
        const { ctx, chartArea, scales } = chart;
        if (!chartArea || !currentSegments.length) return;

        const xScale = scales.x;
        ctx.save();

        currentSegments.forEach(seg => {
            const startX = xScale.getPixelForValue(seg.start);
            const endX = xScale.getPixelForValue(seg.end);
            const color = segmentColors[seg.segment_id] || seg.color || "#cccccc";

            ctx.fillStyle = color + "55";
            ctx.fillRect(
                startX,
                chartArea.top,
                Math.max(endX - startX, 2),
                chartArea.bottom - chartArea.top
            );
        });

        ctx.restore();
    }
};

Chart.register(segmentPlugin);

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function setWidth(id, value) {
    const el = document.getElementById(id);
    if (el) el.style.width = Math.max(0, Math.min(100, value)) + "%";
}

function setState(id, text, type) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.className = "state " + type;
}

function createChart() {
    const ctx = document.getElementById("chart");

    chart = new Chart(ctx, {
        type: "line",
        data: {
            datasets: [
                {
                    label: "Pressure (bar)",
                    data: [],
                    borderColor: "#1f5d22",
                    backgroundColor: "transparent",
                    borderWidth: 3,
                    tension: 0.25,
                    pointRadius: 2,
                    yAxisID: "yPressure"
                },
                {
                    label: "Temperature (°C)",
                    data: [],
                    borderColor: "#b23a2e",
                    backgroundColor: "transparent",
                    borderWidth: 3,
                    tension: 0.25,
                    pointRadius: 2,
                    yAxisID: "yTemp"
                }
            ]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false,
            parsing: false,
            plugins: {
                legend: {
                    position: "bottom",
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
                    type: "linear",
                    min: 0,
                    title: {
                        display: true,
                        text: "Time (seconds)",
                        color: "#3a2417",
                        font: { weight: "bold" }
                    },
                    ticks: {
                        color: "#3a2417",
                        font: { size: 11, weight: "bold", family: "Arial" }
                    },
                    grid: { color: "rgba(90,55,25,0.18)" }
                },
                yPressure: {
                    position: "left",
                    min: 0,
                    max: 16,
                    title: {
                        display: true,
                        text: "Pressure (bar)",
                        color: "#1f5d22",
                        font: { weight: "bold" }
                    },
                    ticks: {
                        color: "#1f5d22",
                        font: { weight: "bold" }
                    },
                    grid: { color: "rgba(90,55,25,0.18)" }
                },
                yTemp: {
                    position: "right",
                    min: 78,
                    max: 102,
                    title: {
                        display: true,
                        text: "Temp (°C)",
                        color: "#b23a2e",
                        font: { weight: "bold" }
                    },
                    ticks: {
                        color: "#b23a2e",
                        font: { weight: "bold" }
                    },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
}

function resetChart() {
    chart.data.datasets[0].data = [];
    chart.data.datasets[1].data = [];
    chart.update("none");
}

function updateStates(temp, pressure, time) {
    const tempOk = temp >= 90 && temp <= 96;
    const pressureOk = pressure >= 8.5 && pressure <= 10.5;
    const timeOk = time >= 25 && time <= 30;

    setState("tempState", tempOk ? "✓ OPTIMAL" : "▲ NOT OPTIMAL", tempOk ? "optimal" : "warning");
    setState("pressureState", pressureOk ? "✓ OPTIMAL" : "▲ NOT OPTIMAL", pressureOk ? "optimal" : "warning");
    setState("timeState", timeOk ? "✓ OPTIMAL" : "▲ NOT OPTIMAL", timeOk ? "optimal" : "warning");
}

function updateStatus(score, label) {
    const statusLabel = document.getElementById("statusLabel");
    const statusIcon = document.getElementById("statusIcon");
    const confidenceFill = document.getElementById("confidenceFill");

    setText("statusLabel", label || "Unknown");

    if (score >= 75) {
        setText("statusIcon", "✓");
        setText("statusText", "Extraction looks stable.");
        if (statusLabel) statusLabel.style.color = "#1f5d22";
        if (statusIcon) {
            statusIcon.style.color = "#1f5d22";
            statusIcon.style.borderColor = "#1f5d22";
        }
        if (confidenceFill) confidenceFill.style.background = "#1f5d22";
    } else if (score >= 45) {
        setText("statusIcon", "!");
        setText("statusText", "Extraction needs some adjustment.");
        if (statusLabel) statusLabel.style.color = "#9a4a12";
        if (statusIcon) {
            statusIcon.style.color = "#9a4a12";
            statusIcon.style.borderColor = "#9a4a12";
        }
        if (confidenceFill) confidenceFill.style.background = "#9a4a12";
    } else {
        setText("statusIcon", "!");
        setText("statusText", "Extraction is outside the target range.");
        if (statusLabel) statusLabel.style.color = "#8b1e12";
        if (statusIcon) {
            statusIcon.style.color = "#8b1e12";
            statusIcon.style.borderColor = "#8b1e12";
        }
        if (confidenceFill) confidenceFill.style.background = "#8b1e12";
    }
}

function updateDashboard(data) {
    const temp = Number(data.temperature?.current ?? 0);
    const pressure = Number(data.pressure?.current ?? 0);
    const time = Number(data.extractionTime?.current ?? data.elapsed_seconds ?? 0);
    const score = Number(data.prediction?.quality_score ?? 0);
    const flowRate = Number(data.flowRate?.current ?? 0);
    const label = data.prediction?.quality_label || "Unknown";
    const feedback = data.prediction?.feedback || ["Waiting for feedback."];

    setText("temp", temp.toFixed(1));
    setText("pressure", pressure.toFixed(2));
    setText("time", time.toFixed(1));
    setText("confidence", Math.round(score) + "%");
    setText("flowRate", flowRate.toFixed(2));

    setWidth("tempBar", temp);
    setWidth("pressureBar", (pressure / 12) * 100);
    setWidth("timeBar", (time / 30) * 100);
    setWidth("confidenceFill", score);

    setText("tip", feedback.join(" "));
    updateStates(temp, pressure, time);
    updateStatus(score, label);

    if (data.process_type) {
        setText("processType", "Process Type: " + data.process_type);
    } else if (data.segment_label) {
        setText("processType", "Segment: " + data.segment_label);
    }
}

function addPoint(data) {
    const x = Number(data.elapsed_seconds ?? 0);

    chart.data.datasets[0].data.push({
        x: x,
        y: Number(data.reading?.pressure ?? data.pressure?.current ?? 0)
    });

    chart.data.datasets[1].data.push({
        x: x,
        y: Number(data.reading?.temperature ?? data.temperature?.current ?? 0)
    });

    chart.update("none");
}

async function loadProcesses() {
    const response = await fetch("/api/process_ids");
    const data = await response.json();

    const select = document.getElementById("processSelect");
    select.innerHTML = "";

    data.process_ids.forEach(id => {
        const option = document.createElement("option");
        option.value = id;
        option.textContent = "Process " + id;
        select.appendChild(option);
    });

    currentProcessId = data.process_ids[0];
    select.value = currentProcessId;
    await loadProcessSummary(currentProcessId);
}

async function loadProcessSummary(processId) {
    const response = await fetch(`/api/process/${processId}/summary`);
    if (!response.ok) return;

    const summary = await response.json();
    currentSegments = summary.segments || [];

    setText("processType", "Process Type: " + summary.process_type);

    const chartBox = document.querySelector(".chart-box h3");
    if (chartBox) {
        chartBox.textContent =
            `Extraction Graph — Brew window: ${summary.brew_duration}s`;
    }

    chart.update("none");
}

function closeCurrentStream() {
    if (currentStream) {
        currentStream.close();
        currentStream = null;
    }
}

async function startSimulation() {
    if (!currentProcessId) return;

    closeCurrentStream();
    resetChart();
    await loadProcessSummary(currentProcessId);

    currentStream = new EventSource(`/api/process/${currentProcessId}/stream`);

    currentStream.onmessage = function (event) {
        const data = JSON.parse(event.data);
        updateDashboard(data);
        addPoint(data);
    };

    currentStream.onerror = function () {
        closeCurrentStream();
    };
}

function startRealLive() {
    closeCurrentStream();
    resetChart();
    currentSegments = [];

    currentStream = new EventSource("/api/live/stream");

    currentStream.onmessage = function (event) {
        const data = JSON.parse(event.data);
        updateDashboard(data);
        addPoint(data);
    };
}

async function resetLive() {
    closeCurrentStream();
    resetChart();
    currentSegments = [];

    await fetch("/api/live/reset", { method: "POST" });

    setText("temp", "-");
    setText("pressure", "-");
    setText("time", "-");
    setText("confidence", "-");
    setText("flowRate", "-");
    setText("tip", "Waiting for live data...");
    setText("statusLabel", "Waiting...");
    setText("statusText", "Waiting for incoming data.");
    setText("statusIcon", "!");
}

createChart();
loadProcesses();

document.getElementById("processSelect").addEventListener("change", async function () {
    currentProcessId = this.value;
    await loadProcessSummary(currentProcessId);
});

document.getElementById("simulateBtn").addEventListener("click", startSimulation);
document.getElementById("realLiveBtn").addEventListener("click", startRealLive);
document.getElementById("resetBtn").addEventListener("click", resetLive);
