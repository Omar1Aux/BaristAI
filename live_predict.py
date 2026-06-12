from predict import predict_quality


def live_prediction(timeseries_df):

    metrics = {
        "temp_avg": timeseries_df["temp"].mean(),
        "temp_max": timeseries_df["temp"].max(),
        "temp_std": timeseries_df["temp"].std(),

        "pressure_avg": timeseries_df["pressure"].mean(),
        "pressure_max": timeseries_df["pressure"].max(),
        "pressure_std": timeseries_df["pressure"].std(),

        "flow_avg": timeseries_df["flowRate"].mean(),
        "flow_max": timeseries_df["flowRate"].max(),
        "flow_std": timeseries_df["flowRate"].std(),

        "duration_seconds": len(timeseries_df),
        "total_volume": timeseries_df["totalVolume"].max()
    }

    return predict_quality(metrics)