import paho.mqtt.client as mqtt
import time

MQTT_HOST = "m4.wqtt.ru"
MQTT_PORT = 15940
MQTT_USER = "u_W69DQW"
MQTT_PASS = "qqLgilhK"

STATE_TOPIC = "home/socket/state"

def send_command(topic, command="ON"):
    try:
        client = mqtt.Client()
        client.username_pw_set(MQTT_USER, MQTT_PASS)

        client.connect(MQTT_HOST, MQTT_PORT, keepalive=10)
        client.loop_start()

        # команда
        result = client.publish(topic, command, qos=1)
        time.sleep(0.3)
        result.wait_for_publish()

        # состояние устройства
        result2 = client.publish(STATE_TOPIC, command, qos=1)
        time.sleep(0.3)
        result2.wait_for_publish()

        time.sleep(0.3)

        client.loop_stop()
        client.disconnect()

        print(f"MQTT отправлено:")
        print(f"  COMMAND -> [{topic}] {command}")
        print(f"  STATE   -> [{STATE_TOPIC}] {command}")

    except Exception as e:
        print(f"Ошибка MQTT: {e}")