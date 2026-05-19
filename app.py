from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

app = Flask(__name__)

model = joblib.load("atm_cash_forecast_model.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        days = int(request.form["days"])

        if days < 1:
            days = 1
        if days > 30:
            days = 30

        forecast = model.forecast(steps=days)

        result = []
        start_date = pd.Timestamp.today().normalize()

        future_dates = pd.date_range(
            start=start_date + pd.Timedelta(days=1),
            periods=days,
            freq="D"
        )

        for i, val in enumerate(forecast):
            val = float(val)

            if val < 50:
                val = np.expm1(val)

            if np.isinf(val) or np.isnan(val):
                val = 0

            result.append({
                "date": future_dates[i].strftime("%d-%b-%Y"),
                "value": round(val, 2)
            })

        return render_template(
            "index.html",
            prediction=result
        )

    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True)