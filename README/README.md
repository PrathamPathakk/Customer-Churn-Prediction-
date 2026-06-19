# Telco Customer Churn Prediction

## Overview

This project predicts whether a telecom customer is likely to churn (leave the company) using Machine Learning.

The model is trained on the IBM Telco Customer Churn dataset containing customer demographics, account information, services subscribed, and billing details.

---

## Dataset

Dataset: IBM Telco Customer Churn Dataset

Features include:

* Gender
* Senior Citizen
* Partner
* Dependents
* Tenure
* Internet Service
* Online Security
* Online Backup
* Device Protection
* Tech Support
* Contract Type
* Payment Method
* Monthly Charges
* Total Charges

Target Variable:

* Churn

  * Yes = 1
  * No = 0

---

## Project Structure

```text
Telco-Churn-Prediction/
│
├── Main app/
│   └── app.py
│
├── model/
│   └── telco_churn_model.pkl
│
├── notebook/
│   └── churn_analysis.ipynb
│
├── static/
│
├── templates/
│
├── WA_Fn-UseC_-Telco-Customer-Churn.csv
│
├── requirements.txt
│
├── README.md
│
└── .gitignore
```

---

## Data Preprocessing

* Removed customerID column
* Converted TotalCharges to numeric
* Handled missing values
* One-Hot Encoding for categorical features
* Feature Scaling for numerical features

---

## Machine Learning Model

Algorithm Used:

* Gradient Boosting Classifier

Pipeline:

* Missing Value Imputation
* One-Hot Encoding
* Standard Scaling
* Classification Model

---

## Model Performance

| Metric            | Score |
| ----------------- | ----- |
| Training Accuracy | 84%   |
| Testing Accuracy  | 80%   |
| ROC-AUC Score     | 0.85  |
| F1 Score          | 0.61  |

---

## Installation

Clone Repository

```bash
git clone https://github.com/yourusername/Telco-Churn-Prediction.git
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Application

```bash
python app.py
```

---

## Sample Prediction

Example Input:

```python
{
    "gender":"Male",
    "SeniorCitizen":0,
    "Partner":"Yes",
    "Dependents":"No",
    "tenure":2,
    "PhoneService":"Yes",
    "MultipleLines":"No",
    "InternetService":"Fiber optic",
    "OnlineSecurity":"No",
    "OnlineBackup":"No",
    "DeviceProtection":"No",
    "TechSupport":"No",
    "StreamingTV":"Yes",
    "StreamingMovies":"Yes",
    "Contract":"Month-to-month",
    "PaperlessBilling":"Yes",
    "PaymentMethod":"Electronic check",
    "MonthlyCharges":95.50,
    "TotalCharges":190.75
}
```

Output:

```text
Customer Will Churn
```

---

## Technologies Used

* Python
* Pandas
* NumPy
* Scikit-Learn
* Flask
* Jupyter Notebook

---

## Future Improvements

* XGBoost Implementation
* CatBoost Implementation
* Hyperparameter Optimization
* Streamlit Dashboard
* SHAP Explainable AI

---

## Author

Pratham Pathak
