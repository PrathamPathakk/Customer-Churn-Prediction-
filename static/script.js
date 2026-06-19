document.addEventListener("DOMContentLoaded", () => {
    // ── Elements ─────────────────────────────────────────────────────────────
    const navbar = document.getElementById("navbar");
    const predictForm = document.getElementById("predict-form");
    const predictBtn = document.getElementById("predict-btn");
    const btnLoader = document.getElementById("btn-loader");
    
    // Form Inputs & Range Values
    const tenureInput = document.getElementById("tenure");
    const tenureVal = document.getElementById("tenure-value");
    const monthlyInput = document.getElementById("MonthlyCharges");
    const monthlyVal = document.getElementById("MonthlyCharges-value");
    const totalChargesInput = document.getElementById("TotalCharges");
    const internetServiceSelect = document.getElementById("InternetService");
    const internetDependents = document.querySelectorAll(".internet-dependent");
    
    // Result elements
    const resultPlaceholder = document.getElementById("result-placeholder");
    const resultContent = document.getElementById("result-content");
    const resultPanel = document.getElementById("result-panel");
    const gaugeFill = document.getElementById("gauge-fill");
    const gaugeValue = document.getElementById("gauge-value");
    const verdictCard = document.getElementById("verdict-card");
    const verdictBadge = document.getElementById("verdict-badge");
    const verdictText = document.getElementById("verdict-text");
    const riskList = document.getElementById("risk-list");
    const resetBtn = document.getElementById("reset-btn");

    // Hero / Dashboard metrics
    const heroChurnRate = document.getElementById("hero-churn-rate");
    const statTotal = document.getElementById("stat-total-value");
    const statChurn = document.getElementById("stat-churn-value");
    const statMonthly = document.getElementById("stat-monthly-value");
    const statTenure = document.getElementById("stat-tenure-value");

    // ── Fetch Dashboard Stats ────────────────────────────────────────────────
    fetch("/api/stats")
        .then(res => res.json())
        .then(data => {
            if (data.error) return;
            
            // Populate metrics
            animateCounter(heroChurnRate, 0, data.churn_rate, "%", 1);
            animateCounter(statTotal, 0, data.total_customers, "", 0);
            animateCounter(statChurn, 0, data.churn_rate, "%", 1);
            animateCounter(statMonthly, 0, data.avg_monthly_charges, "$", 2);
            animateCounter(statTenure, 0, data.avg_tenure, " mo", 1);
        })
        .catch(err => console.error("Error loading dashboard stats:", err));

    // Counter animation helper
    function animateCounter(element, start, end, suffix = "", decimals = 0) {
        let current = start;
        const duration = 1200; // ms
        const steps = 60;
        const stepTime = duration / steps;
        const increment = (end - start) / steps;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                clearInterval(timer);
                current = end;
            }
            if (suffix.startsWith("$")) {
                element.innerText = `$${current.toFixed(decimals)}`;
            } else {
                element.innerText = current.toFixed(decimals) + suffix;
            }
        }, stepTime);
    }

    // ── Interactivity & Dynamic Fields ───────────────────────────────────────
    
    // Scroll effect for Navbar
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.style.padding = "10px 40px";
            navbar.style.background = "rgba(10, 10, 15, 0.9)";
        } else {
            navbar.style.padding = "16px 40px";
            navbar.style.background = "rgba(10, 10, 15, 0.7)";
        }
    });

    // Update range labels on slider inputs
    tenureInput.addEventListener("input", (e) => {
        const val = e.target.value;
        tenureVal.innerText = `${val} mo`;
        updateTotalChargesPlaceholder();
    });

    monthlyInput.addEventListener("input", (e) => {
        const val = parseFloat(e.target.value).toFixed(2);
        monthlyVal.innerText = `$${val}`;
        updateTotalChargesPlaceholder();
    });

    // Smart placeholder generator for Total Charges based on Tenure * Monthly
    function updateTotalChargesPlaceholder() {
        const tenure = parseInt(tenureInput.value);
        const monthly = parseFloat(monthlyInput.value);
        const estimatedTotal = (tenure * monthly).toFixed(2);
        
        // If the user hasn't explicitly customized total charges or it matches default ratio, auto fill
        if (document.activeElement !== totalChargesInput) {
            totalChargesInput.value = estimatedTotal;
        }
    }

    // Disable internet features when No Internet is selected
    function handleInternetDependency() {
        const hasNoInternet = internetServiceSelect.value === "No";
        internetDependents.forEach(group => {
            const select = group.querySelector("select");
            if (hasNoInternet) {
                group.classList.add("disabled");
                select.value = "No internet service";
                select.setAttribute("disabled", "true");
            } else {
                group.classList.remove("disabled");
                if (select.value === "No internet service") {
                    select.value = "No";
                }
                select.removeAttribute("disabled");
            }
        });
    }
    internetServiceSelect.addEventListener("change", handleInternetDependency);
    handleInternetDependency(); // Run initial onload state check

    // ── Form Submission ──────────────────────────────────────────────────────
    predictForm.addEventListener("submit", (e) => {
        e.preventDefault();

        // Loading state
        predictBtn.classList.add("loading");
        predictBtn.setAttribute("disabled", "true");

        // Prepare JSON payload
        const formData = new FormData(predictForm);
        const payload = {};
        
        // Include both enabled and temporarily disabled dropdown values
        const allFormElements = predictForm.querySelectorAll("select, input");
        allFormElements.forEach(el => {
            if (el.name) {
                payload[el.name] = el.value;
            }
        });

        // Call backend API
        fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            // Remove loading indicators
            predictBtn.classList.remove("loading");
            predictBtn.removeAttribute("disabled");

            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }

            displayResult(data);
        })
        .catch(err => {
            predictBtn.classList.remove("loading");
            predictBtn.removeAttribute("disabled");
            alert("Network error: Failed to fetch prediction from server.");
            console.error(err);
        });
    });

    // ── Display Result with Gauge & Risk Factors ─────────────────────────────
    function displayResult(data) {
        // Toggle view
        resultPlaceholder.style.display = "none";
        resultContent.style.display = "flex";
        
        // Scroll to results panel on mobile devices
        if (window.innerWidth <= 1024) {
            resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        const probPercent = Math.round(data.probability * 100);
        
        // Update Gauge Fill:
        // Circle circumference is 534 (2 * PI * r = 2 * 3.14159 * 85).
        // Standard dashoffset is 534 - (percent / 100) * 534.
        const circumference = 534;
        const offset = circumference - (data.probability * circumference);
        
        // Animate counter label inside Gauge
        animateCounter(gaugeValue, 0, probPercent, "%", 0);
        
        // Reset stroke values
        gaugeFill.style.strokeDasharray = circumference;
        gaugeFill.style.strokeDashoffset = circumference;
        
        // Set dynamic gauge color & badge type
        let colorClass = "risk-low";
        let gaugeColor = "var(--accent-green)";
        
        if (data.risk_level === "Medium") {
            colorClass = "risk-medium";
            gaugeColor = "var(--accent-orange)";
        } else if (data.risk_level === "High") {
            colorClass = "risk-high";
            gaugeColor = "var(--accent-red)";
        }

        // Apply gauge attributes
        setTimeout(() => {
            gaugeFill.style.strokeDashoffset = offset;
            gaugeFill.style.stroke = gaugeColor;
        }, 100);

        // Update Verdict Card details
        verdictBadge.className = `verdict-badge ${colorClass}`;
        verdictBadge.innerText = `${data.risk_level} Risk`;
        verdictText.innerText = data.prediction === 1 
            ? `Predicting Customer Churn (${probPercent}% likelihood)` 
            : `Predicting Customer Retention (${100 - probPercent}% likelihood)`;

        // Update Churn Warning style if high risk
        if (data.prediction === 1) {
            verdictCard.style.animation = "pulseGlow 2s infinite";
        } else {
            verdictCard.style.animation = "none";
        }

        // Render Risk Factors list
        riskList.innerHTML = "";
        if (data.risk_factors.length > 0) {
            riskList.parentElement.classList.remove("no-risk");
            riskList.parentElement.querySelector(".risk-title").innerHTML = "⚠️ Risk Factors Identified";
            data.risk_factors.forEach(factor => {
                const li = document.createElement("li");
                li.innerText = factor;
                riskList.appendChild(li);
            });
        } else {
            // Excellent status
            riskList.parentElement.classList.add("no-risk");
            riskList.parentElement.querySelector(".risk-title").innerHTML = "✨ Healthy Profile Parameters";
            const li = document.createElement("li");
            li.innerText = "No critical risk factors identified. Profile indicates strong account health.";
            riskList.appendChild(li);
        }
    }

    // ── Reset Handler ────────────────────────────────────────────────────────
    resetBtn.addEventListener("click", () => {
        // Toggle view back
        resultContent.style.display = "none";
        resultPlaceholder.style.display = "flex";
        
        // Smoothly scroll back to predicting form top
        predictForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});
