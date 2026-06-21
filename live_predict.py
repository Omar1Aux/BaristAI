from predict import predict_quality


def live_prediction(timeseries_df):
    if timeseries_df.empty:
        return {
            "quality_score": 0,
            "quality_label": "Invalid / Other",
            "model_confidence": 0,
            "note": "No live data available."
        }

    metrics = {
        "brew_duration": len(timeseries_df),

        "temp_avg": timeseries_df["temp"].mean(),
        "temp_min": timeseries_df["temp"].min(),
        "temp_max": timeseries_df["temp"].max(),
        "temp_std": timeseries_df["temp"].std(),

        "pressure_avg": timeseries_df["pressure"].mean(),
        "pressure_min": timeseries_df["pressure"].min(),
        "pressure_max": timeseries_df["pressure"].max(),
        "pressure_std": timeseries_df["pressure"].std(),

        "volume_delta": (
            timeseries_df["totalVolume"].max()
            - timeseries_df["totalVolume"].min()
        ),

        "preinfusion": timeseries_df["preinfusion"].max()
            if "preinfusion" in timeseries_df.columns else 0,

        "preinfusionpause": timeseries_df["preinfusionpause"].max()
            if "preinfusionpause" in timeseries_df.columns else 0,

        "setPoint": timeseries_df["setPoint"].max()
            if "setPoint" in timeseries_df.columns else 90,
    }

    metrics = {
        k: 0 if str(v) == "nan" else float(v)
        for k, v in metrics.items()
    }

    return predict_quality(metrics)