document.addEventListener("DOMContentLoaded", async () => {
    try {
        // summary API を取得
        const res = await fetch("/api/Portfolio_Command_Center/summary");
        const data = await res.json();
        displaySummary(data.summary);

        // graphs
        const gres = await fetch("/api/Portfolio_Command_Center/graphs");
        const gdata = await gres.json();

        // ★ 表示順を定義
        const order = [
            "progress_rate",
            "saving_rate",
            "assets",
            "general_balance",
            "special_balance",
            "returns",
            //"general_income_expenditure",
            //"special_income_expenditure",
        ];

        order.forEach(key => {
            const figJson = gdata.graphs[key];
            if (!figJson) return; // 存在しないキーはスキップ
            let titleText = {
                "progress_rate": "<span><img src='/static/icon/star.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> FIRE Readiness</span>",
                "saving_rate": "<span><img src='/static/icon/sail.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Savings Efficiency</span>",
                "assets": "<span><img src='/static/icon/compass.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Net Worth Trajectory</span>",
                "returns": "<span><img src='/static/icon/line-chart.svg' style='height:20px; margin-right:6px; opacity:0.85;'/> Portfolio Performance</span>",
                "general_balance": "<span><img src='/static/icon/waves.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Cash Flow – Routine</span>",
                "special_balance": "<span><img src='/static/icon/lighthouse.svg' style='height:18px; margin-right:6px; opacity:0.85;'/> Cash Flow – Exceptional</span>",
            }[key] || key;

            //console.log(key);
            //console.log(figJson);

            displaySingleGraph(figJson, titleText);
        });

    } catch (err) {
        console.error("Failed to load dashboard summary:", err);
    }
});

// サイドバー下に summary を表示
function displaySummary(summary) {
    const sidebar = document.querySelector(".sidebar");

    if (!sidebar || !summary) return;

    // 既存の div がある場合はクリア
    let summaryDiv = document.getElementById("dashboard-summary");
    if (!summaryDiv) {
        summaryDiv = document.createElement("div");
        summaryDiv.id = "dashboard-summary";
        //summaryDiv.style.marginTop = "60vh";
        summaryDiv.style.fontSize = "2vh";
        sidebar.appendChild(summaryDiv);
    }

    summaryDiv.innerHTML = `
        <div style="
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 12px 16px;
            border-radius: 8px 8px 0 0;
            margin: -8px -8px 12px -8px;
            border-bottom: 2px solid #4a90e2;
        ">
            <h3 style="
                margin: 0;
                font-family: 'Montserrat', sans-serif;
                font-size: 1.1em;
                font-weight: 600;
                letter-spacing: 0.5px;
                color: #ffffff;
                text-transform: uppercase;
            ">📊 KPI Dashboard</h3>
        </div>
        <div class="summary-grid">  
            <div>Date:</div><div>${summary.latest_date}</div>
            <div>Fire Progress:</div><div>${summary.fire_progress.toLocaleString()}%</div>
            <div>Net Assets:</div><div>¥ ${summary.total_assets.toLocaleString()}</div>
            <div>Target:</div><div>¥ ${summary.total_target_assets.toLocaleString()}</div>
            <div>Difference:</div><div>¥ ${summary.difference.toLocaleString()}</div>
        </div>
    `;
}

function displaySingleGraph(figJson, titleText) {
    const main = document.getElementById("graphs-area");
    if (!main || !figJson) return;

    const wrap = document.createElement("div");
    wrap.className = "graph-container";

    // 戻るボタン作成
    const backBtn = document.createElement("button");
    backBtn.className = "back-button";
    backBtn.textContent = "Back";
    wrap.appendChild(backBtn);

    const title = document.createElement("div");
    title.className = "graph-title";
    title.innerHTML = titleText;
    wrap.appendChild(title);

    const graphDiv = document.createElement("div");
    wrap.appendChild(graphDiv);

    main.appendChild(wrap);

    const fig = typeof figJson === "string" ? JSON.parse(figJson) : figJson;

    // デフォルトのフォントサイズを保存
    const layout = fig.layout || {};
    const defaultFonts = {
        font: layout.font?.size || 12,
        title: layout.title?.font?.size || 14,
        xaxis_title: layout.xaxis?.title?.font?.size || 12,
        yaxis_title: layout.yaxis?.title?.font?.size || 12,
        xaxis_tick: layout.xaxis?.tickfont?.size || 10,
        yaxis_tick: layout.yaxis?.tickfont?.size || 10,
        legend: layout.legend?.font?.size || 14
    };

    Plotly.newPlot(graphDiv, fig.data, fig.layout, {
        responsive: true,
        displayModeBar: false,
    });

    // -----------------------------
    // フォントを画面サイズに応じて調整
    // -----------------------------
    function adjustPlotlyFont() {
        const width = window.innerWidth;
        const scale = width / 800; // 800px を基準にスケーリング
        Plotly.relayout(graphDiv, {
            'font.size': defaultFonts.font * scale,
            'title.font.size': defaultFonts.title * scale,
            'xaxis.title.font.size': defaultFonts.xaxis_title * scale,
            'yaxis.title.font.size': defaultFonts.yaxis_title * scale,
            'xaxis.tickfont.size': defaultFonts.xaxis_tick * scale,
            'yaxis.tickfont.size': defaultFonts.yaxis_tick * scale,
            'legend.font.size': defaultFonts.legend * scale
        });
    }
    function resetFonts() {
        Plotly.relayout(graphDiv, {
            "font.size": defaultFonts.font,
            "title.font.size": defaultFonts.title,
            "xaxis.title.font.size": defaultFonts.xaxis_title,
            "yaxis.title.font.size": defaultFonts.yaxis_title,
            "xaxis.tickfont.size": defaultFonts.xaxis_tick,
            "yaxis.tickfont.size": defaultFonts.yaxis_tick,
            "legend.font.size": defaultFonts.legend
        });
    }
    // 初回適用
    //resetFonts();

    // ウィンドウリサイズ時に自動調整
    //window.addEventListener("resize", adjustPlotlyFont);

    // -------------------
    // クリックでフルスクリーン化
    // -------------------
    title.addEventListener("click", () => {
        const main = wrap.parentElement; // .main

        // すでにフルスクリーンなら何もしない（戻るボタンで戻る）
        if (wrap.classList.contains("graph-fullscreen")) {
            return;
        }

        // 他のフルスクリーンを解除
        main.querySelectorAll(".graph-fullscreen").forEach(el => el.classList.remove("graph-fullscreen"));

        // フルスクリーン化
        wrap.classList.add("graph-fullscreen");
        Plotly.Plots.resize(graphDiv);
        adjustPlotlyFont();
    });

    // 戻るボタンクリックで元に戻す
    backBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        wrap.classList.remove("graph-fullscreen");
        Plotly.Plots.resize(graphDiv);
        resetFonts();
    });
}