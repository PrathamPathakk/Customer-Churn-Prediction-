
import pandas as pd
import numpy as np

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    StratifiedKFold
)


from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    f1_score
)

from sklearn.ensemble import RandomForestClassifier

import joblib

df = pd.read_csv("WA_Fn-UseC_-Telco-Customer-Churn.csv")

print("Dataset Shape:", df.shape)


df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"],
    errors="coerce"
)

df.drop("customerID", axis=1, inplace=True)

df["Churn"] = df["Churn"].map({
    "No":0,
    "Yes":1
})


X = df.drop("Churn", axis=1)
y = df["Churn"]

numeric_features = X.select_dtypes(
    include=["int64", "float64"]
).columns

categorical_features = X.select_dtypes(
    include=["object"]
).columns

print("\nNumeric Columns")
print(numeric_features)

print("\nCategorical Columns")
print(categorical_features)


numeric_transformer = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="median")
    ),
    (
        "scaler",
        StandardScaler()
    )
])

categorical_transformer = Pipeline([
    (
        "imputer",
        SimpleImputer(strategy="most_frequent")
    ),
    (
        "onehot",
        OneHotEncoder(
            handle_unknown="ignore"
        )
    )
])

preprocessor = ColumnTransformer([
    (
        "num",
        numeric_transformer,
        numeric_features
    ),
    (
        "cat",
        categorical_transformer,
        categorical_features
    )
])


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

rf = RandomForestClassifier(
    class_weight="balanced",
    random_state=42
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", rf)
])


param_grid = {

    "model__n_estimators":
        [200,300,500,700,1000],

    "model__max_depth":
        [5,10,15,20,None],

    "model__min_samples_split":
        [2,5,10],

    "model__min_samples_leaf":
        [1,2,4],

    "model__max_features":
        ["sqrt","log2"]
}



cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


search = RandomizedSearchCV(
    pipeline,
    param_distributions=param_grid,
    n_iter=30,
    cv=cv,
    scoring="roc_auc",
    verbose=2,
    n_jobs=-1,
    random_state=42
)

search.fit(
    X_train,
    y_train
)


best_model = search.best_estimator_

print("\nBest Parameters")
print(search.best_params_)

train_pred = best_model.predict(X_train)

train_accuracy = accuracy_score(
    y_train,
    train_pred
)

print("\nTraining Accuracy:", train_accuracy)

y_pred = best_model.predict(X_test)

test_accuracy = accuracy_score(
    y_test,
    y_pred
)

print("Testing Accuracy:", test_accuracy)

gap = train_accuracy - test_accuracy

print("\nAccuracy Gap:", round(gap,4))

if gap > 0.10:
    print("Model is OVERFITTING")
elif gap < 0.03:
    print("Model is WELL GENERALIZED")
else:
    print("Slight Overfitting but Acceptable")


y_prob = best_model.predict_proba(
    X_test
)[:,1]



accuracy = accuracy_score(
    y_test,
    y_pred
)

f1 = f1_score(
    y_test,
    y_pred
)

roc = roc_auc_score(
    y_test,
    y_prob
)

print("\nAccuracy:", accuracy)
print("F1 Score:", f1)
print("ROC AUC:", roc)

print("\nClassification Report")
print(
    classification_report(
        y_test,
        y_pred
    )
)

print("\nConfusion Matrix")
print(
    confusion_matrix(
        y_test,
        y_pred
    )
)

joblib.dump(
    best_model,
    "telco_churn_model.pkl"
)

print("\nModel Saved")

import pandas as pd
import joblib

model = joblib.load(
    "telco_churn_model.pkl"
)

sample = pd.DataFrame({
    
     "gender": ["Female"],
    "SeniorCitizen": [0],
    "Partner": ["No"],
    "Dependents": ["No"],
    "tenure": [2],

    "PhoneService": ["Yes"],
    "MultipleLines": ["No"],

    "InternetService": ["Fiber optic"],
    "OnlineSecurity": ["No"],
    "OnlineBackup": ["No"],
    "DeviceProtection": ["No"],
    "TechSupport": ["No"],

    "StreamingTV": ["No"],
    "StreamingMovies": ["No"],

    "Contract": ["Month-to-month"],
    "PaperlessBilling": ["Yes"],
    "PaymentMethod": ["Electronic check"],

    "MonthlyCharges": [70.70],
    "TotalCharges": [151.65]


})




prediction = model.predict(sample)[0]
probability = model.predict_proba(sample)[0][1]

print("Churn Probability:", probability)

if prediction == 1:
    print("Customer Will Churn")
else:
    print("Customer Will Not Churn")