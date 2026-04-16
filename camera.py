import requests
import cv2
import numpy as np
from config import CAM_ROOM_CAPTURE

def capture_room_snapshot(save_path="snapshot.jpg"):
    try:
        resp = requests.get(CAM_ROOM_CAPTURE, timeout=5)
        if resp.status_code == 200:
            img_array = np.frombuffer(resp.content, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            cv2.imwrite(save_path, img)
            print(f"Снимок сохранён: {save_path}")
            return img
        else:
            print(f"Ошибка камеры: {resp.status_code}")
    except Exception as e:
        print(f"Не удалось получить снимок: {e}")
    return None