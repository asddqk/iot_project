import cv2
import time
import numpy as np
import requests
import threading

from config import CAM_EYE_IP, CAM_EYE_STREAM
from camera import capture_room_snapshot
from detector import detect_device
from mqtt_sender import send_command

DELTA_THRESHOLD = 2.5
MIN_CLOSED_FRAMES = 2
DOUBLE_BLINK_SEC = 2.0
BLINK_COOLDOWN = 0.4

blink_times = []
frame_counter = 0
last_blink_time = 0

brightness_history = []
delta_history = []
prev_brightness = None


def smooth(values, new_val, max_len=5):
    values.append(new_val)
    if len(values) > max_len:
        values.pop(0)
    return sum(values) / len(values)


def on_double_blink():
    print("\n>>> ДВОЙНОЕ МОРГАНИЕ! <<<")
    img = capture_room_snapshot("snap.jpg")
    if img is None:
        print("Не удалось получить изображение")
        return
    device, topic = detect_device(img)
    if topic:
        send_command(topic, "ON")
    else:
        print("Устройство не найдено")


def get_frame_from_stream(ip):
    """Читает один кадр из MJPEG потока через requests."""
    try:
        url = f"http://{ip}/capture"  # сначала пробуем /capture
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            img_array = np.frombuffer(resp.content, np.uint8)
            return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except:
        pass
    return None


# Пробуем сначала обычный VideoCapture
print("Подключаемся к камере глаза...")
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(CAM_EYE_STREAM)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Проверяем работает ли VideoCapture за 3 секунды
cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)

use_capture_mode = False

# Тест — пробуем прочитать один кадр
ret, test_frame = cap.read()
if not ret:
    print("VideoCapture не работает — переключаемся на /capture режим")
    cap.release()
    use_capture_mode = True
else:
    print("VideoCapture работает!")

print("Готово! Нажми Q для выхода")

while True:
    if use_capture_mode:
        frame = get_frame_from_stream(CAM_EYE_IP)
        if frame is None:
            print("Камера недоступна, жду...")
            time.sleep(0.5)
            continue
        ret = True
    else:
        ret, frame = cap.read()
        if not ret:
            print("Потеря кадра, переподключение...")
            cap.release()
            cap = cv2.VideoCapture(CAM_EYE_STREAM)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    roi = gray[h//3:h//2, w//3:2*w//3]
    brightness = np.mean(roi)
    brightness = smooth(brightness_history, brightness)

    if prev_brightness is None:
        prev_brightness = brightness

    delta = brightness - prev_brightness
    prev_brightness = brightness
    delta_smooth = smooth(delta_history, delta)

    is_blink = delta_smooth > DELTA_THRESHOLD

    if is_blink:
        frame_counter += 1
    else:
        if frame_counter >= MIN_CLOSED_FRAMES:
            now = time.time()
            if now - last_blink_time > BLINK_COOLDOWN:
                blink_times.append(now)
                blink_times[:] = [t for t in blink_times if now - t < DOUBLE_BLINK_SEC]
                print(f"Моргание! ({len(blink_times)}/2)")
                if len(blink_times) >= 2:
                    blink_times.clear()
                    on_double_blink()
                last_blink_time = now
        frame_counter = 0

    # Отображение
    cv2.rectangle(frame, (w//3, h//3), (2*w//3, h//2), (255, 0, 0), 2)
    cv2.putText(frame, f"Blinks: {len(blink_times)}/2",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
    status = "BLINK" if is_blink else "OPEN"
    color = (0, 0, 255) if is_blink else (0, 255, 0)
    cv2.putText(frame, f"Eye: {status}",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Eye Detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if not use_capture_mode:
    cap.release()
cv2.destroyAllWindows()