# ============================================================
#  models.py  –  Population Prediction Models
#  1. Linear Regression
#  2. Polynomial Regression (degree 3)
#  3. Logistic / S-Curve Model
# ============================================================

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, mean_absolute_error
from scipy.optimize import curve_fit


# ════════════════════════════════════════════════════════
#  1. LINEAR REGRESSION
# ════════════════════════════════════════════════════════
class LinearModel:
    def __init__(self):
        self.model = LinearRegression()
        self.name  = "Linear Regression"
        self.color = "#f97316"   # orange

    def fit(self, years: np.ndarray, populations: np.ndarray):
        X = years.reshape(-1, 1)
        self.model.fit(X, populations)
        preds   = self.model.predict(X)
        self.r2  = r2_score(populations, preds)
        self.mae = mean_absolute_error(populations, preds)
        return self

    def predict(self, year) -> int:
        X = np.array([[year]])
        return max(0, int(self.model.predict(X)[0]))

    def predict_range(self, years) -> np.ndarray:
        X = np.array(years).reshape(-1, 1)
        return np.maximum(0, self.model.predict(X)).astype(int)


# ════════════════════════════════════════════════════════
#  2. POLYNOMIAL REGRESSION (degree 3)
# ════════════════════════════════════════════════════════
class PolynomialModel:
    def __init__(self, degree: int = 3):
        self.degree = degree
        self.model  = make_pipeline(PolynomialFeatures(degree), LinearRegression())
        self.name   = f"Polynomial (deg {degree})"
        self.color  = "#10b981"  # green

    def fit(self, years: np.ndarray, populations: np.ndarray):
        X = years.reshape(-1, 1)
        self.model.fit(X, populations)
        preds   = self.model.predict(X)
        self.r2  = r2_score(populations, preds)
        self.mae = mean_absolute_error(populations, preds)
        return self

    def predict(self, year) -> int:
        X = np.array([[year]])
        return max(0, int(self.model.predict(X)[0]))

    def predict_range(self, years) -> np.ndarray:
        X = np.array(years).reshape(-1, 1)
        return np.maximum(0, self.model.predict(X)).astype(int)


# ════════════════════════════════════════════════════════
#  3. LOGISTIC S-CURVE MODEL
#     P(t) = K / (1 + exp(-r*(t - t0)))
# ════════════════════════════════════════════════════════
def _logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))


class LogisticModel:
    def __init__(self):
        self.name  = "Logistic (S-Curve)"
        self.color = "#8b5cf6"  # purple
        self.params = None

    def fit(self, years: np.ndarray, populations: np.ndarray):
        p0 = [1_750_000_000, 0.03, 2035]
        bounds = ([1e9, 0.001, 1990], [2.5e9, 0.2, 2080])
        popt, _ = curve_fit(
            _logistic, years, populations.astype(float),
            p0=p0, bounds=bounds, maxfev=10_000
        )
        self.params = popt  # K, r, t0
        preds   = _logistic(years, *popt)
        self.r2  = r2_score(populations, preds)
        self.mae = mean_absolute_error(populations, preds)
        return self

    def predict(self, year) -> int:
        return max(0, int(_logistic(year, *self.params)))

    def predict_range(self, years) -> np.ndarray:
        return np.maximum(0, _logistic(np.array(years, dtype=float), *self.params)).astype(int)

    @property
    def carrying_capacity(self) -> float:
        return self.params[0] if self.params is not None else None

    @property
    def inflection_year(self) -> float:
        return self.params[2] if self.params is not None else None


# ════════════════════════════════════════════════════════
#  MODEL MANAGER  –  fits + exposes all models
# ════════════════════════════════════════════════════════
class PopulationModelSuite:
    def __init__(self):
        self.linear     = LinearModel()
        self.polynomial = PolynomialModel(degree=3)
        self.logistic   = LogisticModel()
        self._fitted    = False

    def fit(self, years, populations):
        yrs  = np.array(years, dtype=float)
        pops = np.array(populations, dtype=float)
        self.linear.fit(yrs, pops)
        self.polynomial.fit(yrs, pops)
        self.logistic.fit(yrs, pops)
        self._fitted = True
        return self

    def predict_all(self, year: int) -> dict:
        assert self._fitted, "Call .fit() first"
        return {
            "Linear":     self.linear.predict(year),
            "Polynomial": self.polynomial.predict(year),
            "Logistic":   self.logistic.predict(year),
        }

    def forecast_df(self, future_years) -> pd.DataFrame:
        assert self._fitted
        return pd.DataFrame({
            "year":       future_years,
            "Linear":     self.linear.predict_range(future_years),
            "Polynomial": self.polynomial.predict_range(future_years),
            "Logistic":   self.logistic.predict_range(future_years),
        })

    def model_stats(self) -> pd.DataFrame:
        rows = []
        for m in [self.linear, self.polynomial, self.logistic]:
            rows.append({
                "Model":  m.name,
                "R² Score": f"{m.r2:.6f}",
                "MAE (millions)": f"{m.mae / 1e6:.2f}M",
            })
        return pd.DataFrame(rows)

    def find_peak_year(self) -> int:
        """Year when logistic growth peaks (annual additions drop to ~0)."""
        prev = self.logistic.predict(2030)
        for y in range(2031, 2110):
            curr = self.logistic.predict(y)
            if curr <= prev:
                return y - 1
            prev = curr
        return 2100


# ── Formatting helpers ─────────────────────────────────────────
def fmt_pop(n: int, short=False) -> str:
    if short:
        if n >= 1e9:  return f"{n/1e9:.2f}B"
        if n >= 1e6:  return f"{n/1e6:.1f}M"
        return f"{n:,}"
    if n >= 1e9:  return f"{n/1e9:.3f} Billion"
    if n >= 1e7:  return f"{n/1e7:.2f} Crore"
    return f"{n:,}"


def confidence_score(year: int, current_year: int = 2024) -> int:
    dist = abs(year - current_year)
    return max(40, int(98 - dist * 0.6))
