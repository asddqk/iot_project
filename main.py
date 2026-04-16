import cv2
import numpy as np
import time
from config import CAM_EYE_STREAM
from camera import capture_room_snapshot
import paho.mqtt.publish as publish

# ===================== НАСТРОЙКИ =====================
DELTA_THRESHOLD = 2.5        # порог скачка яркости
MIN_CLOSED_FRAMES = 2
DOUBLE_BLINK_SEC = 2.0
BLINK_COOLDOWN = 0.4

MQTT_TOPIC = "home/microwave"
MQTT_HOST = "localhost"

# ===================== СОСТОЯНИЕ =====================
blink_times = []
frame_counter = 0
last_blink_time = 0

brightness_history = []
delta_history = []
prev_brightness = None

# ===================== ФУНКЦИИ =====================
def smooth(values, new_val, max_len=5):
    values.append(new_val)
    if len(values) > max_len:
        values.pop(0)
    return sum(values) / len(values)


def on_double_blink():
    print("\n>>> ДВОЙНОЕ МОРГАНИЕ! <<<")

    # пока можно отключить вторую камеру
    img = capture_room_snapshot("snapshot.jpg")
    print("снимок комнаты сделан")

   # publish.single(MQTT_TOPIC, "ON", hostname=MQTT_HOST)
    print("MQTT команда отправлена (отключен временно)")


# ===================== ЗАПУСК =====================
print("Подключаемся к камере...")
cap = cv2.VideoCapture(CAM_EYE_STREAM)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Готово! Нажми Q для выхода")

while True:
    ret, frame = cap.read()
    if not ret:
        cap = cv2.VideoCapture(CAM_EYE_STREAM)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # ROI (область глаза)
    roi = gray[h//3:h//2, w//3:2*w//3]
    brightness = np.mean(roi)

    brightness = smooth(brightness_history, brightness)

    # ===== DELTA =====
    if prev_brightness is None:
        prev_brightness = brightness

    delta = brightness - prev_brightness
    prev_brightness = brightness

    delta_smooth = smooth(delta_history, delta)

    # ===== ДЕТЕКЦИЯ МОРГАНИЯ =====
    is_blink = delta_smooth > DELTA_THRESHOLD

    if is_blink:
        frame_counter += 1
    else:
        if frame_counter >= MIN_CLOSED_FRAMES:
            now = time.time()

            # защита от спама
            if now - last_blink_time > BLINK_COOLDOWN:
                blink_times.append(now)
                blink_times[:] = [t for t in blink_times if now - t < DOUBLE_BLINK_SEC]

                print(f"Моргание! ({len(blink_times)}/2)")

                if len(blink_times) >= 2:
                    blink_times.clear()
                    on_double_blink()

                last_blink_time = now

        frame_counter = 0

    # ===== ВИЗУАЛИЗАЦИЯ =====
    cv2.rectangle(frame,
                  (w//3, h//3),
                  (2*w//3, h//2),
                  (255, 0, 0), 2)

    cv2.putText(frame, f"Brightness: {brightness:.1f}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    cv2.putText(frame, f"Delta: {delta_smooth:.2f}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    cv2.putText(frame, f"Blinks: {len(blink_times)}/2",
                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

    status = "BLINK" if is_blink else "OPEN"
    color = (0, 0, 255) if is_blink else (0, 255, 0)

    cv2.putText(frame, f"Eye: {status}",
                (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Eye Detector", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
