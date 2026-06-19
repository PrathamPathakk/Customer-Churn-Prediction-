from pathlib import Path

import pandas as pd
import joblib
from flask import Flask, jsonify, render_template, request

# ── App Setup ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

app = Flask(
    __name__,
    template_folder=str(PROJECT_ROOT / "templates"),
    static_folder=str(PROJECT_ROOT / "static"),
)

# ── Load trained model ─────────────────────────────────────────────────────────
MODEL_PATH = PROJECT_ROOT / "model" / "telco_churn_model.pkl"
model = joblib.load(MODEL_PATH)

# ── Load dataset for dashboard stats ──────────────────────────────────────────
CSV_PATH = PROJECT_ROOT / "dataset" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
df = pd.read_csv(CSV_PATH)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["Churn_binary"] = df["Churn"].map({"No": 0, "Yes": 1})

# ── Feature definitions ───────────────────────────────────────────────────────
FEATURE_ORDER = [
    "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
    "PhoneService", "MultipleLines",
    "InternetService", "OnlineSecurity", "OnlineBackup",
    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
    "Contract", "PaperlessBilling", "PaymentMethod",
    "MonthlyCharges", "TotalCharges",
]

CATEGORICAL_OPTIONS = {
    "gender": ["Male", "Female"],
    "Partner": ["Yes", "No"],
    "Dependents": ["Yes", "No"],
    "PhoneService": ["Yes", "No"],
    "MultipleLines": ["Yes", "No", "No phone service"],
    "InternetService": ["DSL", "Fiber optic", "No"],
    "OnlineSecurity": ["Yes", "No", "No internet service"],
    "OnlineBackup": ["Yes", "No", "No internet service"],
    "DeviceProtection": ["Yes", "No", "No internet service"],
    "TechSupport": ["Yes", "No", "No internet service"],
    "StreamingTV": ["Yes", "No", "No internet service"],
    "StreamingMovies": ["Yes", "No", "No internet service"],
    "Contract": ["Month-to-month", "One year", "Two year"],
    "PaperlessBilling": ["Yes", "No"],
    "PaymentMethod": [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
}


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # Build input DataFrame
        input_data = {}
        for feature in FEATURE_ORDER:
            value = data.get(feature)
            if value is None:
                return jsonify({"error": f"Missing feature: {feature}"}), 400

            if feature in ("SeniorCitizen", "tenure"):
                input_data[feature] = [int(value)]
            elif feature in ("MonthlyCharges", "TotalCharges"):
                input_data[feature] = [float(value)]
            else:
                input_data[feature] = [str(value)]

        sample = pd.DataFrame(input_data)

        prediction = int(model.predict(sample)[0])
        probability = float(model.predict_proba(sample)[0][1])

        # Determine risk level
        if probability < 0.30:
            risk_level = "Low"
        elif probability < 0.60:
            risk_level = "Medium"
        else:
            risk_level = "High"

        # Identify risk factors
        risk_factors = []
        if data.get("Contract") == "Month-to-month":
            risk_factors.append("Month-to-month contract increases churn risk")
        if data.get("InternetService") == "Fiber optic":
            risk_factors.append("Fiber optic customers churn more frequently")
        if int(data.get("tenure", 0)) <= 6:
            risk_factors.append("Short tenure (≤ 6 months) is a strong churn indicator")
        if data.get("PaymentMethod") == "Electronic check":
            risk_factors.append("Electronic check payment correlates with higher churn")
        if float(data.get("MonthlyCharges", 0)) > 70:
            risk_factors.append("High monthly charges (> $70) increase churn likelihood")
        if data.get("OnlineSecurity") == "No":
            risk_factors.append("No online security service increases risk")
        if data.get("TechSupport") == "No":
            risk_factors.append("No tech support subscription detected")
        if data.get("PaperlessBilling") == "Yes":
            risk_factors.append("Paperless billing slightly correlates with churn")
        if int(data.get("SeniorCitizen", 0)) == 1:
            risk_factors.append("Senior citizens have a higher churn rate")

        return jsonify({
            "prediction": prediction,
            "probability": round(probability, 4),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "churn_label": "Will Churn" if prediction == 1 else "Will Not Churn",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
def stats():
    try:
        total = len(df)
        churned = int(df["Churn_binary"].sum())
        churn_rate = round(churned / total * 100, 1)
        avg_monthly = round(float(df["MonthlyCharges"].mean()), 2)
        avg_tenure = round(float(df["tenure"].mean()), 1)
        avg_total = round(float(df["TotalCharges"].mean(skipna=True)), 2)

        # Contract distribution
        contracts = df["Contract"].value_counts().to_dict()

        # Churn by internet service
        internet_churn = (
            df.groupby("InternetService")["Churn_binary"]
            .mean()
            .round(3)
            .to_dict()
        )

        return jsonify({
            "total_customers": total,
            "churned_customers": churned,
            "churn_rate": churn_rate,
            "avg_monthly_charges": avg_monthly,
            "avg_tenure": avg_tenure,
            "avg_total_charges": avg_total,
            "contract_distribution": contracts,
            "internet_churn_rate": internet_churn,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
