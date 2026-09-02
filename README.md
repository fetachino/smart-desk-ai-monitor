# Smart Desk AI Environment Monitor

An IoT-style monitoring system that simulates temperature, humidity, and air-quality readings, classifies environmental conditions, and displays live recommendations in a Flask dashboard.

## Architecture

```text
Sensor simulator -> MQTT broker -> Flask dashboard -> live status/advice
                         |
Synthetic training data -> decision-tree model -> evaluation artifacts
```

## Features

- Local and MQTT-based real-time monitoring modes
- Simulated IoT telemetry with realistic drift and environmental spikes
- Good, Moderate, and Poor environment classification
- Model-training and synthetic-data generation scripts
- Browser dashboard with JSON API updates
- Confusion matrix, class-balance, and decision-tree visualizations

## Stack

Python, Flask, NumPy, pandas, scikit-learn, Joblib, and Paho MQTT.

## Run locally

```console
python -m venv .venv
pip install -r requirements.txt
python app.py
```

For MQTT mode, start `app_mqtt.py` and `sim_device.py` in separate terminals. The public test broker is for demonstration only; do not send sensitive data through it.

## Model evaluation

![Confusion matrix](docs/confusion_matrix.png)

Generated datasets and trained-model binaries are excluded so the analysis remains reproducible from source.

## Course

CSCI 49000 AIT — Artificial Intelligence for IoT, Fall 2025.

## Author

Ahmed Balde
