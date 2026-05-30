from ultralytics import YOLO
import cv2

#свою модель туда надо
model = YOLO("final_model.pt")  

DEVICE_TOPICS = {
    "lamp":     "home/socket/command"
}

def detect_device(img):
    """
    Принимает OpenCV изображение (numpy array).
    Возвращает (название_прибора, mqtt_топик) или (None, None).
    """
    if img is None:
        print("Изображение пустое — детекция невозможна")
        return None, None

    results = model(img, conf=0.35, verbose=False)

    best_device = None
    best_topic = None
    best_conf = 0.0

    for r in results:
        for box in r.boxes:
            cls_name = model.names[int(box.cls)]
            conf = float(box.conf)
            print(f"  Обнаружено: {cls_name} ({conf:.0%})")

            if cls_name in DEVICE_TOPICS and conf > best_conf:
                best_device = cls_name
                best_topic = DEVICE_TOPICS[cls_name]
                best_conf = conf

    if best_device:
        print(f"  → Прибор: {best_device}, топик: {best_topic}")
    else:
        print("  → Прибор не распознан")

    return best_device, best_topic