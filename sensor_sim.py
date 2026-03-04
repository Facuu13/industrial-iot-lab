import time
import json
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883

TOPIC_TELEMETRY = "factory/line1/telemetry"
TOPIC_CMD_PREFIX = "factory/line1/cmd/"  # motor | fault_mech | fault_temp


def parse_bool_payload(payload: str):
    """Acepta '0','1','true','false','on','off'."""
    p = payload.strip().lower()
    if p in ("1", "true", "on"):
        return True
    if p in ("0", "false", "off"):
        return False
    return None


def on_connect(client, userdata, flags, rc):
    # rc=0 => conectado OK
    print(f"[MQTT] connected rc={rc}")
    client.subscribe("factory/line1/cmd/#")


def on_message(client, userdata, msg):
    state = userdata["state"]
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore").strip()

    print(f"[MQTT] {topic} -> {payload}")

    # Esperamos topics del estilo: factory/line1/cmd/<name>
    if not topic.startswith(TOPIC_CMD_PREFIX):
        return

    cmd = topic[len(TOPIC_CMD_PREFIX):]  # motor | fault_mech | fault_temp

    if cmd == "motor":
        if payload.lower() == "toggle":
            state["motor_on"] = 0 if state["motor_on"] else 1
        else:
            b = parse_bool_payload(payload)
            if b is None:
                print("[MQTT] motor: payload inválido. Usá 0/1/true/false/on/off/toggle")
                return
            state["motor_on"] = 1 if b else 0

    elif cmd == "fault_mech":
        b = parse_bool_payload(payload)
        if b is None:
            print("[MQTT] fault_mech: payload inválido. Usá 0/1/true/false/on/off")
            return
        state["fault_mech"] = bool(b)

    elif cmd == "fault_temp":
        b = parse_bool_payload(payload)
        if b is None:
            print("[MQTT] fault_temp: payload inválido. Usá 0/1/true/false/on/off")
            return
        state["fault_temp"] = bool(b)

    else:
        print(f"[MQTT] comando desconocido: {cmd}")


def main():
    # Estado compartido entre loop y callbacks MQTT
    state = {
        "motor_on": 0,
        "fault_mech": False,
        "fault_temp": False,
    }

    client = mqtt.Client(client_id="sensor_sim", userdata={"state": state})
    client.on_connect = on_connect
    client.on_message = on_message

    # (opcional, recomendado) last will
    client.will_set("factory/line1/status", "offline", qos=1, retain=True)

    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()
    client.publish("factory/line1/status", "online", qos=1, retain=True)

    try:
        while True:
            motor_on = state["motor_on"]
            fault_mech = state["fault_mech"]
            fault_temp = state["fault_temp"]

            # Flags digitales (como en el PLC)
            speed_ok = 1 if (motor_on and not fault_mech) else 0
            temp_ok = 0 if fault_temp else 1

            data = {
                "ts": round(time.time(), 3),
                "motor_on": motor_on,
                "speed_ok": speed_ok,
                "temp_ok": temp_ok,
                "fault_mech": fault_mech,
                "fault_temp": fault_temp,
            }

            payload = json.dumps(data)
            client.publish(TOPIC_TELEMETRY, payload, qos=0, retain=False)

            print(data)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[EXIT] Ctrl+C")

    finally:
        try:
            client.publish("factory/line1/status", "offline", qos=1, retain=True)
        except Exception:
            pass
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()