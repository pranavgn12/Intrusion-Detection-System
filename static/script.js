const historyLimit = 120;

const chartState = {
    samples: [],
    featureOrder: [],
    featureMax: {},
    detectionCounts: {}
};

function asNumber(value) {
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
}

function ensureFeatureOrder(features) {
    for (const key of Object.keys(features)) {
        if (!chartState.featureOrder.includes(key)) {
            chartState.featureOrder.push(key);
        }
    }
}

function addSample(data) {
    const cleanFeatures = {};

    for (const [key, value] of Object.entries(data.features || {})) {
        const n = asNumber(value);
        if (n === null) continue;

        cleanFeatures[key] = n;

        if (chartState.featureMax[key] === undefined) {
            chartState.featureMax[key] = n;
        } else {
            chartState.featureMax[key] = Math.max(chartState.featureMax[key], n);
        }
    }

    ensureFeatureOrder(cleanFeatures);

    const prediction = data.prediction || "Unknown";

    chartState.samples.push({
        ts: data.timestamp ? new Date(data.timestamp).getTime() : Date.now(),
        features: cleanFeatures,
        prediction
    });

    if (chartState.samples.length > historyLimit) {
        chartState.samples.shift();
    }

    if (prediction !== "Nothing" && prediction !== "Waiting..." && prediction !== "") {
        chartState.detectionCounts[prediction] =
            (chartState.detectionCounts[prediction] || 0) + 1;
    }
}

async function startScript(name) {
    const response = await fetch("/start", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name })
    });

    const data = await response.json();
    addLog(`[START] ${name} -> ${data.status}`);
}

async function stopScript(name) {
    const response = await fetch("/stop", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ name })
    });

    const data = await response.json();
    addLog(`[STOP] ${name} -> ${data.status}`);
}

function addLog(message) {
    const logs = document.getElementById("logs");
    const line = document.createElement("div");

    line.className = "log-line";
    line.innerText = `[${new Date().toLocaleTimeString()}] ${message}`;

    logs.prepend(line);

    while (logs.children.length > 25) {
        logs.removeChild(logs.lastChild);
    }
}

function setupCanvas(canvas) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    const targetWidth = Math.max(1, Math.floor(rect.width * dpr));
    const targetHeight = Math.max(1, Math.floor(rect.height * dpr));

    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
        canvas.width = targetWidth;
        canvas.height = targetHeight;
    }

    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    return {
        ctx,
        width: rect.width,
        height: rect.height
    };
}

function drawAxes(ctx, width, height, padding, yMax) {
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;

    ctx.strokeStyle = "#b8b8b8";
    ctx.lineWidth = 1;
    ctx.font = "12px sans-serif";
    ctx.fillStyle = "#707070";

    const ticks = 5;
    for (let i = 0; i <= ticks; i++) {
        const y = padding.top + (plotHeight * i) / ticks;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(width - padding.right, y);
        ctx.stroke();

        const val = yMax - (yMax * i) / ticks;
        ctx.fillText(val.toFixed(1), 6, y + 4);
    }

    ctx.fillText("time →", width - 50, height - 8);

    return { plotWidth, plotHeight };
}

