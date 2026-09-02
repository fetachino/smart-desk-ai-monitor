# app_mqtt.py
import json
import threading
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from flask import Flask, jsonify, render_template_string
import paho.mqtt.client as mqtt

# ---------- MQTT SETTINGS ----------
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT   = 1883
MQTT_TOPIC  = "ahmed/smartdesk"
# -----------------------------------

# Simple rule-based classifier (same logic as training)
def classify_env(temp, hum, gas):
    # Tuned for your actual data so we see all 3 states
    # Poor = clearly bad spike
    if (temp > 23.5) or (hum > 49.5) or (gas > 225.0):
        return "Poor"
    # Moderate = somewhat above normal
    elif (temp > 22.3) or (hum > 46.0) or (gas > 205.0):
        return "Moderate"
    # Otherwise Good
    else:
        return "Good"


app = Flask(__name__)

latest_sample: Optional[Dict[str, float]] = None
lock = threading.Lock()

HTML = """
<!doctype html>
<title>Smart Desk Environment Live Simulation Software Version</title>
<h2>Smart Desk Environment Live Simulation Software Version</h2>
<div id="card" style="font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;"></div>
<p style="color:#666">Status updates whenever new MQTT data arrives.</p>
<hr style="margin-top:40px;">
<p style="text-align:center; color:#666; font-size:14px;">
  Created by Ahmed Balde CSCI 49000 AIT Final Project
</p>
<script>
async function tick(){
  const r = await fetch('/latest');
  const j = await r.json();
  const color = {Good:'#34c759', Moderate:'#ffd60a', Poor:'#ff453a'}[j.label] || 'gray';
  document.getElementById('card').innerHTML =
    `<div style="border:1px solid #ddd;padding:14px;border-left:10px solid ${color};border-radius:6px;max-width:640px;">
       <div style="font-size:18px;margin-bottom:8px;"><b>Status:</b> ${j.label}</div>
       <div>Temp: ${j.temp_c.toFixed(1)} °C | Humidity: ${j.humidity.toFixed(0)}% | Gas: ${j.gas_ppm.toFixed(0)}</div>
       <div style="margin-top:6px"><i>Advice:</i> ${j.advice}</div>
     </div>`;
}
setInterval(tick, 1200); tick();
</script>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/latest")
def latest():
    global latest_sample
    with lock:
        sample = latest_sample

    if sample is None:
        # fallback before first MQTT message
        temp = 22.0
        hum  = 45.0
        gas  = 200.0
    else:
        temp = sample["temp_c"]
        hum  = sample["humidity"]
        gas  = sample["gas_ppm"]

    label = classify_env(temp, hum, gas)
    print(f"DEBUG status: temp={temp:.1f} hum={hum:.1f} gas={gas:.1f} -> {label}", flush=True)


    advice = {
        "Good": "All good keep working!",
        "Moderate": "Crack a window or take a 2 minute break.",
        "Poor": "Air out the room now and consider a short walk."
    }.get(label, "Monitoring...")

    return jsonify({
        "temp_c": float(temp),
        "humidity": float(hum),
        "gas_ppm": float(gas),
        "label": label,
        "advice": advice
    })

# ---------- MQTT HANDLERS ----------

def on_connect(client, userdata, flags, rc, properties=None):
    print("MQTT connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_sample
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        t = float(data.get("temp_c", 22.0))
        h = float(data.get("humidity", 45.0))
        g = float(data.get("gas_ppm", 200.0))

        with lock:
            latest_sample = {
                "temp_c": t,
                "humidity": h,
                "gas_ppm": g
            }
    except Exception as e:
        print("Error in on_message:", e)

def start_mqtt():
    # use VERSION2 to avoid deprecation warnings
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    print(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# ---------- MAIN ----------

if __name__ == "__main__":
    threading.Thread(target=start_mqtt, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
