# sim_device.py
import time
import json
import numpy as np
import paho.mqtt.client as mqtt

# ---------- MQTT SETTINGS ----------
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT   = 1883
MQTT_TOPIC  = "ahmed/smartdesk"
# -----------------------------------

rng = np.random.default_rng(123)

def generate_sample(state):
    base_t, base_h, base_g = state

    # small drift of baselines
    base_t += rng.normal(0, 0.02)
    base_h += rng.normal(0, 0.06)
    base_g += rng.normal(0, 0.8)

    sample = {
        "temp_c": base_t + rng.normal(0, 0.7),
        "humidity": base_h + rng.normal(0, 2.5),
        "gas_ppm": base_g + rng.normal(0, 18),
    }

    # more frequent “bad air” events (10% of the time)
    if rng.random() < 0.10:
        sample["temp_c"] += rng.normal(3.0, 0.7)
        sample["humidity"] += rng.normal(10.0, 2.0)
        sample["gas_ppm"] += rng.normal(70.0, 15.0)

    return (base_t, base_h, base_g), sample

def main():
    client = mqtt.Client()
    print(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    state = (22.0, 45.0, 200.0)

    try:
        while True:
            state, sample = generate_sample(state)
            payload = json.dumps(sample)
            client.publish(MQTT_TOPIC, payload)
            print("Published:", payload)
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("Stopping publisher...")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
