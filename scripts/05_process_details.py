import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet("data/segmented_rancilio_data.parquet")

processes = [7,68,34,29,56]

for pid in processes:

    g = df[df["process_id"]==pid].reset_index(drop=True)

    fig, ax = plt.subplots(4,1,figsize=(12,10))

    ax[0].plot(g["temp"])
    ax[0].set_title("Temperature")

    ax[1].plot(g["pressure"])
    ax[1].set_title("Pressure")

    ax[2].plot(g["flowRate"])
    ax[2].set_title("Flow Rate")

    ax[3].plot(g["totalVolume"])
    ax[3].set_title("Total Volume")

    plt.suptitle(f"Process {pid}")
    plt.tight_layout()
    plt.show()