# app.py
import time, threading, queue
from pathlib import Path
import numpy as np
from flask import Flask, render_template_string, jsonify

# --- Simple rule-based classifier for live status ---
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
q = queue.Queue(maxsize=1)
rng = np.random.default_rng(7)

HTML = """
<!doctype html>
<title>Smart Desk Environment — Live</title>
<h2>Smart Desk Environment — Live (Local Simulation)</h2>
<div id="card" style="font-family:system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;"></div>
<p style="color:#666">Status updates once per second.</p>
<script>
async function tick(){
  const r = await fetch('/latest'); const j = await r.json();
  const color = {Good:'#34c759', Moderate:'#ffd60a', Poor:'#ff453a'}[j.label] || 'gray';
  document.getElementById('card').innerHTML =
    `<div style="border:1px solid #ddd;padding:14px;border-left:10px solid ${color};border-radius:6px;max-width:640px;">
       <div style="font-size:18px;margin-bottom:8px;"><b>Status:</b> ${j.label}</div>
       <div>Temp: ${j.temp_c.toFixed(1)} °C | Humidity: ${j.humidity.toFixed(0)}% | Gas: ${j.gas_ppm.toFixed(0)}</div>
       <div style="margin-top:6px"><i>Advice:</i> ${j.advice}</div>
     </div>`;
}
setInterval(tick, 1000); tick();
</script>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/latest")
def latest():
    # get last sample from queue, or fallback
    if q.empty():
        sample = {"temp_c":22.0, "humidity":45.0, "gas_ppm":200.0}
    else:
        sample = q.queue[-1]

    temp = sample["temp_c"]
    hum  = sample["humidity"]
    gas  = sample["gas_ppm"]

    label = classify_env(temp, hum, gas)

    advice = {
        "Good": "All good—keep working!",
        "Moderate": "Crack a window or take a 2-minute break.",
        "Poor": "Air out the room now; consider a short walk."
    }.get(label, "Monitoring...")

    return jsonify({
        "temp_c": float(temp),
        "humidity": float(hum),
        "gas_ppm": float(gas),
        "label": label,
        "advice": advice
    })

def stream():
    # baselines
    base_t, base_h, base_g = 22.0, 45.0, 200.0
    ma_t, ma_h, ma_g = base_t, base_h, base_g

    while True:
        # small drift
        base_t += rng.normal(0, 0.02)
        base_h += rng.normal(0, 0.06)
        base_g += rng.normal(0, 0.8)

        sample = {
            "temp_c": base_t + rng.normal(0, 0.7),
            "humidity": base_h + rng.normal(0, 2.5),
            "gas_ppm": base_g + rng.normal(0, 18)
        }

        # more frequent “bad air” spikes so we see Moderate/Poor
        if rng.random() < 0.10:  # 10% chance
            sample["temp_c"] += rng.normal(3.0, 0.7)
            sample["humidity"] += rng.normal(10.0, 2.0)
            sample["gas_ppm"] += rng.normal(70.0, 15.0)

        # (we keep EMAs out here, but they're not needed for the simple rule)
        if q.full():
            try:
                q.get_nowait()
            except:
                pass
        q.put(sample)

        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=stream, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
