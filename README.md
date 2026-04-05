# 🇮🇳 India Population Prediction Dashboard

An interactive demographic analytics dashboard built with **Python**, **Streamlit**, and **Plotly**.

## 🔮 Features

- **3 ML Prediction Models**: Linear Regression, Polynomial Regression (deg 3), Logistic S-Curve
- **Interactive Year Predictor**: Enter any year (1950–2100) for an instant population estimate
- **Confidence Scoring**: Each prediction comes with a confidence percentage
- **Multiple Charts**:
  - Population Forecast 1950–2075
  - Annual Growth Rate Trend
  - Decadal Census Growth
  - Population Milestones
  - India vs China World Share

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📦 Tech Stack

- **Streamlit** — Dashboard framework
- **Plotly** — Interactive charts
- **scikit-learn** — Linear & Polynomial Regression
- **scipy** — Logistic S-Curve fitting
- **pandas / numpy** — Data processing

## 📊 Data Sources

- UN World Population Prospects
- Census of India (1951–2011)
