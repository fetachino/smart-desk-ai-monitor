# make_data.py
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

def generate_stream(n=6000, seed=42):
    rng = np.random.default_rng(seed)
    t = np.arange(n)

    # Diurnal-ish baselines
    temp = 22 + 4*np.sin(2*np.pi*t/(60*60)) + rng.normal(0, 0.6, n)
    hum  = 45 + 10*np.sin(2*np.pi*(t+900)/(60*60)) + rng.normal(0, 2.0, n)
    gas  = 200 + 50*np.sin(2*np.pi*(t+1800)/(60*30)) + rng.normal(0, 15, n)

    # Occasional spikes to simulate “stuffy” periods
    for start in [1200, 3000, 4800]:
        dur = 300
        temp[start:start+dur] += rng.normal(2.5, 0.7)
        hum[start:start+dur]  += rng.normal(8.0, 1.5)
        gas[start:start+dur]  += rng.normal(60.0, 10.0)

    return pd.DataFrame({"temp_c": temp, "humidity": hum, "gas_ppm": gas})

def bootstrap_label(row):
    """
    Threshold-based labels so we get clear Good / Moderate / Poor.
    """
    temp = row.temp_c
    hum  = row.humidity
    gas  = row.gas_ppm

    # Worst conditions = Poor
    if (temp > 27) or (hum > 60) or (gas > 270):
        return "Poor"
    # Medium conditions = Moderate
    elif (temp > 24.5) or (hum > 52) or (gas > 235):
        return "Moderate"
    # Otherwise = Good
    else:
        return "Good"


def main():
    df = generate_stream(n=6000, seed=42)

    # Optional features (moving averages) to make learning non-trivial
    df["temp_ma5"] = df["temp_c"].rolling(5, min_periods=1).mean()
    df["hum_ma5"]  = df["humidity"].rolling(5, min_periods=1).mean()
    df["gas_ma5"]  = df["gas_ppm"].rolling(5, min_periods=1).mean()

    df["label"] = df.apply(bootstrap_label, axis=1)
    out_csv = OUT / "train_data.csv"
    df.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} with shape {df.shape}")
    print(df["label"].value_counts())

if __name__ == "__main__":
    main()
