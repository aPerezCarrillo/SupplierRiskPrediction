import streamlit as st
import shap
import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import joblib
from shap import TreeExplainer, Explanation
from shap.plots import waterfall

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("../data/historical_ds/sliding_window_supplier_data_with_target.csv")  # Update with actual file path

# Load data
data = load_data()

# Prepare features for model
X = data.drop(columns=["supplier_id", "ncr_or_warning_letter", "analysis_start",
                       "analysis_end", "prediction_start", "prediction_end"])
y = data["ncr_or_warning_letter"]

# Load or train the model
@st.cache_resource
def load_model():
    # model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    # model.fit(X, y)
    model = joblib.load("../models/supplier_warning_model.pkl")
    return model

model = load_model()

# Compute SHAP values
@st.cache_resource
def compute_shap():
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)
    exp = Explanation(shap_values.values[:, :, 1],
                      shap_values.base_values[:, 1],
                      data=X.values,
                      feature_names=X.columns)
    return shap_values, explainer, exp

shap_values, explainer, explanation = compute_shap()

# ======================== STREAMLIT DASHBOARD ========================
st.title("📊 Supplier Risk Analysis Dashboard")

# Select a supplier for individual analysis
supplier_ids = data["supplier_id"].tolist()
selected_supplier = st.selectbox("Select a Supplier:", supplier_ids)

# Get selected supplier index
supplier_index = data[data["supplier_id"] == selected_supplier].index[0]

# Display supplier risk probability
risk_prob = model.predict_proba(X.iloc[[supplier_index]])[:, 1][0]
st.metric(label="🔴 Predicted Risk Probability", value=f"{risk_prob:.2%}")

# ======================== SHAP WATERFALL PLOT ========================
st.subheader("📌 Risk Breakdown (SHAP Waterfall Plot)")

fig, ax = plt.subplots(figsize=(10, 6))
waterfall(explanation[supplier_index])
# shap.waterfall_plot(shap_values[supplier_index], max_display=10)
st.pyplot(fig)

# ======================== SHAP SUMMARY PLOT ========================
st.subheader("🌍 Feature Importance Across All Suppliers")

fig, ax = plt.subplots(figsize=(10, 6))
shap.summary_plot(shap_values[:,:,1], X, show=False)
st.pyplot(fig)

# ======================== GLOBAL FEATURE IMPORTANCE ========================
st.subheader("🔎 Global Feature Impact")

# Convert SHAP values into DataFrame
shap_df = pd.DataFrame(shap_values.values[:,:,1], columns=X.columns)
shap_mean = shap_df.abs().mean().sort_values(ascending=False)

# Plot feature importance with Plotly
fig = px.bar(
    shap_mean[::-1],  # Reverse order for better visualization
    x=shap_mean[::-1].values,
    y=shap_mean[::-1].index,
    orientation="h",
    title="Feature Importance (Mean Absolute SHAP Values)",
    labels={"x": "Mean |SHAP Value|", "y": "Feature"},
)
st.plotly_chart(fig)

# ======================== SUPPLIER SEGMENTATION ========================
st.subheader("📊 Risk Segmentation of Suppliers")

# Categorize risk levels
def categorize_risk(prob):
    if prob < 0.3:
        return "Low Risk"
    elif prob < 0.7:
        return "Medium Risk"
    else:
        return "High Risk"

data["risk_category"] = model.predict_proba(X)[:, 1]
data["risk_category"] = data["risk_category"].apply(categorize_risk)

fig = px.histogram(data, x="risk_category", title="Supplier Risk Distribution", color="risk_category")
st.plotly_chart(fig)

# ======================== END OF DASHBOARD ========================
st.markdown("💡 Use this dashboard to analyze supplier risks and identify key factors contributing to compliance issues!")

