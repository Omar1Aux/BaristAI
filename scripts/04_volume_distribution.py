import pandas as pd
import matplotlib.pyplot as plt

summary = pd.read_csv("data/process_summary.csv")

plt.figure(figsize=(10,6))
plt.hist(summary["total_volume_max"], bins=30)
plt.xlabel("Total Volume")
plt.ylabel("Count")
plt.title("Distribution of Total Volume")
plt.grid()

plt.show()