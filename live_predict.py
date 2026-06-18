from predict import predict_quality


def live_prediction(timeseries_df):

    metrics = {
        "duration": len(timeseries_df),

        "volume_delta":
            timeseries_df["totalVolume"].max()
            - timeseries_df["totalVolume"].min(),

        "temp_avg": timeseries_df["temp"].mean(),
        "temp_min": timeseries_df["temp"].min(),
        "temp_max": timeseries_df["temp"].max(),
        "temp_std": timeseries_df["temp"].std(),

        "pressure_avg": timeseries_df["pressure"].mean(),
        "pressure_min": timeseries_df["pressure"].min(),
        "pressure_max": timeseries_df["pressure"].max(),
        "pressure_std": timeseries_df["pressure"].std(),

        "flow_avg": timeseries_df["flowRate"].mean(),
        "flow_min": timeseries_df["flowRate"].min(),
        "flow_max": timeseries_df["flowRate"].max(),
        "flow_std": timeseries_df["flowRate"].std(),

        "preinfusion": timeseries_df["preinfusion"].max(),
        "preinfusionpause": timeseries_df["preinfusionpause"].max(),
        "setPoint": timeseries_df["setPoint"].max()
    }

    metrics = {
        k: (0 if str(v) == "nan" else float(v))
        for k, v in metrics.items()
    }

    return predict_quality(metrics)