function renderFeatureChart() {
    const canvas = document.getElementById("feature-chart");
    const meta = document.getElementById("feature-chart-meta");
    const legend = document.getElementById("feature-legend");
    if (!canvas) return;

    const { ctx, width, height } = setupCanvas(canvas);
    ctx.clearRect(0, 0, width, height);

    const padding = { top: 20, right: 20, bottom: 30, left: 48 };

    if (chartState.samples.length === 0) {
        ctx.font = "16px sans-serif";
        ctx.fillStyle = "#666";
        ctx.fillText("Waiting for live data...", 20, 30);
        meta.innerText = "Waiting for live data...";
        legend.innerHTML = "";
        return;
    }

    const features = chartState.featureOrder.filter(feature =>
        chartState.samples.some(sample => sample.features[feature] !== undefined)
    );

    const allValues = [];
    for (const sample of chartState.samples) {
        for (const feature of features) {
            const v = sample.features[feature];
            if (typeof v === "number") {
                allValues.push(v);
            }
        }
    }

    const globalMax = Math.max(1, ...allValues);
    const yMax = globalMax * 1.1;

    const { plotWidth, plotHeight } = drawAxes(ctx, width, height, padding, yMax);

    const samples = chartState.samples;
    const count = samples.length;

    const xForIndex = (i) => {
        if (count === 1) return padding.left + plotWidth / 2;
        return padding.left + (i / (count - 1)) * plotWidth;
    };

    const yForValue = (value) => {
        const ratio = value / yMax;
        return padding.top + (1 - ratio) * plotHeight;
    };

    const palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf", "#e41a1c", "#377eb8",
        "#4daf4a", "#984ea3", "#ff7f00", "#a65628"
    ];

    features.forEach((feature, index) => {
        const color = palette[index % palette.length];
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();

        let started = false;

        samples.forEach((sample, i) => {
            const value = sample.features[feature];
            if (typeof value !== "number") return;

            const x = xForIndex(i);
            const y = yForValue(value);

            if (!started) {
                ctx.moveTo(x, y);
                started = true;
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();
    });

    meta.innerText =
        `Points: ${samples.length} | Tracked features: ${features.length}`;

    legend.innerHTML = features.map((feature, index) => {
        const color = palette[index % palette.length];
        return `
            <div class="legend-item">
                <span class="legend-swatch" style="background:${color}"></span>
                <span>${feature}</span>
            </div>
        `;
    }).join("");
}

function renderDetectionChart() {
    const canvas = document.getElementById("detection-chart");
    const meta = document.getElementById("detection-meta");
    if (!canvas) return;

    const entries = Object.entries(chartState.detectionCounts)
        .filter(([label]) => label !== "Nothing")
        .sort((a, b) => b[1] - a[1]);

    const { ctx, width, height } = setupCanvas(canvas);
    ctx.clearRect(0, 0, width, height);

    if (entries.length === 0) {
        ctx.font = "14px sans-serif";
        ctx.fillStyle = "#666";
        ctx.fillText("No detections yet", 20, 30);
        meta.innerText = "No detections yet";
        return;
    }

    const padding = { top: 18, right: 18, bottom: 18, left: 120 };
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;

    const maxCount = Math.max(...entries.map(([, count]) => count), 1);
    const rowGap = 10;
    const rowHeight = Math.max(20, (plotHeight - rowGap * (entries.length - 1)) / entries.length);

    const palette = [
        "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
        "#59a14f", "#edc948", "#b07aa1", "#ff9da7",
        "#9c755f", "#bab0ab", "#1b9e77", "#d95f02"
    ];

    ctx.font = "13px sans-serif";
    ctx.textBaseline = "middle";

    entries.forEach(([label, count], index) => {
        const y = padding.top + index * (rowHeight + rowGap);
        const barWidth = (count / maxCount) * plotWidth;
        const color = palette[index % palette.length];

        ctx.fillStyle = "#d7d7d7";
        ctx.textAlign = "right";
        ctx.fillText(label, padding.left - 10, y + rowHeight / 2);

        ctx.fillStyle = color;
        ctx.fillRect(padding.left, y, barWidth, rowHeight);

        ctx.fillStyle = "#d7d7d7";
        ctx.textAlign = "left";
        ctx.fillText(String(count), padding.left + barWidth + 2, y + rowHeight / 2);
    });

    const total = entries.reduce((sum, [, count]) => sum + count, 0);
    meta.innerText = `Total detections: ${total}`;
}

function renderCurrentFeatureList(features = {}) {
    const featureArea = document.getElementById("feature-area");
    if (!featureArea) return;

    const keys = Object.keys(features);

    if (keys.length === 0) {
        featureArea.innerHTML = "<div>No features received</div>";
        return;
    }

    featureArea.innerHTML = keys.map((key) => `
        <div class="feature-row">
            <span><b>${key}</b></span>
            <span>${features[key]}</span>
        </div>
    `).join("");
}

async function fetchLiveData() {
    try {
        const response = await fetch("/live_data", {
            cache: "no-store"
        });

        const data = await response.json();

        document.getElementById("prediction-label").innerText = data.prediction;

        const topConfidence = data.confidence?.[data.prediction] || 0;
        document.getElementById("prediction-confidence").innerText =
            `Confidence: ${topConfidence}%`;

        const confidenceList = document.getElementById("confidence-list");

confidenceList.innerHTML = "";

const sortedConfidence =
    Object.entries(data.confidence || {})
    .sort((a, b) => b[1] - a[1]);

sortedConfidence.forEach(([cls, val]) => {

    const div = document.createElement("div");

    div.className = "confidence-item confidence-bar-item";

    div.innerHTML = `
        <div class="confidence-bar-bg">

            <div
                class="confidence-bar-fill"
                style="width:${val}%"
            ></div>

            <div class="confidence-bar-content">
                <span class="confidence-name">
                    ${cls}
                </span>

                <span class="confidence-value">
                    ${val}%
                </span>
            </div>

        </div>
    `;

    confidenceList.appendChild(div);
});

        addSample(data);
        renderFeatureChart();
        renderDetectionChart();
        renderCurrentFeatureList(data.features || {});
    } catch (err) {
        console.log(err);
    }
}

window.addEventListener("resize", () => {
    renderFeatureChart();
    renderDetectionChart();
});

setInterval(fetchLiveData, 1000);
fetchLiveData();
